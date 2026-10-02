import math
import time
from pathlib import Path
from maya_toolkit.framework import BaseMayaTool,ToolResult

class GEToolsOverlappyTool(BaseMayaTool):
    tool_id='getools_overlappy';tool_name='GETools / Overlappy / CenterOfMass';category='animation'
    description='完整中文GETools与固定MIT依赖；GUI重叠动力学/完整套件，COM和预设独立API'
    parameters_schema={'type':'object','additionalProperties':False,'properties':{
        'action':{'type':'string','enum':['inspect','show_ui','close','create_com','activate_com','add_com_targets','project_com','delete_com','setup_overlap','bake_overlap','clear_overlap','read_preset','save_preset'],'default':'inspect'},
        'targets':{'type':'array','uniqueItems':True,'items':{'type':'string'}},'weight':{'type':'number','minimum':0.001,'maximum':1000,'default':1},
        'mode':{'type':'string','enum':['point','aim','combo'],'default':'point'},'axis':{'type':'string','enum':['x','y','z'],'default':'y'},
        'preset_path':{'type':'string'},'preset_values':{'type':'object'},'confirm_bake':{'type':'boolean','default':False}}}
    def plan(self,**kw):
        if set(kw)-set(self.parameters_schema['properties']):raise ValueError('Unknown parameter')
        action=kw.get('action','inspect')
        if action not in self.parameters_schema['properties']['action']['enum']:raise ValueError('Invalid action')
        weight=kw.get('weight',1)
        if isinstance(weight,bool) or not isinstance(weight,(int,float)) or not math.isfinite(weight) or not 0.001<=weight<=1000:raise ValueError('Invalid weight')
        if kw.get('mode','point') not in ('point','aim','combo') or kw.get('axis','y') not in ('x','y','z'):raise ValueError('Invalid mode/axis')
        if not isinstance(kw.get('confirm_bake',False),bool):raise ValueError('confirm_bake must be boolean')
        data={'action':action,'impact':'Native suite scene operations; physics depends on frame rate, bake modifies keys/layers. External preset writes are not Undo-able.'}
        if action=='inspect':
            import json
            provenance=json.loads(Path(__file__).with_name('dependency_provenance.json').read_text(encoding='utf-8'))
            data.update(dependency_commit=provenance['commit'],localized_modules=8,features=['Transformations','Tools','Rigging','Overlappy point/aim/combo','CenterOfMass','MotionTrail','Experimental'],maya_gui_acceptance='not_run')
            return data
        if action in ('read_preset','save_preset'):
            from .preset_io import preset_plan
            data.update(preset_plan(action,kw.get('preset_path'),kw.get('preset_values')));return data
        import maya.cmds as cmds
        from . import runtime,ownership
        if action not in ('show_ui','close','activate_com') and not cmds.undoInfo(q=True,state=True):raise ValueError('Enable Maya Undo first')
        if action in ('show_ui','setup_overlap','bake_overlap','clear_overlap') and cmds.about(batch=True):raise ValueError('Interactive Maya required')
        if action=='bake_overlap' and not kw.get('confirm_bake',False):raise ValueError('confirm_bake=True required; back up animation first')
        targets=kw.get('targets',[])
        if not isinstance(targets,list) or not all(isinstance(t,str) and t for t in targets) or len(targets)!=len(set(targets)):raise ValueError('Invalid targets')
        resolved=[]
        for target in targets:
            names=cmds.ls(target,long=True) or []
            if len(names)!=1 or not cmds.objectType(names[0],isAType='transform'):raise ValueError('Expected unique transform '+target)
            if cmds.referenceQuery(names[0],isNodeReferenced=True) or cmds.lockNode(names[0],q=True,lock=True)[0]:raise ValueError('Reference/locked target refused')
            resolved.append(names[0])
        if action in ('activate_com','setup_overlap') and len(resolved)!=1:raise ValueError('Exactly one target required')
        if action=='add_com_targets' and not resolved:raise ValueError('At least one target required')
        if action in ('add_com_targets','project_com','delete_com'):
            # Do not construct or activate state during preflight.
            instance=runtime.COM
            if instance is None or not instance.COMObject or not cmds.objExists(instance.COMObject):raise ValueError('Create or activate COM first')
            if action=='delete_com':ownership.assert_com_owned(instance)
            if cmds.referenceQuery(instance.COMObject,isNodeReferenced=True) or cmds.lockNode(instance.COMObject,q=True,lock=True)[0]:raise ValueError('Locked/reference COM refused')
            data['com_object']=instance.COMObject
            if action=='add_com_targets' and any(cmds.ls(n,uuid=True)==cmds.ls(instance.COMObject,uuid=True) for n in resolved):raise ValueError('COM cannot constrain itself')
            if action=='add_com_targets' and any(cmds.getAttr(instance.COMObject+'.'+a,lock=True) for a in ('tx','ty','tz')):raise ValueError('COM translation locked')
        if action in ('setup_overlap','bake_overlap','clear_overlap'):
            instance=runtime.overlap_instance()
            from .bundle.GETOOLS_SOURCE.modules.Overlappy import OverlappySettings
            ownership.assert_group_owned(instance,OverlappySettings.nameGroup)
            if action=='bake_overlap' and not instance.setupCreated:raise ValueError('Create current setup first')
        if len(resolved)!=len(set(resolved)):raise ValueError('Duplicate resolved target')
        data['targets']=resolved;return data
    def validate(self,**kw):
        try:return ToolResult.ok(message='GETools预检通过，无窗口/场景/文件写入',data=self.plan(**kw),dry_run=True)
        except Exception as error:return ToolResult.fail(message=str(error),errors=[str(error)],dry_run=True)
    def execute(self,**kw):
        plan=self.plan(**kw);action=plan['action']
        if action=='inspect':return ToolResult.ok(data=plan)
        if action in ('read_preset','save_preset'):
            from .preset_io import execute_preset
            return ToolResult.ok(data=execute_preset(action,kw['preset_path'],kw.get('preset_values')))
        import maya.cmds as cmds
        from . import runtime
        if action=='show_ui':runtime.show()
        elif action=='close':runtime.close()
        elif action=='create_com':runtime.com_instance().COMCreate();plan['com_object']=runtime.COM.COMObject
        elif action=='activate_com':runtime.com_instance().COMObject=plan['targets'][0];plan['com_object']=runtime.COM.COMObject
        elif action=='delete_com':runtime.COM.COMClean()
        elif action=='add_com_targets':
            for target in plan['targets']:
                if target==runtime.COM.COMObject:raise ValueError('COM cannot constrain itself')
                cmds.pointConstraint(target,runtime.COM.COMObject,maintainOffset=False,weight=kw.get('weight',1))
            plan['constraints']=cmds.listConnections(runtime.COM.COMObject,source=True,destination=False,type='pointConstraint') or []
        elif action=='project_com':runtime.COM.COMFloorProjection(kw.get('axis','y'))
        elif action=='setup_overlap':
            cmds.select(plan['targets'],replace=True)
            runtime.overlap_instance().ParticleSetupLogic({'point':1,'aim':2,'combo':3}[kw.get('mode','point')])
            plan['setup_created']=runtime.overlap_instance().setupCreated
            if not plan['setup_created']:return ToolResult.fail(message='Native setup not created',data=plan)
        elif action=='clear_overlap':runtime.overlap_instance().ParticleSetupDelete()
        elif action=='bake_overlap':
            if not runtime.overlap_instance().BakeParticleLogic():return ToolResult.fail(message='Native baking failed',data=plan)
        return ToolResult.ok(message='GETools操作完成',data=plan)
    def run(self,dry_run=False,**kw):
        start=time.time()
        if not isinstance(dry_run,bool):return ToolResult.fail(message='dry_run must be boolean',tool_id=self.tool_id)
        result=self.validate(**kw)
        if result.success and not dry_run:
            try:
                if kw.get('action','inspect') in ('inspect','read_preset','save_preset','show_ui','close','activate_com'):result=self.execute(**kw)
                else:
                    from .ownership import scene_operation
                    result=scene_operation(self.execute)(**kw)
            except Exception as error:result=ToolResult.fail(message=str(error),errors=[str(error)])
        result.tool_id=self.tool_id;result.dry_run=dry_run;result.execution_time=round(time.time()-start,4);return result
    def show_ui(self,parent=None):
        from .runtime import show
        return show()
