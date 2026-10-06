import maya.cmds as cmds
import maya.mel as mel

def make_cycle_pre():
    cmds.setInfinity(preInfinite="cycle")
    try:
        mel.eval("animCurveEditor -edit -displayInfinities true graphEditor1GraphEd;")
    except RuntimeError:
        pass

make_cycle_pre()