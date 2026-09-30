"""Compile untouched NoUI suite and try readonly procedures in isolated mayapy."""
import json
import os
from pathlib import Path
import sys

if not os.environ.get('STAGING_ISOLATED_MAYAPY'):
    raise RuntimeError('Use isolated mayapy')
import maya.standalone
maya.standalone.initialize(name='python')
import maya.cmds as cmds
import maya.mel as mel

ROOT = Path(__file__).resolve().parents[2]
source = ROOT / 'tools_staging_pool/01_animation/anim_layer_v4_0/release_candidate/maya_toolkit/tools/anim_layer_v4_0/upstream/no_UI_version/layerEditor_no_UI.mel'
try:
    mel.eval('source ' + json.dumps(source.as_posix()) + ';')
    print('SOURCE_OK')
    cube = cmds.polyCube()[0]
    for time in (1, 5):
        cmds.setKeyframe(cube, attribute='translateX', time=time, value=time)
    cmds.select(cube)
    print(json.dumps({'range': mel.eval('get_anim_time_range_from_anim_layer("BaseAnimation");'),
                      'origin': mel.eval('whatIs "get_anim_time_range_from_anim_layer";')}))
except Exception as error:
    print('PROBE_ERROR: ' + str(error))
    sys.exit(1)
