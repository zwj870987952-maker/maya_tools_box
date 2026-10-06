from __future__ import absolute_import, division, print_function, unicode_literals

import os
import sys

import maya.cmds as cmds


def _get_animo_tools_module_path(animo_data_path):
    return os.path.join(animo_data_path, "Animo_Tools_Editor", "animo_tools")


def _import_animo_tools_modules(animo_tools_path):
    sys._animo_tools_path = animo_tools_path

    if animo_tools_path not in sys.path:
        sys.path.insert(0, animo_tools_path)

    for mod_name in ("animo_compat", "hotkey_utils", "hotkey_binding", "animo_hotkeys", "animo_data"):
        if mod_name in sys.modules:
            del sys.modules[mod_name]

    import animo_data as animo_data_mod
    import animo_hotkeys as animo_hotkeys_mod
    return animo_data_mod, animo_hotkeys_mod


def apply_saved_hotkeys(animo_data_path):
    animo_tools_path = _get_animo_tools_module_path(animo_data_path)

    if not os.path.isdir(animo_tools_path):
        return 0, 0

    try:
        animo_data_mod, animo_hotkeys_mod = _import_animo_tools_modules(animo_tools_path)
    except Exception as e:
        cmds.warning("Animo: Could not load hotkey modules - {}".format(str(e)))
        return 0, 0

    try:
        tools_data = animo_data_mod.load_tools_data()
    except Exception as e:
        cmds.warning("Animo: Could not read saved hotkeys - {}".format(str(e)))
        return 0, 0

    applied_count = 0
    failed_count = 0

    for category in tools_data.get("custom_categories", []):
        for entry in category.get("tools_data", []):
            hotkey_text = entry.get("hotkey", "")
            if not hotkey_text:
                continue

            command = entry.get("script", "")
            if not command:
                continue

            tool_name = entry.get("name", "")
            script_type = entry.get("script_type", "Python")
            language = "python" if script_type == "Python" else "mel"

            try:
                success, message = animo_hotkeys_mod.assign_hotkey(command, hotkey_text, tool_name, language)
            except Exception:
                success = False

            if success:
                applied_count += 1
            else:
                failed_count += 1

    return applied_count, failed_count
