import os
from maya import cmds
from maya import mel
import inspect

def main():
    top_shelf = mel.eval('$nul = $gShelfTopLevel')
    cur_shelf = cmds.tabLayout(top_shelf, q=1, st=1)
    tool_path = os.path.dirname(inspect.getfile(inspect.currentframe()))
    command = "\n    import imp, os, sys\nif not r'{0}' in sys.path:\n    sys.path.insert(0, r'{0}')\n\nimport eblabs_hub.WorldSpaceTools.scripts.worldspace as tool\ntool.window.load()\n".format(tool_path).strip()
    print(command)
    cmds.shelfButton(stp='python', iol=u'', parent=cur_shelf, ann=u'', i='{}/eblabs_hub/WorldSpaceTools/images/eblabs_worldSpaceTools.png'.format(tool_path), c=command)
    cmds.confirmDialog(title=u'提示', message='Installation Successful.', button=['OK'])
