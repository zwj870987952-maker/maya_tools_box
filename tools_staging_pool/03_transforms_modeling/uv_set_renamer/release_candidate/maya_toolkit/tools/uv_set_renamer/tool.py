import re
import uuid
from maya_toolkit.framework.base_tool import BaseMayaTool
from maya_toolkit.framework.models import ToolResult

PROPS={'action':{'type':'string','enum':['inspect','rename'],'default':'inspect'},'objects':{'type':'array','items':{'type':'string'},'uniqueItems':True},'renames':{'type':'object','additionalProperties':{'type':'string'}}}


def normalize(kwargs):
    if set(kwargs)-set(PROPS): raise ValueError('Unknown arguments')
    p=dict(action='inspect'); p.update(kwargs)
    if p['action'] not in ('inspect','rename'): raise ValueError('Unknown action')
    if 'objects' in p and (not isinstance(p['objects'],list) or not p['objects'] or any(not isinstance(n,str) or not n for n in p['objects']) or len(p['objects'])!=len(set(p['objects']))): raise ValueError('Explicit unique mesh objects required')
    if p['action']=='inspect' and 'renames' in p: raise ValueError('Renames only apply to rename action')
    if p['action']=='rename':
        mapping=p.get('renames')
        if not isinstance(mapping,dict) or not mapping or any(not isinstance(old,str) or not old or not isinstance(new,str) or not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*',new) for old,new in mapping.items()): raise ValueError('Nonempty old/new mapping; new names use ASCII identifier syntax')
    return p


def meshes(values,write):
    from maya import cmds
    from maya.api import OpenMaya as om
    if not values: raise ValueError('Select at least one polygon mesh')
    rows=[]; seen=set()
    for value in values:
        if any(c in value for c in ('*','?','.',';','"','\n','\r','\\')): raise ValueError('Explicit whole mesh required')
        matches=cmds.ls(value,long=True) or []
        if len(matches)!=1: raise ValueError('Missing/ambiguous mesh')
        node=matches[0]
        if cmds.nodeType(node)=='mesh': shape=node
        elif cmds.nodeType(node)=='transform':
            shapes=cmds.listRelatives(node,shapes=True,noIntermediate=True,type='mesh',fullPath=True) or []
            if len(shapes)!=1: raise ValueError('Exactly one visible mesh per transform required')
            shape=shapes[0]
        else: raise ValueError('Polygon mesh required')
        if cmds.getAttr(shape+'.intermediateObject'): raise ValueError('Intermediate mesh unsupported')
        selection=om.MSelectionList(); selection.add(shape)
        if len(om.MDagPath.getAllPathsTo(selection.getDependNode(0)))!=1: raise ValueError('Instanced UV data unsupported')
        uid=cmds.ls(shape,uuid=True)[0]
        if uid in seen: raise ValueError('Duplicate mesh alias')
        seen.add(uid)
        if write and (cmds.referenceQuery(shape,isNodeReferenced=True) or any(cmds.lockNode(shape,query=True,lock=True) or []) or any(cmds.lockNode(node,query=True,lock=True) or [])): raise ValueError('Referenced/locked mesh')
        names=cmds.polyUVSet(shape,query=True,allUVSets=True) or []
        indices=cmds.polyUVSet(shape,query=True,allUVSetsIndices=True) or []
        if len(names)!=len(indices) or len(names)!=len(set(names)): raise ValueError('Invalid UV set table')
        current=cmds.polyUVSet(shape,query=True,currentUVSet=True) or []
        rows.append({'node':node,'shape':shape,'uuid':uid,'names':names,'indices':indices,'current':current})
    return rows


def plan(p):
    from maya import cmds
    rows=meshes(p.get('objects') or cmds.ls(selection=True,long=True) or [],p['action']=='rename')
    union=sorted({n for row in rows for n in row['names']})
    if p['action']=='inspect': return {'rows':rows,'uv_sets':union}
    if not cmds.undoInfo(query=True,state=True): raise ValueError('Undo must be enabled')
    if set(p['renames'])-set(union): raise ValueError('Old set absent from every mesh')
    for row in rows:
        mapping={old:new for old,new in p['renames'].items() if old in row['names'] and old!=new}
        final=[mapping.get(old,old) for old in row['names']]
        if len(set(final))!=len(final): raise ValueError('Final UV names collide on '+row['shape'])
        if mapping and (cmds.getAttr(row['shape']+'.uvSet',lock=True) or cmds.getAttr(row['shape']+'.currentUVSet',lock=True) or cmds.listConnections(row['shape']+'.currentUVSet',source=True,destination=False)): raise ValueError('Locked/driven UV set table/current set')
        for old in mapping:
            index=row['indices'][row['names'].index(old)]; plug=row['shape']+'.uvSet[%d].uvSetName'%index
            if cmds.getAttr(plug,lock=True) or cmds.listConnections(plug,source=True,destination=False): raise ValueError('UV name locked/driven')
        row['renames']=mapping; row['final_names']=final; row['final_current']=[mapping.get(name,name) for name in row['current']]
    return {'rows':rows,'uv_sets':union,'two_phase_names':True}


class UVSetRenamerTool(BaseMayaTool):
    tool_id='uv_set_renamer'; tool_name='UV集改名工具'; category='modeling_surfacing'; version='1.0-candidate.1'
    description='完整跨模型UV集合并列表与批量改名UI；只改拥有旧集的mesh，全部最终名称冲突/锁预检，两阶段支持交换循环，保留UV数据/index/当前集，一次Undo。'
    parameters_schema={'type':'object','properties':PROPS,'additionalProperties':False}

    def validate(self,**kwargs):
        try: return ToolResult.ok(data=plan(normalize(kwargs)),dry_run=True)
        except Exception as e: return ToolResult.fail(message=str(e),errors=[str(e)])

    def execute(self,**kwargs):
        from maya import cmds
        p=normalize(kwargs); data=plan(p)
        if p['action']=='inspect': return ToolResult.ok(data=data)
        # Prepare all temporary names before touching any mesh.
        temporary=[]
        reserved=set(data['uv_sets'])|set(p['renames'].values())
        for row in data['rows']:
            for old,new in row['renames'].items():
                temp='mtbUV_'+uuid.uuid4().hex
                while temp in reserved: temp='mtbUV_'+uuid.uuid4().hex
                reserved.add(temp); temporary.append((row['shape'],old,temp,new))
        for shape,old,temp,new in temporary: cmds.polyUVSet(shape,rename=True,uvSet=old,newUVSet=temp)
        for shape,old,temp,new in temporary: cmds.polyUVSet(shape,rename=True,uvSet=temp,newUVSet=new)
        for row in data['rows']:
            if row['renames'] and row['final_current']: cmds.polyUVSet(row['shape'],currentUVSet=True,uvSet=row['final_current'][0])
        return ToolResult.ok(data=data)

    def show_ui(self,parent=None):
        from maya import cmds
        if cmds.about(batch=True): raise RuntimeError('Interactive Maya required')
        initial=self.run(action='inspect')
        if not initial.success: raise ValueError(initial.message)
        win='mtbRenameUVSetsWindow'
        if cmds.window(win,exists=True): cmds.deleteUI(win)
        cmds.window(win,title='UV Set Renamer Candidate',widthHeight=(350,260),sizeable=True); main=cmds.columnLayout(adjustableColumn=True)
        fields={}
        for name in initial.data['uv_sets']:
            cmds.rowLayout(numberOfColumns=2,columnWidth2=(150,180)); cmds.text(label=name,align='left',backgroundColor=(.1,.1,.1),width=150,height=30)
            fields[name]=cmds.textField(backgroundColor=(1,1,1),height=30); cmds.setParent(main)
        ids=[row['uuid'] for row in initial.data['rows']]
        def call(dry):
            mapping={old:cmds.textField(field,query=True,text=True).strip() for old,field in fields.items()}; mapping={old:new for old,new in mapping.items() if new}
            if not mapping: cmds.warning('没有输入新UV集名'); return
            objects=[]
            for uid in ids:
                matches=cmds.ls(uid,long=True) or []
                if len(matches)!=1: cmds.warning('打开窗口时的mesh已删除/失效，请刷新'); return
                objects.append(matches[0])
            result=self.run(action='rename',objects=objects,renames=mapping,dry_run=dry); print(result.to_dict())
            if not result.success: cmds.warning(result.message)
        cmds.button(label='预检全部改名',command=lambda *_:call(True)); cmds.button(label='重命名',height=40,backgroundColor=(.9,.4,.4),command=lambda *_:call(False))
        cmds.button(label='按当前选择刷新列表',command=lambda *_:self.show_ui()); cmds.text(label='by ZWJ',height=30,align='right'); cmds.showWindow(win); return win


def create_uv_set_renamer(): return UVSetRenamerTool().show_ui()


def rename_uv_sets(uv_set_inputs,uv_sets):
    from maya import cmds
    mapping={old:cmds.textField(field,query=True,text=True).strip() for old,field in uv_set_inputs.items()}; mapping={old:new for old,new in mapping.items() if new}
    if not mapping: return ToolResult.ok(data={'rows':[]},message='No UV names entered')
    objects=list(dict.fromkeys(node for old in mapping for node in uv_sets[old]))
    return UVSetRenamerTool().run(action='rename',objects=objects,renames=mapping)
