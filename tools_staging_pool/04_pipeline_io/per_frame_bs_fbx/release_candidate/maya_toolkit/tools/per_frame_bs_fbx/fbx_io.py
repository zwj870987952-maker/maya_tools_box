"""Packaged FBX export implementation; no dependency on staging paths."""
from contextlib import contextmanager

import json

import math

import os

from pathlib import Path

import re

import shutil

import tempfile

FLAGS = {'input_connections': 'FBXExportInputConnections', 'ascii': 'FBXExportInAscii', 'smoothing_groups': 'FBXExportSmoothingGroups', 'smooth_mesh': 'FBXExportSmoothMesh', 'referenced_assets': 'FBXExportReferencedAssetsContent', 'triangulate': 'FBXExportTriangulate', 'skins': 'FBXExportSkins', 'cameras': 'FBXExportCameras', 'embedded_textures': 'FBXExportEmbeddedTextures'}

DEFAULTS = dict(export_animation=True, input_connections=False, ascii=True, smoothing_groups=True, smooth_mesh=True, referenced_assets=True, triangulate=False, skins=True, cameras=True, embedded_textures=True, up_axis='Y', file_version='FBX202000')

@contextmanager
def preserve_session():
    from maya import cmds
    enabled = cmds.undoInfo(query=True, state=True)
    selected = cmds.ls(selection=True, long=True) or []
    time = cmds.currentTime(query=True)
    auto = cmds.autoKeyframe(query=True, state=True)
    playback = {key: cmds.playbackOptions(query=True, **{key: True}) for key in ('animationStartTime', 'animationEndTime', 'minTime', 'maxTime')}
    cmds.undoInfo(stateWithoutFlush=False)
    try:
        yield
    finally:
        cmds.playbackOptions(**playback)
        if cmds.currentTime(query=True) != time:
            cmds.currentTime(time)
        cmds.autoKeyframe(state=auto)
        valid = [n for n in selected if cmds.objExists(n)]
        cmds.select(valid, replace=True) if valid else cmds.select(clear=True)
        cmds.undoInfo(stateWithoutFlush=enabled)

def mel_string(value):
    return json.dumps(str(value).replace('\\', '/'), ensure_ascii=False)

@contextmanager
def fbx_settings():
    from maya import mel
    commands = list(FLAGS.values()) + ['FBXExportBakeComplexAnimation', 'FBXExportBakeComplexStep', 'FBXExportBakeComplexStart', 'FBXExportBakeComplexEnd', 'FBXExportUpAxis', 'FBXExportFileVersion']
    state = {cmd: mel.eval(cmd + ' -q') for cmd in commands}
    animation = mel.eval('FBXProperty "Export|IncludeGrp|Animation" -q')
    try:
        yield
    finally:
        errors = []
        for command, value in state.items():
            argument = mel_string(value) if command == 'FBXExportFileVersion' else str(value).lower() if command == 'FBXExportUpAxis' else 'true' if value is True else 'false' if value is False else str(value)
            try:
                mel.eval(command + (' ' if command in ('FBXExportUpAxis', 'FBXExportFileVersion') else ' -v ') + argument)
            except RuntimeError as exc:
                errors.append(str(exc))
        try:
            mel.eval('FBXProperty "Export|IncludeGrp|Animation" -v ' + ('true' if animation else 'false'))
        except RuntimeError as exc:
            errors.append(str(exc))
        if errors:
            raise RuntimeError('FBX settings restore failed: ' + '; '.join(errors))

def export(data):
    from maya import cmds, mel
    if not cmds.pluginInfo('fbxmaya', query=True, loaded=True):
        cmds.loadPlugin('fbxmaya', quiet=True)
    outputs = []
    opts = data['options']
    with preserve_session(), fbx_settings():
        for task in data['tasks']:
            for key, command in FLAGS.items():
                mel.eval(command + ' -v ' + ('true' if opts[key] else 'false'))
            mel.eval('FBXProperty "Export|IncludeGrp|Animation" -v ' + ('true' if opts['export_animation'] else 'false'))
            mel.eval('FBXExportBakeComplexAnimation -v ' + ('true' if opts['export_animation'] else 'false'))
            for command, value in (('FBXExportBakeComplexStep', 1), ('FBXExportBakeComplexStart', task['start']), ('FBXExportBakeComplexEnd', task['end'])):
                mel.eval(command + ' -v ' + str(value))
            mel.eval('FBXExportUpAxis ' + opts['up_axis'].lower())
            mel.eval('FBXExportFileVersion ' + mel_string(opts['file_version']))
            cmds.playbackOptions(animationStartTime=task['start'], animationEndTime=task['end'], minTime=task['start'], maxTime=task['end'])
            cmds.select(task['objects'], replace=True, hierarchy=True)
            target = Path(task['output'])
            with tempfile.TemporaryDirectory(prefix='mtb_fbx_', dir=str(target.parent)) as directory:
                generated = Path(directory) / 'result.fbx'
                mel.eval('FBXExport -f ' + mel_string(generated) + ' -s')
                if not generated.is_file() or not generated.stat().st_size:
                    raise RuntimeError('FBX exporter produced no file')
                owned = False
                try:
                    with target.open('xb') as writer:
                        owned = True
                        with generated.open('rb') as reader:
                            shutil.copyfileobj(reader, writer)
                        writer.flush()
                        os.fsync(writer.fileno())
                except Exception:
                    if owned:
                        target.unlink(missing_ok=True)
                    raise
            outputs.append(dict(task, bytes=target.stat().st_size))
    return outputs
FLAGS['blend_shapes']='FBXExportShapes'
DEFAULTS['blend_shapes']=True
