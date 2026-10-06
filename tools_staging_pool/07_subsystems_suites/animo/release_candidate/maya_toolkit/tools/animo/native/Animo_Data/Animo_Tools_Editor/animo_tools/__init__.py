from __future__ import absolute_import, division, print_function, unicode_literals

import os
import sys

def _get_this_dir():
    if hasattr(sys, '_animo_tools_path') and sys._animo_tools_path:
        return sys._animo_tools_path
    try:
        return os.path.dirname(os.path.abspath(__file__))
    except NameError:
        pass
    try:
        import maya.cmds as cmds
        maya_scripts_dir = cmds.internalVar(userScriptDir=True)
        global_scripts_dir = os.path.normpath(os.path.join(maya_scripts_dir, "..", "..", "scripts"))
        return os.path.join(global_scripts_dir, "Animo_Data", "Animo_Tools_Editor", "animo_tools")
    except:
        return ""

_this_dir = _get_this_dir()
if _this_dir and _this_dir not in sys.path:
    sys.path.insert(0, _this_dir)

__version__ = "1.0.0"
__author__ = "Animo Tools"

import animo_tools_manager as animo_tools_manager
show_animo_tools = animo_tools_manager.show_animo_tools
animo_dialog = animo_tools_manager.animo_dialog

import dialog_main as dialog_main
AnimoToolsDialog = dialog_main.AnimoToolsDialog

import animo_icons as animo_icons
IconManager = animo_icons.IconManager

import animo_widgets as animo_widgets
ToolButton = animo_widgets.ToolButton
ToolItem = animo_widgets.ToolItem
HotkeyLineEdit = animo_widgets.HotkeyLineEdit

import animo_dialogs as animo_dialogs
ScriptEditorDialog = animo_dialogs.ScriptEditorDialog

import animo_data as animo_data
import animo_hotkeys as animo_hotkeys
