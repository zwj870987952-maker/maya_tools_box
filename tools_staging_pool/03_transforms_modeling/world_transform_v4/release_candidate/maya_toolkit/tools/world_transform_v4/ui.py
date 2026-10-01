"""Complete original native UI, callbacks routed through the candidate API."""
import maya.cmds as cmds
from .tool import WorldTransformV4Tool
DEFAULT_MAX_ATTEMPTS=10
DEFAULT_FULL_CHECK_ATTEMPTS=5

def report(result):
    cmds.text('mtbWorld_statusLabel',edit=True,label=result.message)
    if not result.success: cmds.warning(result.message)
    return result

def copy_world_transform():
    return report(WorldTransformV4Tool().run(action='copy'))

def paste_world_transform():
    channels=cmds.channelBox('mainChannelBox',query=True,selectedMainAttributes=True) or []
    t=any(c in ('tx','ty','tz','translate','translateX','translateY','translateZ') for c in channels)
    r=any(c in ('rx','ry','rz','rotate','rotateX','rotateY','rotateZ') for c in channels)
    if not t and not r: t=r=True
    p={'action':'paste','channels':'both' if t and r else 'translate' if t else 'rotate',
       'max_attempts':cmds.intSliderGrp('mtbWorld_maxAttemptsSlider',query=True,value=True),
       'full_check_attempts':cmds.intSliderGrp('mtbWorld_fullCheckAttemptsSlider',query=True,value=True),
       'only_keyframes':cmds.checkBox('mtbWorld_keyframesOnlyCheckBox',query=True,value=True)}
    import maya.mel as mel
    slider=mel.eval('$mtbWorldSlider=$gPlayBackSlider')
    if cmds.timeControl(slider,query=True,rangeVisible=True):
        bounds=cmds.timeControl(slider,query=True,rangeArray=True)
        p['start']=bounds[0]; p['end']=bounds[1]-1
    return report(WorldTransformV4Tool().run(**p))

def show_world_transform_ui():
    """创建美观的用户界面"""
    if cmds.window('mtbWorldTransformWin', exists=True):
        cmds.deleteUI('mtbWorldTransformWin')
    window = cmds.window('mtbWorldTransformWin', title='世界坐标复制/还原工具', widthHeight=(400, 320), bgc=(0.2, 0.2, 0.22))
    main_layout = cmds.columnLayout(adjustableColumn=True, rowSpacing=5, columnAttach=('both', 5))
    cmds.text('mtbWorld_titleLabel', label='世界坐标复制/还原工具', font='boldLabelFont', height=30, align='center')
    cmds.separator(height=10, style='double')
    cmds.frameLayout(label='参数设置', collapsable=True, collapse=False, marginWidth=5, marginHeight=5)
    params_layout = cmds.columnLayout(adjustableColumn=True, rowSpacing=8)
    cmds.intSliderGrp('mtbWorld_maxAttemptsSlider', label='最大尝试次数:', field=True, minValue=1, maxValue=20, value=DEFAULT_MAX_ATTEMPTS, fieldMinValue=1, fieldMaxValue=50)
    cmds.intSliderGrp('mtbWorld_fullCheckAttemptsSlider', label='完整检查尝试次数:', field=True, minValue=1, maxValue=10, value=DEFAULT_FULL_CHECK_ATTEMPTS, fieldMinValue=1, fieldMaxValue=20)
    cmds.checkBox('mtbWorld_keyframesOnlyCheckBox', label='只处理关键帧', value=False)
    cmds.setParent('..')
    cmds.setParent('..')
    cmds.frameLayout(label='操作', collapsable=False, marginWidth=5, marginHeight=5)
    buttons_layout = cmds.columnLayout(adjustableColumn=True, rowSpacing=5)
    cmds.rowLayout(numberOfColumns=2, columnWidth2=(190, 190), adjustableColumn=1)
    cmds.button('mtbWorld_copyBtn', label='复制世界坐标', height=50, command=lambda x: copy_world_transform(), bgc=(0.3, 0.3, 0.35))
    cmds.button('mtbWorld_pasteBtn', label='粘贴世界坐标', height=50, command=lambda x: paste_world_transform(), bgc=(0.3, 0.3, 0.35))
    cmds.setParent('..')
    cmds.text(label='提示: 在通道栏中选择特定通道可以只粘贴对应属性', align='center', height=30)
    cmds.setParent('..')
    cmds.setParent('..')
    cmds.separator(height=10)
    cmds.text('mtbWorld_statusLabel', label='就绪', align='center')
    cmds.showWindow('mtbWorldTransformWin')
