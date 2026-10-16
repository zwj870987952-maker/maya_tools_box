"""Explicit Maya-only smoke test. Temporary nodes and clipboard files are restored."""
import json
from pathlib import Path
import sys
import uuid
import maya.cmds as cmds
import maya.mel as mel
from mtb_adv_animation_candidate import AdvancedSkeletonAnimationTool


def run():
    if cmds.file(q=True,sceneName=True) or cmds.file(q=True,modified=True):
        raise RuntimeError('Only run in an empty, unmodified, isolated Maya session; native paste clears Undo.')
    if any('animrescue' in p.lower() for p in (cmds.pluginInfo(q=True,listPlugins=True) or [])):
        raise RuntimeError('Do not run fixture tests with animRescue loaded; callback crash was observed.')
    tool = AdvancedSkeletonAnimationTool()
    ns = 'ADVApiTest_' + uuid.uuid4().hex[:8]
    old_time = cmds.currentTime(q=True)
    old_selection = cmds.ls(sl=True, long=True) or []
    auto = cmds.autoKeyframe(q=True, state=True)
    directory = Path(mel.eval('asGetTempDirectory()')) / 'AdvancedSkeleton/Selector'
    backups = {directory/('ClipBoard%d.ma' % i): (directory/('ClipBoard%d.ma' % i)).read_bytes()
               if (directory/('ClipBoard%d.ma' % i)).exists() else None for i in (0, 1)}
    results = []
    cmds.undoInfo(openChunk=True, chunkName='ADV API fixture')
    try:
        cmds.autoKeyframe(state=False)
        cmds.namespace(add=ns)
        ns += ':'
        main = cmds.createNode('transform', name=ns+'Main')
        extra = cmds.createNode('transform', name=ns+'FKExtraArm_L', parent=main)
        ctrl = cmds.circle(name=ns+'FKArm_L', constructionHistory=False)[0]
        cmds.parent(ctrl, extra)
        target = cmds.createNode('transform', name=ns+'Target', parent=main)
        cmds.setAttr(target+'.tx', 7)
        cmds.sets([main,extra,ctrl,target], name=ns+'ControlSet')
        pose = cmds.createNode('transform', name=ns+'buildPose')
        cmds.addAttr(pose, ln='udAttr', dt='string')
        cmds.setAttr(pose+'.udAttr', 'setAttr FKArm_L.tx 3;', type='string')
        cmds.currentTime(2)

        def invoke(op, check=None, **args):
            r = tool.run(operation=op, namespace=ns, **args)
            evidence = {'operation':op, 'success':r.success, 'errors':r.errors, 'seconds':r.execution_time}
            if r.success and check:
                evidence['effect_verified'] = bool(check())
            results.append(evidence)
            return r.success

        cmds.setAttr(ctrl+'.tx', 3)
        invoke('pose_copy', lambda: (directory/'ClipBoard0.ma').is_file())
        cmds.setAttr(ctrl+'.tx', 12)
        invoke('pose_paste', lambda: abs(cmds.getAttr(ctrl+'.tx')-3)<1e-5, accept_undo_history_loss=True)
        for f,v in ((0,1),(2,3),(4,5)):
            cmds.setKeyframe(ctrl, attribute='translateX', time=f, value=v)
        invoke('animation_copy', lambda: (directory/'ClipBoard1.ma').is_file())
        cmds.keyframe(ctrl, attribute='translateX', e=True, relative=True, valueChange=10)
        invoke('animation_paste', lambda: cmds.keyframe(ctrl, attribute='translateX',q=True,vc=True)==[1.0,3.0,5.0], accept_undo_history_loss=True)
        invoke('key', lambda: bool(cmds.keyframe(target,q=True,time=(2,2),kc=True)), nodes=[target])
        invoke('linear_key', lambda: set(cmds.keyTangent(target,q=True,time=(2,2),ott=True))=={'linear'}, nodes=[target])
        invoke('switch_pivot', lambda: cmds.keyframe(extra,q=True,kc=True)>0, nodes=[target,ctrl])
        invoke('pivot_control', lambda: cmds.objExists(target+'_PivotControl'), nodes=[target])
        # Isolate curve transfer from keyed Extra channels introduced by switch_pivot.
        cmds.cutKey(extra,clear=True)
        invoke('bake_controls_to_extra', lambda: bool(cmds.listConnections(extra+'.tx',type='animCurve')))
        invoke('bake_extra_to_controls', lambda: bool(cmds.listConnections(ctrl+'.tx',type='animCurve')), time_range=[0,4])
        invoke('parent_constraint', lambda: bool(cmds.listConnections(ctrl,type='parentConstraint')), nodes=[target,ctrl])
    finally:
        cmds.currentTime(old_time)
        cmds.autoKeyframe(state=auto)
        cmds.select(old_selection,r=True) if old_selection else cmds.select(clear=True)
        cmds.undoInfo(closeChunk=True)
        cmds.undo()
        if cmds.namespace(exists=ns.strip(':')):
            cmds.namespace(removeNamespace=ns.strip(':'),deleteNamespaceContent=True)
        cmds.currentTime(old_time)
        cmds.autoKeyframe(state=auto)
        cmds.select(old_selection,r=True) if old_selection else cmds.select(clear=True)
        for path, data in backups.items():
            if data is None:
                path.unlink(missing_ok=True)
            else:
                path.write_bytes(data)
    result = {'operations':results,'fixture_removed':not cmds.namespace(exists=ns.strip(':')),
              'time_restored':cmds.currentTime(q=True)==old_time,'clipboard_restored':True}
    sys.modules['mtb_adv_animation_candidate'].fixture_evidence = result
    print(json.dumps(result,ensure_ascii=False))
    return result


if __name__ == '__main__':
    run()
