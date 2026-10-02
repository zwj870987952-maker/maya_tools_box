"""Whole-input validation before original file/sequence operations."""
import re
from . import config_io
def plan_files(paths,mode,namespace='',confirm_replace_scene=False):
    from maya import cmds
    if mode not in ('open','import','reference'):raise ValueError('Unknown file mode')
    if not isinstance(paths,list) or not paths or len(paths)>64 or any(not isinstance(p,str) for p in paths) or len(set(paths))!=len(paths):raise ValueError('1-64 unique absolute files required')
    resolved=[]
    for value in paths:
        p=config_io.path(value)
        if not p.is_file() or p.suffix.lower() not in config_io.FILES:raise ValueError('Unsupported/absent source: '+value)
        if str(p.resolve()).casefold() in {r.casefold() for r in resolved}:raise ValueError('Duplicate resolved input')
        resolved.append(str(p.resolve()))
    if not isinstance(namespace,str) or namespace and not re.fullmatch(r'[A-Za-z_]\w*(?::[A-Za-z_]\w*)*',namespace):raise ValueError('Namespace must contain valid identifiers')
    if mode=='open':
        if len(resolved)!=1 or not confirm_replace_scene:raise ValueError('Open requires exactly one file and confirm_replace_scene=True')
        if cmds.file(query=True,modified=True):raise ValueError('Save the current dirty scene before opening another file')
    spaces=[]
    if mode=='reference':
        if not namespace:raise ValueError('Explicit reference namespace required')
        for index in range(len(resolved)):
            ns=namespace if len(resolved)==1 else namespace+'_'+str(index+1)
            if cmds.namespace(exists=ns):raise ValueError('Reference namespace already exists: '+ns)
            spaces.append(ns)
    return {'paths':resolved,'mode':mode,'namespaces':spaces,'scene_replace_undo':False,'script_nodes':False}
def execute_files(plan):
    from maya import cmds
    from maya_toolkit.core.context import UndoChunkContext
    if plan['mode']=='open':
        cmds.file(plan['paths'][0],open=True,force=False,executeScriptNodes=False)
        return {'opened':plan['paths'][0],'scene_replace_undo':False}
    if not cmds.undoInfo(query=True,state=True):raise ValueError('Enable Undo before import/reference')
    created=[]
    with UndoChunkContext('Smart Assistant '+plan['mode']):
        for index,p in enumerate(plan['paths']):
            if plan['mode']=='reference':created.extend(cmds.file(p,reference=True,namespace=plan['namespaces'][index],returnNewNodes=True,executeScriptNodes=False) or [])
            else:created.extend(cmds.file(p,i=True,ignoreVersion=True,renameAll=True,mergeNamespacesOnClash=False,preserveReferences=True,returnNewNodes=True,executeScriptNodes=False) or [])
    return {'created_nodes':created,'paths':plan['paths'],'mode':plan['mode'],'file_reference_undo':'Requires real Maya verification; no file rollback'}
def create_sequence(info,open_view=False):
    from maya import cmds
    from maya_toolkit.core.context import UndoChunkContext
    if open_view and cmds.about(batch=True):raise ValueError('Real Maya GUI needed for camera view')
    if not cmds.undoInfo(query=True,state=True):raise ValueError('Enable Maya Undo')
    before=cmds.ls(selection=True,long=True) or []
    with UndoChunkContext('Smart Assistant camera sequence'):
        try:
            camera,shape=cmds.camera(name='MTB_sa_bg_cam')
            plane,plane_shape=cmds.imagePlane(camera=camera,showInAllViews=True,width=10,height=10)
            cmds.setAttr(plane_shape+'.imageName',info['first_image'],type='string')
            cmds.setAttr(plane_shape+'.useFrameExtension',1);cmds.setAttr(plane_shape+'.displayOnlyIfCurrent',1)
            cmds.setAttr(camera+'.visibility',0)
            # Explicit, inspectable frame linkage rather than relying on a UI checkbox.
            connections=cmds.listConnections(plane_shape+'.frameExtension',source=True,destination=False,plugs=True) or []
            if len(connections)>1:raise RuntimeError('Unexpected imagePlane frame linkage')
            driver=connections[0] if connections else cmds.expression(name='MTB_sa_sequenceFrame',string=plane_shape+'.frameExtension = frame;',alwaysEvaluate=True,unitConversion='none')
        finally:cmds.select([n for n in before if cmds.objExists(n)],replace=True)
    view=None
    if open_view:
        from .native.main import camera_view
        view=camera_view(camera)
    return {'camera':camera,'camera_shape':shape,'image_plane':plane,'image_plane_shape':plane_shape,'frame_driver':driver,'view':view,**info}
