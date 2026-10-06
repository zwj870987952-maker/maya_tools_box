import maya.cmds as cmds
import maya.mel as mel

def make_cycle_post():
    cmds.setInfinity(postInfinite="cycle")
    try:
        mel.eval("animCurveEditor -edit -displayInfinities true graphEditor1GraphEd;")
    except RuntimeError:
        pass

make_cycle_post()