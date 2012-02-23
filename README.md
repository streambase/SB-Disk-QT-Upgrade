# StreamBase Disk Query Table Upgrade Helper #

This utility will help upgrade disk querytables between versions of StreamBase.

1. Update the schemas in `gen_disk_qt_upgrade.py` `__main__` section.  The generation methods support upgrading multiple tables in the same app simulatenously.

    1. Update the table definitions

            example_table = { 
                # TableName -> the table to upgrade
                'TableName' : 'WorkspaceConfigurationTable2',

                # Schema -> the table's schema in ssql form
                'Schema' : '''( 
                    x int,
                    y int,
                    z int,
                    name string)''',

                # pkey -> comma separated list of fields
                'pkey' : 'name, x',

                # skeys -> list of comma separated lists of fields
                'skeys' : ['y, z', 'z']
            }

    2. Update the list of tables and container names

            tables = [example_table1, example_table2]
            container = 'table_container'

2. run `gen_disk_qt_upgrade.py`
3. manually start two sbds

    1. the old one should be started with the old version of StreamBase on port 10000
    
            sbd -p 10000 --datadir data-old

    2. the new one should be started with the new version of StreamBase on port 10001

            sbd -p 10001 --datadir data-new

4. run the `driver.sh` shell script
5. wait for the computer to finish computing (this will be quick for small tables)


