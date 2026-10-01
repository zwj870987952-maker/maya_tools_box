# Embedded file name: S:\Git\eblabs-hub\eblabs_hub\UXFramework\scripts\Prefs.py
from functools import partial
from maya import cmds, mel, OpenMaya, OpenMayaUI
import os
import json
import time
import sys
import re
import copy

class PrefsDataStruct:

    @classmethod
    def new(cls):
        newDict = {}
        newDict['activeProfile'] = 'default'
        newDict['data'] = {}
        return newDict


class PrefsManager:
    instance = False
    prefs_group = 'eblabs_Hub_Main'

    @classmethod
    def getInstance(cls):
        """
        override this method to set prefs group
        """
        if not cls.instance:
            kwargs = {}
            kwargs['prefsGroup'] = cls.prefs_group
            cls.instance = Prefs(**kwargs)
        return cls.instance

    @classmethod
    def setProperty(cls, key, value):
        """
        commit data
        """
        cls.getInstance().setFilePref(key, value)

    @classmethod
    def getProperty(cls, key, defaultValue):
        """
        load existing prefs
        """
        return cls.getInstance().getFilePref(key, default=defaultValue)

    @classmethod
    def setActiveProfile(cls, profile):
        """
        set profile
        """
        cls.getInstance().setActiveProfile(profile)

    @classmethod
    def removeProfile(cls, profile):
        """
        set profile
        """
        cls.getInstance().removeProfile(profile)

    @classmethod
    def get_active_profile(cls):
        """
        set profile
        """
        return cls.getInstance().getActiveProfile()

    @classmethod
    def get_all_profiles(cls):
        """
        set profile
        """
        return cls.getInstance().listProfiles()


class Prefs:
    """
    kwargs = {}
    kwargs['prefsGroup'] = 'IDForGroupingPrefs'
    Prefs(**kwargs)
    """

    def __init__(self, *args, **kwargs):
        """
        grouping keyword
        """
        self.prefsGroup = 'default'
        if 'prefsGroup' in kwargs:
            self.prefsGroup = kwargs.pop('prefsGroup')
        self.prefsDataID = False
        self.configDataID = False
        self.data = False
        self.rawData = False
        self.activeProfile = 'default'
        self.prefsPath = os.path.normpath(os.path.join(cmds.internalVar(userAppDir=True), 'scripts', 'eblabs_prefs', '{0}.prefs'.format(self.prefsGroup)))
        self.tempData = {}
        self.refreshData()

    def getActiveProfile(self):
        """
        cached loading
        """
        self.refreshData()
        return self.rawData['activeProfile']

    def removeProfile(self, profileVar):
        if not profileVar:
            return False
        else:
            self.refreshData()
            if profileVar in self.rawData['data'].keys():
                self.rawData['data'].pop(profileVar, None)
            self.writePrefsToFile()
            if profileVar == self.getActiveProfile():
                self.setActiveProfile('default')
            return

    def setActiveProfile(self, profileVar):
        """
        cached loading
        """
        self.refreshData()
        self.activeProfile = profileVar
        self.rawData['activeProfile'] = profileVar
        if profileVar not in self.listProfiles():
            self.rawData['data'][profileVar] = {}
        self.data = self.rawData['data'][profileVar]
        self.writePrefsToFile()

    def listProfiles(self):
        return self.rawData['data'].keys()

    def setTempKey(self, key, value, group = 'default'):
        try:
            self.tempData[group]
        except:
            self.tempData[group] = {}

        self.tempData[group][key] = value

    def getTempKey(self, key, group = 'default', default = False):
        try:
            self.tempData[group]
        except:
            self.tempData[group] = {}

        if key not in self.tempData[group].keys():
            return default
        return self.tempData[group][key]

    def setScenePref(self, key, value):
        prefsKey = '{0}.{1}'.format(self.prefsGroup, key)
        cmds.fileInfo(prefsKey, value)

    def getScenePref(self, key, default = 'NOTSET'):
        prefsKey = '{0}.{1}'.format(self.prefsGroup, key)
        queryPrefs = cmds.fileInfo(prefsKey, query=True)
        if queryPrefs:
            queryPrefs = queryPrefs[0]
            try:
                queryPrefs = eval(queryPrefs)
            except:
                pass

        else:
            queryPrefs = default
        return queryPrefs

    def getFilePref(self, key, default = 'NOTSET'):
        self.refreshData()
        if key not in self.data.keys():
            return default
        return copy.deepcopy(self.data[key])

    def setFilePref(self, key, value):
        self.refreshData()
        self.data[key] = value
        self.writePrefsToFile()

    def getMayaObjectPref(self, key, default = 'NOTSET'):
        pass

    def setMayaObjectPref(self, key, value):
        pass

    def clearPrefs(self):
        self.rawData = PrefsDataStruct.new()
        self.writePrefsToFile()

    def getEditID(self, filepath):
        try:
            return os.path.getmtime(filepath)
        except:
            return False

    def hasEditIDChanged(self, filepath, previousEditID):
        editID = False
        try:
            editID = os.path.getmtime(filepath)
        except:
            return False

        if editID:
            if previousEditID != editID:
                return True
            else:
                return False

    def refreshData(self):
        """
        load data if its changed
        """
        if self.hasEditIDChanged(self.prefsPath, self.prefsDataID) or not self.prefsDataID:
            self.loadPrefsFromFile()
            self.prefsDataID = self.getEditID(self.prefsPath)
        self.data = self.rawData['data'].get(self.activeProfile, {})

    def writePrefsToFile(self):
        """
        prep folder
        """
        filePathRoot = os.path.split(self.prefsPath)[0]
        if not os.path.exists(filePathRoot):
            os.makedirs(filePathRoot)
        self.rawData['data'][self.activeProfile] = self.data
        data = json.dumps(self.rawData, sort_keys=True, indent=4)
        with open(self.prefsPath, 'w') as f:
            f.write(data)

    def loadPrefsFromFile(self):
        try:
            with open(self.prefsPath, 'r') as f:
                self.rawData = json.load(f)
        except Exception as e:
            pass

        if not self.rawData:
            self.rawData = PrefsDataStruct.new()
        self.activeProfile = self.rawData['activeProfile']
