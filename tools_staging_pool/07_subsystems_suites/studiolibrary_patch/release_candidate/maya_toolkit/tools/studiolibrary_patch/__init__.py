"""Full Studio Library PlusPatch candidate with pure preflight and explicit IO."""
from maya_toolkit.framework import BaseMayaTool,ToolResult
from . import guards
ACTIONS=['inspect','show_ui','close_ui','install_extension','uninstall_extension','apply_theme','repair_cache','capture_pose','save_pose','load_pose','capture_animation','save_animation','load_animation','install_theme','uninstall_theme','set_language','show_history']
class StudioLibraryPatchTool(BaseMayaTool):
    tool_id='studiolibrary_patch';tool_name='Studio Library 世界空间与主题扩展';category='animation';version='1.0.0'
    description='Complete bundled Studio Library, world pose/animation, version history, Chinese localization and reversible ModernDark theme'
    parameters_schema={'type':'object','additionalProperties':False,'properties':{
        'action':{'type':'string','enum':ACTIONS,'default':'inspect'},'objects':{'type':'array','items':{'type':'string'},'maxItems':4096},
        'asset_path':{'type':'string'},'library_root':{'type':'string'},'resource_path':{'type':'string'},
        'frame_start':{'type':'number','default':1},'frame_end':{'type':'number','default':24},'sample_by':{'type':'number','exclusiveMinimum':0,'default':1},
        'blend':{'type':'number','minimum':0,'maximum':100,'default':100},'key':{'type':'boolean','default':False},'additive':{'type':'boolean','default':False},
        'start_frame':{'type':'number'},'option':{'type':'string','enum':['replace','merge','insert'],'default':'replace'},
        'language':{'type':'string','enum':['en_US','zh_CN']},'enabled':{'type':'boolean'}}}
    def validate(self,action='inspect',**kw):
        try:
            if action not in ACTIONS or set(kw)-set(self.parameters_schema['properties']):raise ValueError('Unknown action/arguments')
            for k in ('key','additive','enabled'):
                if k in kw and type(kw[k]) is not bool:raise ValueError('Boolean required: '+k)
            if not 0<=guards.finite(kw.get('blend',100))<=100:raise ValueError('Blend 0-100 required')
            if kw.get('option','replace') not in ('replace','merge','insert'):raise ValueError('Invalid paste option')
            if 'start_frame' in kw:guards.finite(kw['start_frame'])
            if action in ('capture_animation','save_animation'):guards.frames(kw.get('frame_start',1),kw.get('frame_end',24),kw.get('sample_by',1))
            if action in ('capture_pose','save_pose','load_pose','capture_animation','save_animation','load_animation'):guards.targets(kw.get('objects'),action.startswith('load'))
            if action in ('save_pose','load_pose','save_animation','load_animation'):guards.asset(kw.get('asset_path'),action.endswith('animation'),action.startswith('save'))
            if action=='show_ui' and not guards.path(kw.get('library_root')).is_dir():raise ValueError('Existing library root required')
            if action in ('install_theme','uninstall_theme'):
                from .theme_io import target
                target(kw.get('resource_path'))
            if action=='set_language' and kw.get('language') not in ('en_US','zh_CN'):raise ValueError('Language required')
            if action=='show_history' and 'enabled' not in kw:raise ValueError('Explicit enabled flag required')
            return ToolResult.ok(message='无副作用预检通过；未导入Studio Library或安装钩子',data={'action':action})
        except Exception as e:return ToolResult.fail(message=str(e),errors=[str(e)])
    def execute(self,action='inspect',**kw):
        from . import runtime
        if action=='inspect':return ToolResult.ok(data={'features':['full_studio_library','world_pose','world_animation','history','localization','ModernDark'],'dependency_commit':'d2173f64460f3fa413ebb3696c28efacc60ef0dd','gui_acceptance':'not_run'})
        if action=='show_ui':runtime.show(kw['library_root']);return ToolResult.ok(data={'window':'MTB_StudioLibraryPlusPatch'})
        if action=='close_ui':
            if runtime.window:runtime.window.close();runtime.window=None
            return ToolResult.ok()
        if action=='install_extension':return ToolResult.ok(data=runtime.activate())
        if action=='uninstall_extension':return ToolResult.ok(data=runtime.deactivate())
        if action=='apply_theme':return ToolResult.ok(data=runtime.apply_theme())
        if action=='repair_cache':return ToolResult.ok(data=runtime.repair())
        if action in ('install_theme','uninstall_theme'):
            from . import theme_io
            return ToolResult.ok(data=getattr(theme_io,action.split('_')[0])(kw['resource_path']))
        if action in ('set_language','show_history'):
            runtime.activate()
            from studiolibrary_wanimation import localization
            if action=='set_language':localization.set_language(kw['language'])
            else:localization.set_history_enabled(kw['enabled'])
            localization.retranslate_windows([runtime.window] if runtime.window else [])
            return ToolResult.ok(data={'settings_written':True,'undo':'Use inverse settings action; not Maya Undo'})
        posemod,animmod=runtime.core();objects=guards.targets(kw['objects'],action.startswith('load'))
        from maya import cmds
        time=cmds.currentTime(q=True);selection=cmds.ls(sl=True,long=True) or []
        try:
            if action in ('capture_pose','save_pose'):world=posemod.WorldPose.capture(objects)
            elif action in ('capture_animation','save_animation'):world=animmod.WorldAnimation.capture(objects,(kw.get('frame_start',1),kw.get('frame_end',24)),kw.get('sample_by',1))
            if action.startswith('capture'):return ToolResult.ok(data={'world_data':world.data})
            if action.startswith('save'):
                import mutils
                p=guards.asset(kw['asset_path'],action.endswith('animation'),True);p.mkdir()
                try:
                    if action=='save_pose':mutils.savePose(str(p/'pose.json'),objects);world.save(str(p/'world_pose.json'))
                    else:
                        # Preserve the original world-only pose branch and
                        # full native anim.ma branch for keyed custom attrs.
                        frame_range=(kw.get('frame_start',1),kw.get('frame_end',24))
                        standard=any(cmds.keyframe(obj+'.'+attr,q=True,keyframeCount=True,time=frame_range) for obj in objects for attr in (cmds.listAttr(obj,keyable=True,unlocked=True) or []) if attr not in animmod.WORLD_ATTRIBUTES)
                        if standard:mutils.saveAnim(objects,str(p),time=frame_range,sampleBy=kw.get('sample_by',1),fileType='mayaAscii',bakeConnected=False)
                        else:
                            anim=mutils.Animation.fromObjects(objects);anim.setMetadata('startFrame',frame_range[0]);anim.setMetadata('endFrame',frame_range[1]);mutils.Pose.save(anim,str(p/'pose.json'))
                        world.save(str(p/'world_transform.json'))
                except Exception as e:raise RuntimeError('Save failed; partial NEW asset retained at '+str(p)+': '+str(e))
                return ToolResult.ok(data={'asset_path':str(p),'files':[q.name for q in p.iterdir()],'undo':'External asset files cannot be undone'})
            p=guards.asset(kw['asset_path'],action.endswith('animation'))
            if action=='load_pose':report=posemod.load_wpose(str(p),objects=objects,blend=kw.get('blend',100),key=kw.get('key',False),additive=kw.get('additive',False),refresh=False,clearSelection=False)
            else:report=animmod.load_wanimation(str(p),objects=objects,start_frame=kw.get('start_frame'),option=kw.get('option','replace'))
            if report.get('failed') or report.get('cancelled'):return ToolResult.fail(message='Native load reported incomplete result; use Undo and inspect',errors=[str(report)],data=report)
            return ToolResult.ok(data=report)
        finally:
            cmds.currentTime(time,edit=True);cmds.select(selection,r=True) if selection else cmds.select(clear=True)
    def show_ui(self,parent=None):
        # Full original library; ask for an existing asset root through Maya UI.
        from maya import cmds
        if cmds.about(batch=True):raise RuntimeError('Real Maya GUI required')
        selected=cmds.fileDialog2(fileMode=3,caption='StudioLibrary 候选：选择已有资产目录')
        if not selected:return None
        from .runtime import show
        return show(selected[0],parent)
