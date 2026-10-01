from maya import cmds
from .tool import VelocityCalculatorTool, get_linear_distance

_TOOL = None


def get_average_velocity(*args):
    result = _TOOL.run(mode='average', show_result=True)
    if not result.success:
        cmds.warning(result.message)
    return result


def get_instant_velocity(*args):
    result = _TOOL.run(mode='instant', show_result=True)
    if not result.success:
        cmds.warning(result.message)
    return result


def create_ui(adapter=None):
    global _TOOL
    if cmds.about(batch=True):
        raise RuntimeError('Interactive Maya required for velocity window')
    _TOOL = adapter or VelocityCalculatorTool()
    name = 'velocityCalculator_candidate'
    if cmds.window(name, exists=True):
        cmds.deleteUI(name)
    window = cmds.window(name, title='速度计算器', width=320)
    cmds.columnLayout(adjustableColumn=True)
    cmds.text(label='区间：端点位移/秒；瞬时：向后一帧差分\n世界空间，保持当前时间不变')
    cmds.button(label='计算平均速度', command=get_average_velocity)
    cmds.button(label='计算瞬时速度', command=get_instant_velocity)
    cmds.showWindow(window)
    return window
