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

import hashlib
import time
import re
import maya.cmds as cmds

import animo_compat as compat
IS_MAC = compat.IS_MAC

HOTKEY_REGISTRY = {}

def validate_hotkey_name(name):
    if not name or not name.strip():
        return None
    
    name = name.strip()
    name = re.sub(r'[^a-zA-Z0-9_]', '_', name)
    
    if name and name[0].isdigit():
        name = '_' + name
    
    name = re.sub(r'_+', '_', name)
    name = name.rstrip('_')
    
    if len(name) < 1:
        return None
    
    if len(name) > 50:
        name = name[:50]
    
    return name

def is_hotkey_name_available(name):
    if not name:
        return False
    
    for registered_name in HOTKEY_REGISTRY.values():
        if registered_name == name:
            return False
    
    try:
        result = cmds.runTimeCommand(name + "Cmd", query=True, command=True)
        if result:
            return False
    except Exception:
        pass
    
    try:
        result = cmds.nameCommand(name + "Name", query=True, command=True)
        if result:
            return False
    except Exception:
        pass
    
    return True

def generate_unique_name(hotkey, command, tool_name=None):
    if tool_name:
        cleaned_name = validate_hotkey_name(tool_name)
        if cleaned_name and is_hotkey_name_available(cleaned_name):
            return cleaned_name
        else:
            if cleaned_name:
                base_name = cleaned_name
            else:
                base_name = "animo_tool"
            
            command_hash = hashlib.md5(command.encode('utf-8')).hexdigest()[:6]
            timestamp = str(int(time.time()))[-4:]
            return "{0}_{1}_{2}".format(base_name, timestamp, command_hash)
    
    command_hash = hashlib.md5(command.encode('utf-8')).hexdigest()[:8]
    timestamp = str(int(time.time()))[-6:]
    
    clean_hotkey = hotkey.replace("+", "_").replace(" ", "")
    clean_hotkey = re.sub(r'[^a-zA-Z0-9_]', '_', clean_hotkey)
    
    unique_name = "animo_{0}_{1}_{2}".format(clean_hotkey, timestamp, command_hash)
    return unique_name

def parse_hotkey_modifiers(hotkey):
    if not IS_MAC and "Cmd+" in hotkey:
        hotkey = hotkey.replace("Cmd+", "Ctrl+")
    
    ctl = "Ctrl+" in hotkey
    alt = "Alt+" in hotkey
    sht = "Shift+" in hotkey
    cmd = "Cmd+" in hotkey
    
    key = hotkey.split("+")[-1].strip()
    
    if key.isdigit() or key.isalpha():
        key = key.lower()
    
    return ctl, alt, sht, cmd, key

def parse_hotkey_string(hotkey_str):
    parts = [p.strip() for p in hotkey_str.split('+')]
    
    ctl = any(p in ['Ctrl', 'ctrl', 'Control', 'control'] for p in parts)
    alt = any(p in ['Alt', 'alt'] for p in parts)
    sht = any(p in ['Shift', 'shift'] for p in parts)
    cmd = any(p in ['Cmd', 'cmd', 'Command', 'command'] for p in parts)
    
    key = None
    for part in parts:
        if part.lower() not in ['ctrl', 'control', 'alt', 'shift', 'cmd', 'command']:
            key = part
            break
    
    return key, ctl, alt, sht, cmd
