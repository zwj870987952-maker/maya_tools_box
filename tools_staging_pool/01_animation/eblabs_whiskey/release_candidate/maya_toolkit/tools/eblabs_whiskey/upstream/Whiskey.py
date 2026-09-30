# -*- coding: utf-8 -*-
###################################################################


import os
from maya import cmds
from maya import mel
import inspect


def main():
    top_shelf = mel.eval('$nul = $gShelfTopLevel')
    cur_shelf = cmds.tabLayout(top_shelf, q=1, st=1)
    tool_path = os.path.dirname(inspect.getfile(inspect.currentframe()))
    command = '''
    import imp, os, sys
if not r'{0}' in sys.path:
    sys.path.insert(0, r'{0}')

import eblabs_hub.Whiskey.scripts.WhiskeyPro as tool
tool.window.load()
'''.format(tool_path).strip()
    cmds.shelfButton(stp='python',
                     iol=u'',
                     parent=cur_shelf,
                     ann=u'',
                     i="{}/eblabs_hub/Whiskey/images/whisKEYPro.png".format(tool_path),
                     c=command)
    cmds.confirmDialog(title=u'提示',
                       message='Installation Successful.',
                       button=['OK'])


main()
