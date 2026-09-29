# -*- coding:utf-8 -*- 
import os


try:
    import maya.mel as mel
    import maya.cmds as cmds
    isMaya = True
except ImportError:
    isMaya = False

def onMayaDroppedPythonFile(*args, **kwargs):
    """This function is only supported since Maya 2017 Update 3"""
    pass

def _onMayaDropped():
    """Dragging and dropping this file into the scene executes the file."""
    srcPath = os.path.join(os.path.dirname(__file__), 'thRigToolsFiles')
    iconPath = os.path.join(srcPath, 'thLibrary', 'data', 'resource', 'icons')
    srcPath = os.path.normpath(srcPath)
    iconPath = os.path.normpath(iconPath)
    if not os.path.exists(iconPath):
        raise IOError('Cannot find ' + iconPath)
    command = '''\
import os
import sys
    
if not os.path.exists(r'{path}'):
    raise IOError(r'The source path "{path}" does not exist!')
if r'{path}' not in sys.path:
    sys.path.insert(0, r'{path}')

import thLibrary.main as th
reload(th)
'''
    command = command.format(path=srcPath)
    shelf = mel.eval('$gShelfTopLevel=$gShelfTopLevel')
    parent = cmds.tabLayout(shelf, query=True, selectTab=True)
    cmds.shelfButton(
        command=command+'win = th.ThShowRigWin("zh")',
        annotation='TH RIG TOOLS',
        sourceType='Python',
        image=os.path.join(iconPath, 'icon.png'),
        image1=os.path.join(iconPath, 'icon.png'),
        parent=parent
    )

if isMaya:
    _onMayaDropped()
