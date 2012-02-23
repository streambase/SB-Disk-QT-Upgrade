#!/usr/bin/python

SSQL_HEADER = '''---
---                    THIS IS A GENERATED FILE.
--- It was created from gen_disk_qt_upgrade.py changes made to this file
--- will be lost if the generate script is rerun.
---

CREATE INPUT STREAM ReadAll (
    start int
);
'''

SSQL_FOOTER = '''
CREATE OUTPUT STREAM Finished ;
APPLY JAVA "com.streambase.sb.adapter.logger.Log" AS Log (
    messageIdentifier = "done", 
    logLevel = "Warn", 
    customFormat = "", 
    verbose = "false", 
    messagePrefix = ""
) FROM ReadAll INTO Finished;
'''

SSQL_SKEY_TEMPL = '''
	SECONDARY KEY (%s) USING BTREE'''

SSQL_TEMPL = '''
--
-- Begin template for %(TableName)s
--
CREATE SCHEMA %(TableName)sSchema %(Schema)s;
CREATE TABLE SCHEMA %(TableName)sTableSchema %(TableName)sSchema
	PRIMARY KEY (%(pkey)s) USING BTREE %(skey_templ)s
;
CREATE DISK TABLE %(TableName)s %(TableName)sTableSchema;
CREATE OUTPUT STREAM %(TableName)sReadOut;
SELECT %(TableName)s.*
FROM ReadAll, %(TableName)s
WHERE true INTO %(TableName)sReadOut;

CREATE INPUT STREAM %(TableName)sWriteIn %(Schema)s;
REPLACE INTO %(TableName)s
SELECT %(TableName)sWriteIn.*
FROM %(TableName)sWriteIn;
--
-- End template for %(TableName)s
--
'''

def make_table_export(table_def):
    skeys = table_def['skeys']
    skey_templ = ''
    for s in skeys:
        skey_templ += SSQL_SKEY_TEMPL % s

    table_def['skey_templ'] = skey_templ
    return SSQL_TEMPL % table_def
    
def make_ssql_file(table_defs):
    res = SSQL_HEADER
    for td in table_defs:
        res += make_table_export(td)
    res += SSQL_FOOTER
    return res

SHELL_HEADER = '''#!/bin/bash
###
###                    THIS IS A GENERATED FILE.
### It was created from gen_disk_qt_upgrade.py changes made to this file
### will be lost if the generate script is rerun.
###

# 1) manually start two sbds
#  - the old one should be started with the old version of StreamBase
#  - the new one should be started with the new version of StreamBase
#  sbd -p 10000 --datadir data-old
#  sbd -p 10001 --datadir data-new
# 2) wait for the computer to finish computing (this will be quick for small tables)
# 3) stop both sbds

sbadmin -p 10000 addContainer %(container)s upgrade-disk-qt.ssql
sbadmin -p 10001 addContainer %(container)s upgrade-disk-qt.ssql
'''

SHELL_TEMPL = '''
sbadmin modifyContainer %(container)s addConnection '(sb://localhost:10001/%(container)s.%(TableName)sWriteIn)=%(container)s.%(TableName)sReadOut' '''

SHELL_FOOTER = '''
echo 1 | sbc enq %(container)s.ReadAll
'''

def make_shell_file(container, table_defs):
    res = SHELL_HEADER % { 'container' : container }
    for td in table_defs:
        td['container'] = container
        res += SHELL_TEMPL % td
    res += SHELL_FOOTER % { 'container' : container }
    return res

if __name__ == '__main__':
    wct2 = { 
        'TableName' : 'WorkspaceConfigurationTable2',
        'Schema' : '''( 
            Id string,
            Name string,
            Area string,
            Description string,
            Owner string,
            IsActive boolean,
            Data blob,
            Layout blob)''',
        'pkey' : 'Id',
        'skeys' : ['Area', 'Owner']
    }
    uwct = {
        'TableName' : 'UserWorkspaceConfigurationTable',
        'Schema' : '''(
            Username string,
            WorkspaceId string,
            Layout blob,
            IsActive boolean)''',
        'pkey' : 'Username, WorkspaceId',
        'skeys' : []
    }
    uct = {
        'TableName' : 'UserConfigurationTable',
        'Schema' : '''(
            Username string,
            Layout blob)''',
        'pkey' : 'Username',
        'skeys' : []
    }
    tables = [wct2, uwct, uct]

    f = open('upgrade-disk-qt.ssql', 'w')
    f.write(make_ssql_file(tables))
    f.close()

    f = open('driver.sh', 'w')
    f.write(make_shell_file('GuiLayout', tables))
    f.close()

    import os, stat
    os.chmod('driver.sh', stat.S_IXUSR | os.stat('driver.sh').st_mode)


