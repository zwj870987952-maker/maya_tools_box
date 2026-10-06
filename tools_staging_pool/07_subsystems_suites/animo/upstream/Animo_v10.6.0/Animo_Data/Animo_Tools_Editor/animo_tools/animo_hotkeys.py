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

import hotkey_utils as hotkey_utils
HOTKEY_REGISTRY = hotkey_utils.HOTKEY_REGISTRY
validate_hotkey_name = hotkey_utils.validate_hotkey_name
is_hotkey_name_available = hotkey_utils.is_hotkey_name_available
generate_unique_name = hotkey_utils.generate_unique_name
parse_hotkey_modifiers = hotkey_utils.parse_hotkey_modifiers
parse_hotkey_string = hotkey_utils.parse_hotkey_string

import hotkey_binding as hotkey_binding
unbind_existing_hotkey = hotkey_binding.unbind_existing_hotkey
cleanup_old_hotkey = hotkey_binding.cleanup_old_hotkey
assign_hotkey = hotkey_binding.assign_hotkey
remove_hotkey = hotkey_binding.remove_hotkey
