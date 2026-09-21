"""
Entry point to launch, reload, or toggle animBot UI clone in Autodesk Maya.
"""

import sys
import importlib

_UI_INSTANCE = None

def reload_modules():
    """Reload all submodules under animbot_copy for quick development."""
    to_reload = []
    for mod_name in list(sys.modules.keys()):
        if mod_name.startswith("animbot_copy.") or mod_name == "animbot_copy":
            to_reload.append(mod_name)
            
    for mod_name in sorted(to_reload, key=lambda x: len(x.split('.')), reverse=True):
        try:
            importlib.reload(sys.modules[mod_name])
        except Exception:
            pass

def launch(use_workspace_control=True):
    """Launch or restore animBot UI."""
    global _UI_INSTANCE
    reload_modules()
    
    from .ui.workspace_control import create_workspace_control, create_floating_window, close_workspace_control
    
    close_workspace_control()
    if use_workspace_control:
        try:
            _UI_INSTANCE = create_workspace_control()
        except Exception as e:
            print(f"[animBot] Warning: workspaceControl failed ({e}), falling back to floating dialog.")
            _UI_INSTANCE = create_floating_window()
    else:
        _UI_INSTANCE = create_floating_window()
        
    print("[animBot] animBot UI Clone launched successfully.")
    return _UI_INSTANCE

def close():
    """Close animBot UI."""
    global _UI_INSTANCE
    from .ui.workspace_control import close_workspace_control
    close_workspace_control()
    _UI_INSTANCE = None
    print("[animBot] animBot UI Closed.")

def toggle():
    """Toggle visibility."""
    import maya.cmds as cmds
    from .ui.workspace_control import CONTROL_NAME
    if cmds.workspaceControl(CONTROL_NAME, exists=True) and cmds.workspaceControl(CONTROL_NAME, q=True, visible=True):
        close()
    else:
        launch()

if __name__ == "__main__":
    launch()
