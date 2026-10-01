def apply_ui():
    from maya import cmds
    from .tool import StaggerGuiTool
    name='mayaToolkitStagger_'
    height=cmds.window(name+'stagger_window',query=True,height=True)
    try:
        args={'start':cmds.intField(name+'sf',query=True,value=True),'end':cmds.intField(name+'ef',query=True,value=True),'amount':cmds.floatSlider(name+'fl',query=True,value=True)}
        cmds.window(name+'stagger_window',edit=True,height=height+20)
        cmds.progressBar(name+'pb',edit=True,beginProgress=True,progress=0,visible=True)
        result=StaggerGuiTool().run(**args)
        if result.success:
            cmds.progressBar(name+'pb',edit=True,progress=100)
            cmds.inViewMessage(amg='Stagger complete',pos='topCenter',fade=True)
        else:
            cmds.warning(result.message)
        return result
    finally:
        cmds.progressBar(name+'pb',edit=True,endProgress=True,visible=False)
        cmds.window(name+'stagger_window',edit=True,height=height)
