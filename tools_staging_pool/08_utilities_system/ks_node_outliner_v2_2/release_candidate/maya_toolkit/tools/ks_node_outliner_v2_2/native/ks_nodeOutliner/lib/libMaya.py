from __future__ import absolute_import
from __future__ import print_function
from maya_toolkit.tools.ks_node_outliner_v2_2.session import cmdshim as cmds
import maya.app.general.resourceBrowser as resourceBrowser

from maya import utils

import sys
PYTHON_VERSION_3 = False
if sys.version_info[0] >= 3:
    PYTHON_VERSION_3 = True

from maya_toolkit.tools.ks_node_outliner_v2_2.qt_compat import QtWidgets
from maya_toolkit.tools.ks_node_outliner_v2_2.qt_compat import wrapInstance
from maya_toolkit.tools.ks_node_outliner_v2_2.qt_compat import shiboken

from maya import OpenMayaUI as omui

def getWorkspaceQtPointer(workspaceName):
    qtCtrl = omui.MQtUtil.findControl(workspaceName)
    if PYTHON_VERSION_3:
        ptr = wrapInstance(int(qtCtrl), QtWidgets.QWidget)
    else:
        ptr = wrapInstance(int(qtCtrl), QtWidgets.QWidget)
    return ptr


def getMayaFullDagPath(QObject):
    if PYTHON_VERSION_3:
        try:
            ptr = int(shiboken.getCppPointer(QObject)[0])
        except:
            ptr = omui.MQtUtil.fullName(int(QtWidgets.shiboken.unwrapinstance(QObject)))
    else:
        try:
            ptr = int(shiboken.getCppPointer(QObject)[0])
        except:
            ptr = omui.MQtUtil.fullName(int(QtWidgets.shiboken.unwrapinstance(QObject)))
    mayaFullDagPath = omui.MQtUtil.fullName(ptr)
    return mayaFullDagPath


def mayaMainWindow():
    mainWindowPtr = omui.MQtUtil.mainWindow()
    mainWindow = shiboken.wrapInstance(int(mainWindowPtr), QtWidgets.QMainWindow)
    return mainWindow


# def evalDeferred(command):
#     cmds.evalDeferred(command)

# def runEvalIdle():
#     utils.processIdleEvents()


def warning(string):
    cmds.warning(string)

def getOptionVar(key):
    from maya_toolkit.tools.ks_node_outliner_v2_2.session import option_get
    return option_get(key)

def setOptionVar(key,value):
    from maya_toolkit.tools.ks_node_outliner_v2_2.session import option_set
    return option_set(key,value)


def maya_getBuiltInFilters():
    maya_builtInNodeFilterPresets = []
    for filterName in cmds.itemFilter(query=True, listBuiltInFilters=True):
        if filterName.isalpha():
            maya_builtInNodeFilterPresets.append(filterName)
    return sorted(maya_builtInNodeFilterPresets)


def openIconBrowser():
    resBrowser = resourceBrowser.resourceBrowser()
    iconPath = resBrowser.run()
    if not iconPath:
        return None
    return iconPath


def nodeList_makeShortNames(nodeList):
    nodeList = [x.split('|')[-1] for x in nodeList]
    return nodeList



def getAllNodeTypes():
    return cmds.ls(nt=True)


def nodeTypesFromSelection():
    selection = cmds.ls(sl=True, long=True)
    if not selection:
        cmds.warning('No selected objects!')
        return None

    nodeTypes = []
    for node in selection:
        nodeType = cmds.nodeType(node)
        if nodeType == 'transform':
            nodeShapeType = cmds.nodeType(cmds.listRelatives(node, shapes=True, fullPath=True))
            if nodeShapeType:
                nodeTypes.append(nodeShapeType)
                continue
        nodeTypes.append(nodeType)
    nodeTypes = list(set(nodeTypes))
    return nodeTypes


def getSelection(fullPath=True):
    return cmds.ls(sl=True, long=fullPath)

def names_longToShort(nodeList):
    return cmds.ls(nodeList, long=False)

def getRelatedNodes(rootSelection, inclHierarchy=False, inclShaders=False, inclInputs=False):
    if not type(rootSelection) == list:
        rootSelection = [rootSelection]

    relatedNodes = []
    hierarchyNodes = list(rootSelection)
    hierarchyNodes += getShapes(hierarchyNodes)
    relatedNodes += hierarchyNodes
    if inclHierarchy:
        hierarchyNodes += getHierarchy(rootSelection)
        relatedNodes += hierarchyNodes
    if inclShaders:
        relatedNodes += getShadingNetwork(hierarchyNodes)
    if inclInputs:
        relatedNodes += getAllConnections(hierarchyNodes)

    relatedNodes = cmds.ls(relatedNodes, long=True)
    relatedNodes = list(set(relatedNodes))

    return relatedNodes

def getShapes(nodeList):
    nodeOutput = []
    result = cmds.listRelatives(nodeList, shapes=True, fullPath=True)
    if result:
        nodeOutput += result
    return nodeOutput

def getHierarchy(nodeList):
    nodeOutput = []
    for node in nodeList:
        result = cmds.listRelatives(node, allDescendents=True, shapes=False, path=True, fullPath=True)
        if result:
            nodeOutput += result

    nodeOutput = list(set(nodeOutput))
    return nodeOutput

def getAllConnections(nodeList):
    nodeOutput = []
    for node in nodeList:
        result = cmds.listHistory(node, allConnections=True, interestLevel=1)
        if result:
            result = cmds.ls(result, long=True)
            nodeOutput += result

    return nodeOutput


def getShadingNetwork(nodeList=[]):
    if not type(nodeList) == list:
        nodeList = [nodeList]

    nodeOutput = []
    SGs = []
    for node in nodeList:
        shadingEngine = cmds.listConnections(node, type="shadingEngine")
        if shadingEngine:
            SGs += shadingEngine

    SGs = list(set(SGs))
    nodeOutput += SGs

    rootShadingNodes = []
    for SG in SGs:
        SG_connections = cmds.listConnections(SG)
        rootShadingNodes += cmds.ls(SG_connections, materials=True)


    rootShadingNodes = list(set(rootShadingNodes))
    for node in rootShadingNodes:
        nodeOutput += cmds.listHistory(node, allConnections=True, future=False, interestLevel=2)

    nodeOutput = list(set(nodeOutput))
    return nodeOutput






if __name__ == "__main__":
    rootObj = ['Body_geo_05Shape']
    output = getShadingNetwork(rootObj)
    print(output)
