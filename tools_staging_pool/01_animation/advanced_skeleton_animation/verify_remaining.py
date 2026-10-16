"""Explicit GUI Maya acceptance harness; only the isolated empty test instance.

Synthetic MocapX attributes exercise native wiring, not a device or plugin stream.
Dialog automation clicks a matching native confirmation in this test only.
"""
import json
import time
import maya.cmds as cmds
from PySide2 import QtCore, QtWidgets
from mtb_adv_animation_candidate import AdvancedSkeletonAnimationTool

tool = AdvancedSkeletonAnimationTool()
evidence = {}
timers = []


def setup():
    assert not cmds.file(q=True, sn=True) and not cmds.file(q=True, modified=True)
    assert not any('animrescue' in p.lower() for p in cmds.pluginInfo(q=True,listPlugins=True))
    cmds.createNode('transform', name='Main')
    cmds.sets(['Main'], name='ControlSet')
    cmds.setKeyframe('Main.tx', time=1, value=3)
    cmds.setKeyframe('Main.tx', time=3, value=3)
    cmds.setKeyframe('Main.ty', time=1, value=1)
    cmds.setKeyframe('Main.ty', time=3, value=5)
    evidence['initial_nodes'] = len(cmds.ls())


def answer_dialog(message, answer='Yes'):
    timer = QtCore.QTimer()
    timer.setInterval(50)
    started = time.monotonic()
    def tick():
        for w in QtWidgets.QApplication.topLevelWidgets():
            if w.isVisible() and w.windowTitle() == 'Confirm':
                labels = ' '.join(x.text() for x in w.findChildren(QtWidgets.QLabel))
                if message in labels:
                    for b in w.findChildren(QtWidgets.QPushButton):
                        if b.text().replace('&','') == answer:
                            timer.stop()
                            evidence.setdefault('dialogs', []).append({'message': labels, 'answer': answer})
                            b.click()
                            return
        if time.monotonic()-started > 10:
            timer.stop()
            evidence['dialog_timeout'] = message
    timer.timeout.connect(tick)
    timers.append(timer)
    timer.start()


def clean(answer='Yes'):
    answer_dialog('Clean animation', answer)
    r = tool.run(operation='animation_clean', namespace='')
    evidence['clean_dispatch_'+answer] = r.to_dict()
    return r.to_dict()


def check_clean(undo=False):
    result = {'static_count':cmds.keyframe('Main.tx',q=True,kc=True),
              'varying_values':cmds.keyframe('Main.ty',q=True,vc=True)}
    if undo:
        cmds.undo()
        result['undo_static_values'] = cmds.keyframe('Main.tx',q=True,vc=True)
        result['undo_varying_values'] = cmds.keyframe('Main.ty',q=True,vc=True)
    evidence['clean_result'] = result
    return result


def mocapx():
    assert not cmds.objExists('MocapX')
    cmds.undoInfo(openChunk=True,chunkName='MocapX fixture')
    try:
        cmds.createNode('transform',name='MocapX')
        attrs = ['browInnerUp','cheekPuff','jawForward','jawLeft','jawRight','mouthClose',
                 'mouthPucker','jawOpen','mouthRollUpper','mouthRollLower','mouthShrugUpper',
                 'mouthShrugLower','transformRotateX','transformRotateY','transformRotateZ']
        for side,word,cap in [('_R','right','Right'),('_L','left','Left')]:
            attrs += [word+'EyeTransformRotateY',word+'EyeTransformRotateX','mouth'+cap]
            attrs += [a+side for a in ['eyeBlink','browDown','browOuterUp','eyeSquint','eyeWide',
                       'cheekSquint','noseSneer','mouthSmile','mouthFrown','mouthDimple',
                       'mouthUpperUp','mouthLowerDown','mouthStretch']]
            for name in ['ctrlEye','EyeBrowInner','EyeBrowOuter','lowerLid','Cheek',
                         'NoseCorner','ctrlMouthCorner','Lip']:
                cmds.createNode('transform',name=name+side)
            for a in ['blink','squint']:
                cmds.addAttr('ctrlEye'+side,ln=a,at='double',keyable=True)
            cmds.addAttr('Lip'+side,ln='sticky',at='double',keyable=True)
        for a in attrs:
            cmds.addAttr('MocapX',ln=a,at='double',keyable=True)
        for n in ['FKHead_M','ctrlBox','Jaw_M','upperLip_M','lowerLip_M','ctrlMouth_M','ctrlLips_M']:
            cmds.createNode('transform',name=n)
        for n,a in [('ctrlBox','limits'),('ctrlLips_M','upperRoll'),('ctrlLips_M','lowerRoll')]:
            cmds.addAttr(n,ln=a,at='double',keyable=True)
        cmds.setAttr('ctrlBox.limits',1)
        r = tool.run(operation='connect_mocapx',namespace='')
        checks = {}
        if r.success:
            for attr,value,target,expected in [('rightEyeTransformRotateY',30,'ctrlEye_R.tx',1),
                    ('eyeBlink_L',1,'ctrlEye_L.blink',10),('jawOpen',1,'ctrlMouth_M.ty',-2),
                    ('transformRotateX',15,'FKHead_M.rx',15)]:
                cmds.setAttr('MocapX.'+attr,value)
                got=cmds.getAttr(target)
                checks[target]={'actual':got,'expected':expected,'pass':abs(got-expected)<1e-6}
        evidence['mocapx']={'result':r.to_dict(),'checks':checks,'driven_curves':len(cmds.ls(type='animCurveUU') or [])}
    finally:
        cmds.undoInfo(closeChunk=True)
        cmds.undo()
    evidence['mocapx']['undo_removed_fixture']=not cmds.objExists('MocapX') and not cmds.objExists('AdvancedSkeletonHeadOffset')
    return evidence['mocapx']


def playback():
    old=cmds.currentTime(q=True)
    r=tool.run(operation='dynamics_playback',namespace='')
    evidence['playback']={'result':r.to_dict(),'playing':cmds.play(q=True,state=True)}
    def stop():
        evidence['playback']['advanced']=cmds.currentTime(q=True)!=old
        cmds.play(state=False)
        cmds.currentTime(old)
        evidence['playback']['stopped']=not cmds.play(q=True,state=True)
    QtCore.QTimer.singleShot(300,stop)
    return r.to_dict()


def report():
    from mtb_adv_animation_candidate import engine
    return dict(evidence,jobs=engine.JOBS)
