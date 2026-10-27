from maya_toolkit.tools.rdm_tools_v2.support import legacy_reload, bundled_scripts_dir, checked_output, explicit_ui_input
smoothAmount = 4
bsNode = 'IBIS_BS'
targetBS = 'LBrowUP'


def run_script():
    exec(compile("middleVtx = cmds.ls(sl=True)\nonSide = cmds.ls(sl=True)\noffSide = cmds.ls(sl=True)\nsmoothAmount = 4\nbsNode = 'IBIS_BS'\ntargetBS = 'LBrowUP'\nvertices = cmds.ls(sl=True)\nweights = cmds.getAttr('IBIS_BS.inputTarget[0].inputTargetGroup[10].targetWeights[607]')", __file__, "exec"), globals())
