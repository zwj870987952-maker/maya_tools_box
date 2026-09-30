"""Compile all extracted procedures in disposable mayapy; never open UI/install shelf."""
import json
import hashlib
import os
from pathlib import Path

if not os.environ.get('STAGING_ISOLATED_MAYAPY'):
    raise RuntimeError('Run through the isolated mayapy runner')
import maya.standalone
maya.standalone.initialize(name='python')
import maya.cmds as cmds
import maya.mel as mel

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / 'tools_staging_pool/01_animation/animirror_v2_0/release_candidate/maya_toolkit/tools/animirror_v2_0'
catalog = json.loads((PACKAGE / 'catalog.json').read_text(encoding='utf-8'))
before = sorted(cmds.ls())
mel.eval('source ' + json.dumps((PACKAGE / 'runtime.mel').as_posix()) + ';')
for name in catalog['runtime_procedures']:
    origin = str(mel.eval('whatIs ' + json.dumps(name) + ';')).replace('\\', '/').casefold()
    assert origin.endswith((PACKAGE / 'runtime.mel').as_posix().casefold()), (name, origin)
mel.eval('mtbAV2_globals_variables();')
assert sorted(cmds.ls()) == before
assert not cmds.window('mtbAV2_AniMirror', exists=True)
assert cmds.about(batch=True)
print(json.dumps({'compiled_procedures': catalog['runtime_procedures'], 'runtime_mel_sha256': hashlib.sha256((PACKAGE / 'runtime.mel').read_bytes()).hexdigest(), 'scene_unchanged': True, 'ui_created': False, 'gui_acceptance': False}))

# The early query-stub exploration is preserved in Git and its historical report.
# Current real algorithm/ownership tests use the complete standard adapter in
# release_candidate/tests/test_animirror_v2_0_maya.py; do not bypass its guards.
