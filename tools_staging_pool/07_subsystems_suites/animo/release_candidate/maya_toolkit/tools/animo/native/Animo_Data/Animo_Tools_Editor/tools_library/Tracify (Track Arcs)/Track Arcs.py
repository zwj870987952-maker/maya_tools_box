import os
import sys

import maya.cmds as cmds


def _get_animo_data_path():
    version_script_dir = cmds.internalVar(userScriptDir=True)
    script_dir = os.path.normpath(os.path.join(version_script_dir, "..", "..", "scripts"))
    return os.path.join(script_dir, "Animo_Data")


def track_arcs():
    animo_data_path = _get_animo_data_path()
    tracify_dir = os.path.join(animo_data_path, "Animo_Launcher")

    if not os.path.exists(os.path.join(tracify_dir, "tracify_launcher.py")):
        cmds.error("Track Arcs: Could not find tracify_launcher.py in {}".format(tracify_dir))
        return

    if tracify_dir not in sys.path:
        sys.path.insert(0, tracify_dir)

    tracify_launcher = sys.modules.get("tracify_launcher")
    if tracify_launcher is None:
        import tracify_launcher

    tracify_launcher.track_arcs()


track_arcs()
