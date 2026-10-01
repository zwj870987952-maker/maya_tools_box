"""Read-only vendor MEL compilation in isolated Maya; no UI or business call."""
import json
import os
from pathlib import Path

if os.environ.get('STAGING_ISOLATED_MAYAPY')!='1':
    raise RuntimeError('Isolated runner required')
import maya.standalone
maya.standalone.initialize(name='python')
import maya.cmds as cmds
import maya.mel as mel

root=Path(__file__).resolve().parents[2]
path=root/'tools_staging_pool/01_animation/shift_animation_v3_2/Shift_animation_v3_2/barnev_Shift_animation_code.mel'
before=set(cmds.ls(uuid=True))
mel.eval('source '+json.dumps(path.as_posix())+';')
assert before==set(cmds.ls(uuid=True))
print('Complete unchanged MEL source compiled; no scene/UI execution')
