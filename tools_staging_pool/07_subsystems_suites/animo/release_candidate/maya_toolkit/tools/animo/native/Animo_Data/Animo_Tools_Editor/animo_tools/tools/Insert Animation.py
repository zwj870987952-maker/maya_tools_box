import os
import sys

from maya import cmds

try:
    _script_dir = os.path.dirname(os.path.abspath(__file__))
    ANIMO_DATA_PATH = os.path.normpath(os.path.join(_script_dir, ".."))
except NameError:
    _version_script_dir = cmds.internalVar(userScriptDir=True)
    ANIMO_DATA_PATH = os.path.normpath(os.path.join(_version_script_dir, "..", "..", "scripts", "Animo_Data"))

TRANSIFY_PATH = os.path.join(ANIMO_DATA_PATH, "Animo_Transify")

if TRANSIFY_PATH not in sys.path:
    sys.path.insert(0, TRANSIFY_PATH)

for _mod_name in ("transify_common", "transify_engine", "action_paste_insert"):
    if _mod_name in sys.modules:
        del sys.modules[_mod_name]

from transify_engine import AnimationCopyPasteJson
import action_paste_insert


class _StandaloneContext(object):

    def __init__(self):
        self.tool = AnimationCopyPasteJson()
        self.selected_file = None

    def has_selection(self):
        return bool(cmds.ls(selection=True))

    def get_target_namespace(self):
        selected = cmds.ls(selection=True)
        if selected:
            return self.tool.detect_most_common_namespace_from_selection(selected)
        return ""

    def update_file_info(self):
        pass

    def clear_focus(self):
        try:
            cmds.setFocus("MayaWindow")
        except Exception:
            pass


action_paste_insert.run(_StandaloneContext())
