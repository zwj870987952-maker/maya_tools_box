"""Small launcher for the native Mirror, using Maya controls only."""
from . import runtime

WINDOW = 'mayaToolkitAdvNativeMirror'


def show(tool):
    cmds, _ = runtime.maya()
    if cmds.window(WINDOW, exists=True):
        cmds.deleteUI(WINDOW)
    cmds.window(WINDOW, title='ADV 原生 Mirror', widthHeight=(460, 360))
    cmds.columnLayout(adjustableColumn=True, rowSpacing=8)
    cmds.text(label='直接调用 ADV Mirror · 无需配置镜像映射', align='left')
    source = cmds.textFieldButtonGrp(label='ADV 源文件', text=runtime.configured_source(), buttonLabel='浏览')
    def browse(*_):
        result = cmds.fileDialog2(fileMode=1, fileFilter='AdvancedSkeleton (*.mel)')
        if result:
            cmds.textFieldButtonGrp(source, e=True, text=result[0])
    cmds.textFieldButtonGrp(source, e=True, buttonCommand=browse)
    try:
        default_ns = runtime.resolve_namespace(None)
    except ValueError:
        default_ns = ''
    ns = cmds.textFieldGrp(label='角色命名空间', text=default_ns)
    side = cmds.optionMenuGrp(label='方向')
    for label in ('左右交换', '左 → 右', '右 → 左'):
        cmds.menuItem(label=label)
    axis = cmds.optionMenuGrp(label='轴')
    for label in ('X', 'Y', 'Z'):
        cmds.menuItem(label=label)
    space = cmds.optionMenuGrp(label='空间')
    for label in ('Main', 'World', 'RootX_M'):
        cmds.menuItem(label=label)
    frame_range = cmds.intFieldGrp(label='动画范围（含首尾）', numberOfFields=2,
        value1=int(cmds.playbackOptions(q=True, min=True)), value2=int(cmds.playbackOptions(q=True, max=True)))
    status = cmds.text(label='当前姿态遵循原生行为及 AutoKey；逐帧扩展不支持动画层。', wordWrap=True)
    def invoke(action, dry=False):
        args = {'action': action,
                'source_path': cmds.textFieldButtonGrp(source, q=True, text=True),
                'namespace': cmds.textFieldGrp(ns, q=True, text=True) or None,
                'side': ('swap', 'left_to_right', 'right_to_left')[cmds.optionMenuGrp(side, q=True, select=True)-1],
                'axis': cmds.optionMenuGrp(axis, q=True, value=True),
                'space': ('main', 'world', 'root')[cmds.optionMenuGrp(space, q=True, select=True)-1]}
        if action == 'mirror_animation':
            args['time_range'] = cmds.intFieldGrp(frame_range, q=True, value=True)[:2]
        result = tool.run(dry_run=dry, **args)
        cmds.text(status, e=True, label=result.message + '  %.2f 秒' % result.execution_time)
        print(result.to_json())
        return result
    cmds.button(label='预检（不修改场景）', command=lambda *_: invoke('mirror', True))
    cmds.button(label='Mirror 当前姿态', command=lambda *_: invoke('mirror'))
    cmds.button(label='打开 ADV 原生 Mirror 选项', command=lambda *_: invoke('open_options'))
    cmds.button(label='逐帧调用 Mirror 并设键', command=lambda *_: invoke('mirror_animation'))
    cmds.showWindow(WINDOW)
    return WINDOW
