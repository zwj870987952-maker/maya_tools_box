"""Full original editors plus common safe API controls; no automatic startup."""
import importlib
_window=None


def call(**kwargs):
    from maya import cmds
    from .tool import CvWrapWeightDriverTool
    result=CvWrapWeightDriverTool().run(**kwargs)
    print(result.to_json())
    if not result.success:
        cmds.warning(result.message)
    return result


def rebind_dialog(dialog):
    return call(action='rebind',objects=dialog.components_to_rebind.text().split(),faces=dialog.target_faces.text().split(),wrap=str(dialog.cvwrap_combo.currentText()),radius=dialog.sample_radius.value())


def menu_dispatch(action):
    from maya import cmds
    menu=importlib.import_module('cvwrap.menu')
    if action=='create_wrap':
        native=menu.get_create_command_kwargs()
        p={'action':action,'objects':cmds.ls(selection=True,long=True) or [],'name':native.get('name','cvWrap#'),'radius':native.get('radius',0.1),'new_bind_mesh':bool(native.get('newBindMesh',False))}
        if native.get('binding'):
            p['path']=native['binding']
        return call(**p)
    wrap=menu.get_wrap_node_from_selected()
    if not wrap:
        return
    p={'action':action,'wrap':str(wrap)}
    if action in ('import_binding','export_binding'):
        paths=cmds.fileDialog2(fileMode=0 if action=='export_binding' else 1,fileFilter='cvWrap Binding (*.wrap)',dialogStyle=2)
        if not paths:
            return
        p['path']=paths[0]
    return call(**p)


def show_ui():
    global _window
    from maya import cmds
    if cmds.about(batch=True):
        raise RuntimeError('Interactive Maya required; no Qt construction in standalone')
    if _window and cmds.window(_window,exists=True):
        cmds.deleteUI(_window)
    _window=cmds.window(title='cvWrap / weightDriver / mGear 4.0.9 — 待验收',widthHeight=(550,490))
    cmds.columnLayout(adjustableColumn=True,rowSpacing=7)
    cmds.text(label='完整第三方套件入口；先查看依赖状态。\n本包未带编译插件，需兼容的用户插件和 PyMel。',align='left')
    cmds.button(label='只读依赖状态',command=lambda *a:call(action='status'))
    cmds.text(label='显式加载本机兼容 .mll（仅本次 Maya，不设自动加载）',align='left')
    choice=cmds.optionMenu()
    for name in ('cvwrap','weightDriver','mgear_solvers'):
        cmds.menuItem(label=name)
    binary=cmds.textField(placeholderText='绝对插件文件路径')
    cmds.button(label='加载选定插件',command=lambda *a:call(action='load_plugin',plugin=cmds.optionMenu(choice,query=True,value=True),path=cmds.textField(binary,query=True,text=True)))
    radius=cmds.floatField(value=0.1,minValue=0,maxValue=100,precision=3)
    new=cmds.checkBox(label='Create new bind mesh',value=False)
    cmds.button(label='按当前选择创建 cvWrap',command=lambda *a:call(action='create_wrap',objects=cmds.ls(selection=True,long=True) or [],radius=cmds.floatField(radius,query=True,value=True),new_bind_mesh=cmds.checkBox(new,query=True,value=True)))
    for label,action in [('完整 cvWrap 创建选项','cvwrap_options'),('完整 cvWrap Rebind 对话框','cvwrap_rebind_ui'),('原 weightDriver 3.6 MEL 编辑器','weightdriver_editor'),('完整 mGear RBF Manager','rbf_manager'),('显式安装完整 mGear 菜单（备份场景）','mgear_menu')]:
        cmds.button(label=label,command=lambda *a,action=action:call(action=action))
    # Binding import/export/paint are also present in the retained original
    # cvWrap menu module; expose them directly without installing global menus.
    field=cmds.textField(placeholderText='明确的 cvWrap 节点')
    def binding(action,*unused):
        p={'action':action,'wrap':cmds.textField(field,query=True,text=True)}
        if action!='paint_wrap':
            paths=cmds.fileDialog2(fileMode=0 if action=='export_binding' else 1,fileFilter='*.wrap',dialogStyle=2)
            if not paths:
                return
            p['path']=paths[0]
        return call(**p)
    for label,action in [('Import Binding','import_binding'),('Export Binding（拒绝覆盖）','export_binding'),('Paint cvWrap Weights','paint_wrap')]:
        cmds.button(label=label,command=lambda *a,action=action:binding(action))
    cmds.showWindow(_window)
    return _window
