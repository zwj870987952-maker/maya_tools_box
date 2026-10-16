from .catalog import OPERATIONS
from . import engine


def show(tool):
    cmds, _ = engine.mirror.maya()
    window = 'mayaToolkitAdvAnimation'
    if cmds.window(window, exists=True):
        cmds.deleteUI(window)
    cmds.window(window, title='ADV 本机动画 API（待整理）', widthHeight=(600, 470))
    cmds.columnLayout(adjustableColumn=True, rowSpacing=8)
    cmds.text(label='选择功能，预检后调用；交互窗口中的后续操作由 ADV 执行。', align='left')
    try:
        ns = engine.mirror.resolve_namespace(None)
    except ValueError:
        ns = ''
    namespace = cmds.textFieldGrp(label='角色', text=ns)
    limb = cmds.textFieldGrp(label='肢体（FK/IK 用）', text='Arm_L')
    operations = cmds.textScrollList(height=270, allowMultiSelection=False,
                                    append=[v['label'] for v in OPERATIONS.values()], selectIndexedItem=1)
    status = cmds.text(label='预检不会修改场景', wordWrap=True)
    undo_loss = cmds.checkBox(label='粘贴时接受 ADV 清空 Maya 撤销历史', value=False)
    def invoke(dry):
        op = list(OPERATIONS)[cmds.textScrollList(operations, q=True, selectIndexedItem=True)[0]-1]
        args = {'operation': op, 'namespace': cmds.textFieldGrp(namespace, q=True, text=True)}
        if op in ('pose_paste', 'animation_paste'):
            args['accept_undo_history_loss'] = cmds.checkBox(undo_loss,q=True,value=True)
        if OPERATIONS[op]['binding'] in ('limb','bake_one','bake_zero'):
            args['limb'] = cmds.textFieldGrp(limb, q=True, text=True)
        result = tool.run(dry_run=dry, **args)
        cmds.text(status, e=True, label=result.message)
        print(result.to_json())
    cmds.button(label='预检', command=lambda *_: invoke(True))
    cmds.button(label='调用所选功能', command=lambda *_: invoke(False))
    cmds.showWindow(window)
    return window
