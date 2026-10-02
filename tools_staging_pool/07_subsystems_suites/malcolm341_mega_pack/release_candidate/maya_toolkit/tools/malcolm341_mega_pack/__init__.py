"""Complete personal native MEL suite with a bounded tool contract."""
from maya_toolkit.framework.base_tool import BaseMayaTool
from maya_toolkit.framework.models import ToolResult
from . import runtime

class Malcolm341MegaPackTool(BaseMayaTool):
    tool_id='malcolm341_mega_pack'
    tool_name='Malcolm341 Mega Pack'
    category='modeling_surfacing'
    description='完整49按钮原生MEL建模/UV/材质套件，按固定按钮与菜单调用；文件与全局偏好影响详见说明'
    version='1.0.0'
    parameters_schema={'type':'object','additionalProperties':False,'properties':{
        'action':{'type':'string','enum':['inspect','show_ui','close_ui','run_button'],'default':'inspect'},
        'button_id':{'type':'string','pattern':'^button_[0-9]{3}$'},
        'event':{'type':'string','enum':['primary','double','menu_001','menu_002','menu_003','menu_004','menu_005'],'default':'primary'},
        'confirm_native':{'type':'boolean','default':False},
        'file_path':{'type':['string','null'],'description':'临时导出/导入的显式绝对路径；导出只允许新文件'},
        'selection':{'type':'array','items':{'type':'string'},'minItems':1,'uniqueItems':True,'description':'可选明确对象/组件，预检解析全部对象后才设置选择'}},'required':[]}

    def _plan(self,kwargs):
        if set(kwargs)-set(self.parameters_schema['properties']):raise ValueError('Unknown argument')
        action=kwargs.get('action','inspect')
        if action not in self.parameters_schema['properties']['action']['enum']:raise ValueError('Unknown action')
        confirm=kwargs.get('confirm_native',False)
        if type(confirm) is not bool:raise ValueError('confirm_native must be boolean')
        plan={'action':action,'gui_acceptance':'not_run'}
        if action=='inspect':return plan
        from maya import cmds
        if action in ('show_ui','close_ui'):
            if cmds.about(batch=True):raise ValueError('Real Maya GUI required')
            return plan
        row,c=runtime.lookup(kwargs.get('button_id'),kwargs.get('event','primary'))
        if not confirm:raise ValueError('confirm_native=True required for supplied native operations')
        if cmds.about(batch=True) and (row['id'],c['event'])!=('button_018','primary'):
            raise ValueError('This native callback requires real Maya GUI acceptance')
        if not cmds.undoInfo(query=True,state=True):raise ValueError('Enable Maya Undo before native operations')
        supplied=kwargs.get('selection')
        if supplied is not None and (not isinstance(supplied,list) or not supplied or any(not isinstance(n,str) or not n or '*' in n or '?' in n for n in supplied) or len(set(supplied))!=len(supplied)):
            raise ValueError('Selection must contain unique explicit objects/components')
        selection=[]
        for item in (supplied if supplied is not None else cmds.ls(selection=True,long=True,flatten=True) or []):
            found=cmds.ls(item,long=True,flatten=True) or []
            if not found or ('.' not in item and len(found)!=1):raise ValueError('Missing or ambiguous selection: '+item)
            for n in found:
                base=n.split('.')[0]
                if cmds.referenceQuery(base,isNodeReferenced=True) or any(cmds.lockNode(base,query=True,lock=True)):
                    raise ValueError('Locked/referenced selection refused: '+base)
                if n not in selection:selection.append(n)
        if row['id']=='button_018' and c['event']=='primary':
            vertices=cmds.ls(cmds.polyListComponentConversion(selection,toVertex=True),flatten=True,long=True) or []
            meshes={v.split('.')[0] for v in vertices}
            if not vertices or len(meshes)!=1:raise ValueError('Pivot requires nonempty vertices from exactly one polygon mesh')
            mesh=next(iter(meshes));shape=mesh if cmds.nodeType(mesh)=='mesh' else next(iter(cmds.listRelatives(mesh,shapes=True,noIntermediate=True,fullPath=True) or []),None)
            if not shape or cmds.nodeType(shape)!='mesh':raise ValueError('Polygon mesh required')
            transform=(cmds.listRelatives(shape,parent=True,fullPath=True) or [None])[0]
            if not transform:raise ValueError('Mesh transform required')
            if cmds.referenceQuery(transform,isNodeReferenced=True) or any(cmds.lockNode(transform,query=True,lock=True)):raise ValueError('Locked/referenced transform refused')
            if any(cmds.getAttr(transform+'.'+p+a,lock=True) for p in ('rotatePivot','scalePivot') for a in ('X','Y','Z')):raise ValueError('Pivot attributes locked')
        mode=runtime.temp_mode(row['id'],c['event']);path=kwargs.get('file_path')
        if mode and mode<=6:
            from .file_guard import checked_path,require_new
            p=checked_path(path);ext={1:'.ma',2:'.obj',3:'.fbx',4:'.ma',5:'.obj',6:'.fbx'}[mode]
            if p.suffix.lower()!=ext:raise ValueError('Transfer requires '+ext+' path')
            if mode<=3:require_new(str(p))
            elif not p.is_file():raise ValueError('Import source absent')
            path=str(p)
        elif path is not None:raise ValueError('file_path only applies to native temporary transfer')
        return {**plan,'button_id':row['id'],'label':row['label'],'event':c['event'],
                'effects':c['effects'],'selection':selection,'set_selection':supplied is not None,'file_path':path,
                'external_file_undo':False,'native_scope':'Original callback may use all scene objects/global preferences'}

    def validate(self,**kwargs):
        try:return ToolResult.ok('Native operation plan',data=self._plan(kwargs),dry_run=True)
        except Exception as e:return ToolResult.fail(str(e),errors=[str(e)])

    def execute(self,**kwargs):
        p=self._plan(kwargs);action=p['action']
        if action=='inspect':return ToolResult.ok('Complete native inventory',data=runtime.metadata())
        if action=='show_ui':return ToolResult.ok('Owned complete shelf',data={'shelf':runtime.show_shelf()})
        if action=='close_ui':runtime.close_shelf();return ToolResult.ok('Owned shelf closed')
        from maya import cmds
        from maya_toolkit.core.context import UndoChunkContext
        # Explicit selection writes belong to the same Undo group as the native operation.
        with UndoChunkContext('Malcolm341_'+p['button_id']):
            if p['set_selection']:cmds.select(p['selection'],replace=True)
            value=runtime.run_native(p['button_id'],p['event'],p['file_path'])
        return ToolResult.ok('Native callback completed; verify the scene/output in Maya',data={'button_id':p['button_id'],'event':p['event'],'native_result':value,'file_path':p['file_path']})

    def run(self,dry_run=False,**kwargs):
        if type(dry_run) is not bool:return ToolResult.fail('dry_run must be boolean')
        try:
            result=self.validate(**kwargs)
            if result.success and not dry_run:result=self.execute(**kwargs)
        except Exception as e:result=ToolResult.fail(str(e),errors=[str(e)])
        result.tool_id=self.tool_id;result.dry_run=dry_run;return result

    def show_ui(self,parent=None):return self.run(action='show_ui')
