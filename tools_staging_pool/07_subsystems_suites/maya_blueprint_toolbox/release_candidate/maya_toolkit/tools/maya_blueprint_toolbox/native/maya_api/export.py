"""Full FBX operation with explicit file protection and temporary globals."""
import json
import math
from .common import MayaApiError,maya_modules
from .scene_nodes import existing_nodes
from ...file_io import output_path,backup_file
def export_fbx(nodes,target_path,bake_animation=False,frame_start=1.,frame_end=120.,overwrite_existing=False):
    cmds,mel=maya_modules(include_mel=True)
    nodes=existing_nodes(nodes)
    p=output_path(target_path,overwrite_existing)
    if p.suffix.lower()!='.fbx':raise MayaApiError('FBX extension required')
    start,end=float(frame_start),float(frame_end)
    if not math.isfinite(start) or not math.isfinite(end) or end<start:raise MayaApiError('Invalid FBX frame bounds')
    if p.exists():backup_file(p)
    if not cmds.pluginInfo('fbxmaya',query=True,loaded=True):cmds.loadPlugin('fbxmaya')
    flags=('FBXExportBakeComplexAnimation','FBXExportBakeComplexStart','FBXExportBakeComplexEnd')
    previous={f:mel.eval(f+' -q') for f in flags}
    selection=cmds.ls(selection=True,long=True) or []
    try:
        mel.eval('FBXExportBakeComplexAnimation -v '+str(bool(bake_animation)).lower())
        if bake_animation:
            mel.eval('FBXExportBakeComplexStart -v '+str(start));mel.eval('FBXExportBakeComplexEnd -v '+str(end))
        cmds.select(nodes,replace=True)
        mel.eval('FBXExport -f '+json.dumps(p.as_posix(),ensure_ascii=False)+' -s')
    finally:
        for f,value in previous.items():mel.eval(f+' -v '+(str(value).lower() if isinstance(value,bool) else str(value)))
        cmds.select([n for n in selection if cmds.objExists(n)],replace=True)
    if not p.is_file():raise MayaApiError('Native export produced no file')
    return str(p)
