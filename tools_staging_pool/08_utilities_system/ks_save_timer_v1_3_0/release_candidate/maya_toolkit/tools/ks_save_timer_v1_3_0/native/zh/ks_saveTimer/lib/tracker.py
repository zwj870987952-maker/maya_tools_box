from __future__ import absolute_import
from __future__ import print_function
from maya_toolkit.tools.ks_save_timer_v1_3_0 import compat_six as six
from maya_toolkit.tools.ks_save_timer_v1_3_0.qt_compat import QtCore,QtGui,QtWidgets,Signal,Property,wrapInstance
_PYSIDE_VERSION_ = 2

import os
import re
import pprint
import json

from ks_saveTimer.lib import timer, Singleton, config
from ks_saveTimer.libApp import getLibApp as libApp
__HOST_APP__ = libApp.__HOST_APP__
__LIB_APP__ = libApp.__LIB_APP__



import sys
PYTHON_VERSION_3 = False
if sys.version_info[0] >= 3:
    PYTHON_VERSION_3 = True

def readFromJson(filePath):
    from maya_toolkit.tools.ks_save_timer_v1_3_0.storage import read_history
    return read_history(filePath)

def writeToJson(localData,filePath):
    from maya_toolkit.tools.ks_save_timer_v1_3_0.storage import write_history
    return write_history(filePath,localData)
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


def QDateTime_fromString(timeString, timeFormat='yyyyMMdd-HHmmss'):
    return QtCore.QDateTime.fromString(timeString, timeFormat)

def QDateTime_toString(QDateTime, timeFormat='yyyyMMdd-HHmmss'):
    return QDateTime.toString(timeFormat)


class _timeTracker(QtCore.QObject):
    def __init__(self):
        super(_timeTracker, self).__init__()

        self._DATA = {}
        self._CONFIG_ = config.configuration()
        self._SAVEPATH = self.getHistoryPath()
        self.loadHistory()

        self._TIMER = timer.timerObject()
        self._TIMER.preSave_addHistory.connect(self.timerSaved)


    def getHistoryPath(self):
        from maya_toolkit.tools.ks_save_timer_v1_3_0.session import data_root
        return str(data_root/"KSSaveTimer_timeTrackHistory.json")



    def loadHistory(self):
        # return
        if os.path.exists(self._SAVEPATH):
            self._DATA = readFromJson(self._SAVEPATH)
        else:
            self._DATA = {}

        if not self._DATA.get(__HOST_APP__):
            self._DATA[__HOST_APP__] = {}


    def saveHistory(self):
        # return
        writeToJson(self._DATA, self._SAVEPATH)


    def timerSaved(self):
        filePath = __LIB_APP__.get_filePath()
        if not filePath:return
        minutes = self._TIMER.counter
        if not self._TIMER.isActive():
            minutes = 0
        self.addHistory(filePath, minutes)

    def addHistory(self, fileName, minutes):
        if not isinstance(fileName,str) or not os.path.isabs(fileName) or type(minutes) is not int or not 0<=minutes<=1000000:raise ValueError("Absolute filename/nonnegative integer minutes required")
        self.loadHistory()

        dirPath, fileName = os.path.split(fileName)

        baseName = fileName
        versionInt = 0
        try:
            versionTag = re.findall("[_.-]v[0-9]+[_.-]", fileName)[-1]
            versionInt = int(re.findall("[0-9]+", versionTag)[0])
            baseName = fileName.split(versionTag)[0]
        except:
            pass

        fileHistory = self.getHistory(baseName)
        fileHistory['totalTime'] = fileHistory.get('totalTime') + minutes
        fileHistory['dirPath'] = dirPath

        currentDT = QtCore.QDateTime.currentDateTime()
        saveTime = QDateTime_toString(currentDT)

        fileHistory['lastSave'] = saveTime

        ### VERSION FILE HISTORY ###
        versionHistory = fileHistory['history'].get(str(versionInt), None)
        if not versionHistory:
            versionHistory = {}

        versionHistory['time'] = versionHistory.get('time', 0) + minutes
        versionHistory['date'] = saveTime
        versionHistory['fileName'] = fileName
        fileHistory['history'][str(versionInt)] = versionHistory


        self._DATA[__HOST_APP__][baseName] = fileHistory
        self.saveHistory()


    def removeHistoryItems(self, topNodes=None, versionNodes=None):
        self.loadHistory()

        for fileName in topNodes or []:
            self._DATA[__HOST_APP__].pop(fileName)

        for fileName, versionList in six.iteritems(versionNodes or {}):
            for versionInt in versionList:
                # print self._DATA[__HOST_APP__][fileName].get(versionInt)
                self._DATA[__HOST_APP__][fileName]['history'].pop(str(versionInt))

        self.saveHistory()


    def deleteHistory(self):
        self._DATA = {}
        self.saveHistory()

    def printData(self):
        pprint.pprint(self._DATA)

    def getHistory(self, baseName):
        fileHistory = self._DATA[__HOST_APP__].get(baseName, None)
        if not fileHistory:
            fileHistory = {
                'totalTime': 0,
                'lastSave': None,
                'history': {},
            }
        return fileHistory

    def getHistory_fileNameList(self):
        return list(self._DATA[__HOST_APP__].keys())

    def getHistory_filenameData(self, fileName):
        return self._DATA[__HOST_APP__].get(fileName)

    def getHistory_versionHistory(self, fileName):
        return self._DATA[__HOST_APP__][fileName].get('history')




if __name__ == '__main__':
    tracker = timeTracker()
    # tracker.deleteHistory()

    fileName = "prp_rock_sha_v004_kimSt.ma"
    minutes = 20
    tracker.addHistory(fileName, minutes)
    fileName = "prp_rock_sha_v005_kimSt.ma"
    minutes = 15
    tracker.addHistory(fileName, minutes)

    tracker.printData()
    # pprint.pprint(_TRACKINGDATA)

_INSTANCE=None
def timeTracker(*args,**kwargs):
    import sys
    from maya_toolkit.tools.ks_save_timer_v1_3_0.session import singleton
    return singleton(sys.modules[__name__],"timeTracker",*args,**kwargs)
