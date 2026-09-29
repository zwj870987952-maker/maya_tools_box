from __future__ import absolute_import
from maya import cmds


def exampleFilter(*args):
    nodeOutput = []
    nodeInput = args[0]
    for node in nodeInput:
        nodeOutput.append(node)
    return nodeOutput


def ks_attrMatch_true(*args):
    nodeOutput = []
    nodeInput = args[0]
    attr = args[1]
    value = args[2]

    for node in nodeInput:
        if cmds.getAttr(node+'.'+attr) == value:
            nodeOutput.append(node)
    return nodeOutput

def ks_attrMatch_false(*args):
    nodeOutput = []
    nodeInput = args[0]
    attr = args[1]
    value = args[2]

    for node in nodeInput:
        if not cmds.getAttr(node+'.'+attr) == value:
            nodeOutput.append(node)
    return nodeOutput

def ks_geometryWithNGons(*args):
    nodeOutput = []
    nodeInput = args[0]

    selection = cmds.ls(sl=True)
    cmds.select(nodeInput)
    cmds.polySelectConstraint(mode=3, type=0x0008, size=3)
    cmds.polySelectConstraint(disable=True)
    ngons = cmds.filterExpand(ex=True, sm=34, fp=True) or []
    nodeOutput = [obj.split('.')[0] for obj in ngons]
    nodeOutput = list(set(nodeOutput))
    cmds.select(selection)
    return nodeOutput

def ks_vertexCount(*args):
    nodeOutput = []
    nodeInput = args[0]
    for node in nodeInput:
        nodeOutput.append(node)
    return nodeOutput


def ks_passthrough(*args):
    nodeInput = args[0]
    return nodeInput

