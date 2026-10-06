from maya import OpenMayaUI as omui
import maya.cmds as cmds
import time
import hashlib
import json
import os
import platform
import re
from datetime import datetime

try:
    from PySide6 import QtWidgets, QtGui, QtCore
    from shiboken6 import wrapInstance
except ImportError:
    from PySide2 import QtWidgets, QtGui, QtCore
    from shiboken2 import wrapInstance

HOTKEY_REGISTRY = {}

IS_MAC = platform.system() == "Darwin"
DEBUG_HOTKEYS = True


def debug_log(msg):
    if DEBUG_HOTKEYS:
        print("[HotkeyMod DEBUG] {0}".format(msg))


def get_animo_hotkeys_path():
    try:
        animo_prefs_path = os.path.normpath(os.path.join(
            cmds.internalVar(userScriptDir=True), '..', '..', 'scripts', 'Animo_Data', 'Animo_Prefs'
        ))
        if not os.path.exists(animo_prefs_path):
            os.makedirs(animo_prefs_path)
        return animo_prefs_path
    except:
        return os.path.expanduser('~')


def validate_custom_name(name):
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


def is_custom_name_available(custom_name):
    if not custom_name:
        return False
    
    for registered_name in HOTKEY_REGISTRY.values():
        if registered_name == custom_name:
            return False
    
    try:
        result = cmds.runTimeCommand(custom_name + "Cmd", query=True, command=True)
        if result:
            return False
    except RuntimeError:
        pass
    except Exception:
        pass
    
    try:
        result = cmds.nameCommand(custom_name + "Name", query=True, command=True)
        if result:
            return False
    except RuntimeError:
        pass
    except Exception:
        pass
    
    return True


def save_hotkey_to_json(command, hotkey, language, unique_name, custom_name=None, tool_name=None):
    try:
        hotkeys_path = get_animo_hotkeys_path()
        json_file_path = os.path.join(hotkeys_path, "animo_hotkeys_data.json")
        
        hotkeys_data = []
        if os.path.exists(json_file_path):
            try:
                with open(json_file_path, 'r', encoding='utf-8') as f:
                    hotkeys_data = json.load(f)
            except:
                hotkeys_data = []
        
        new_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "hotkey": hotkey,
            "language": language,
            "command": command,
            "unique_name": unique_name,
            "custom_name": custom_name,
            "tool_name": tool_name,
            "display_name": tool_name if tool_name else (custom_name if custom_name else unique_name),
            "status": "active",
            "platform": platform.system()
        }
        
        for entry in hotkeys_data:
            if entry.get("hotkey") == hotkey and entry.get("status") == "active":
                entry["status"] = "replaced"
                entry["replaced_timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        hotkeys_data.append(new_entry)
        
        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(hotkeys_data, f, indent=4, ensure_ascii=False)
        
    except Exception:
        pass


def generate_unique_name(hotkey, command, custom_name=None):
    if custom_name:
        cleaned_name = validate_custom_name(custom_name)
        if cleaned_name and is_custom_name_available(cleaned_name):
            return cleaned_name
        else:
            if cleaned_name:
                base_name = cleaned_name
            else:
                base_name = "animo_hotkey"
            
            command_hash = hashlib.md5(command.encode('utf-8')).hexdigest()[:6]
            timestamp = str(int(time.time()))[-4:]
            return "{0}_{1}_{2}".format(base_name, timestamp, command_hash)
    
    command_hash = hashlib.md5(command.encode('utf-8')).hexdigest()[:8]
    timestamp = str(int(time.time()))[-6:]
    
    clean_hotkey = hotkey.replace("+", "_").replace(" ", "")
    clean_hotkey = re.sub(r'[^a-zA-Z0-9_]', '_', clean_hotkey)
    
    unique_name = "animo_{0}_{1}_{2}".format(clean_hotkey, timestamp, command_hash)
    return unique_name


def unbind_existing_hotkey(key, ctl=False, alt=False, sht=False):
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
        
        cmds.hotkey(keyShortcut=hotkey_key, ctl=ctl, alt=alt, sht=use_shift, name='', releaseName='')
    except:
        pass


def parse_hotkey_modifiers(hotkey):
    debug_log("Parsing hotkey: '{0}'".format(hotkey))
    debug_log("  Platform: {0} (IS_MAC={1})".format(platform.system(), IS_MAC))
    
    has_cmd = "Cmd+" in hotkey
    has_ctrl = "Ctrl+" in hotkey
    
    debug_log("  Found Cmd+: {0}, Found Ctrl+: {1}".format(has_cmd, has_ctrl))
    
    if IS_MAC:
        if has_cmd:
            ctl = True
        else:
            ctl = has_ctrl
    else:
        if has_cmd:
            ctl = True
        else:
            ctl = has_ctrl
    
    alt = "Alt+" in hotkey
    sht = "Shift+" in hotkey
    
    key = hotkey.split("+")[-1].strip()
    
    if key.isdigit() or key.isalpha():
        key = key.lower()
    
    debug_log("  Result -> ctl={0}, alt={1}, sht={2}, key='{3}'".format(ctl, alt, sht, key))
    
    return ctl, alt, sht, key


def cleanup_old_hotkey(hotkey):
    if hotkey in HOTKEY_REGISTRY:
        old_name = HOTKEY_REGISTRY[hotkey]
        
        ctl, alt, sht, key = parse_hotkey_modifiers(hotkey)
        
        unbind_existing_hotkey(key, ctl, alt, sht)
        
        try:
            result = cmds.runTimeCommand(old_name + "Cmd", query=True, command=True)
            if result:
                cmds.runTimeCommand(old_name + "Cmd", edit=True, delete=True)
        except:
            pass
        
        try:
            result = cmds.nameCommand(old_name + "Name", query=True, command=True)
            if result:
                cmds.nameCommand(old_name + "Name", edit=True, delete=True)
        except:
            pass
        
        del HOTKEY_REGISTRY[hotkey]
    else:
        ctl, alt, sht, key = parse_hotkey_modifiers(hotkey)
        unbind_existing_hotkey(key, ctl, alt, sht)


def assign_hotkey(command, hotkey, language="python", custom_name=None, tool_name=None):
    debug_log("=" * 50)
    debug_log("ASSIGN_HOTKEY CALLED")
    debug_log("  hotkey: '{0}'".format(hotkey))
    debug_log("  tool_name: {0}".format(tool_name))
    debug_log("  custom_name: {0}".format(custom_name))
    
    ctl, alt, sht, key = parse_hotkey_modifiers(hotkey)
    
    current_set = cmds.hotkeySet(query=True, current=True)
    
    if current_set == "Maya_Default":
        custom_set_name = "animo_hotkeys"
        
        if not cmds.hotkeySet(custom_set_name, query=True, exists=True):
            cmds.hotkeySet(custom_set_name, source="Maya_Default")
        
        cmds.hotkeySet(custom_set_name, edit=True, current=True)
        current_set = custom_set_name
    
    cleanup_old_hotkey(hotkey)
    
    if sht and key in ['1','2','3','4','5','6','7','8','9','0','-','=','[',']','\\',';',"'",'.',',','/','`']:
        try:
            cmds.hotkey(keyShortcut=key, sht=True, name='', releaseName='')
        except:
            pass
    
    unique_name = generate_unique_name(hotkey, command, custom_name)
    
    annotation_text = "Animo hotkey: {0}".format(hotkey)
    if tool_name:
        annotation_text = "{0} ({1})".format(tool_name, hotkey)
    elif custom_name:
        annotation_text += " (Name: {0})".format(custom_name)
    
    final_command = command
    if language == "python":
        lines = command.split('\n')
        has_import = any('import' in line and 'cmds' in line for line in lines)
        if not has_import:
            final_command = "import maya.cmds as cmds\n" + command
    
    runtime_cmd_name = unique_name + "Cmd"
    name_cmd_name = unique_name + "Name"
    
    try:
        if cmds.runTimeCommand(runtime_cmd_name, query=True, exists=True):
            cmds.runTimeCommand(runtime_cmd_name, edit=True, delete=True)
    except:
        pass
    
    cmds.runTimeCommand(runtime_cmd_name,
                        annotation=annotation_text,
                        category="Animo Tools",
                        commandLanguage=language,
                        command=final_command)

    try:
        cmds.nameCommand(name_cmd_name,
                        annotation=annotation_text,
                        command=runtime_cmd_name)
    except:
        try:
            cmds.nameCommand(name_cmd_name, edit=True, 
                           annotation=annotation_text,
                           command=runtime_cmd_name)
        except:
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
        debug_log("  Shift+symbol detected, converted '{0}' -> '{1}', use_shift=False".format(key, hotkey_key))
    elif sht and len(key) == 1 and key.isalpha():
        hotkey_key = key.upper()
        use_shift = True
        debug_log("  Shift+letter detected, key='{0}', use_shift=True".format(hotkey_key))
    
    debug_log("  FINAL MAYA BINDING:")
    debug_log("    keyShortcut='{0}'".format(hotkey_key))
    debug_log("    ctl={0}".format(ctl))
    debug_log("    alt={0}".format(alt))
    debug_log("    sht={0}".format(use_shift))
    debug_log("    nameCommand='{0}'".format(name_cmd_name))
    
    try:
        cmds.hotkey(keyShortcut=hotkey_key,
                    ctl=ctl,
                    alt=alt,
                    sht=use_shift,
                    name=name_cmd_name)
        cmds.hotkey(keyShortcut=hotkey_key,
                    ctl=ctl,
                    alt=alt,
                    sht=use_shift,
                    releaseName='')
        debug_log("  Maya hotkey binding SUCCESS")
    except Exception as e:
        debug_log("  Maya hotkey binding FAILED: {0}".format(str(e)))
    
    try:
        cmds.hotkeySet(current_set, edit=True, save=True)
        cmds.savePrefs(hotkeys=True)
    except:
        pass
    
    HOTKEY_REGISTRY[hotkey] = unique_name

    save_hotkey_to_json(command, hotkey, language, unique_name, custom_name, tool_name)

    platform_note = " (using Ctrl internally)" if IS_MAC and "Cmd+" in hotkey else ""
    display_name = tool_name if tool_name else (custom_name if custom_name else "command")
    set_note = " [Created animo_hotkeys set]" if current_set == "animo_hotkeys" else ""
    cmds.inViewMessage(
        amg='<span style="color:#82C99A;">Hotkey {0} assigned to {1}{2}{3}</span>'.format(
            hotkey, display_name, platform_note, set_note
        ),
        pos='topCenter', fade=True, fadeStayTime=1500
    )


class HotkeyCapture(QtWidgets.QLineEdit):
    def __init__(self, *args, **kwargs):
        super(HotkeyCapture, self).__init__(*args, **kwargs)
        self.setPlaceholderText("Press hotkey combination...")
        self.setReadOnly(True)
        self.hotkey = ""
        self.manual_mode = False
        
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def show_context_menu(self, position):
        menu = QtWidgets.QMenu(self)
        menu.setStyleSheet('''
            QMenu { background-color: #3a3a3a; border: 1px solid #555; padding: 3px; }
            QMenu::item { padding: 6px 20px; color: #ccc; }
            QMenu::item:selected { background-color: #555; color: #fff; }
        ''')
        
        manual_action = menu.addAction("Type hotkey manually")
        clear_action = menu.addAction("Clear")
        menu.addSeparator()
        capture_action = menu.addAction("Switch to key capture mode")
        
        action = menu.exec_(self.mapToGlobal(position))
        
        if action == manual_action:
            self.enable_manual_mode()
        elif action == clear_action:
            self.clear_hotkey()
        elif action == capture_action:
            self.enable_capture_mode()

    def enable_manual_mode(self):
        self.manual_mode = True
        self.setReadOnly(False)
        example = "Cmd+Alt+D" if IS_MAC else "Ctrl+Alt+D"
        self.setPlaceholderText("Type hotkey (e.g., {0}, Shift+F1)...".format(example))
        self.setStyleSheet("background-color: #3C3C3C; border: 1px solid #82C99A; color: #E0E0E0; padding: 8px; border-radius: 4px;")
        self.selectAll()
        self.setFocus()

    def enable_capture_mode(self):
        self.manual_mode = False
        self.setReadOnly(True)
        self.setPlaceholderText("Press hotkey combination...")
        self.setStyleSheet("")

    def clear_hotkey(self):
        self.clear()
        self.hotkey = ""

    def focusOutEvent(self, event):
        if self.manual_mode:
            manual_text = self.text().strip()
            if manual_text:
                self.hotkey = manual_text
            self.enable_capture_mode()
        super(HotkeyCapture, self).focusOutEvent(event)

    def keyPressEvent(self, event):
        if self.manual_mode:
            if event.key() in [QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter]:
                manual_text = self.text().strip()
                if manual_text:
                    self.hotkey = manual_text
                self.enable_capture_mode()
                return
            elif event.key() == QtCore.Qt.Key_Escape:
                self.enable_capture_mode()
                return
            else:
                super(HotkeyCapture, self).keyPressEvent(event)
                return

        mods = []
        modifiers = event.modifiers()
        
        debug_log("-" * 40)
        debug_log("KEY PRESS EVENT")
        debug_log("  Qt key code: {0}".format(event.key()))
        debug_log("  Qt modifiers (raw): {0}".format(str(modifiers)))
        debug_log("  event.text(): '{0}'".format(event.text()))
        debug_log("  nativeVirtualKey: {0}".format(event.nativeVirtualKey()))
        debug_log("  nativeScanCode: {0}".format(event.nativeScanCode()))
        
        if IS_MAC:
            debug_log("  MAC modifier check (Qt swaps Ctrl/Meta on Mac):")
            debug_log("    ControlModifier (physical Cmd ⌘): {0}".format(bool(modifiers & QtCore.Qt.ControlModifier)))
            debug_log("    MetaModifier (physical Ctrl ^): {0}".format(bool(modifiers & QtCore.Qt.MetaModifier)))
            if modifiers & QtCore.Qt.ControlModifier:
                mods.append("Cmd")
            if modifiers & QtCore.Qt.MetaModifier:
                mods.append("Ctrl")
        else:
            debug_log("  WINDOWS modifier check:")
            debug_log("    ControlModifier: {0}".format(bool(modifiers & QtCore.Qt.ControlModifier)))
            debug_log("    MetaModifier (Win key): {0}".format(bool(modifiers & QtCore.Qt.MetaModifier)))
            if modifiers & QtCore.Qt.ControlModifier:
                mods.append("Ctrl")
            if modifiers & QtCore.Qt.MetaModifier:
                if "Ctrl" not in mods:
                    mods.append("Ctrl")
        
        if modifiers & QtCore.Qt.AltModifier:
            mods.append("Alt")
            debug_log("    AltModifier (Option ⌥ on Mac): True")
        if modifiers & QtCore.Qt.ShiftModifier:
            mods.append("Shift")
            debug_log("    ShiftModifier: True")
        
        debug_log("  Modifiers collected: {0}".format(mods))

        special_keys = {
            QtCore.Qt.Key_Space: "Space",
            QtCore.Qt.Key_Tab: "Tab",
            QtCore.Qt.Key_Return: "Return",
            QtCore.Qt.Key_Enter: "Return",
            QtCore.Qt.Key_Escape: "Escape",
            QtCore.Qt.Key_Backspace: "BackSpace",
            QtCore.Qt.Key_Delete: "Delete",
            QtCore.Qt.Key_Insert: "Insert",
            QtCore.Qt.Key_Home: "Home",
            QtCore.Qt.Key_End: "End",
            QtCore.Qt.Key_PageUp: "Page_Up",
            QtCore.Qt.Key_PageDown: "Page_Down",
            QtCore.Qt.Key_Up: "Up",
            QtCore.Qt.Key_Down: "Down",
            QtCore.Qt.Key_Left: "Left",
            QtCore.Qt.Key_Right: "Right",
            QtCore.Qt.Key_F1: "F1", QtCore.Qt.Key_F2: "F2", QtCore.Qt.Key_F3: "F3",
            QtCore.Qt.Key_F4: "F4", QtCore.Qt.Key_F5: "F5", QtCore.Qt.Key_F6: "F6",
            QtCore.Qt.Key_F7: "F7", QtCore.Qt.Key_F8: "F8", QtCore.Qt.Key_F9: "F9",
            QtCore.Qt.Key_F10: "F10", QtCore.Qt.Key_F11: "F11", QtCore.Qt.Key_F12: "F12",
        }

        key_str = ""
        
        if event.key() in special_keys:
            key_str = special_keys[event.key()]
            debug_log("  Key found in special_keys: '{0}'".format(key_str))
        elif IS_MAC:
            native_key = event.nativeVirtualKey()
            mac_keycode_map = {
                0: "A", 1: "S", 2: "D", 3: "F", 4: "H", 5: "G", 6: "Z", 7: "X",
                8: "C", 9: "V", 11: "B", 12: "Q", 13: "W", 14: "E", 15: "R",
                16: "Y", 17: "T", 18: "1", 19: "2", 20: "3", 21: "4", 22: "6",
                23: "5", 24: "=", 25: "9", 26: "7", 27: "-", 28: "8", 29: "0",
                30: "]", 31: "O", 32: "U", 33: "[", 34: "I", 35: "P", 37: "L",
                38: "J", 39: "'", 40: "K", 41: ";", 42: "\\", 43: ",", 44: "/",
                45: "N", 46: "M", 47: ".", 50: "`", 36: "Return", 48: "Tab",
                49: "Space", 51: "BackSpace", 53: "Escape", 117: "Delete",
                115: "Home", 119: "End", 116: "Page_Up", 121: "Page_Down",
                123: "Left", 124: "Right", 125: "Down", 126: "Up"
            }
            
            if native_key in mac_keycode_map:
                key_str = mac_keycode_map[native_key]
                debug_log("  Mac native keycode {0} -> '{1}'".format(native_key, key_str))
            else:
                debug_log("  Mac native keycode {0} not in map, trying Qt key...".format(native_key))
                key_map = {
                    QtCore.Qt.Key_A: "A", QtCore.Qt.Key_B: "B", QtCore.Qt.Key_C: "C", QtCore.Qt.Key_D: "D",
                    QtCore.Qt.Key_E: "E", QtCore.Qt.Key_F: "F", QtCore.Qt.Key_G: "G", QtCore.Qt.Key_H: "H",
                    QtCore.Qt.Key_I: "I", QtCore.Qt.Key_J: "J", QtCore.Qt.Key_K: "K", QtCore.Qt.Key_L: "L",
                    QtCore.Qt.Key_M: "M", QtCore.Qt.Key_N: "N", QtCore.Qt.Key_O: "O", QtCore.Qt.Key_P: "P",
                    QtCore.Qt.Key_Q: "Q", QtCore.Qt.Key_R: "R", QtCore.Qt.Key_S: "S", QtCore.Qt.Key_T: "T",
                    QtCore.Qt.Key_U: "U", QtCore.Qt.Key_V: "V", QtCore.Qt.Key_W: "W", QtCore.Qt.Key_X: "X",
                    QtCore.Qt.Key_Y: "Y", QtCore.Qt.Key_Z: "Z",
                    QtCore.Qt.Key_0: "0", QtCore.Qt.Key_1: "1", QtCore.Qt.Key_2: "2", QtCore.Qt.Key_3: "3",
                    QtCore.Qt.Key_4: "4", QtCore.Qt.Key_5: "5", QtCore.Qt.Key_6: "6", QtCore.Qt.Key_7: "7",
                    QtCore.Qt.Key_8: "8", QtCore.Qt.Key_9: "9",
                    QtCore.Qt.Key_Period: ".", QtCore.Qt.Key_Comma: ",", QtCore.Qt.Key_Semicolon: ";",
                    QtCore.Qt.Key_Apostrophe: "'", QtCore.Qt.Key_Slash: "/", QtCore.Qt.Key_Backslash: "\\",
                    QtCore.Qt.Key_BracketLeft: "[", QtCore.Qt.Key_BracketRight: "]", QtCore.Qt.Key_Minus: "-",
                    QtCore.Qt.Key_Equal: "=", QtCore.Qt.Key_QuoteLeft: "`",
                }
                if event.key() in key_map:
                    key_str = key_map[event.key()]
                    debug_log("  Qt key_map fallback: '{0}'".format(key_str))
        else:
            key_map = {
                QtCore.Qt.Key_A: "A", QtCore.Qt.Key_B: "B", QtCore.Qt.Key_C: "C", QtCore.Qt.Key_D: "D",
                QtCore.Qt.Key_E: "E", QtCore.Qt.Key_F: "F", QtCore.Qt.Key_G: "G", QtCore.Qt.Key_H: "H",
                QtCore.Qt.Key_I: "I", QtCore.Qt.Key_J: "J", QtCore.Qt.Key_K: "K", QtCore.Qt.Key_L: "L",
                QtCore.Qt.Key_M: "M", QtCore.Qt.Key_N: "N", QtCore.Qt.Key_O: "O", QtCore.Qt.Key_P: "P",
                QtCore.Qt.Key_Q: "Q", QtCore.Qt.Key_R: "R", QtCore.Qt.Key_S: "S", QtCore.Qt.Key_T: "T",
                QtCore.Qt.Key_U: "U", QtCore.Qt.Key_V: "V", QtCore.Qt.Key_W: "W", QtCore.Qt.Key_X: "X",
                QtCore.Qt.Key_Y: "Y", QtCore.Qt.Key_Z: "Z",
                QtCore.Qt.Key_0: "0", QtCore.Qt.Key_1: "1", QtCore.Qt.Key_2: "2", QtCore.Qt.Key_3: "3",
                QtCore.Qt.Key_4: "4", QtCore.Qt.Key_5: "5", QtCore.Qt.Key_6: "6", QtCore.Qt.Key_7: "7",
                QtCore.Qt.Key_8: "8", QtCore.Qt.Key_9: "9",
                QtCore.Qt.Key_Period: ".", QtCore.Qt.Key_Comma: ",", QtCore.Qt.Key_Semicolon: ";",
                QtCore.Qt.Key_Apostrophe: "'", QtCore.Qt.Key_Slash: "/", QtCore.Qt.Key_Backslash: "\\",
                QtCore.Qt.Key_BracketLeft: "[", QtCore.Qt.Key_BracketRight: "]", QtCore.Qt.Key_Minus: "-",
                QtCore.Qt.Key_Equal: "=", QtCore.Qt.Key_QuoteLeft: "`",
            }
            
            symbol_key_map = {
                QtCore.Qt.Key_Exclam: "!", QtCore.Qt.Key_At: "@", QtCore.Qt.Key_NumberSign: "#",
                QtCore.Qt.Key_Dollar: "$", QtCore.Qt.Key_Percent: "%", QtCore.Qt.Key_AsciiCircum: "^",
                QtCore.Qt.Key_Ampersand: "&", QtCore.Qt.Key_Asterisk: "*", QtCore.Qt.Key_ParenLeft: "(",
                QtCore.Qt.Key_ParenRight: ")", QtCore.Qt.Key_Underscore: "_", QtCore.Qt.Key_Plus: "+",
                QtCore.Qt.Key_BraceLeft: "{", QtCore.Qt.Key_BraceRight: "}", QtCore.Qt.Key_Bar: "|",
                QtCore.Qt.Key_Colon: ":", QtCore.Qt.Key_QuoteDbl: '"', QtCore.Qt.Key_Less: "<",
                QtCore.Qt.Key_Greater: ">", QtCore.Qt.Key_Question: "?", QtCore.Qt.Key_AsciiTilde: "~"
            }
            
            shift_to_base = {
                QtCore.Qt.Key_Exclam: "1", QtCore.Qt.Key_At: "2", QtCore.Qt.Key_NumberSign: "3",
                QtCore.Qt.Key_Dollar: "4", QtCore.Qt.Key_Percent: "5", QtCore.Qt.Key_AsciiCircum: "6",
                QtCore.Qt.Key_Ampersand: "7", QtCore.Qt.Key_Asterisk: "8", QtCore.Qt.Key_ParenLeft: "9",
                QtCore.Qt.Key_ParenRight: "0", QtCore.Qt.Key_Underscore: "-", QtCore.Qt.Key_Plus: "=",
                QtCore.Qt.Key_BraceLeft: "[", QtCore.Qt.Key_BraceRight: "]", QtCore.Qt.Key_Bar: "\\",
                QtCore.Qt.Key_Colon: ";", QtCore.Qt.Key_QuoteDbl: "'", QtCore.Qt.Key_Less: ",",
                QtCore.Qt.Key_Greater: ".", QtCore.Qt.Key_Question: "/", QtCore.Qt.Key_AsciiTilde: "`"
            }
            
            if event.key() in key_map:
                key_str = key_map[event.key()]
                debug_log("  Key found in key_map: '{0}'".format(key_str))
            elif event.key() in symbol_key_map:
                if "Shift" in mods and event.key() in shift_to_base:
                    key_str = shift_to_base[event.key()]
                    debug_log("  Symbol key with Shift, using base: '{0}'".format(key_str))
                else:
                    key_str = symbol_key_map[event.key()]
                    if "Shift" in mods:
                        mods = [m for m in mods if m != "Shift"]
                        debug_log("  Symbol key, removed Shift: '{0}'".format(key_str))
                    else:
                        debug_log("  Symbol key: '{0}'".format(key_str))
            else:
                debug_log("  Key not in standard maps, trying event.text()...")
                try:
                    key_text = event.text()
                    debug_log("    event.text() = '{0}'".format(key_text))
                    if key_text and len(key_text) == 1:
                        if key_text.isalnum():
                            key_str = key_text.upper() if key_text.isalpha() else key_text
                            debug_log("    Alphanumeric: '{0}'".format(key_str))
                        elif key_text in "!@#$%^&*()_+{}|:\"<>?~":
                            key_str = key_text
                            if "Shift" in mods:
                                mods = [m for m in mods if m != "Shift"]
                            debug_log("    Shifted symbol: '{0}'".format(key_str))
                        elif key_text in "-=[]\\;',./`":
                            key_str = key_text
                            debug_log("    Base symbol: '{0}'".format(key_str))
                except Exception as e:
                    debug_log("    event.text() failed: {0}".format(str(e)))

        if not key_str or key_str in ["CTRL", "ALT", "SHIFT", "META", "CMD", "CONTROL"]:
            debug_log("  Key ignored (modifier-only or empty)")
            return

        self.hotkey = "+".join(mods + [key_str])
        self.setText(self.hotkey)
        debug_log("  FINAL KEY: '{0}'".format(key_str))
        debug_log("  FINAL HOTKEY STRING: '{0}'".format(self.hotkey))
        debug_log("-" * 40)


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    if main_window_ptr is not None:
        return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)
    return None


class HotkeyAssignDialog(QtWidgets.QDialog):
    def __init__(self, tool_name, command, tool_folder=None, entry_func=None, icon_path=None, parent=None):
        if parent is None:
            parent = maya_main_window()
        
        super(HotkeyAssignDialog, self).__init__(parent)
        
        self.tool_name = tool_name
        self.command = command
        self.tool_folder = tool_folder
        self.entry_func = entry_func
        self.icon_path = icon_path
        
        self.setWindowTitle("Assign Hotkey - {0}".format(tool_name))
        self.setMinimumWidth(400)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.Window)
        
        self.init_ui()
        self.apply_styles()

    def init_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        title_layout = QtWidgets.QHBoxLayout()
        
        if self.icon_path and os.path.exists(self.icon_path):
            icon_label = QtWidgets.QLabel()
            pixmap = QtGui.QPixmap(self.icon_path).scaled(32, 32, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            icon_label.setPixmap(pixmap)
            title_layout.addWidget(icon_label)
        
        title_label = QtWidgets.QLabel(self.tool_name)
        title_label.setStyleSheet("font-size: 14pt; font-weight: bold; color: #82C99A;")
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        main_layout.addLayout(title_layout)
        
        info_label = QtWidgets.QLabel("Press a key combination or right-click to type manually")
        info_label.setStyleSheet("color: #AAAAAA; font-size: 9pt;")
        main_layout.addWidget(info_label)
        
        hotkey_label = QtWidgets.QLabel("Hotkey:")
        hotkey_label.setStyleSheet("font-weight: bold; margin-top: 5px;")
        main_layout.addWidget(hotkey_label)
        
        self.hotkey_input = HotkeyCapture()
        main_layout.addWidget(self.hotkey_input)
        
        if IS_MAC:
            platform_hint = "Cmd (⌘), Ctrl (^), Alt/Option (⌥), Shift"
            hint_note = "Note: Cmd maps to Maya's Ctrl internally for reliability"
        else:
            platform_hint = "Ctrl, Alt, Shift"
            hint_note = ""
        
        hint_label = QtWidgets.QLabel("Supports: {0}".format(platform_hint))
        hint_label.setStyleSheet("color: #888888; font-size: 8pt;")
        main_layout.addWidget(hint_label)
        
        if hint_note:
            note_label = QtWidgets.QLabel(hint_note)
            note_label.setStyleSheet("color: #666666; font-size: 7pt; font-style: italic;")
            main_layout.addWidget(note_label)
        
        main_layout.addSpacing(10)
        
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        
        cancel_button = QtWidgets.QPushButton("Cancel")
        cancel_button.setMinimumWidth(80)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        self.assign_button = QtWidgets.QPushButton("Assign Hotkey")
        self.assign_button.setMinimumWidth(120)
        self.assign_button.clicked.connect(self.assign_hotkey_action)
        self.assign_button.setStyleSheet("""
            QPushButton {
                background-color: #82C99A;
                border: none;
                color: #1a1a1a;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #9BD4AC;
            }
        """)
        button_layout.addWidget(self.assign_button)
        
        main_layout.addLayout(button_layout)

    def apply_styles(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #2B2B2B;
                color: #E0E0E0;
            }
            QLabel {
                color: #E0E0E0;
            }
            QLineEdit {
                background-color: #3C3C3C;
                color: #E0E0E0;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 8px;
                font-size: 11pt;
            }
            QLineEdit:focus {
                border: 1px solid #82C99A;
            }
            QPushButton {
                background-color: #3C3C3C;
                color: #E0E0E0;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #4A4A4A;
                border: 1px solid #777777;
            }
        """)

    def assign_hotkey_action(self):
        hotkey = self.hotkey_input.hotkey.strip()
        
        if not hotkey:
            cmds.warning("Please press a hotkey combination.")
            return
        
        if hotkey in HOTKEY_REGISTRY:
            reply = QtWidgets.QMessageBox.question(
                self, 
                "Replace Hotkey?", 
                "Hotkey '{0}' is already assigned.\nDo you want to replace it?".format(hotkey),
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
            )
            if reply == QtWidgets.QMessageBox.No:
                return
        
        assign_hotkey(self.command, hotkey, language="python", tool_name=self.tool_name)
        self.accept()


def show_hotkey_dialog(tool_name, command, tool_folder=None, entry_func=None, icon_path=None):
    dialog = HotkeyAssignDialog(tool_name, command, tool_folder, entry_func, icon_path)
    dialog.exec_()


def build_tool_command(launcher_name, tool_folder=None, entry_func=None):
    if tool_folder:
        if entry_func:
            call_code = "launcher.{0}()".format(entry_func)
        else:
            call_code = """
if hasattr(launcher, 'show'):
    launcher.show()
elif hasattr(launcher, 'main'):
    launcher.main()
elif hasattr(launcher, 'ui'):
    launcher.ui()
elif hasattr(launcher, 'run'):
    launcher.run()
"""
        
        command = '''
import sys
import os
import importlib
import maya.cmds as cmds

animo_data_path = os.path.normpath(os.path.join(cmds.internalVar(userScriptDir=True), '..', '..', 'scripts', 'Animo_Data'))
tool_path = os.path.normpath(os.path.join(animo_data_path, '{tool_folder}'))

if tool_path not in sys.path:
    sys.path.insert(0, tool_path)

try:
    import maya.OpenMayaUI as _mui
    try:
        from PySide2 import QtWidgets as _QW
        from shiboken2 import wrapInstance as _wi
    except ImportError:
        from PySide6 import QtWidgets as _QW
        from shiboken6 import wrapInstance as _wi
    _main_ptr = _mui.MQtUtil.mainWindow()
    if _main_ptr:
        _maya_main = _wi(int(_main_ptr), _QW.QMainWindow)
        for _child in _maya_main.children():
            try:
                _name = _child.objectName()
            except (AttributeError, RuntimeError):
                continue
            if _name.endswith('UIWindow'):
                try:
                    _child.close()
                    _child.setParent(None)
                    _child.deleteLater()
                except (AttributeError, RuntimeError):
                    continue
except (ImportError, AttributeError, RuntimeError):
    pass

for mod in list(sys.modules.keys()):
    if '{launcher_name}' in mod:
        del sys.modules[mod]

launcher = importlib.import_module('{launcher_name}')
{call_code}
'''.format(
            tool_folder=tool_folder.replace('\\', '/'),
            launcher_name=launcher_name,
            call_code=call_code
        )
    else:
        if entry_func:
            command = '''
import sys
import os
import importlib
import maya.cmds as cmds

animo_data_path = os.path.normpath(os.path.join(cmds.internalVar(userScriptDir=True), '..', '..', 'scripts', 'Animo_Data'))
icons_path = os.path.normpath(os.path.join(animo_data_path, 'Animo_Launcher'))

if icons_path not in sys.path:
    sys.path.insert(0, icons_path)

try:
    import maya.OpenMayaUI as _mui
    try:
        from PySide2 import QtWidgets as _QW
        from shiboken2 import wrapInstance as _wi
    except ImportError:
        from PySide6 import QtWidgets as _QW
        from shiboken6 import wrapInstance as _wi
    _main_ptr = _mui.MQtUtil.mainWindow()
    if _main_ptr:
        _maya_main = _wi(int(_main_ptr), _QW.QMainWindow)
        for _child in _maya_main.children():
            try:
                _name = _child.objectName()
            except (AttributeError, RuntimeError):
                continue
            if _name.endswith('UIWindow'):
                try:
                    _child.close()
                    _child.setParent(None)
                    _child.deleteLater()
                except (AttributeError, RuntimeError):
                    continue
except (ImportError, AttributeError, RuntimeError):
    pass

for mod in list(sys.modules.keys()):
    if '{launcher_name}' in mod:
        del sys.modules[mod]

launcher = importlib.import_module('{launcher_name}')
launcher.{entry_func}()
'''.format(launcher_name=launcher_name, entry_func=entry_func)
        else:
            command = '''
import sys
import os
import maya.cmds as cmds

animo_data_path = os.path.normpath(os.path.join(cmds.internalVar(userScriptDir=True), '..', '..', 'scripts', 'Animo_Data'))
icons_path = os.path.normpath(os.path.join(animo_data_path, 'Animo_Launcher'))

py_path = os.path.normpath(os.path.join(icons_path, '{launcher_name}.py'))
if os.path.exists(py_path):
    with open(py_path, 'r', encoding='utf-8') as f:
        script_content = f.read()
    exec(compile(script_content, py_path, 'exec'), {{'__name__': '__main__', '__file__': py_path}})
'''.format(launcher_name=launcher_name)
    
    return command