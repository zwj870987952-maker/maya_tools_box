from maya_toolkit.tools.rdm_tools_v2.support import legacy_reload, bundled_scripts_dir, checked_output, explicit_ui_input
from maya import cmds

def OrientJoints(oj='xzy', sao='zup', *args):
    cmds.undoInfo(openChunk=True)
    cmds.makeIdentity(a=1, t=1, r=1, s=1, n=0, pn=1)
    cmds.joint(e=True, zso=True, oj=oj, sao=sao)
    cmds.undoInfo(closeChunk=True)
    print('Orient joint')


def run_script():
    exec(compile('', __file__, "exec"), globals())
