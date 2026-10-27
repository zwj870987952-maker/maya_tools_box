import sys
import maya.cmds as cmds
from pathlib import Path
import importlib.util
import importlib

# Clean any existing modules of anim_polish
for mod in list(sys.modules):
    if 'anim_polish' in mod or 'animPolish' in mod:
        del sys.modules[mod]

rc_path = Path(r"c:\Users\zhongweijie\Documents\GitHub\maya_tools_box\tools_staging_pool\01_animation\anim_polish_premium_v1_23\release_candidate").resolve()
spec = importlib.util.spec_from_file_location('polish_loader', rc_path / 'launch_candidate.py')
loader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(loader)
tool = loader.load_tool()

cyl = cmds.polyCube(name='test_cube')[0]
res = tool.run(action='invoke', function='growShrink.run', arguments={'geo': cyl})
print("Result success:", res.success)
print("Errors:", res.errors)
print("Warnings:", res.warnings)
print("Outcome:", res.data.get('outcome'))
cmds.delete(cyl)
