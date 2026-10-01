"""
Functions to work with skinCluster data.

This module is derivated from Chad Vernon's Skin IO.

`Chad Vernon's github

<https://github.com/chadmv/cmt/tree/master/scripts/cmt/deform>`_
"""
from maya_toolkit.tools.cvwrap_weightdriver.safe_data import load_basic_pickle as candidate_load_pickle
import os
import json
import pickle as pickle
import pymel.core as pm
from maya import cmds
import maya.OpenMaya as OpenMaya
from .six import string_types
FILE_EXT = '.gSkin'
FILE_JSON_EXT = '.jSkin'
PACK_EXT = '.gSkinPack'

def getSkinCluster(obj):
    """Get the skincluster of a given object

    Arguments:
        obj (dagNode): The object to get skincluster

    Returns:
        pyNode: The skin cluster pynode object

    """
    skinCluster = None
    if isinstance(obj, string_types):
        obj = pm.PyNode(obj)
    try:
        if pm.nodeType(obj.getShape()) in ['mesh', 'nurbsSurface', 'nurbsCurve']:
            for shape in obj.getShapes():
                try:
                    for skC in pm.listHistory(shape, type='skinCluster'):
                        try:
                            if skC.getGeometry()[0] == shape:
                                skinCluster = skC
                        except Exception:
                            pass
                except Exception:
                    pass
    except Exception:
        pm.displayWarning('%s: is not supported.' % obj.name())
    return skinCluster

def get_mesh_components_from_tag_expression(skinCls, tag='*'):
    """Get the mesh components from the  component tag expression

    Thanks to Roy Nieterau a.k.a BigRoyNL from colorBleed for the snippet

    Args:
        skinCls (PyNode): Skin cluster node
        tag (str, optional): Component tag expression

    Returns:
        dagPath, MObject: The dagpath tho the shpe and the MObject components
    """
    geo_types = ['mesh', 'nurbsSurface', 'nurbsCurve']
    for t in geo_types:
        obj = skinCls.listConnections(et=True, t=t)
        if obj:
            geo = obj[0].getShape().name()
    out_attr = cmds.deformableShape(geo, localShapeOutAttr=True)[0]
    sel = OpenMaya.MSelectionList()
    sel.add(geo)
    dep = OpenMaya.MObject()
    sel.getDependNode(0, dep)
    fn_dep = OpenMaya.MFnDependencyNode(dep)
    plug = fn_dep.findPlug(out_attr, True)
    obj = plug.asMObject()
    fn_geodata = OpenMaya.MFnGeometryData(obj)
    components = fn_geodata.resolveComponentTagExpression(tag)
    dagPath = OpenMaya.MDagPath.getAPathTo(dep)
    return (dagPath, components)

def getGeometryComponents(skinCls):
    """Get the geometry components from skincluster

    Arguments:
        skinCls (PyNode): The skincluster node

    Returns:
        dagPath: The dagpath for the components
        componets: The skincluster componets
    """
    try:
        fnSet = OpenMaya.MFnSet(skinCls.__apimfn__().deformerSet())
        members = OpenMaya.MSelectionList()
        fnSet.getMembers(members, False)
        dagPath = OpenMaya.MDagPath()
        components = OpenMaya.MObject()
        members.getDagPath(0, dagPath, components)
        return (dagPath, components)
    except:
        return get_mesh_components_from_tag_expression(skinCls)

def getCurrentWeights(skinCls, dagPath, components):
    """Get the skincluster weights

    Arguments:
        skinCls (PyNode): The skincluster node
        dagPath (MDagPath): The skincluster dagpath
        components (MObject): The skincluster components

    Returns:
        MDoubleArray: The skincluster weights

    """
    weights = OpenMaya.MDoubleArray()
    util = OpenMaya.MScriptUtil()
    util.createFromInt(0)
    pUInt = util.asUintPtr()
    skinCls.__apimfn__().getWeights(dagPath, components, weights, pUInt)
    return weights

def collectInfluenceWeights(skinCls, dagPath, components, dataDic):
    weights = getCurrentWeights(skinCls, dagPath, components)
    influencePaths = OpenMaya.MDagPathArray()
    numInfluences = skinCls.__apimfn__().influenceObjects(influencePaths)
    numComponentsPerInfluence = int(weights.length() / numInfluences)
    for ii in range(influencePaths.length()):
        influenceName = influencePaths[ii].partialPathName()
        influenceWithoutNamespace = pm.PyNode(influenceName).stripNamespace()
        inf_w = {jj: weights[jj * numInfluences + ii] for jj in range(numComponentsPerInfluence) if weights[jj * numInfluences + ii] != 0.0}
        dataDic['vertexCount'] = int(weights.length() / float(numInfluences))
        dataDic['weights'][str(influenceWithoutNamespace)] = inf_w

def collectBlendWeights(skinCls, dagPath, components, dataDic):
    weights = OpenMaya.MDoubleArray()
    skinCls.__apimfn__().getBlendWeights(dagPath, components, weights)
    dataDic['blendWeights'] = {i: round(weights[i], 6) for i in range(weights.length()) if round(weights[i], 6) != 0.0}

def collectData(skinCls, dataDic):
    dagPath, components = getGeometryComponents(skinCls)
    collectInfluenceWeights(skinCls, dagPath, components, dataDic)
    collectBlendWeights(skinCls, dagPath, components, dataDic)
    for attr in ['skinningMethod', 'normalizeWeights']:
        dataDic[attr] = skinCls.attr(attr).get()
    dataDic['skinClsName'] = skinCls.name()

def exportSkin(filePath=None, objs=None, *args):
    if not objs:
        if pm.selected():
            objs = pm.selected()
        else:
            pm.displayWarning('Please Select One or more objects')
            return False
    packDic = {'objs': [], 'objDDic': [], 'bypassObj': []}
    if not filePath:
        f2 = 'jSkin ASCII  (*{});;gSkin Binary (*{})'.format(FILE_JSON_EXT, FILE_EXT)
        f3 = ';;All Files (*.*)'
        fileFilters = f2 + f3
        filePath = pm.fileDialog2(fileMode=0, fileFilter=fileFilters)
        if filePath:
            filePath = filePath[0]
        else:
            return False
    if not filePath.endswith(FILE_EXT) and (not filePath.endswith(FILE_JSON_EXT)):
        pm.displayWarning('Not valid file extension for: {}'.format(filePath))
        return
    _, file_ext = os.path.splitext(filePath)
    for obj in objs:
        skinCls = getSkinCluster(obj)
        if not skinCls:
            pm.displayWarning(obj.name() + ": Skipped because don't have Skin Cluster")
            pass
        else:
            if isinstance(obj.getShape(), pm.nodetypes.Mesh):
                pm.skinPercent(skinCls, obj, pruneWeights=0.001)
            dataDic = {'weights': {}, 'blendWeights': [], 'skinClsName': '', 'objName': '', 'nameSpace': '', 'vertexCount': 0, 'skinDataFormat': 'compressed'}
            dataDic['objName'] = obj.name()
            dataDic['nameSpace'] = obj.namespace()
            collectData(skinCls, dataDic)
            packDic['objs'].append(obj.name())
            packDic['objDDic'].append(dataDic)
            exportMsg = 'Exported skinCluster {} ({} influences, {} points) {}'
            pm.displayInfo(exportMsg.format(skinCls.name(), len(dataDic['weights'].keys()), len(dataDic['blendWeights']), obj.name()))
    if packDic['objs']:
        if filePath.endswith(FILE_EXT):
            with open(filePath, 'wb') as fp:
                pickle.dump(packDic, fp, pickle.HIGHEST_PROTOCOL)
        else:
            with open(filePath, 'w') as fp:
                json.dump(packDic, fp, indent=4, sort_keys=True)
        return True

def exportSkinPack(packPath=None, objs=None, use_json=False, *args):
    if use_json:
        file_ext = FILE_JSON_EXT
    else:
        file_ext = FILE_EXT
    if not objs:
        if pm.selected():
            objs = pm.selected()
        else:
            pm.displayWarning('Please Select Some Objects')
            return
    packDic = {'packFiles': [], 'rootPath': []}
    if packPath is None:
        packPath = pm.fileDialog2(fileMode=0, fileFilter='mGear skinPack (*%s)' % PACK_EXT)
        if not packPath:
            return
        packPath = packPath[0]
        if not packPath.endswith(PACK_EXT):
            packPath += PACK_EXT
    if not packPath.endswith(PACK_EXT):
        pm.displayWarning('Not valid file extension for: {}'.format(packPath))
        return
    packDic['rootPath'], packName = os.path.split(packPath)
    for obj in objs:
        fileName = obj.stripNamespace() + file_ext
        filePath = os.path.join(packDic['rootPath'], fileName)
        if exportSkin(filePath, [obj], use_json):
            packDic['packFiles'].append(fileName)
            pm.displayInfo(filePath)
        else:
            pm.displayWarning(obj.name() + ": Skipped because don't have Skin Cluster")
    if packDic['packFiles']:
        data_string = json.dumps(packDic, indent=4, sort_keys=True)
        with open(packPath, 'w') as f:
            f.write(data_string + '\n')
        pm.displayInfo('Skin Pack exported: ' + packPath)
    else:
        pm.displayWarning('Any of the selected objects have Skin Cluster. Skin Pack export aborted.')

def exportJsonSkinPack(packPath=None, objs=None, *args):
    exportSkinPack(packPath, objs, use_json=True)

def setInfluenceWeights(skinCls, dagPath, components, dataDic, compressed):
    unusedImports = []
    weights = getCurrentWeights(skinCls, dagPath, components)
    influencePaths = OpenMaya.MDagPathArray()
    numInfluences = skinCls.__apimfn__().influenceObjects(influencePaths)
    numComponentsPerInfluence = int(weights.length() / numInfluences)
    for importedInfluence, wtValues in dataDic['weights'].items():
        for ii in range(influencePaths.length()):
            influenceName = influencePaths[ii].partialPathName()
            nnspace = pm.PyNode(influenceName).stripNamespace()
            influenceWithoutNamespace = nnspace
            if influenceWithoutNamespace == importedInfluence:
                if compressed:
                    for jj in range(numComponentsPerInfluence):
                        wt = wtValues.get(jj) or wtValues.get(str(jj)) or 0.0
                        weights.set(wt, jj * numInfluences + ii)
                else:
                    for jj in range(numComponentsPerInfluence):
                        wt = wtValues[jj]
                        weights.set(wt, jj * numInfluences + ii)
                    break
        else:
            unusedImports.append(importedInfluence)
    influenceIndices = OpenMaya.MIntArray(numInfluences)
    for ii in range(numInfluences):
        influenceIndices.set(ii, ii)
    skinCls.__apimfn__().setWeights(dagPath, components, influenceIndices, weights, False)

def setBlendWeights(skinCls, dagPath, components, dataDic, compressed):
    if compressed:
        blendWeights = OpenMaya.MDoubleArray(dataDic['vertexCount'])
        for key, value in dataDic['blendWeights'].items():
            blendWeights.set(value, int(key))
    else:
        blendWeights = OpenMaya.MDoubleArray(len(dataDic['blendWeights']))
        for ii, w in enumerate(dataDic['blendWeights']):
            blendWeights.set(w, ii)
    skinCls.__apimfn__().setBlendWeights(dagPath, components, blendWeights)

def setData(skinCls, dataDic, compressed):
    dagPath, components = getGeometryComponents(skinCls)
    setInfluenceWeights(skinCls, dagPath, components, dataDic, compressed)
    for attr in ['skinningMethod', 'normalizeWeights']:
        skinCls.attr(attr).set(dataDic[attr])
    setBlendWeights(skinCls, dagPath, components, dataDic, compressed)

def _getObjsFromSkinFile(filePath=None, *args):
    if not filePath:
        f1 = 'mGear Skin (*{0} *{1})'.format(FILE_EXT, FILE_JSON_EXT)
        f2 = ';;gSkin Binary (*{0});;jSkin ASCII  (*{1})'.format(FILE_EXT, FILE_JSON_EXT)
        f3 = ';;All Files (*.*)'
        fileFilters = f1 + f2 + f3
        filePath = pm.fileDialog2(fileMode=1, fileFilter=fileFilters)
    if not filePath:
        return
    if not isinstance(filePath, string_types):
        filePath = filePath[0]
    with open(filePath, 'rb') as fp:
        if filePath.endswith(FILE_EXT):
            data = candidate_load_pickle(fp)
        else:
            data = json.load(fp)
        return data['objs']

def getObjsFromSkinFile(filePath=None, *args):
    objs = _getObjsFromSkinFile(filePath)
    if objs:
        for x in objs:
            print(x)

def importSkin(filePath=None, *args):
    if not filePath:
        f1 = 'mGear Skin (*{0} *{1})'.format(FILE_EXT, FILE_JSON_EXT)
        f2 = ';;gSkin Binary (*{0});;jSkin ASCII  (*{1})'.format(FILE_EXT, FILE_JSON_EXT)
        f3 = ';;All Files (*.*)'
        fileFilters = f1 + f2 + f3
        filePath = pm.fileDialog2(fileMode=1, fileFilter=fileFilters)
    if not filePath:
        return
    if not isinstance(filePath, string_types):
        filePath = filePath[0]
    if filePath.endswith(FILE_EXT):
        with open(filePath, 'rb') as fp:
            dataPack = candidate_load_pickle(fp)
    else:
        with open(filePath, 'rb') as fp:
            dataPack = json.load(fp)
    for data in dataPack['objDDic']:
        compressed = False
        if 'skinDataFormat' in data:
            if data['skinDataFormat'] == 'compressed':
                compressed = True
        try:
            skinCluster = False
            objName = data['objName']
            objNode = pm.PyNode(objName)
            try:
                objShapes = objNode.getShapes(noIntermediate=True)
                if isinstance(objNode.getShape(), pm.nodetypes.Mesh):
                    meshVertices = pm.polyEvaluate(objShapes, vertex=True)
                elif isinstance(objNode.getShape(), pm.nodetypes.NurbsSurface):
                    meshVertices = sum([len(shape.cv) for shape in objShapes])
                elif isinstance(objNode.getShape(), pm.nodetypes.NurbsCurve):
                    meshVertices = sum([len(shape.cv) for shape in objShapes])
                else:
                    meshVertices = 0
                if compressed:
                    importedVertices = data['vertexCount']
                else:
                    importedVertices = len(data['blendWeights'])
                if meshVertices != importedVertices:
                    warningMsg = 'Vertex counts on {} do not match. {} != {}'
                    pm.displayWarning(warningMsg.format(objName, meshVertices, importedVertices))
                    continue
            except Exception:
                pass
            if getSkinCluster(objNode):
                skinCluster = getSkinCluster(objNode)
            else:
                try:
                    joints = list(data['weights'].keys())
                    skinName = data['skinClsName'].replace('|', '')
                    skinCluster = pm.skinCluster(joints, objNode, tsb=True, nw=2, n=skinName)
                except Exception:
                    sceneJoints = set([pm.PyNode(x).name() for x in pm.ls(type='joint')])
                    notFound = []
                    for j in data['weights'].keys():
                        if j not in sceneJoints:
                            notFound.append(str(j))
                    pm.displayWarning('Object: ' + objName + " Skiped. Can't found corresponding deformer for the following joints: " + str(notFound))
                    continue
            if skinCluster:
                setData(skinCluster, data, compressed)
                print('Imported skin for: {}'.format(objName))
        except Exception:
            warningMsg = 'Object: {} Skipped. Can NOT be found in the scene'
            pm.displayWarning(warningMsg.format(objName))

def importSkinPack(filePath=None, *args):
    if not filePath:
        filePath = pm.fileDialog2(fileMode=1, fileFilter='mGear skinPack (*%s)' % PACK_EXT)
    if not filePath:
        return
    if not isinstance(filePath, string_types):
        filePath = filePath[0]
    with open(filePath) as fp:
        packDic = json.load(fp)
        for pFile in packDic['packFiles']:
            filePath = os.path.join(os.path.split(filePath)[0], pFile)
            importSkin(filePath, True)

def skinCopy(sourceMesh=None, targetMesh=None, *args):
    if not sourceMesh or not targetMesh:
        if len(pm.selected()) >= 2:
            sourceMesh = pm.selected()[-1]
            targetMeshes = pm.selected()[:-1]
        else:
            pm.displayWarning('Please select target mesh/meshes and source mesh with skinCluster.')
            return
    else:
        targetMeshes = [targetMesh]
        if isinstance(sourceMesh, string_types):
            sourceMesh = pm.PyNode(sourceMesh)
    for targetMesh in targetMeshes:
        if isinstance(targetMesh, string_types):
            sourceMesh = pm.PyNode(targetMesh)
        ss = getSkinCluster(sourceMesh)
        if ss:
            skinMethod = ss.skinningMethod.get()
            oDef = pm.skinCluster(sourceMesh, query=True, influence=True)
            skinName = targetMesh.name().replace('|', '') + '_SkinCluster'
            skinCluster = pm.skinCluster(oDef, targetMesh, tsb=True, nw=1, n=targetMesh.name() + '_SkinCluster')
            pm.copySkinWeights(sourceSkin=ss.stripNamespace(), destinationSkin=skinCluster.name(), noMirror=True, influenceAssociation='oneToOne', smooth=True, normalize=True)
            skinCluster.skinningMethod.set(skinMethod)
        else:
            errorMsg = "Source Mesh : {} doesn't have a skinCluster."
            pm.displayError(errorMsg.format(sourceMesh.name()))

def selectDeformers(*args):
    if pm.selected():
        try:
            oSel = pm.selected()[0]
            oColl = pm.skinCluster(oSel, query=True, influence=True)
            pm.select(oColl)
        except Exception:
            pm.displayError('Select one object with skinCluster')
    else:
        pm.displayWarning('Select one object with skinCluster')
