from __future__ import absolute_import
from maya_toolkit.tools.ks_node_outliner_v2_2.qt_compat import QtCore,QtGui,QtWidgets
from maya_toolkit.tools.ks_node_outliner_v2_2.qt_compat import Signal
from configparser import ConfigParser
import os
import copy
import json

import ks_nodeOutliner

import pprint
from maya_toolkit.tools.ks_node_outliner_v2_2 import compat_six as six


import sys
PYTHON_VERSION_3 = False
if sys.version_info[0] >= 3:
    PYTHON_VERSION_3 = True

class SingletonMetaclass(type):
    '''Basic Singleton metaclass'''
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonMetaclass, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class QtSingletonMetaclass(SingletonMetaclass, type(QtCore.QObject)):
    pass


class _Configuration(QtCore.QObject):
    # __metaclass__ = QtSingletonMetaclass
    updated = Signal()
    guiRefresh = Signal()


    def __init__(self):
        super(_Configuration, self).__init__()

        self.userConfigPath = ks_nodeOutliner._CONFIG_USER_

        self._filterNodes = {}
        self._filterNodes_temp = {}

        self._menuPresets = {}
        self._menuPresets_temp = {}

        self._filterOrder = []

        self.loadData(self.userConfigPath)



    def loadData(self, filePath):
        if not os.path.exists(filePath):
            return
        configData = readFromJson(filePath)
        filterDataDict = configData.get('FILTERS', {})
        for filterName, filterData in six.iteritems(filterDataDict):
            node = FilterNode(filterName, filterData)
            self._filterNodes[filterName] = node

        presetData = configData.get('MENUPRESETS', {})
        self._menuPresets = presetData

        self._filterOrder = configData.get('FILTERORDER')


    def saveData(self):
        filterData = {}
        for filterName, node in six.iteritems(self._filterNodes):
            filterData[node._filterName] = node.getDataDict()

        presetData = self._menuPresets

        configData = {}
        configData['FILTERS'] = filterData
        configData['FILTERORDER'] = self._filterOrder
        configData['MENUPRESETS'] = presetData
        writeToJson(configData, self.userConfigPath)

        self.updated.emit()

    def snapshotData(self):
        self._filterOrder_snapshot = list(self._filterOrder)
        self._filterNodes_snapshot = copy.deepcopy(self._filterNodes)
        self._menuPresets_snapshot = copy.deepcopy(self._menuPresets)

    def restoreData(self):
        self._filterOrder = list(self._filterOrder_snapshot)
        self._filterNodes = copy.deepcopy(self._filterNodes_snapshot)
        self._menuPresets = copy.deepcopy(self._menuPresets_snapshot)


    def importFromFile(self, filePath):
        configData = readFromJson(filePath)

        for filterName, filterData in six.iteritems(configData['FILTERS']):
            node = self.filter_addNew(filterName, filterData)


    def exportToFile(self, filePath, filterList):
        filterData = {}
        for filterName in filterList:
            node = self.getFilterNode(filterName)
            filterData[node._filterName] = node.getDataDict()

        # presetData = {}
        # for presetName in presetList:
        #     data = self._menuPresets.get(presetName, {})
        #     if not data:
        #         continue
        #     presetData[presetName] = data

        configData = {}
        configData['FILTERS'] = filterData
        # configData['MENUPRESETS'] = presetData
        writeToJson(configData, filePath)


    def getFilterNode(self, filterName):
        return self._filterNodes.get(filterName, None)

    def getFilterNames(self):
        return list(self._filterNodes.keys())

    def filter_addNew(self, filterName, filterData={}):
        allFilters = self.getFilterNames()
        filterName = resolveNamingConflict(filterName, allFilters)

        node = FilterNode(filterName, filterData)
        self._filterNodes[filterName] = node
        self._filterOrder.append(filterName)
        return node

    def filter_delete(self, filterName):
        if filterName not in self.getFilterNames():
            return

        node = self._filterNodes.pop(filterName)
        self._filterOrder = [n for n in self._filterOrder if n != filterName]

        for presetName in self.getMenuPresetNames():
            for menuName in self._menuPresets[presetName].keys():
                if filterName in self._menuPresets[presetName][menuName]:
                    self._menuPresets[presetName][menuName].remove(filterName)


    def filter_rename(self, oldName, newName):
        if oldName == newName:
            return

        newName = resolveNamingConflict(newName, self.getFilterNames())

        node = self.getFilterNode(oldName)
        node.setFilterName(newName)
        self._filterOrder = [newName if n == oldName else n for n in self._filterOrder]
        self._filterNodes[newName] = self._filterNodes.pop(oldName)


        for presetName in self.getMenuPresetNames():
            for menuName in self._menuPresets[presetName].keys():
                menuList = self._menuPresets[presetName][menuName]
                if oldName in menuList:
                    i = menuList.index(oldName)
                    menuList.pop(i)
                    menuList.insert(i, newName)

        self.guiRefresh.emit()
        return newName

    def filter_duplicate(self, filterName):
        filterData = self.getFilterNode(filterName).getDataDict()
        node = self.filter_addNew(filterName, filterData)

        self.guiRefresh.emit()
        return node

    def getMenuPresetNames(self):
        return list(self._menuPresets.keys())

    def menuPreset_addNew(self, presetName):
        if presetName in self.getMenuPresetNames():
            return

        # defaultData = {'iconMenu':[], 'outlinerMenu':[], 'defaultFilter_nodeOutlinerA':[], 'defaultFilter_nodeOutlinerB':[]}
        defaultData = {'iconMenu':[], 'outlinerMenu':[]}
        self.menuPreset_setDict(presetName, defaultData)

        # pprint.pprint(self._menuPresets)
        return presetName


    def menuPreset_delete(self, presetName):
        if presetName not in self.getMenuPresetNames():
            return

        self._menuPresets.pop(presetName)

    def menuPreset_getDict(self, presetName):
        return self._menuPresets.get(presetName)

    def menuPreset_setDict(self, presetName, dataDict):
        self._menuPresets[presetName] = dataDict

    def menuPreset_getList(self, presetName, listName):
        return self._menuPresets[presetName].get(listName, [])

    def menuPreset_setList(self, presetName, listName, itemList):
        self._menuPresets[presetName][listName] = itemList

    def getFilterListOrder(self):
        return self._filterOrder

    def setFilterListOrder(self, filterList):
        self._filterOrder = filterList

    # def getFilterList(self):
    #     return self.DATA_TEMP["FILTERLIST"]

    # def setFilterList(self, filterList):
    #     self.DATA_TEMP["FILTERLIST"] = filterList




class FilterNode(object):
    def __init__(self, filterName, filterData={}):
        self._filterName = filterName
        self._filterData = {
            "icon": ":/defaultOutliner.svg",
            "baseFilter": True,
            "baseFilterType": "internalFilter",
            "internalFilter": "",
            "nodeTypes": [],
            "selectionFilter": False,
            "sf_getHierarchy": False,
            "sf_getShadingNetwork": False,
            "sf_getInputConnections": False,
            "scriptFilter": False,
            "scriptFunction": '',
            "scriptModule": '',
            "scriptArgs": '',
            "searchInvert": False,
            "searchString": "",
            "showShapes": False,
            "ignoreHierarchy": False,
            "expandObjects": False
        }

        self.mergeFilterData(filterData)


    def getFilterName(self):
        return self._filterName

    def setFilterName(self, name):
        self._filterName = name

    def getData(self, key):
        return self._filterData.get(key)

    def setData(self, key, value):
        self._filterData[key] = value

    def getDataDict(self):
        return self._filterData

    def setDataDict(self, dataDict):
        self._filterData = dataDict

    def mergeFilterData(self, dataDict):
        self._filterData = mergeDicts(dataDict, self._filterData)





def readFromJson(filePath):
    from maya_toolkit.tools.ks_node_outliner_v2_2.config_io import read
    return read(filePath)

def writeToJson(localData,filePath):
    from maya_toolkit.tools.ks_node_outliner_v2_2.session import native_save
    return native_save(filePath,localData)
    # print 'Written to %s' %(filePath)

def byteify(input):
    if isinstance(input, dict):
        return {byteify(key): byteify(value) for key, value in six.iteritems(input)}
    elif isinstance(input, list):
        return [byteify(element) for element in input]
    elif isinstance(input, six.text_type):
        return input.encode('utf-8')
    else:
        return input


def byteifyPy3(input):
    if isinstance(input, dict):
        return {byteifyPy3(key): byteifyPy3(value) for key, value in six.iteritems(input)}
    elif isinstance(input, list):
        return [byteifyPy3(element) for element in input]
    elif isinstance(input, six.text_type):
        return input.encode('utf-8').decode('utf-8')
    else:
        return input


def mergeDicts(source, destination):
    for key, value in source.items():
        if isinstance(value, dict):
            # get node or create one
            node = destination.setdefault(key, {})
            mergeDicts(value, node)
        else:
            destination[key] = value

    return destination

def resolveNamingConflict(name, nameList):
    nameList = [i.lower() for i in nameList]
    if not name.lower() in nameList:
        return name

    orig = name.rstrip('0123456789')
    origLower = orig.lower()

    i=1
    name = origLower + str(i)
    while name in nameList:
        i += 1
        name = origLower + str(i)
    return orig + str(i)




if __name__ == "__main__":
    import pprint
    config = configuration()
    pprint.pprint(config.__dict__)
    # node = config.getFilterNode('Textures')

    # config.debug()
    # config.saveData()

_CONFIGURATION_INSTANCE = None
def configuration():
    global _CONFIGURATION_INSTANCE
    if _CONFIGURATION_INSTANCE is None:_CONFIGURATION_INSTANCE = _Configuration()
    return _CONFIGURATION_INSTANCE
