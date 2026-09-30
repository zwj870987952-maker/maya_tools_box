from maya import cmds
from .runtime import require_active

def valueAverage(attrName, keyframeList):
    require_active()
    new_keyframeList = []
    new_valueList = []
    for i in range(len(keyframeList)):
        if not keyframeList[i] in [keyframeList[0], keyframeList[-1]]:
            new_keyframeList.append(keyframeList[i])
            valuePrev = cmds.keyframe(attrName, q=True, vc=True, t=(keyframeList[i - 1],))[0]
            valueCur = cmds.keyframe(attrName, q=True, vc=True, t=(keyframeList[i],))[0]
            valueNext = cmds.keyframe(attrName, q=True, vc=True, t=(keyframeList[i + 1],))[0]
            average = (valuePrev + valueCur + valueNext) / 3
            new_valueList.append(average)
    zipKeyValue = zip(new_keyframeList, new_valueList)
    for kv in zipKeyValue:
        cmds.setKeyframe(attrName, time=(kv[0],), value=kv[1])
