# -*- coding: utf-8 -*-
import maya.cmds as cmds

cube = cmds.polyCube(name="test_simplify_tol")[0]
# 线性增加的点，中间有轻微扰动
for f in range(1, 21):
    val = f * 1.0 + (0.1 if f % 2 == 0 else -0.1)
    cmds.setKeyframe(cube, attribute="translateY", time=f, value=val)

curve = cmds.findKeyframe(cube, curve=True)[0]
print("Before simplify keys:", len(cmds.keyframe(curve, query=True, timeChange=True)))

# 测试不同 valueTolerance
cmds.simplify(curve, time=(1.01, 19.99), timeTolerance=0.01, valueTolerance=0.5)
print("After simplify (tol=0.5) keys:", len(cmds.keyframe(curve, query=True, timeChange=True)))

cmds.delete(cube)
