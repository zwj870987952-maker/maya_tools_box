def cmds_module():
    from maya import cmds
    return cmds

def identity(node):
    cmds = cmds_module()
    reference = cmds.referenceQuery(node, referenceNode=True) if cmds.referenceQuery(node, isNodeReferenced=True) else None
    return (cmds.ls(node, uuid=True)[0], cmds.ls(reference, uuid=True)[0] if reference else '')

def world_matrix(node, time):
    from maya.api import OpenMaya as om
    cmds = cmds_module()
    raw = cmds.getAttr(node + '.worldMatrix[0]', time=time)
    if cmds.getAttr(node + '.rotatePivot')[0] == (0, 0, 0):
        return list(raw)
    pivot = cmds.getAttr(node + '.rotatePivot', time=time)[0]
    matrix = om.MMatrix(raw)
    point = om.MPoint(*pivot) * matrix
    result = om.MTransformationMatrix()
    result.setRotation(om.MTransformationMatrix(matrix).rotation(asQuaternion=True))
    result.setTranslation(om.MVector(point.x, point.y, point.z), om.MSpace.kTransform)
    return list(result.asMatrix())

def ensure_nodes():
    cmds = cmds_module()
    loaded = []
    try:
        types = set(cmds.allNodeTypes())
        for required, plugin in (('multMatrix', 'matrixNodes'), ('quatToEuler', 'quatNodes')):
            if required not in types:
                already = cmds.pluginInfo(plugin, query=True, loaded=True)
                cmds.loadPlugin(plugin, quiet=True)
                if not already:
                    loaded.append(plugin)
        return loaded
    except Exception:
        for plugin in reversed(loaded):
            if cmds.pluginInfo(plugin, query=True, unloadOk=True):
                cmds.unloadPlugin(plugin)
        raise
