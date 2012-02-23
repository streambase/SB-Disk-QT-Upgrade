#!/bin/bash
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

sbadmin -p 10000 addContainer GuiLayout upgrade-disk-qt.ssql
sbadmin -p 10001 addContainer GuiLayout upgrade-disk-qt.ssql

sbadmin modifyContainer GuiLayout addConnection '(sb://localhost:10001/GuiLayout.WorkspaceConfigurationTable2WriteIn)=GuiLayout.WorkspaceConfigurationTable2ReadOut' 
sbadmin modifyContainer GuiLayout addConnection '(sb://localhost:10001/GuiLayout.UserWorkspaceConfigurationTableWriteIn)=GuiLayout.UserWorkspaceConfigurationTableReadOut' 
sbadmin modifyContainer GuiLayout addConnection '(sb://localhost:10001/GuiLayout.UserConfigurationTableWriteIn)=GuiLayout.UserConfigurationTableReadOut' 
echo 1 | sbc enq GuiLayout.ReadAll
