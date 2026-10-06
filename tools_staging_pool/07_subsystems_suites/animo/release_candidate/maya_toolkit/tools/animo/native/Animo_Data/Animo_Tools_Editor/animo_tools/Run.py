from __future__ import absolute_import, division, print_function, unicode_literals

import sys
import os
import maya.cmds as cmds

try:
    import animo_tools
    if hasattr(animo_tools, 'animo_dialog'):
        dialog = animo_tools.animo_dialog
        if dialog:
            dialog.close()
            dialog.deleteLater()
except Exception:
    pass

maya_scripts_dir = cmds.internalVar(userScriptDir=True)
animo_tools_path = os.path.join(maya_scripts_dir, "Animo_Data", "Animo_Tools_Editor")
animo_tools_subfolder = os.path.join(animo_tools_path, "animo_tools")

modules_to_remove = []
if os.path.isdir(animo_tools_subfolder):
    self_module_names = set()
    for filename in os.listdir(animo_tools_subfolder):
        if filename.endswith('.py'):
            self_module_names.add(filename[:-3])
        elif filename.endswith('.pyc'):
            base_name = filename[:-4]
            prefix, marker, suffix = base_name.rpartition('_py')
            if marker and suffix.isdigit():
                base_name = prefix
            self_module_names.add(base_name)
    
    normalized_subfolder = os.path.normcase(os.path.normpath(animo_tools_subfolder))
    
    for module_name in self_module_names:
        cached_module = sys.modules.get(module_name)
        if cached_module is None:
            continue
        
        cached_file = getattr(cached_module, '__file__', None)
        if not cached_file:
            continue
        
        cached_dir = os.path.normcase(os.path.normpath(os.path.dirname(cached_file)))
        if cached_dir != normalized_subfolder:
            continue
        
        modules_to_remove.append(module_name)

for module_name in modules_to_remove:
    del sys.modules[module_name]

if animo_tools_path not in sys.path:
    sys.path.insert(0, animo_tools_path)

import animo_tools
animo_tools.show_animo_tools()
