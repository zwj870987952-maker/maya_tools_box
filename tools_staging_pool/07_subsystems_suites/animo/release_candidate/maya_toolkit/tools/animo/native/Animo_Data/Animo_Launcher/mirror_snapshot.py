import maya.cmds as cmds

import mirror_launcher as ml


def snapshotAllControls():
    userSelection = cmds.ls(selection=True) or []
    if not userSelection:
        ml._warn("Select one or more controls on the rig, then run this script "
                  "again so it can auto-select the rest and snapshot the "
                  "default pose.")
        return

    allCtrls = ml.autoSelectAllCtrls(userSelection)
    if not allCtrls:
        ml._warn("Auto-select all controls failed for this rig. Please select "
                  "all controls on the rig yourself, then run this script "
                  "again so it can do a snapshot for a perfect mirror "
                  "experience.")
        return

    cmds.select(allCtrls, replace=True)
    originalSelection = cmds.ls(selection=True) or []

    confirm = cmds.confirmDialog(
        title="Mirror Snapshot",
        message="Is this the default pose?",
        button=["Yes", "Cancel"],
        defaultButton="Yes",
        cancelButton="Cancel",
        dismissString="Cancel")
    if confirm != "Yes":
        return

    ml.beginProgress("Snapshotting All Controls", 100)
    ml.updateProgress(20, "Calculating mirror axes & L/R pairs...")

    tableData = ml.buildMirrorTableData(allCtrls)

    ml.updateProgress(90, "Saving settings...")
    cmds.select(originalSelection, replace=True)

    if not tableData or not tableData.get("controls"):
        ml.endProgress()
        ml._warn("Snapshot failed - no valid controls were found.")
        return

    ml.saveMirrorTableToDisk(tableData)
    ml.endProgress()


snapshotAllControls()