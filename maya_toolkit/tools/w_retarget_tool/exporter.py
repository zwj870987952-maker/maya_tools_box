"""Explicit new-file FBX exports; restore all changed source options."""
import os
from pathlib import Path
import uuid
from maya import cmds, mel
from .tool import output_path


def quote(value):
    return '"' + str(value).replace('\\', '/').replace('"', '\\"') + '"'


def export(plan, params):
    commands = {'FBXExportUpAxis': params['up_axis'], 'FBXExportInAscii': int(params['ascii']), 'FBXExportFileVersion': params['fbx_version'], 'FBXExportBakeComplexAnimation': int(params['bake']), 'FBXExportBakeComplexStart': plan['start_frame'], 'FBXExportBakeComplexEnd': plan['end_frame_exclusive'] - 1, 'FBXExportBakeComplexStep': 1}
    old = {command: mel.eval(command + ' -q') for command in commands}
    selection = cmds.ls(selection=True, long=True) or []
    completed = []
    try:
        for command, value in commands.items():
            flag = ' ' if command == 'FBXExportUpAxis' else ' -v '
            mel.eval(command + flag + (quote(value) if isinstance(value, str) else str(value)))
        for job in plan['exports']:
            target = output_path(job['path'])
            temporary = target.with_name('.wRetarget_' + uuid.uuid4().hex + '.fbx')
            try:
                cmds.select(job['nodes'], replace=True)
                mel.eval('FBXExport -f ' + quote(temporary) + ' -s')
                if not temporary.is_file() or temporary.stat().st_size == 0:
                    raise RuntimeError('FBX exporter did not produce a file')
                output_path(str(target))
                if os.name == 'nt':
                    os.rename(str(temporary), str(target))
                else:
                    # Exclusive reservation prevents replacing an existing file.
                    with target.open('xb') as stream:
                        stream.write(temporary.read_bytes())
                    temporary.unlink()
                completed.append(str(target))
            finally:
                if temporary.exists():
                    temporary.unlink()
        return dict(plan, written_files=completed)
    finally:
        try:
            for command, value in old.items():
                flag = ' ' if command == 'FBXExportUpAxis' else ' -v '
                mel.eval(command + flag + (quote(value) if isinstance(value, str) else str(int(value)) if isinstance(value, bool) else str(value)))
        finally:
            if selection:
                cmds.select(selection, replace=True)
            else:
                cmds.select(clear=True)
