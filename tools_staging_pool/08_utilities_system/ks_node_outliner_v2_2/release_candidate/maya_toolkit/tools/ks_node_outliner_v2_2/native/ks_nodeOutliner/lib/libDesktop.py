def maya_getBuiltInFilters():
    maya_builtInNodeFilterPresets = ['', 'DefaultMaterialsAndShaderGlowFilter', 'DefaultTexturesFilter', 'DefaultRenderUtilitiesFilter', 'DefaultPolygonObjectsFilter', 'DefaultCameraShapesImagePlanesFilter', 'DefaultJointsFilter', 'MashFilter', 'DefaultUsesImageFileFilter', 'DefaultNotInRenderLayersFilter', 'DefaultInRenderLayersFilter', 'DefaultNotInSelectedRenderLayersFilter', 'DefaultInSelectedRenderLayersFilter', 'DefaultContainerFilter', 'DefaultGeometryFilter', 'DefaultNURBSObjectsFilter', 'DefaultSubdivObjectsFilter', 'DefaultCameraShapesFilter', 'DefaultIkHandlesFilter', 'characterSetsFilter', 'clipsFilter', 'partitionFilter', 'DefaultSetsFilter', 'defaultSetFilter', 'clusterSetsFilter', 'deformerSetsFilter', 'latticeSetsFilter', 'nonLinearSetsFilter', 'skinClusterSetsFilter', 'jointClusterSetsFilter', 'otherDeformerSetsFilter', 'DefaultOpticalFXFilter', 'DefaultLightsAndOpticalFXFilter', 'renderableObjectShapeFilter', 'DefaultShadingGroupsFilter', 'DefaultBakeSetsFilter', 'renderPassSetsFilter', 'renderPassesFilter', 'DefaultTexturePlacementsFilter', 'DefaultContainerNodeFilter', 'DefaultShaderGlowFilter', 'DefaultNoShaderGlowFilter', 'DefaultLightLinkingLightFilter', 'DefaultLightShapesFilter', 'DefaultImagePlanesFilter', 'DefaultTexturesSGFilter', 'DefaultSGLightShapesTexturesFilter', 'DefaultSGLightShapesFilter', 'DefaultBasicRenderNodesFilter', 'DefaultShadingGroupsAndMaterialsFilter', 'DefaultAllRenderNodesFilter', 'DefaultAllShadingNodesFilter', 'DefaultCreateNodeFilter', 'layersFilter', 'animLayersFilter', 'notAnimLayersFilter', 'defaultRenderLayerFilter', 'renderLayerFilter', 'renderingSetsFilter', 'renderableObjectsAndSetsFilter', 'lightLinkingObjectFilter', 'CustomGPUCacheFilter']
    return maya_builtInNodeFilterPresets

def openIconBrowser():
    return ''

def nodeTypesFromSelection():
    return []

def getAllNodeTypes():
    return ['nodeTypeA', 'nodeTypeB', 'nodeTypeC']

def getSelection(fullPath=True):
    return ['rootObj']


def getOptionVar(key):
    return None

def setOptionVar(key, value):
    pass

def names_longToShort(nodeList):
    return nodeList

def getRelatedNodes(rootSelection, hierarchy=False, shaders=False, inputs=False):
    relatedNodes = []
    return relatedNodes


def evalDeferred(command):
    pass

def runEvalIdle():
    pass
