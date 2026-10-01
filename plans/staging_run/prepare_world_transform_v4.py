"""Preserve complete supplied UI and archive, with isolated clipboard API."""
import ast
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
UNIT=ROOT/'tools_staging_pool/03_transforms_modeling/world_transform_v4'
RC=UNIT/'release_candidate'
PKG=RC/'maya_toolkit/tools/world_transform_v4'
PKG.mkdir(parents=True,exist_ok=True)
source=(UNIT/'复制粘贴世界坐标v4.py').read_text(encoding='utf8')
tree=ast.parse(source)
ui=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='show_world_transform_ui')
ui_source=ast.unparse(ui)
ui_source=ui_source.replace('worldTransformWin','mtbWorldTransformWin').replace('mainChannelBox','mainChannelBox')
header='''"""Complete original native UI, callbacks routed through the candidate API."""
import maya.cmds as cmds
from .tool import WorldTransformV4Tool
DEFAULT_MAX_ATTEMPTS=10
DEFAULT_FULL_CHECK_ATTEMPTS=5

def report(result):
    cmds.text('statusLabel',edit=True,label=result.message)
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
       'max_attempts':cmds.intSliderGrp('maxAttemptsSlider',query=True,value=True),
       'full_check_attempts':cmds.intSliderGrp('fullCheckAttemptsSlider',query=True,value=True),
       'only_keyframes':cmds.checkBox('keyframesOnlyCheckBox',query=True,value=True)}
    import maya.mel as mel
    slider=mel.eval('$mtbWorldSlider=$gPlayBackSlider')
    if cmds.timeControl(slider,query=True,rangeVisible=True):
        bounds=cmds.timeControl(slider,query=True,rangeArray=True)
        p['start']=bounds[0]; p['end']=bounds[1]-1
    return report(WorldTransformV4Tool().run(**p))
'''
content=header+'\n'+ui_source+'\n'
for name in ('maxAttemptsSlider','fullCheckAttemptsSlider','keyframesOnlyCheckBox','titleLabel','statusLabel','copyBtn','pasteBtn'):
    content=content.replace(name,'mtbWorld_'+name)
(PKG/'ui.py').write_text(content,encoding='utf8',newline='\n')
(PKG/'__init__.py').write_text('from .tool import WorldTransformV4Tool, copy_world_transform, paste_world_transform, show_world_transform_ui\n',encoding='utf8')
print('Complete original UI preserved; no module-level window launch')
