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

import maya.cmds as cmds

import animo_compat as compat
IS_MAC = compat.IS_MAC

import hotkey_utils as hotkey_utils
HOTKEY_REGISTRY = hotkey_utils.HOTKEY_REGISTRY
generate_unique_name = hotkey_utils.generate_unique_name
parse_hotkey_modifiers = hotkey_utils.parse_hotkey_modifiers
parse_hotkey_string = hotkey_utils.parse_hotkey_string

def unbind_existing_hotkey(key, ctl=False, alt=False, sht=False, cmd=False):
    try:
        hotkey_key = key
        use_shift = sht
        
        shift_char_map = {
            '1': '!', '2': '@', '3': '#', '4': '$', '5': '%',
            '6': '^', '7': '&', '8': '*', '9': '(', '0': ')',
            '-': '_', '=': '+', '[': '{', ']': '}', '\\': '|',
            ';': ':', "'": '"', ',': '<', '.': '>', '/': '?', '`': '~'
        }
        
        if sht and key in shift_char_map:
            hotkey_key = shift_char_map[key]
            use_shift = False
        elif sht and len(key) == 1 and key.isalpha():
            hotkey_key = key.upper()
            use_shift = True
        
        if IS_MAC and cmd:
            cmds.hotkey(keyShortcut=hotkey_key, ctl=ctl, alt=alt, sht=use_shift, cmd=cmd, name='', releaseName='')
        else:
            cmds.hotkey(keyShortcut=hotkey_key, ctl=ctl, alt=alt, sht=use_shift, name='', releaseName='')
    except Exception:
        pass

def cleanup_old_hotkey(hotkey):
    if hotkey in HOTKEY_REGISTRY:
        old_name = HOTKEY_REGISTRY[hotkey]
        
        ctl, alt, sht, cmd, key = parse_hotkey_modifiers(hotkey)
        
        unbind_existing_hotkey(key, ctl, alt, sht, cmd)
        
        try:
            result = cmds.runTimeCommand(old_name + "Cmd", query=True, command=True)
            if result:
                cmds.runTimeCommand(old_name + "Cmd", edit=True, delete=True)
        except Exception:
            pass
        
        try:
            result = cmds.nameCommand(old_name + "Name", query=True, command=True)
            if result:
                cmds.nameCommand(old_name + "Name", edit=True, delete=True)
        except Exception:
            pass
        
        del HOTKEY_REGISTRY[hotkey]
    else:
        ctl, alt, sht, cmd, key = parse_hotkey_modifiers(hotkey)
        
        unbind_existing_hotkey(key, ctl, alt, sht, cmd)

def assign_hotkey(command, hotkey_str, tool_name=None, language="python"):
    try:
        ctl, alt, sht, cmd, key = parse_hotkey_modifiers(hotkey_str)
        
        if not key:
            return False, "Invalid hotkey format"
        
        current_set = cmds.hotkeySet(query=True, current=True)
        
        if current_set == "Maya_Default":
            custom_set_name = "animo_hotkeys"
            
            if not cmds.hotkeySet(custom_set_name, query=True, exists=True):
                cmds.hotkeySet(custom_set_name, source="Maya_Default")
            
            cmds.hotkeySet(custom_set_name, edit=True, current=True)
            current_set = custom_set_name
        
        cleanup_old_hotkey(hotkey_str)
        
        if sht and key in ['1','2','3','4','5','6','7','8','9','0','-','=','[',']','\\',';',"'",'.',',','/','`']:
            try:
                cmds.hotkey(keyShortcut=key, sht=True, name='', releaseName='')
            except Exception:
                pass
        
        unique_name = generate_unique_name(hotkey_str, command, tool_name)
        
        annotation_text = "Animo: {0}".format(hotkey_str)
        if tool_name:
            annotation_text = "Animo: {0}".format(tool_name)
        
        final_command = command
        if language == "python":
            lines = command.split('\n')
            has_import = any('import' in line and 'cmds' in line for line in lines)
            if not has_import:
                final_command = "import maya.cmds as cmds\n" + command
        
        command_name = unique_name + "Cmd"
        name_command = unique_name + "Name"
        
        if cmds.runTimeCommand(command_name, exists=True):
            cmds.runTimeCommand(command_name, edit=True, delete=True)
        
        cmds.runTimeCommand(
            command_name,
            annotation=annotation_text,
            category="Animo Tools",
            commandLanguage=language,
            command=final_command
        )
        
        try:
            cmds.nameCommand(name_command, annotation=annotation_text, command=command_name)
        except Exception:
            try:
                cmds.nameCommand(name_command, edit=True, annotation=annotation_text, command=command_name)
            except Exception:
                pass
        
        hotkey_key = key
        use_shift = sht
        
        shift_char_map = {
            '1': '!', '2': '@', '3': '#', '4': '$', '5': '%',
            '6': '^', '7': '&', '8': '*', '9': '(', '0': ')',
            '-': '_', '=': '+', '[': '{', ']': '}', '\\': '|',
            ';': ':', "'": '"', ',': '<', '.': '>', '/': '?', '`': '~'
        }
        
        if sht and key in shift_char_map:
            hotkey_key = shift_char_map[key]
            use_shift = False
        elif sht and len(key) == 1 and key.isalpha():
            hotkey_key = key.upper()
            use_shift = True
        
        try:
            if IS_MAC and cmd:
                cmds.hotkey(keyShortcut=hotkey_key, ctl=ctl, alt=alt, sht=use_shift, cmd=cmd, name=name_command)
                cmds.hotkey(keyShortcut=hotkey_key, ctl=ctl, alt=alt, sht=use_shift, cmd=cmd, releaseName='')
            else:
                cmds.hotkey(keyShortcut=hotkey_key, ctl=ctl, alt=alt, sht=use_shift, name=name_command)
                cmds.hotkey(keyShortcut=hotkey_key, ctl=ctl, alt=alt, sht=use_shift, releaseName='')
        except Exception:
            cmds.hotkey(keyShortcut=hotkey_key, ctl=ctl, alt=alt, sht=use_shift, name=name_command)
            cmds.hotkey(keyShortcut=hotkey_key, ctl=ctl, alt=alt, sht=use_shift, releaseName='')
        
        try:
            cmds.hotkeySet(current_set, edit=True, save=True)
            cmds.savePrefs(hotkeys=True)
        except Exception:
            pass
        
        HOTKEY_REGISTRY[hotkey_str] = unique_name
        
        return True, "Hotkey assigned successfully"
        
    except Exception as e:
        return False, str(e)

def remove_hotkey(hotkey_str):
    try:
        key, ctrl, alt, shift, cmd = parse_hotkey_string(hotkey_str)
        
        if not key:
            return False
        
        unbind_existing_hotkey(key, ctrl, alt, shift, cmd)
        
        if hotkey_str in HOTKEY_REGISTRY:
            del HOTKEY_REGISTRY[hotkey_str]
        
        return True
        
    except Exception:
        return False
