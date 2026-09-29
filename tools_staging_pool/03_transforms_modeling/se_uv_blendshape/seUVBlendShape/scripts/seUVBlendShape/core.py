'''
Core seUVBlendShape functions to perform operations on the deformer
'''
from __future__ import absolute_import
import re
import six
from maya import cmds, mel
mel.eval('source "artAttrCreateMenuItems.mel"')

def loadPlugin():
    '''
    Load the seUVBlendShape plugin
    
    :returns: None
    '''
    cmds.loadPlugin('seUVBlendShape', qt=True)
    cmds.makePaintable('seUVBlendShape', 'weights', attrType='multiFloat', sm='deformer')
    cmds.makePaintable('seUVBlendShape', 'deltaWeights', attrType='multiFloat', sm='deformer')
    cmds.makePaintable('seUVBlendShape', 'paintTargetWeights', attrType='multiFloat', sm='deformer')
    
def unloadPlugin(force=False):
    '''
    Unload the seUVBlendShape plugin

    :param force: Force the plugin to unload even if it's in use.
        Default False
    :type force: bool
    :returns: None
    '''
    cmds.unloadPlugin('seUVBlendShape', force=force)

def create(baseMesh, targetMesh, baseUVSet=None, targetUVSet=None, name=None,
           keepOffset=False, tolerance=0.01):
    '''
    Create a new seUVBlendShape deformer on the given base mesh with the given
    target mesh(s). See documentation for more information.

    :param baseMesh: name of the base polyon mesh
    :type baseMesh: str
    :param targetMesh: name of target polygon mesh(s)
    :type targetMesh: str or list of str
    :param baseUVSet: base mesh UV set. Default is the first found
    :type baseUVSet: str
    :param targetUVSet: target mesh UV set. Default is the first found
    :type targetUVSet: str
    :param name: name to give the deformer. Default is seUVBlendShape#
    :type name: str
    :param keepOffset: keep offsets on base mesh (can be set after later)
    :type keepOffset: bool
    :param tolerance: bind tolerance for outside border UVs
    :type tolerance: float
    :returns: name of created deformer
    :rtype: str
    '''
    if not isinstance(targetMesh, (tuple, list)):
        geoList = [targetMesh]
    else:
        geoList = list(targetMesh)
    geoList.append(baseMesh)

    params = {'tol' : tolerance}
    if baseUVSet:
        params['bs'] = baseUVSet
    if targetUVSet:
        params['ts'] = targetUVSet
    if name:
        params['n'] = name
    if keepOffset:
        params['ko'] = True

    return cmds.seUVBlendShape(*geoList, **params)

def addTarget(deformer, targetMesh, baseUVSet=None, targetUVSet=None,
             tolerance=0.01):
    '''
    Add a target mesh to an existing seUVBlendShape deformer.

    :param deformer: name of the existing deformer node
    :type deformer: str
    :param targetMesh: name of the target polygon mesh
    :type targetMesh: str
    :param baseUVSet: base mesh UV set. Default is the first found
    :type baseUVSet: str
    :param targetUVSet: target mesh UV set. Default is the first found
    :type targetUVSet: str
    :param tolerance: bind tolerance for outside border UVs
    :type tolerance: float
    :returns: None
    '''
    params = {'tol' : tolerance}
    if baseUVSet:
        params['bs'] = baseUVSet
    if targetUVSet:
        params['ts'] = targetUVSet

    cmds.seUVBlendShape(deformer, e=True, add=targetMesh, **params)

def removeTarget(deformer, target):
    '''
    Remove a target from the deformer.

    :param deformer: name of the seUVBlendShape deformer
    :type deformer: str
    :param target: name of target
    :type target: str
    :rtype: None
    '''
    targetIndex = getTargetIndexFromName(deformer, target)
    return cmds.seUVBlendShape(deformer, e=True, rm=True, i=targetIndex)

def rebind(deformer, target=None, tolerance=0.01):
    '''
    Rebinds the base mesh to specific targets. If targets is None, all targets
    will be rebound. Rebinding is used when you have moved the uvs or want to
    set the bind pose of the target.

    :param deformer: name of the seUVBlendShape deformer
    :type deformer: str
    :param target: name(s) of targets to rebind. If None, all targets
    :type target: str or list of str
    :param tolerance: bind tolerance for outside border UVs
    :type tolerance: float
    :returns: None
    '''
    if target:
        if isinstance(target, (tuple, list)):
            targetIndices = [getTargetIndexFromName(deformer, t) for t in target]
        else:
            targetIndices = [getTargetIndexFromName(deformer, target)]
    else:
        targetIndices = getTargetIndexes(deformer)

    [cmds.seUVBlendShape(deformer, e=True, i=i, rb=True, tol=tolerance) for i in targetIndices]

def changeUVSet(deformer, target=None, baseUVSet=None, targetUVSet=None,
                tolerance=0.01):
    '''
    Change the UV sets used for binding an existing target to the base
    geometry. A rebind will be automatically be triggered after changing the
    UV sets.

    :param deformer: name of the seUVBlendShape deformer
    :type deformer: str
    :param target: name(s) of the targest to change UV sets on. If None,
        all targets will be used
    :type target: str or list of str
    :param baseUVSet: change the base geometry UV set. If None, no change will
        be performed
    :type baseUVSet: str
    :param targetUVSet: change the target geometry UV set. If None, no change
        will be performed
    :type targetUVSet: str
    :param tolerance: bind tolerance for outside border UVs
    :type tolerance: float
    :returns: None
    '''
    if not baseUVSet and not targetUVSet:
        raise ValueError('Base UV set and/or target UV set must be given.')

    if target:
        if isinstance(target, (tuple, list)):
            targetIndices = [getTargetIndexFromName(deformer, t) for t in target]
        else:
            targetIndices = [getTargetIndexFromName(deformer, target)]
    else:
        targetIndices = getTargetIndexes(deformer)

    params = {'tol' : tolerance}
    if baseUVSet:
        params['bs'] = baseUVSet
    if targetUVSet:
        params['ts'] = targetUVSet

    [cmds.seUVBlendShape(deformer, e=True, i=i, rb=True, **params) for i in targetIndices]

def getTargetCount(deformer):
    '''
    Return the number of targets on the deformer.

    :param deformer: name of the seUVBlendShape deformer
    :type deformer: str
    :rtype: int
    '''
    return cmds.seUVBlendShape(deformer, q=True, tc=True)

def getTargetIndexes(deformer):
    '''
    Return a list of target indexes on the deformer.

    :param deformer: name of the seUVBlendShape deformer
    :type deformer: str
    :rtype: list of int
    '''
    return cmds.seUVBlendShape(deformer, q=True, ti=True) or []

def getTargetNames(deformer):
    '''
    Return a list of target names on the deformer.

    :param deformer: name of the seUVBlendShape deformer
    :type deformer: str
    :rtype: list of str
    '''
    targetIndexes = getTargetIndexes(deformer)
    weightAttribute = deformer + '.weight[%i]'
    return [cmds.attributeName(weightAttribute % i) for i in targetIndexes]

def getBaseUVSet(deformer, target):
    '''
    Return the name of the base uv set used to associate with a target.

    :param deformer: name of the seUVBlendShape deformer
    :type deformer: str
    :param target: name of target
    :type target: str
    :rtype: str
    '''
    targetIndex = getTargetIndexFromName(deformer, target)
    return cmds.seUVBlendShape(deformer, q=True, i=targetIndex, bs=True)

def getTargetUVSet(deformer, target):
    '''
    Return the name of the target uv set used to associate with a target.

    :param deformer: name of the seUVBlendShape deformer
    :type deformer: str
    :param target: name of target
    :type target: str
    :rtype: str
    '''
    targetIndex = getTargetIndexFromName(deformer, target)
    return cmds.seUVBlendShape(deformer, q=True, i=targetIndex, ts=True)

def getBoundVertices(deformer, target):
    '''
    Return a list of vertex indexes that are bound on the deformer.

    :param deformer: name of the seUVBlendShape deformer
    :type deformer: str
    :param target: name of target
    :type target: str
    :rtype: list of int
    '''
    targetIndex = getTargetIndexFromName(deformer, target)
    return cmds.seUVBlendShape(deformer, q=True, i=targetIndex, bv=True)

def pruneDeformerVertices(deformer):
    '''
    Optimizes the deformer by pruning vertices from the deformer set. This is
    done by turning all targets on and any vertices that do not move are
    removed from the deformation set. This should only be called after all
    targets are added. Adding or removing targets may affect vertices that are
    pruned out. See the :py:func:`.unpruneDeformerVertices` to restore all
    vertices.

    .. note::

        If any target weight attributes are locked or connected and are
        set to 0, it may prune out vertices affected by those targets. If this
        is the case, then you should activate these targets first before calling
        this function.

    :param deformer: name of the seUVBlendShape deformer
    :type deformer: str
    :returns: None
    '''
    if not cmds.objExists(deformer):
        raise ValueError('Deformer does not exist: %s' % deformer)

    targetIndexes = getTargetIndexes(deformer)
    storedWeightValues = []
    for i in targetIndexes:
        weightAttr = '%s.weight[%i]' % (deformer, i)
        weightValue = cmds.getAttr(weightAttr)

        try:
            cmds.setAttr(weightAttr, 1)
        except RuntimeError:
            cmds.warning('Unable to set value on target weight attribute: %s' \
                          % weightAttr)
        else:
            storedWeightValues.append((weightAttr, weightValue))
        
    cmds.deformer(deformer, e=True, prune=True)

    for a, v in storedWeightValues:
        cmds.setAttr(a, v)

def unpruneDeformerVertices(deformer, baseMesh=None):
    '''
    Restores the deformer set to affect all vertices on the deformed mesh.
    This will undo what the :py:func:`.pruneDeformerVertices` function does.
    This is needed if you are adding or removing new targets to the deformer.

    .. note::

        If the base mesh has all vertices pruned out, you must pass the name
        of the base mesh to this function. Otherwise the base mesh may not
        be determined automatically.

    :param deformer: name of the seUVBlendShape deformer
    :type deformer: str
    :param baseMesh: name of the base mesh. If None, an attempt will be made
        to determine the name.
    :type baseMesh: str
    :returns: None
    :raises: RuntimeError
    '''
    if baseMesh:
        if cmds.nodeType(baseMesh) == 'transform':
            shape = cmds.listRelatives(baseMesh, f=True, type='shape')
            if not shape:
                raise ValueError('Base mesh is not a polygon mesh: %s' % 
                                  baseMesh)
            baseMesh = shape[0]
    else:
        baseMesh = cmds.deformer(deformer, q=True, g=True)
        if not baseMesh:
            raise RuntimeError('Unable to determine base mesh for ' \
                               'deformer: %s' % deformer)
        baseMesh = baseMesh[0]

    vertexCount = cmds.polyEvaluate(baseMesh, v=True)
    deformerSet = cmds.listConnections('%s.message' % deformer,
                                       type='objectSet')[0]

    cmds.sets('%s.vtx[0:%i]' % (baseMesh, vertexCount-1),
              include=deformerSet)
    
def paintTargetWeights(deformer, target):
    '''
    Activates weight painting for the given target on the deformer.

    ..note::

        In Maya 2016, the GPU override will be disabled as changing weights
        is not supported in this mode. After painting, you may re-enable it.

    :param deformer: name of the seUVBlendShape deformer
    :type deformer: str
    :param target: name of the target to paint weights on
    :type target: str
    :returns: None
    '''
    if cmds.about(api=True) >= 201600:
        cmds.evaluator(enable=False, name='deformer')

    targetIndex = getTargetIndexFromName(deformer, target)
    cmds.setAttr('%s.inputTarget[0].paintTargetIndex' % deformer, targetIndex)

    baseGeometry = cmds.deformer(deformer, q=True, g=True)
    cmds.select(baseGeometry, r=True)

    mel.eval('artSetToolAndSelectAttr("artAttrCtx", \
             "seUVBlendShape.%s.paintTargetWeights")' % deformer)
    mel.eval('ArtPaintAttrToolOptions()')

def paintDeltaWeights(deformer):
    '''
    Activates weight painting for all target deltas.

    ..note::

        In Maya 2016, the GPU override will be disabled as changing weights
        is not supported in this mode. After painting, you may re-enable it.

    :param deformer: name of the seUVBlendShape deformer
    :type deformer: str
    :returns: None
    '''
    if cmds.about(api=True) >= 201600:
        cmds.evaluator(enable=False, name='deformer')

    baseGeometry = cmds.deformer(deformer, q=True, g=True)
    cmds.select(baseGeometry, r=True)

    mel.eval('artSetToolAndSelectAttr("artAttrCtx", \
             "seUVBlendShape.%s.deltaWeights")' % deformer)
    mel.eval('ArtPaintAttrToolOptions()')

def paintDeformerWeights(deformer):
    '''
    Activates weight painting for the overall deformer influence.

    ..note::

        In Maya 2016, the GPU override will be disabled as changing weights
        is not supported in this mode. After painting, you may re-enable it.

    :param deformer: name of the seUVBlendShape deformer
    :type deformer: str
    :returns: None
    '''
    if cmds.about(api=True) >= 201600:
        cmds.evaluator(enable=False, name='deformer')

    baseGeometry = cmds.deformer(deformer, q=True, g=True)
    cmds.select(baseGeometry, r=True)

    mel.eval('artSetToolAndSelectAttr("artAttrCtx", \
             "seUVBlendShape.%s.weights")' % deformer)
    mel.eval('ArtPaintAttrToolOptions()')

def getTargetIndexFromName(deformer, target):
    '''
    Returns the target index on the defomer that matches the given target
    name. If the target name does not exist on the deformer, a ValueError
    is raised.

    :param deformer: name of the seUVBlendShape deformer
    :type deformer: str
    :param target: name of target to get index for
    :type target: str
    :rtype: int
    :raises: ValueError
    '''
    aliasAttributes = cmds.aliasAttr(deformer, q=True)
    try:
        aliasIndex = aliasAttributes.index(target)
    except ValueError:
        raise ValueError("Target '%s' does not exist on deformer " \
                        "'%s'." % (target, deformer))

    weightAttr = aliasAttributes[aliasIndex+1]
    matched = re.match('weight\[(\d+)\]', weightAttr)
    if not matched:
        raise RuntimeError('Unable to get target index from deformer: ' \
                           '%s' % deformer)

    return int(matched.group(1))

def getTargetMesh(deformer, target):
    '''
    Returns the mesh shape that is connected to the deformer for the given
    target.

    :param deformer: name of the seUVBlendShape deformer
    :type deformer: str
    :param target: name of target or target index
    :type target: str or int
    :returns: name of connected shape node or None if no mesh is connected
    :rtype: str
    '''
    if not isinstance(target, int):
        target = getTargetIndexFromName(deformer, target)

    if target not in getTargetIndexes(deformer):
        raise ValueError('No target exists at index: %i' % target)

    targetMesh = cmds.listConnections(
                '%s.inputTarget[0].inputTargetGroup[%i].inputGeomTarget' %
                (deformer, target), sh=True)

    if targetMesh:
        return targetMesh[0]

def getTargetIndexFromMesh(deformer, targetMesh):
    '''
    Returns the target index on the deformer for the given target mesh. If
    the target mesh is not connected to the deformer, a ValueError is raised.

    :param deformer: name of the seUVBlendShape deformer
    :type deformer: str
    :param targetMesh: name of target mesh
    :type targetMesh: str
    :returns: index of target or list of indexes if multiple connections
    :rtype: int or list of int
    :raises: ValueError
    '''
    if cmds.nodeType(targetMesh) == 'transform':
        shape = cmds.listRelatives(targetMesh, f=True, type='shape')
        if not shape:
            raise ValueError('Target mesh is not a polygon mesh: %s' % 
                              targetMesh)
        targetMesh = shape[0]

    connections = cmds.listConnections('%s.worldMesh' % targetMesh, p=True,
                                     s=False, d=True)
    if not connections:
        raise ValueError("Target mesh '%s' has no connections to the " \
                         "worldMesh." % targetMesh)

    targetIndexes = []
    for plug in connections:
        plugSplit = plug.split('.')
        if plugSplit[0] == deformer:
            matched = re.match('inputTargetGroup\[(\d+)\]', plugSplit[2])
            if not matched:
                raise RuntimeError("Unable to get target index from " \
                                   "deformer '%s' for target mesh: %s" \
                                    % (deformer, targetMesh))
            targetIndexes.append(int(matched.group(1)))

    if not targetIndexes:
        raise ValueError("Target mesh '%s' is not connected to deformer: %s" \
                        % (targetMesh, deformer))

    if len(targetIndexes) == 1:
        return targetIndexes[0]

    return targetIndexes

print('Loading seUVBlendShape plugin...')
loadPlugin()