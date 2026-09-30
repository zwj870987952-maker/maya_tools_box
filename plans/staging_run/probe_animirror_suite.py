"""Compile all extracted procedures in disposable mayapy; never open UI/install shelf."""
import json
import hashlib
import os
import re
import tempfile
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

# Real disposable scene algorithm check. UI query expressions alone are replaced
# by fixed values; no native UI or production rig is created/used.
source = (PACKAGE / 'runtime.mel').read_text(encoding='utf-8')
for control, value in {'TranslationsCheckbox': 1, 'RotationsCheckbox': 1, 'XAxisRotCheckbox': 0,
                       'YAxisRotCheckbox': 1, 'ZAxisRotCheckbox': 1}.items():
    source = source.replace('`checkBox -q -v mtbAV2_' + control + '`', str(value))
for control, value in {'XAxisTransRadio': 1, 'YAxisTransRadio': 0, 'ZAxisTransRadio': 0}.items():
    source = source.replace('`radioButton -q -sl mtbAV2_' + control + '`', str(value))
with tempfile.TemporaryDirectory(prefix='animirror_mel_probe_') as directory:
    script = Path(directory) / 'runtime_query_stub.mel'
    script.write_text(source, encoding='utf-8')
    mel.eval('source ' + json.dumps(script.as_posix()) + ';')
    cmds.file(new=True, force=True)
    # floatMath is supplied by the installed Autodesk lookdevKit plug-in.
    cmds.loadPlugin('lookdevKit', quiet=True)
    assert 'floatMath' in cmds.allNodeTypes()
    center = cmds.createNode('transform', name='center')
    reference = cmds.createNode('transform', name='reference')
    target = cmds.createNode('transform', name='mirrorTarget')
    cmds.setAttr(reference + '.translate', 3, 2, 1, type='double3')
    cmds.setKeyframe(reference, attribute='tx', time=1, value=3)
    cmds.setKeyframe(reference, attribute='tx', time=5, value=5)
    cmds.currentTime(1)
    mel.eval('mtbAV2_globals_variables();')
    cmds.select([center, reference, target], replace=True)
    mel.eval('mtbAV2_mirror_animation(0);')
    initial = cmds.getAttr(target + '.translate')[0]
    cmds.currentTime(5)
    moved = cmds.getAttr(target + '.translate')[0]
    # XAxisTransRadio negates constraintTranslateX even though mirrorJoint uses XY.
    # Preserve and document this original coupling; do not infer a plane from labels.
    assert abs(initial[0] + 3) < 1e-5 and abs(initial[2] - 1) < 1e-5, initial
    assert abs(moved[0] + 5) < 1e-5, moved
    before_constraints = cmds.ls(type='constraint') or []
    mel.eval('mtbAV2_delete_all_created();')
    after_constraints = cmds.ls(type='constraint') or []
    print(json.dumps({'probe': 'real_scene_with_only_ui_query_stubs', 'initial_translate': initial, 'animated_translate': moved,
                      'constraints_before_clear': before_constraints, 'constraints_after_clear': after_constraints,
                      'joints_after_clear': cmds.ls(type='joint') or [], 'floatmath_after_clear': cmds.ls(type='floatMath') or [],
                      'gui_acceptance': False}))
