from maya_toolkit.tools.rdm_tools_v2.support import legacy_reload, bundled_scripts_dir, checked_output, explicit_ui_input
import maya.cmds as cmd
attributes = []


def run_script():
    exec(compile("sel = cmd.ls(sl=1)\nattributes = []\nif sel:\n    for obj in sel:\n        allAttrs = cmd.listAttr(obj)\n        cbAttrs = cmd.listAnimatable(obj)\n        if allAttrs and cbAttrs:\n            orderedAttrs = [attr for attr in allAttrs for cb in cbAttrs if cb.endswith(attr)]\n            if 'visibility' in orderedAttrs:\n                orderedAttrs.remove('visibility')\n                orderedAttrs.append('visibility')\n            attributes.extend(orderedAttrs)\nfor i in attributes:\n    print(i)", __file__, "exec"), globals())
