"""One-time behavior probe in a disposable mayapy scene, not a validation claim."""
import ast
import importlib.util
import json
import os
from pathlib import Path

if not os.environ.get("STAGING_ISOLATED_MAYAPY"):
    raise RuntimeError("Requires isolated runner")
import maya.standalone
maya.standalone.initialize(name="python")
import maya.cmds as cmds
import maya.api.OpenMaya as om
import maya.api.OpenMayaAnim as oma

try:
    source = Path(__file__).resolve().parents[2] / "tools_staging_pool/01_animation/anim_filters/animFilters-v1.0-maya17/scripts/animFilters/animFilters.py"
    tree = ast.parse(source.read_bytes())
    subset = ast.Module(body=[node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in ("add_keys", "apply_curves")], type_ignores=[])
    namespace = {"cmds": cmds, "om": om, "oma": oma}
    exec(compile(subset, str(source), "exec"), namespace)
    reports = []
    for attribute in ("translateX", "rotateX"):
        cmds.file(new=True, force=True)
        cube = cmds.polyCube()[0]
        for time, value in ((0, -3), (1, 1), (2, 9), (3, 2), (4, 7)):
            cmds.setKeyframe(cube, attribute=attribute, time=time, value=value)
        curve = cmds.listConnections(cube + "." + attribute, source=True, destination=False)[0]
        raw = {curve: {1: 1.0, 2: 9.0, 3: 2.0}}
        filtered = {curve: {"1": 100.0, "2": 5.0, "3": 200.0}}
        namespace["apply_curves"](raw, filtered)
        reports.append({"attribute": attribute, "times": cmds.keyframe(curve, query=True, timeChange=True), "values": cmds.keyframe(curve, query=True, valueChange=True)})
    print(json.dumps({"original_apply": reports, "numpy_available": importlib.util.find_spec("numpy") is not None, "scipy_available": importlib.util.find_spec("scipy") is not None}, ensure_ascii=True))
finally:
    maya.standalone.uninitialize()
