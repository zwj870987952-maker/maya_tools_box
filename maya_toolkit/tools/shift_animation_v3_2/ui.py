"""Complete external frontend; vendor UI and code stay byte for byte unchanged."""
import maya.cmds as cmds

from .tool import ShiftAnimationTool
from .runtime import PKG

WINDOW='mtkShiftCandidateWindow'
_owned_window=None
_fields={}


def take(field,kind):
    if kind=='text':
        return cmds.textField(_fields[field],query=True,text=True).strip()
    if kind=='int':
        return cmds.intField(_fields[field],query=True,value=True)
    return cmds.checkBox(_fields[field],query=True,value=True)


def selected_into(field,*args):
    nodes=cmds.ls(selection=True,long=True) or []
    if len(nodes)!=1:
        cmds.warning('请恰好选择一个完整对象')
        return
    cmds.textField(_fields[field],edit=True,text=nodes[0])


def selected_layer(*args):
    nodes=[n for n in cmds.ls(type='animLayer') or [] if cmds.animLayer(n,query=True,selected=True) and n!=cmds.animLayer(query=True,root=True)]
    if len(nodes)!=1:
        cmds.warning('请选择一个非 BaseAnimation 的动画层')
        return
    cmds.textField(_fields['layer'],edit=True,text=nodes[0])


def invoke(action,*args):
    options={'action':action}
    session=take('session','text')
    if session:
        options['session']=session
    if action in ('match','extract','auto_path','create_path','create_circle','root_motion'):
        layer=take('layer','text')
        if layer:
            options['layer']=layer
    if action in ('create_path','auto_path','create_circle'):
        value=take('curve_object','text')
        if value:
            options['curve_object']=value
    if action in ('create_path','auto_path'):
        options.update(cv_count=take('cv_count','int'),flat=take('flat','bool'))
    if action in ('auto_path','apply_path'):
        options.update(easing=take('easing','int'),vertical_independent=take('vertical_independent','bool'))
    if action in ('auto_path','apply_path','apply_circle','root_motion'):
        options['allow_attribute_cleanup']=take('allow_attribute_cleanup','bool')
    if action=='root_motion':
        options.update(main=take('main','text'),pelvis=take('pelvis','text'),rotate=take('rotate','bool'),flat=take('root_flat','bool'))
    tool=ShiftAnimationTool()
    result=tool.run(dry_run=take('dry_run','bool'),**options)
    if result.success:
        if result.data.get('session'):
            cmds.textField(_fields['session'],edit=True,text=result.data['session'])
        cmds.text(_fields['message'],edit=True,label=result.message)
        print(result.data)
    else:
        cmds.warning(result.message)
        cmds.text(_fields['message'],edit=True,label=result.message)
    return result


def text_field(parent,key,label,pick=True):
    row=cmds.rowLayout(parent=parent,numberOfColumns=3,adjustableColumn=2)
    cmds.text(label=label,parent=row)
    _fields[key]=cmds.textField(parent=row)
    if pick:
        cmds.button(label='<<',parent=row,command=lambda *a:selected_into(key))
    else:
        cmds.text(label='',parent=row)


def buttons(parent,items):
    for action,label in items:
        cmds.button(parent=parent,label=label,height=30,command=lambda *a,action=action:invoke(action))


def show_ui():
    global _owned_window
    if cmds.about(batch=True):
        raise RuntimeError('Open this frontend in a real interactive Maya')
    if cmds.window('SHIFTING_animation',exists=True):
        raise RuntimeError('Close the original vendor window first')
    if cmds.window(WINDOW,exists=True):
        if _owned_window!=WINDOW:
            raise RuntimeError('An unowned window uses the candidate window name')
        cmds.showWindow(WINDOW)
        return WINDOW
    window=cmds.window(WINDOW,title='SHIFTING v3.2 候选 · (c) Pavel Barnev',widthHeight=(470,760),sizeable=True)
    _owned_window=WINDOW
    scroll=cmds.scrollLayout(parent=window,childResizable=True)
    top=cmds.columnLayout(parent=scroll,adjustableColumn=True,rowSpacing=4)
    cmds.image(parent=top,image=str(PKG/'vendor/ico/Shift_animation.bmp'),width=32,height=32)
    cmds.text(parent=top,label='完整原算法外围适配 · 真实 Maya 验收待完成',align='left')
    cmds.text(parent=top,label='原软件不可修改/再分发；商业使用按原许可证购买',align='left')
    text_field(top,'session','候选会话 UUID',False)
    layer_row=cmds.rowLayout(parent=top,numberOfColumns=3,adjustableColumn=2)
    cmds.text(parent=layer_row,label='输入动画层')
    _fields['layer']=cmds.textField(parent=layer_row,placeholderText='留空使用恰好一个已选层')
    cmds.button(parent=layer_row,label='<<',command=selected_layer)
    _fields['dry_run']=cmds.checkBox(parent=top,label='仅预检，不执行',value=False)
    _fields['allow_attribute_cleanup']=cmds.checkBox(parent=top,label='允许原路径/Root Motion 清理控制器全部自定义属性（先备份）',value=False)
    buttons(top,[('match','MATCH from animLayer'),('extract','extract to separate animLayer')])
    path_frame=cmds.frameLayout(parent=top,label='path from layer / manual path',collapsable=True,collapse=False)
    path=cmds.columnLayout(parent=path_frame,adjustableColumn=True,rowSpacing=3)
    text_field(path,'curve_object','curve object')
    cmds.text(parent=path,label='留空使用原算法自动检测；需移动的 Root Motion 控制器',align='left')
    row=cmds.rowLayout(parent=path,numberOfColumns=4)
    cmds.text(parent=row,label='CV')
    _fields['cv_count']=cmds.intField(parent=row,value=5,minValue=1,width=55)
    cmds.text(parent=row,label='easing')
    _fields['easing']=cmds.intField(parent=row,value=10,minValue=0,width=55)
    _fields['flat']=cmds.checkBox(parent=path,label='flat',value=True)
    _fields['vertical_independent']=cmds.checkBox(parent=path,label='vertical independent',value=True)
    buttons(path,[('auto_path','AUTOPATH from animLayer'),('create_path','create path curve'),('lock_curve','lock_len'),('unlock_curve','unlock_len'),('project_curve','project (选曲线、参考曲线)'),('curve_controls','curve control'),('arrange_controls','arrange (选本系统控制器)'),('delete_controls','delete system, keep curve'),('apply_path','apply manual path')])
    root_frame=cmds.frameLayout(parent=top,label='rootmotion',collapsable=True,collapse=True)
    root=cmds.columnLayout(parent=root_frame,adjustableColumn=True)
    text_field(root,'main','Main')
    text_field(root,'pelvis','Pelvis')
    _fields['rotate']=cmds.checkBox(parent=root,label='rotate',value=False)
    _fields['root_flat']=cmds.checkBox(parent=root,label='flat from first root position',value=True)
    buttons(root,[('root_motion','calculate rootmotion')])
    circle_frame=cmds.frameLayout(parent=top,label='circle walk (同上 curve object)',collapsable=True,collapse=True)
    circle=cmds.columnLayout(parent=circle_frame,adjustableColumn=True)
    buttons(circle,[('create_circle','create bend curve'),('apply_circle','calculate circle walk')])
    buttons(top,[('euler_filter','Euler filter (selected objects)'),('refresh_viewport','VP'),('status','读取会话状态')])
    _fields['message']=cmds.text(parent=top,label='仅在备份场景验收；失败后检查 Script Editor 并 Undo',wordWrap=True,align='left')
    cmds.text(parent=top,label='(c) Pavel Barnev · pavel_barnev2000@mail.ru',align='right')
    cmds.showWindow(window)
    return window
