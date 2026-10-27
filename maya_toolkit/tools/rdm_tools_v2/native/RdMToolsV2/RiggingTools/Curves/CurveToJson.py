from maya_toolkit.tools.rdm_tools_v2.support import legacy_reload, bundled_scripts_dir, checked_output, explicit_ui_input
import json
import maya.OpenMaya as openmaya
output = []


def run_script():
    exec(compile("dagIter = openmaya.MItDag(openmaya.MItDag.kDepthFirst, openmaya.MFn.kCurve)\noutput = []\nwhile not dagIter.isDone():\n    curveIter = openmaya.MItCurveCV(dagIter.currentItem())\n    curve = openmaya.MFnDagNode(dagIter.currentItem())\n    dagIter.next()\n    node = {'name': curve.name(), 'points': []}\n    while not curveIter.isDone():\n        pos = curveIter.position()\n        curveIter.next()\n        node['points'].append([pos.x, pos.y, pos.z])\n    output.append(node)\nprint(output)\nwith checked_output() as fOut:\n    json.dump(output, fOut)", __file__, "exec"), globals())
