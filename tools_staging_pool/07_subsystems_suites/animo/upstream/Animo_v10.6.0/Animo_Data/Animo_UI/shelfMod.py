'''
    Animo Shelf Module
    Handles adding tools to Maya shelf and assigning hotkeys
'''

import maya.cmds as cmds
import os


def add_tool_to_shelf(icon_path, tool_name, launcher_name, tool_folder=None, entry_func=None):
    """
    Add a tool to the current Maya shelf
    
    Args:
        icon_path: Full path to the icon image file
        tool_name: Display name for the tool
        launcher_name: Name of the launcher script
        tool_folder: Optional subfolder in Animo_Data
        entry_func: Optional entry function to call
    """
    try:
        current_shelf = cmds.shelfTabLayout("ShelfLayout", query=True, selectTab=True)
        
        if tool_folder:
            if entry_func:
                call_code = "launcher.{}()".format(entry_func)
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
        
        image = icon_path if icon_path and os.path.exists(icon_path) else "commandButton.png"
        
        cmds.shelfButton(
            parent=current_shelf,
            image=image,
            label=tool_name,
            command=command,
            sourceType="python",
            annotation=tool_name
        )
        
        cmds.inViewMessage(
            amg='<span style="color:#82C99A;">{} added to shelf</span>'.format(tool_name),
            pos='topCenter', fade=True, fadeStayTime=1000
        )
        
    except Exception as e:
        cmds.warning("Could not add {} to shelf: {}".format(tool_name, str(e)))


def assign_hotkey_to_tool(icon_path, tool_name, launcher_name, tool_folder=None, entry_func=None):
    """
    Open hotkey assignment dialog for a tool
    """
    import sys
    import os
    import importlib
    
    try:
        animo_data_path = os.path.normpath(os.path.join(
            cmds.internalVar(userScriptDir=True), '..', '..', 'scripts', 'Animo_Data'
        ))
        ui_path = os.path.normpath(os.path.join(animo_data_path, 'Animo_UI'))
        
        if ui_path not in sys.path:
            sys.path.insert(0, ui_path)
        
        if 'hotkeyMod' in sys.modules:
            del sys.modules['hotkeyMod']
        
        import hotkeyMod
        
        command = hotkeyMod.build_tool_command(launcher_name, tool_folder, entry_func)
        hotkeyMod.show_hotkey_dialog(tool_name, command, tool_folder, entry_func, icon_path)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        cmds.warning("Could not open hotkey dialog: {}".format(str(e)))


def create_shelf_context_menu(button, icon_path, tool_name, launcher_name, tool_folder=None, entry_func=None, include_hotkey=True):
    """
    Create a context menu for a button with "Add to Shelf" and optionally "Assign Hotkey" options
    """
    try:
        from PySide2 import QtWidgets, QtCore
    except ImportError:
        from PySide6 import QtWidgets, QtCore
    
    def show_context_menu(pos):
        menu = QtWidgets.QMenu()
        menu.setStyleSheet('''
            QMenu { background-color: #3a3a3a; border: 1px solid #555; padding: 3px; }
            QMenu::item { padding: 6px 25px; color: #ccc; }
            QMenu::item:selected { background-color: #555; color: #fff; }
        ''')
        
        shelf_action = menu.addAction("Add to Shelf")
        shelf_action.triggered.connect(
            lambda: add_tool_to_shelf(icon_path, tool_name, launcher_name, tool_folder, entry_func)
        )
        
        if include_hotkey:
            hotkey_action = menu.addAction("Assign Hotkey")
            hotkey_action.triggered.connect(
                lambda: assign_hotkey_to_tool(icon_path, tool_name, launcher_name, tool_folder, entry_func)
            )
        
        menu.exec_(button.mapToGlobal(pos))
    
    button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
    button.customContextMenuRequested.connect(show_context_menu)


def add_shelf_action_to_menu(menu, icon_path, tool_name, launcher_name, tool_folder=None, entry_func=None):
    """
    Add "Add to Shelf" and "Assign Hotkey" actions to an existing menu
    """
    menu.addSeparator()
    
    shelf_action = menu.addAction("Add to Shelf")
    shelf_action.triggered.connect(
        lambda: add_tool_to_shelf(icon_path, tool_name, launcher_name, tool_folder, entry_func)
    )
    
    hotkey_action = menu.addAction("Assign Hotkey")
    hotkey_action.triggered.connect(
        lambda: assign_hotkey_to_tool(icon_path, tool_name, launcher_name, tool_folder, entry_func)
    )