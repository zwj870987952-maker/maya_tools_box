"""Keep all original controls/assets, routing scene commands through the API."""
from pathlib import Path
import xml.etree.ElementTree as ET


def ui_text(language=''):
    if language not in ('','chn','eng','jpn'):
        raise ValueError('Unknown interface language')
    native=Path(__file__).parent/'native'
    tree=ET.fromstring((native/('springMagic'+('_'+language if language else '')+'.ui')).read_text(encoding='utf-8-sig'))
    for element in tree.iter():
        for attr in ('text','tail'):
            value=getattr(element,attr)
            if value and value.strip().startswith('icons/'):
                setattr(element,attr,str(native/value.strip()).replace('\\','/'))
    return ET.tostring(tree,encoding='unicode')


def load_ui(language=''):
    from maya import cmds
    return cmds.loadUI(uiString=ui_text(language))


def selected_range(widget):
    from maya import cmds
    if widget.active_radioButton.getSelect():
        return {'start':int(cmds.playbackOptions(query=True,minTime=True)),'end':int(cmds.playbackOptions(query=True,maxTime=True))}
    return {'start':int(widget.from_lineEdit.getText()),'end':int(widget.end_lineEdit.getText())}


def dispatch(widget,action,**kwargs):
    from maya import cmds
    from .tool import SpringMagicTool
    if action=='bake_controls':
        kwargs.update(selected_range(widget))
    if action=='bind_pose':
        choice=cmds.confirmDialog(title='Spring Magic bind pose',message='GoToBindPose 会影响所选骨骼连接的绑定姿态层级，请在备份场景中使用。',button=['继续','取消'],defaultButton='取消',cancelButton='取消',dismissString='取消')
        if choice!='继续':
            return None
        kwargs['allow_bind_pose_hierarchy']=True
    result=SpringMagicTool().run(action=action,**kwargs)
    cmds.text(widget.main_processLabel,edit=True,label=result.message)
    if not result.success:
        cmds.warning(result.message)
    elif action in ('add_capsule','add_plane','add_wind','bind_controls'):
        from . import runtime
        state=runtime.read_state(result.data['session'])
        role={'add_capsule':'capsules','add_plane':'planes','add_wind':'winds'}.get(action)
        ids=state[role] if role else list(state['bindings'])
        nodes=[runtime.resolve(u) for u in ids if runtime.resolve(u)]
        if nodes:
            cmds.select(nodes,replace=True)
    return result


def compute(widget):
    from maya import cmds
    widget.apply_button.setEnable(False)
    try:
        args=dict(selected_range(widget),spring=float(widget.spring_lineEdit.getText()),twist=float(widget.Xspring_lineEdit.getText()),tension=float(widget.tension_lineEdit.getText()),extend=float(widget.extend_lineEdit.getText()),inertia=float(widget.inertia_lineEdit.getText()),subdivision=float(widget.sub_division_lineEdit.getText()),loop=bool(widget.loop_checkBox.getValue()),pose_match=bool(widget.pose_match_checkBox.getValue()),collision=bool(widget.collision_checkBox.getValue()),fast_move=bool(widget.fast_move_checkBox.getValue()),clear_subframes=bool(widget.clear_subframe_checkBox.getValue()))
        if not args['pose_match']:
            choice=cmds.confirmDialog(title='Spring Magic key cleanup',message='原版普通模式会删除处理骨骼及其子骨骼在区间内所有可关键帧通道的键。请先备份场景；操作可整组 Undo。',button=['继续','取消'],defaultButton='取消',cancelButton='取消',dismissString='取消')
            if choice!='继续':
                return None
            args['allow_key_cleanup']=True
        return dispatch(widget,'compute',**args)
    except Exception as exc:
        cmds.warning(str(exc))
        cmds.text(widget.main_processLabel,edit=True,label=str(exc))
    finally:
        widget.apply_button.setEnable(True)
        cmds.progressBar(widget.main_progressBar,edit=True,progress=0)


def add_shelf_button():
    from maya import cmds,mel
    tab=mel.eval('global string $gShelfTopLevel; tabLayout -query -selectTab $gShelfTopLevel;')
    package=Path(__file__).parent
    # Works both before and after promotion: candidate launcher if present,
    # otherwise the formal package. No execfile or sys.path removal.
    rc=package.parents[2]
    launcher=rc/'launch_candidate.py'
    command=("import runpy\nrunpy.run_path(%r)['load_tool']().show_ui()" % str(launcher)) if launcher.is_file() else 'from maya_toolkit.tools.spring_magic_v3_5a import SpringMagicTool\nSpringMagicTool().show_ui()'
    return cmds.shelfButton(commandRepeatable=True,image1=str(package/'native/icons/Title.png'),label='Spring Magic 3.5a',parent=tab,sourceType='python',command=command)
