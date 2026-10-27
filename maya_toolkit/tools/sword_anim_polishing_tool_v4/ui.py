"""Independent full-function UI; no licensed vendor code/UI rewritten."""
def show_ui():
    from maya import cmds
    from .tool import SwordAnimPolishTool
    if cmds.about(batch=True):
        raise RuntimeError('Interactive Maya required')
    if cmds.window('sword_anim_polish_window_ui',exists=True):
        raise RuntimeError('Close original vendor UI before using candidate shared globals')
    name='mayaToolkitSwordPolish'
    if cmds.window(name,exists=True):
        cmds.deleteUI(name)
    window=cmds.window(name,title='Sword Anim Polishing — candidate',widthHeight=(370,580))
    cmds.columnLayout(adjustableColumn=True,rowSpacing=4)
    session=cmds.textFieldGrp(label='Session (optional)',text='')
    sizes=cmds.floatFieldGrp(label='Locator size',numberOfFields=1,value1=1,minValue=0.01)
    cmds.rowLayout(numberOfColumns=4)
    start=cmds.intField(value=int(cmds.playbackOptions(query=True,animationStartTime=True)))
    end=cmds.intField(value=int(cmds.playbackOptions(query=True,animationEndTime=True)))
    cmds.text(label='Start / End')
    cmds.setParent('..')
    knots=cmds.intSliderGrp(label='Path controls',field=True,minValue=2,maxValue=20,value=3)
    source=cmds.checkBox(label='Show source path',value=False)
    message=cmds.text(label='布置 Top/Side/Pivot 后点击完成；原 MEL 不作改写。',align='left')
    def apply(action,**extra):
        args={'action':action,**extra}
        selected_session=cmds.textFieldGrp(session,query=True,text=True).strip()
        if selected_session:
            args['session']=selected_session
        if action in ('parent_in','begin_aim','begin_reverse'):
            args['size']=cmds.floatFieldGrp(sizes,query=True,value1=True)
        if action in ('parent_in','begin_aim','begin_sword','begin_reverse','bake','bake_layer'):
            args.update(start=cmds.intField(start,query=True,value=True),end=cmds.intField(end,query=True,value=True))
        if action=='arc_polish':
            args.update(knots=cmds.intSliderGrp(knots,query=True,value=True),show_source=bool(cmds.checkBox(source,query=True,value=True)))
        tool=SwordAnimPolishTool()
        result=tool.run(**args)
        cmds.text(message,edit=True,label=result.message)
        if not result.success:
            cmds.warning(result.message)
        elif result.data.get('session'):
            cmds.textFieldGrp(session,edit=True,text=result.data['session'])
            if action in ('begin_aim','begin_sword','begin_reverse','parent_in','arc_polish'):
                from . import runtime
                ledger=runtime.v.Ledger(result.data['session'])
                group='base' if action in ('parent_in','begin_reverse') else ('path_locator' if action=='arc_polish' else 'aim_top')
                nodes=runtime.live_group(ledger,group)
                if nodes:
                    cmds.select(nodes,replace=True)
        if action=='help' and result.success:
            help_name='mayaToolkitSwordHelp'
            if cmds.window(help_name,exists=True):
                cmds.deleteUI(help_name)
            cmds.window(help_name,title='Sword original help',widthHeight=(620,430))
            cmds.columnLayout(adjustableColumn=True)
            cmds.scrollField(editable=False,wordWrap=True,text=result.data['text'],height=400)
            cmds.showWindow(help_name)
        return result
    for label,action in (('Parent In','parent_in'),('Make Aim — begin','begin_aim'),('Make Sword — begin','begin_sword'),('Make Reverse — begin','begin_reverse'),('完成 Top / Side / Pivot 布置','finish_setup'),('Arc Polish（实际时间滑块 / Graph Editor 区间）','arc_polish'),('Bake','bake'),('Layer Bake','bake_layer'),('Euler Filter','euler_filter'),('Delete owned system after bake','delete_system'),('MT Update','update_motion_trails'),('VP Restore','refresh_viewport'),('Status','status')):
        cmds.button(label=label,command=lambda _,a=action:apply(a))
    cmds.rowColumnLayout(numberOfColumns=4)
    for group in ('source','aim_top','aim_side','base','all','path_source','path_locator','path_system'):
        cmds.button(label=group,command=lambda _,g=group:apply('select_group',group=g))
    cmds.setParent('..')
    cmds.rowColumnLayout(numberOfColumns=4)
    for topic in ('base','reverse','path','bake'):
        cmds.button(label=topic+' help',command=lambda _,t=topic:apply('help',topic=t))
    cmds.showWindow(window)
    return window
