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
    print(tool_path)

    command = '''
    import imp, os, sys
if not r'{0}' in sys.path:
    sys.path.insert(0, r'{0}')
try:
    imp.reload(RetimeTools)
except:
    import RetimeTools
finally:
    w = RetimeTools.Window()
    w.display()
'''.format(tool_path).strip()
    print(command)
    cmds.shelfButton(stp='python',
                     iol=u'',
                     parent=cur_shelf,
                     ann=u'RetimeTools',
                     i="{}/eblabs_retime.png".format(tool_path),
                     c=command)
    cmds.confirmDialog(title='eblabs_RetimeTools',
                       message=u'      安 装 成 功',
                       button=[u'好的'])
