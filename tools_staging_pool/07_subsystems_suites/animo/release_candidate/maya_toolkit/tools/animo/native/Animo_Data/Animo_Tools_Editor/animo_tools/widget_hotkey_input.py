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

import animo_compat as compat
QtWidgets = compat.QtWidgets
QtCore = compat.QtCore
QtGui = compat.QtGui
IS_MAC = compat.IS_MAC

import dpi_utils as dpi_utils
scale_size = dpi_utils.scale_size

class HotkeyLineEdit(QtWidgets.QLineEdit):
    
    hotkey_captured = QtCore.Signal()
    hotkey_cleared = QtCore.Signal()
    
    def __init__(self, parent=None):
        super(HotkeyLineEdit, self).__init__(parent)
        self.hotkey = ""
        self.setReadOnly(True)
        self.setPlaceholderText("Press a key combination...")
    
    MODIFIER_ONLY_KEYS = (
        QtCore.Qt.Key_Shift,
        QtCore.Qt.Key_Control,
        QtCore.Qt.Key_Alt,
        QtCore.Qt.Key_Meta,
        QtCore.Qt.Key_AltGr,
        QtCore.Qt.Key_CapsLock,
        QtCore.Qt.Key_NumLock,
        QtCore.Qt.Key_ScrollLock,
        QtCore.Qt.Key_Super_L,
        QtCore.Qt.Key_Super_R,
        QtCore.Qt.Key_Menu,
    )
    
    def keyPressEvent(self, event):
        if event.key() in (QtCore.Qt.Key_unknown, 0):
            return
        
        if event.key() in self.MODIFIER_ONLY_KEYS:
            return
        
        mods = []
        modifiers = event.modifiers()
        
        if modifiers & QtCore.Qt.ShiftModifier:
            mods.append("Shift")
        if modifiers & QtCore.Qt.AltModifier:
            mods.append("Alt")
        
        if IS_MAC:
            if modifiers & QtCore.Qt.ControlModifier:
                mods.append("Cmd")
            if modifiers & QtCore.Qt.MetaModifier:
                mods.append("Ctrl")
        else:
            if modifiers & QtCore.Qt.ControlModifier:
                if "Ctrl" not in mods:
                    mods.append("Ctrl")
        
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
            QtCore.Qt.Key_F1: "F1",
            QtCore.Qt.Key_F2: "F2",
            QtCore.Qt.Key_F3: "F3",
            QtCore.Qt.Key_F4: "F4",
            QtCore.Qt.Key_F5: "F5",
            QtCore.Qt.Key_F6: "F6",
            QtCore.Qt.Key_F7: "F7",
            QtCore.Qt.Key_F8: "F8",
            QtCore.Qt.Key_F9: "F9",
            QtCore.Qt.Key_F10: "F10",
            QtCore.Qt.Key_F11: "F11",
            QtCore.Qt.Key_F12: "F12",
        }
        
        key_str = ""
        
        if event.key() in special_keys:
            key_str = special_keys[event.key()]
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
            
            shift_map = {
                QtCore.Qt.Key_1: "!", QtCore.Qt.Key_2: "@", QtCore.Qt.Key_3: "#", QtCore.Qt.Key_4: "$",
                QtCore.Qt.Key_5: "%", QtCore.Qt.Key_6: "^", QtCore.Qt.Key_7: "&", QtCore.Qt.Key_8: "*",
                QtCore.Qt.Key_9: "(", QtCore.Qt.Key_0: ")", QtCore.Qt.Key_Minus: "_", QtCore.Qt.Key_Equal: "+",
                QtCore.Qt.Key_BracketLeft: "{", QtCore.Qt.Key_BracketRight: "}", QtCore.Qt.Key_Backslash: "|",
                QtCore.Qt.Key_Semicolon: ":", QtCore.Qt.Key_Apostrophe: "\"", QtCore.Qt.Key_Comma: "<",
                QtCore.Qt.Key_Period: ">", QtCore.Qt.Key_Slash: "?", QtCore.Qt.Key_QuoteLeft: "~"
            }
            
            shifted_chars = ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '_', '+', '{', '}', '|', ':', '"', '<', '>', '?', '~']
            
            if event.key() in key_map:
                key_str = key_map[event.key()]
                
                if key_str in shifted_chars and "Shift" in mods:
                    mods = [m for m in mods if m != "Shift"]
                elif "Shift" in mods and event.key() in shift_map:
                    if not ("Ctrl" in mods or "Alt" in mods or "Cmd" in mods):
                        key_str = shift_map[event.key()]
                        mods = [m for m in mods if m != "Shift"]
                    else:
                        key_str = shift_map[event.key()]
                        mods = [m for m in mods if m != "Shift"]
            else:
                try:
                    key_text = event.text()
                    
                    if key_text in shifted_chars and "Shift" in mods:
                        key_str = key_text
                        mods = [m for m in mods if m != "Shift"]
                    elif key_text and key_text.isprintable() and ord(key_text) >= 32:
                        key_str = key_text.upper() if key_text.isalpha() else key_text
                    else:
                        key_sequence = QtGui.QKeySequence(event.key()).toString()
                        if key_sequence and key_sequence not in ["Ctrl", "Alt", "Shift", "Meta", "Cmd"]:
                            key_str = key_sequence.upper() if key_sequence.isalpha() else key_sequence
                except Exception:
                    pass
        
        if not key_str or key_str.upper() in ["CTRL", "ALT", "SHIFT", "META", "CMD"]:
            return
        
        self.hotkey = "+".join(mods + [key_str])
        self.setText(self.hotkey)
        self.hotkey_captured.emit()
    
    def contextMenuEvent(self, event):
        parent_dialog = self.window()
        if hasattr(parent_dialog, 'close_all_tooltips'):
            parent_dialog.close_all_tooltips()
        
        menu = QtWidgets.QMenu(self)
        menu.setStyleSheet("""
            QMenu {{
                background-color: #3A3A3A;
                color: #CCCCCC;
                border: 1px solid #555555;
                padding: {menu_pad}px;
            }}
            QMenu::item {{
                padding: {item_pad_v}px {item_pad_h}px;
            }}
            QMenu::item:selected {{
                background-color: #4A4A4A;
            }}
        """.format(
            menu_pad=scale_size(5),
            item_pad_v=scale_size(5),
            item_pad_h=scale_size(20)
        ))
        
        clear_action = menu.addAction("Clear")
        menu.addSeparator()
        type_action = menu.addAction("Type Manually")
        
        action = menu.exec_(event.globalPos())
        
        if action == clear_action:
            self.clear()
            self.hotkey = ""
            self.hotkey_cleared.emit()
        elif action == type_action:
            self.setReadOnly(False)
            self.clear()
            self.setFocus()
