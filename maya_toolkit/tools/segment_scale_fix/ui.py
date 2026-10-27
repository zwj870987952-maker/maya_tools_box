from maya import cmds
from .tool import SegmentScaleFixTool


def show_ui():
    if cmds.about(batch=True):
        raise RuntimeError('Interactive Maya required')
    name = 'stagingSegmentScaleFixWindow'
    if cmds.window(name, exists=True):
        cmds.showWindow(name)
        return name
    cmds.window(name, title='关闭骨骼分段比例补偿', widthHeight=(350, 130))
    cmds.columnLayout(adjustableColumn=True)
    cmds.text(label='仅所选关节；不展开层级。可能改变缩放外观。')
    def callback(dry):
        result = SegmentScaleFixTool().run(dry_run=dry)
        if result.success:
            cmds.text('stagingSegmentScaleStatus', edit=True, label='{} 项待改 / {} 项已关闭'.format(len(result.data['changes']), result.data['unchanged_count']))
        else:
            cmds.warning(result.message)
    cmds.button(label='只读预检', command=lambda unused=False: callback(True))
    cmds.button(label='关闭所选关节补偿', command=lambda unused=False: callback(False))
    cmds.text('stagingSegmentScaleStatus', label='请选择关节')
    cmds.showWindow(name)
    return name
