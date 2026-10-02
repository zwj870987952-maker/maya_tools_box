from __future__ import absolute_import
from maya_toolkit.tools.ks_node_outliner_v2_2.session import cmdshim as cmds


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
    from maya.api import OpenMaya
    result=[]
    for node in args[0]:
        candidates=[node] if cmds.nodeType(node)=='mesh' else cmds.listRelatives(node,shapes=True,fullPath=True,type='mesh') or []
        for mesh in candidates:
            selection=OpenMaya.MSelectionList();selection.add(mesh);fn=OpenMaya.MFnMesh(selection.getDagPath(0))
            counts,vertices=fn.getVertices()
            if any(n>4 for n in counts):result.append(node);break
    return list(dict.fromkeys(result))

def ks_vertexCount(*args):
    nodeOutput = []
    nodeInput = args[0]
    for node in nodeInput:
        nodeOutput.append(node)
    return nodeOutput


def ks_passthrough(*args):
    nodeInput = args[0]
    return nodeInput
