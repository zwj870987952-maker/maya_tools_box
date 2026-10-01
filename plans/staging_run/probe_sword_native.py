"""Diagnose original source availability only in isolated mayapy."""
import os
from pathlib import Path
import runpy
if os.environ.get('STAGING_ISOLATED_MAYAPY')!='1':
    raise RuntimeError('Isolated mayapy only')
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds,mel
root=Path(__file__).resolve().parents[2]
runpy.run_path(str(root/'tools_staging_pool/01_animation/sword_anim_polishing_tool_v4/release_candidate/launch_candidate.py'))['load_tool']()
from maya_toolkit.tools.sword_anim_polishing_tool_v4 import runtime
v=runtime.v
v.load_vendor()
node=cmds.createNode('transform',name='weapon')
for attr in ('tx','ty','tz','rx','ry','rz'):
    cmds.setKeyframe(node,attribute=attr,time=1,value=0)
    cmds.setKeyframe(node,attribute=attr,time=5,value=5 if attr=='tx' else 0)
cmds.selectPref(trackSelectionOrder=True)
cmds.select(node)
for command in ('getApplicationVersionAsFloat','SW_ac692345fba3e827ad5d6e26de39ba07;','SW_54d92f8424c4459e6d996d9fd93902f0();','SW_17431451b1be026fdeee93b86579c6b6({"weapon"},{"locator1"});','SW_cc20e95399a3b6da44eb78e45451d764(22);','SW_6de8028af587b467034457b4d6349f89(1);','SW_c89bf830cdb2b9cc874e6c8604e8b257;','SW_de88efca2929f0080ae1d45ff5db42d4;'):
    try:
        print('NATIVE_PROBE',command,mel.eval(command),flush=True)
    except Exception as exc:
        print('NATIVE_FAILED',command,str(exc),flush=True)
        print('DETAIL',repr(exc),flush=True)
cmds.undoInfo(openChunk=True,chunkName='probe_parent')
print('UNDO_PARENT',repr(cmds.undoInfo(query=True,chunkName=True)),flush=True)
cmds.undoInfo(openChunk=True,chunkName='curve_motion_path')
print('UNDO_CHILD',repr(cmds.undoInfo(query=True,chunkName=True)),flush=True)
cmds.undoInfo(closeChunk=True)
from maya.api import OpenMaya as om
seen=[]
callback=om.MCommandMessage.addCommandCallback(lambda command,*_:seen.append(command))
mel.eval('global proc mtkSwordProbeUndo(){undoInfo -ock -cn "inner_probe"; undoInfo -cck;}')
mel.eval('mtkSwordProbeUndo();')
om.MMessage.removeCallback(callback)
print('NESTED_COMMAND_CALLBACK',repr(seen),flush=True)
print('UNDO_AFTER_CHILD',repr(cmds.undoInfo(query=True,chunkName=True)),flush=True)
cmds.undoInfo(closeChunk=True)
