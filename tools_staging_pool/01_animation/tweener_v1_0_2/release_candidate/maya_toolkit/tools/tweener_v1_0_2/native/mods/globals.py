# Modified complete source port, 2026-10-01. Morten Andersen / original GPL LICENSE preserved.
"""
globals
"""

import os
import maya.cmds as cmds

plugin_name = 'staging_tweener_plugin.py'
plugin_path = ''
plugin_version = '1.0.2'


def refresh_plug_in_path():
    global plugin_name
    global plugin_path

    try:
        plugin_path = os.path.dirname(
            cmds.pluginInfo(plugin_name, q=True, path=True)) + '/'
    except Exception as e:
        cmds.warning(str(e))
