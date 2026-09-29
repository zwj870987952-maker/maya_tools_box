# Embedded file name: S:\Git\eblabs-hub\eblabs_hub\Whiskey\scripts\WhiskeyPro.py
import maya.cmds as cmds
import maya.mel as mel
from functools import partial
import string
import colorsys
import maya.api.OpenMaya as OpenMaya
import math
import os
import json
from itertools import groupby
import copy
import traceback
# from . import LicenseManager
from ..data import PackageData
package_data = PackageData.get_data()
__author__ = 'Eric Bates, ebLabs.com'
__copyright__ = 'Copyright 2020, Eric Bates'
__credits__ = ['Eric Bates']
__maintainer__ = 'Eric Bates'
__email__ = 'eric@eric-bates.com'
__status__ = 'Production'
__version__ = package_data.get('version', '')

class window():
    version = __version__

    @classmethod
    def load(cls):
        # license_safe_check = LicenseManager.Query.LicenseSafeCheck()
        # if not license_safe_check:
        #     return
        print ('whisKEY_Pro:' + cls.version)
        windowName = 'whisKEY_Pro'
        if cmds.window(windowName, exists=True):
            cmds.deleteUI(windowName, window=True)
        storeWindowPosition = Prefs.getPrefsKey('storeWindowPosition')
        if not storeWindowPosition:
            if cmds.windowPref(windowName, exists=True):
                cmds.windowPref(windowName, remove=True)
        cls.window = cmds.window(windowName, widthHeight=(270, 400), title=windowName, bgc=[0.25] * 3)
        cls.mainLayoutContainerForm = cmds.formLayout()
        cls.mainColumnLayout = cmds.columnLayout(parent=cls.mainLayoutContainerForm, adjustableColumn=True, columnAttach=['both', 1], rowSpacing=2)
        cmds.formLayout(cls.mainLayoutContainerForm, edit=True, attachForm=[(cls.mainColumnLayout, 'top', 0)])
        cmds.formLayout(cls.mainLayoutContainerForm, edit=True, attachForm=[(cls.mainColumnLayout, 'left', 0)])
        cmds.formLayout(cls.mainLayoutContainerForm, edit=True, attachNone=[(cls.mainColumnLayout, 'bottom')])
        cmds.formLayout(cls.mainLayoutContainerForm, edit=True, attachForm=[(cls.mainColumnLayout, 'right', 0)])
        Prefs.setPrefsKey('version', cls.version)
        widget_base.clearInstances()
        slider_base.clearInstances()
        widget_base.setWidgetParent(parent=cls.getParent())
        widget_base.addWidgetsFromPrefs()
        cmds.showWindow(cls.window)
        cmds.setFocus(cls.window)
        cls.resizeUI()

    @classmethod
    def resizeUI(cls, *args, **kwargs):
        command = partial(cls.resizeUI_deferred)
        command()

    @classmethod
    def resizeUI_deferred(cls, *args, **kwargs):
        cmds.window(cls.window, edit=True, height=1)
        fudgeFactor = 0
        scrollLayoutHeight = cmds.formLayout(cls.mainLayoutContainerForm, query=True, height=True)
        scrollLayoutHeight += fudgeFactor
        cmds.window(cls.window, edit=True, height=scrollLayoutHeight)

    @classmethod
    def addWidgets(cls, *args, **kwargs):
        parent = cls.getParent()
        widgetData = Prefs.getProfileData()
        if not widgetData:
            widgetData = cls.getDefaultWidgetData()
        for w in widgetData:
            widgetDescription = w['description']
            widgetType = w['widgetType']
            widgetState = w['state']
            widgetExpandedState = True
            try:
                widgetExpandedState = w['expanded']
            except:
                pass

            if widgetType == 'inbetween':
                newItem = widget_tween(parent=parent, description=widgetDescription, expandedState=widgetExpandedState, stateData=widgetState)
            if widgetType == 'extras':
                newItem = widget_extras(parent=parent, description=widgetDescription, expandedState=widgetExpandedState, stateData=widgetState)
            if widgetType == 'worldSpace':
                newItem = widget_worldSpace(parent=parent, description=widgetDescription, expandedState=widgetExpandedState, stateData=widgetState)
            if widgetType == 'classic':
                newItem = widget_classic(parent=parent, description=widgetDescription, expandedState=widgetExpandedState, stateData=widgetState)
            if widgetType == 'curveOptions':
                newItem = widget_curveOptions(parent=parent, description=widgetDescription, expandedState=widgetExpandedState, stateData=widgetState)
            if widgetType == 'snapshot':
                newItem = widget_snapshot(parent=parent, description=widgetDescription, expandedState=widgetExpandedState, stateData=widgetState)
            if widgetType == 'principles':
                newItem = widget_principles(parent=parent, description=widgetDescription, expandedState=widgetExpandedState, stateData=widgetState)
            if widgetType == 'tools':
                newItem = widget_tools(parent=parent, description=widgetDescription, expandedState=widgetExpandedState, stateData=widgetState)

        cmds.evalDeferred(cls.resizeUI)

    @classmethod
    def getDefaultWidgetData(cls, *args, **kwargs):
        widgetData = widget_base.getDefaultWidgetData()
        return widgetData

    @classmethod
    def resetPrefs(cls, *args, **kwargs):
        profile = False
        if 'profile' in kwargs:
            profile = kwargs.pop('profile')
        Prefs.setProfileData(profileData={})

    @classmethod
    def getParent(cls):
        return cls.mainColumnLayout

    @classmethod
    def addItem(cls, addItem, *args, **kwargs):
        widget_base.addItem(addItem)
        cls.storePrefs()
        cmds.evalDeferred(cls.resizeUI)

    @classmethod
    def storePrefs(cls, *args, **kwargs):
        widget_base.storePrefs()


class Prefs():

    @classmethod
    def listProfiles(cls):
        cls.loadPrefs()
        try:
            cls.data['data']
        except:
            cls.data['data'] = {}

        profiles = cls.data['data'].keys()
        return profiles

    @classmethod
    def getPrefsPath(cls):
        return os.path.normpath(os.path.join(cmds.internalVar(userAppDir=True), 'scripts', 'eblabs_prefs', 'whiskey.prefs'))

    @classmethod
    def removeProfile(cls, profile = False):
        cls.loadPrefs()
        try:
            cls.data['data']
        except:
            cls.data['data'] = {}

        if profile in cls.data['data'].keys():
            cls.data['data'].pop(profile)
        cls.savePrefs()

    @classmethod
    def getActiveProfile(cls):
        try:
            cls.data
        except:
            cls.data = {}

        try:
            cls.data['activeProfile']
        except:
            cls.data['activeProfile'] = 'default'

        return cls.data['activeProfile']

    @classmethod
    def setProfileData(cls, profile = False, profileData = {}):
        cls.loadPrefs()
        activeProfile = cls.getActiveProfile()
        if profile:
            cls.setPrefsKey('activeProfile', profile)
            activeProfile = profile
        try:
            cls.data['data']
        except:
            cls.data['data'] = {}

        try:
            cls.data['data'][activeProfile]
        except:
            cls.data['data'][activeProfile] = {}

        cls.data['data'][activeProfile]['data'] = profileData
        cls.savePrefs()

    @classmethod
    def getProfileData(cls, profile = False):
        cls.loadPrefs()
        activeProfile = cls.getActiveProfile()
        if profile:
            activeProfile = profile
        returnData = {}
        try:
            returnData = copy.deepcopy(cls.data['data'][activeProfile]['data'])
        except Exception as e:
            pass

        return returnData

    @classmethod
    def getPrefsKey(cls, key, *args, **kwargs):
        cls.loadPrefs()
        try:
            cls.data
        except:
            cls.data = {}

        defaultPrefs = {}
        defaultPrefs['storeWindowPosition'] = False
        defaultPrefs['activeProfile'] = 'default'
        defaultPrefs['profilesData'] = {}
        defaultPrefs['version'] = 'not set'
        if key not in defaultPrefs.keys():
            cls.cmds.warning(389, 'ebLabs_whisKEY, Key Not Found', key)
            return None
        else:
            if key not in cls.data.keys():
                if key in defaultPrefs.keys():
                    cls.data[key] = defaultPrefs[key]
            return copy.deepcopy(cls.data[key])

    @classmethod
    def setPrefsKey(cls, key, value, *args, **kwargs):
        cls.loadPrefs()
        try:
            cls.data
        except:
            cls.data = {}

        if key:
            cls.data[key] = value
            cls.savePrefs()

    @classmethod
    def savePrefs(cls, *args, **kwargs):
        prefsPath = cls.getPrefsPath()
        if prefsPath:
            try:
                cls.data
            except:
                cls.data = {}

        cls.writeDataToFile(prefsPath, cls.data)

    @classmethod
    def loadPrefs(cls, *args, **kwargs):
        try:
            prefsPath = cls.getPrefsPath()
            if prefsPath:
                cls.data = cls.loadDataFromFile(prefsPath)
                if not cls.data:
                    cls.data = {}
        except:
            pass

    @classmethod
    def writeDataToFile(cls, filePath, dictionary):
        filePathRoot = os.path.split(filePath)[0]
        if not os.path.exists(filePathRoot):
            os.makedirs(filePathRoot)
        fileObject = open(filePath, 'w')
        data = json.dumps(dictionary, sort_keys=True, indent=4)
        fileObject.write(data)
        fileObject.close()

    @classmethod
    def loadDataFromFile(cls, filename, *args, **kwargs):
        data = None
        try:
            filePath = open(filename, 'r')
            data = json.loads(filePath.read())
            filePath.close()
        except:
            pass

        return data


class Functions():
    prefsFilepath = os.path.normpath(os.path.join(cmds.internalVar(userAppDir=True), 'scripts', 'eblabs_prefs', 'whiskey.prefs'))
    version = 1
    activeProfile = 'default'
    profilesData = {}

    @classmethod
    def quickUndo(cls, *args, **kwargs):
        command = partial(cls.quickUndo_wrapped)
        cmds.evalDeferred(command)

    @classmethod
    def quickUndo_wrapped(cls, *args, **kwargs):
        try:
            cls.suspendUI(True)
            cmds.undo()
        except Exception as e:
            print (236, e)
        finally:
            cls.suspendUI(False)

    @classmethod
    def quickRedo(cls, *args, **kwargs):
        command = partial(cls.quickRedo_wrapped)
        cmds.evalDeferred(command)

    @classmethod
    def quickRedo_wrapped(cls, *args, **kwargs):
        try:
            cls.suspendUI(True)
            cmds.redo()
        except Exception as e:
            print (255, e)
        finally:
            cls.suspendUI(False)

    @classmethod
    def smashBaker(cls, selected, startTime, endTime, *args, **kwargs):
        count = 0
        if selected:
            count = len(selected)
        message = 'Smash Bake Selected {0} Objects?'.format(count)
        confirm = cmds.confirmDialog(title='Smash Bake', message=message, button=['Yes', 'No'], defaultButton='No', cancelButton='No', dismissString='No')
        if confirm == 'Yes':
            try:
                rootLayer = cmds.animLayer(query=True, root=True)
                if rootLayer:
                    allLayers = cmds.ls(type='animLayer')
                    for l in allLayers:
                        state = False
                        if l == rootLayer:
                            state = True
                        cmds.animLayer(l, edit=True, selected=state)

                timeRange = [startTime, endTime + 1]
                currentTime = cmds.currentTime(query=True)
                data = {}
                if selected:
                    cls.suspendUI(True)
                    attributeList = []
                    for s in selected:
                        attributes = cmds.listAttr(s, scalar=True, keyable=True, unlocked=True)
                        if attributes:
                            for a in attributes:
                                attribute = '{0}.{1}'.format(s, a)
                                attributeList.append(attribute)

                        else:
                            print ('SKIPPING, NO ATTRS FOR: ', s)

                    for f in range(timeRange[0], timeRange[1]):
                        cmds.currentTime(f, edit=True)
                        data[f] = {}
                        for a in attributeList:
                            data[f][a] = cmds.getAttr(a)

                    for a in attributeList:
                        if cmds.connectionInfo(a, isDestination=True):
                            destination = cmds.connectionInfo(a, getExactDestination=True)
                            try:
                                source = cmds.connectionInfo(destination, sourceFromDestination=True)
                                cmds.disconnectAttr(source, destination)
                            except:
                                cmds.delete(destination, inputConnectionsAndNodes=True)

                    for f in data.keys():
                        for a in data[f].keys():
                            value = data[f][a]
                            cmds.setKeyframe(a, value=value, time=f)

                    cmds.currentTime(currentTime, edit=True)
                    for a in attributeList:
                        animLayers = cmds.listConnections(a, type='animLayer')
                        if animLayers:
                            for l in animLayers:
                                cmds.animLayer(l, edit=True, removeAttribute=a)

            except:
                pass
            finally:
                cls.suspendUI(False)

    @classmethod
    def queryTimeRange(cls, *args, **kwargs):
        checkHighlighted = False
        if 'checkHighlighted' in kwargs:
            checkHighlighted = kwargs.pop('checkHighlighted')
        startTime = int(cmds.playbackOptions(q=True, animationStartTime=True))
        endTime = int(cmds.playbackOptions(q=True, animationEndTime=True))
        if checkHighlighted:
            rangeStart, rangeEnd = str(cmds.timeControl(mel.eval('$tmpVar=$gPlayBackSlider'), query=True, range=True)).replace('"', '').split(':')
            rangeStart = float(rangeStart)
            rangeEnd = float(rangeEnd) - 1
            if rangeEnd - rangeStart > 1:
                startTime = rangeStart
                endTime = rangeEnd
        return (startTime, endTime)

    @classmethod
    def getHighlightedRange(cls, *args, **kwargs):
        rangeStart, rangeEnd = str(cmds.timeControl(mel.eval('$tmpVar=$gPlayBackSlider'), query=True, range=True)).replace('"', '').split(':')
        rangeStart = float(rangeStart)
        rangeEnd = float(rangeEnd) - 1
        if rangeEnd - rangeStart > 1:
            return [rangeStart, rangeEnd]
        else:
            return False

    @classmethod
    def removeProfile(cls, profile, *args, **kwargs):
        profilesData = cls.getProfilesData()
        removed = False
        if profile in profilesData.keys():
            removed = profilesData.pop(profile, False)
        if removed:
            cls.setProfilesData(profilesData)

    @classmethod
    def getProfiles(cls):
        profilesData = cls.getProfilesData()
        return profilesData.keys()

    @classmethod
    def setActiveProfile(cls, profile):
        cls.activeProfile = str(profile)

    @classmethod
    def getActiveProfile(cls):
        try:
            cls.activeProfile
        except Exception as e:
            cls.activeProfile = 'default'

        return cls.activeProfile

    @classmethod
    def setProfilesData(cls, data):
        cls.profilesData = copy.deepcopy(data)

    @classmethod
    def getProfilesData(cls):
        try:
            cls.profilesData
        except:
            cls.profilesData = {}

        if 'default' not in cls.profilesData.keys():
            cls.profilesData['default'] = {}
            cls.profilesData['default']['data'] = []
        return copy.deepcopy(cls.profilesData)

    @classmethod
    def groupDuplicates(cls, values, *args, **kwargs):
        if not values:
            return False
        return [ (k, sum((1 for i in g))) for k, g in groupby(values) ]

    @classmethod
    def cleanSubframeKeys(cls, *args, **kwargs):
        selection = False
        if 'selection' in kwargs:
            selection = kwargs.pop('selection')
        count = 0
        if selection:
            count = len(selection)
        message = 'Clean Subframe Keys for {0} Objects?'.format(count)
        confirm = cmds.confirmDialog(title='Clean Subframe Keys?', message=message, button=['Yes', 'No'], defaultButton='No', cancelButton='No', dismissString='No')
        if confirm == 'Yes':
            if not selection:
                return False
            checkShapes = cmds.listRelatives(selection, shapes=True, fullPath=True)
            if checkShapes:
                selection += checkShapes
            selection = list(set(selection))
            removalStats = {}
            removalStats['keysCleaned'] = 0
            gMainProgressBar = mel.eval('$tmp = $gMainProgressBar')
            cmds.progressBar(gMainProgressBar, edit=True, beginProgress=True, isInterruptable=True, status='whisKEY Processing...', maxValue=len(selection))
            try:
                curveNodesToClean = []
                for s in selection:
                    cmds.progressBar(gMainProgressBar, edit=True, step=1)
                    curveNodes = cls.getAnimCurvesForAttribute(s)
                    if curveNodes:
                        for curveNode in curveNodes:
                            timesValues = cmds.getAttr('{0}.{1}'.format(curveNode, 'keyTimeValue[:]'))
                            if timesValues:
                                times = []
                                values = []
                                wholeTimes = set()
                                subframeTimes = set()
                                for t, v in timesValues:
                                    times.append(t)
                                    wholeTimes.add(int(float(t) + 0.5))
                                    values.append(v)
                                    if not float(t).is_integer():
                                        subframeTimes.add(t)
                                        removalStats['keysCleaned'] += 1

                                newTimes = list(wholeTimes - set(times))
                                for t in newTimes:
                                    cmds.setKeyframe(curveNode, insert=True, time=tuple([t, t]))

                                for t in subframeTimes:
                                    cmds.cutKey(curveNode, time=tuple([t, t]))

            except Exception as e:
                print (813, Exception, e)
                print (traceback.format_exc())
            finally:
                cmds.progressBar(gMainProgressBar, edit=True, endProgress=True)

            print ('ebLabs_whisKEY:Clean Subframe Keys Info:', removalStats)

    @classmethod
    def getAnimCurvesForAttribute(cls, attribute, *args, **kwargs):
        connections = cmds.listConnections(attribute, destination=False, source=True)
        whiteList = ['animCurve', 'animBlend', 'character']
        keepLooking = True
        recursionLimit = 100
        count = 0
        while keepLooking:
            keepLooking = False
            check = cmds.listConnections(connections, destination=False, source=True)
            if check:
                check = list(set(check))
                for n in check:
                    if n not in connections:
                        whiteListCheck = False
                        nType = cmds.objectType(n)
                        for w in whiteList:
                            if w in nType:
                                whiteListCheck = True
                                break

                        if whiteListCheck:
                            if nType == 'character':
                                characterSetMember = cmds.character(attribute, query=True, characterPlug=True)
                                characterSetAnimCurve = cmds.listConnections(characterSetMember, destination=False, source=True)
                                if characterSetAnimCurve:
                                    if characterSetAnimCurve[0] not in connections:
                                        connections.append(characterSetAnimCurve[0])
                                        keepLooking = True
                            else:
                                connections.append(n)
                                keepLooking = True

                count += 1
                if count >= recursionLimit:
                    keepLooking = False

        animCurves = []
        if connections:
            for c in connections:
                nType = cmds.objectType(c)
                if 'animCurve' in nType:
                    if c not in animCurves:
                        animCurves.append(c)

        return animCurves

    @classmethod
    def removeBoringKeys(cls, *args, **kwargs):
        selection = False
        if 'selection' in kwargs:
            selection = kwargs.pop('selection')
        regions = False
        if 'regions' in kwargs:
            regions = kwargs.pop('regions')
        if not selection:
            return False
        count = 0
        selectedChannels = False
        count = len(selection)
        selectedChannels = cls.getSelectedChannels(selection=selection)
        message = []
        message += ['Remove Boring Keys for {0} Objects?'.format(count)]
        if selectedChannels:
            message += ['Using selected channels, [{0}]'.format('], ['.join(selectedChannels))]
        confirm = cmds.layoutDialog(ui=partial(cls.removeBoringKeysPrompt, '\n'.join(message)))
        if 'True' in confirm:
            leaveFirstKey = ''
            if confirm == 'TrueLeaveFirst':
                leaveFirstKey = True
            elif confirm == 'TrueLeaveNone':
                leaveFirstKey = False
            removalStats = {}
            removalStats['keysRemoved'] = 0
            gMainProgressBar = mel.eval('$tmp = $gMainProgressBar')
            cmds.progressBar(gMainProgressBar, edit=True, beginProgress=True, isInterruptable=True, status='whisKEY Processing...', maxValue=len(selection))
            try:
                for s in selection:
                    cmds.progressBar(gMainProgressBar, edit=True, step=1)
                    if not cmds.progressBar(gMainProgressBar, query=True, isCancelled=True):
                        attributes = cls.listAttributes(s, filterEnums=False)
                        if selectedChannels:
                            attributes = list(set(attributes) & set(selectedChannels))
                        for a in attributes:
                            attribute = '{0}.{1}'.format(s, a)
                            curveNodes = cmds.findKeyframe(s, curve=True, at=a)
                            if curveNodes:
                                for curveNode in curveNodes:
                                    timesValues = cmds.getAttr('{0}.{1}'.format(curveNode, 'keyTimeValue[:]'))
                                    times = []
                                    values = []
                                    for t, v in timesValues:
                                        times.append(t)
                                        values.append(v)

                                    groupedValues = cls.groupDuplicates(values)
                                    if len(groupedValues) == 1:
                                        if leaveFirstKey:
                                            if len(times) == 1:
                                                pass
                                            else:
                                                secondKey = times[1]
                                                lastKey = times[-1]
                                                cmds.cutKey(curveNode, time=(secondKey, lastKey))
                                        else:
                                            cmds.cutKey(curveNode)
                                    else:
                                        index = 0
                                        previousGroupWasBoring = False
                                        indicesForRemoval = []
                                        for value, count in groupedValues:
                                            countRange = range(count)
                                            for c in countRange:
                                                if c == 0:
                                                    if previousGroupWasBoring or count > 1:
                                                        cmds.keyTangent(curveNode, edit=True, inTangentType='fixed', outTangentType='fixed', index=(index, index))
                                                if count >= 2 and c >= 1:
                                                    if c < countRange[-1]:
                                                        indicesForRemoval.append(index)
                                                index += 1

                                            if count > 1:
                                                previousGroupWasBoring = True
                                            else:
                                                previousGroupWasBoring = False

                                        for i in sorted(indicesForRemoval, reverse=True):
                                            cmds.cutKey(curveNode, index=tuple([i, i]))

                                        if not leaveFirstKey:
                                            timesValues = []
                                            try:
                                                timesValues = cmds.getAttr('{0}.{1}'.format(curveNode, 'keyTimeValue[:]'))
                                            except:
                                                pass

                                            if timesValues and len(timesValues) == 1:
                                                cmds.cutKey(curveNode)
                                        removalStats['keysRemoved'] += len(indicesForRemoval)

            except:
                pass
            finally:
                cmds.progressBar(gMainProgressBar, edit=True, endProgress=True)

            print ('ebLabs_whisKEY:Remove Boring Keys Info:', removalStats)

    @classmethod
    def removeBoringKeysPrompt(cls, message):
        form = cmds.setParent(query=True)
        cmds.formLayout(form, e=True, width=300)
        text = cmds.text(l=message)
        checkbox = cmds.checkBox(label='Leave first keys?', value=True)

        def dismiss(value, *args, **kwargs):
            if value == 'True':
                checkboxValue = cmds.checkBox(checkbox, query=True, value=True)
                if checkboxValue:
                    value = 'TrueLeaveFirst'
                else:
                    value = 'TrueLeaveNone'
            cmds.layoutDialog(dismiss=value)

        trueButton = cmds.button(l='Yes', c=partial(dismiss, 'True'))
        falseButton = cmds.button(l='No', c=partial(dismiss, 'Cancel'))
        padding = 10
        cmds.formLayout(form, edit=True, attachForm=[(text, 'top', padding)])
        cmds.formLayout(form, edit=True, attachForm=[(text, 'left', 0)])
        cmds.formLayout(form, edit=True, attachNone=[(text, 'bottom')])
        cmds.formLayout(form, edit=True, attachForm=[(text, 'right', 0)])
        cmds.formLayout(form, edit=True, attachControl=[(checkbox,
          'top',
          padding,
          text)])
        cmds.formLayout(form, edit=True, attachForm=[(checkbox, 'left', padding)])
        cmds.formLayout(form, edit=True, attachNone=[(checkbox, 'bottom')])
        cmds.formLayout(form, edit=True, attachForm=[(checkbox, 'right', 0)])
        cmds.formLayout(form, edit=True, attachControl=[(falseButton,
          'top',
          padding,
          checkbox)])
        cmds.formLayout(form, edit=True, attachForm=[(falseButton, 'left', padding)])
        cmds.formLayout(form, edit=True, attachNone=[(falseButton, 'bottom')])
        cmds.formLayout(form, edit=True, attachPosition=[(falseButton,
          'right',
          padding,
          50)])
        cmds.formLayout(form, edit=True, attachControl=[(trueButton,
          'top',
          padding,
          checkbox)])
        cmds.formLayout(form, edit=True, attachControl=[(trueButton,
          'left',
          padding,
          falseButton)])
        cmds.formLayout(form, edit=True, attachNone=[(trueButton, 'bottom')])
        cmds.formLayout(form, edit=True, attachForm=[(trueButton, 'right', padding)])

    @classmethod
    def getAttributeType(cls, controlObject, attribute):
        if cmds.objExists(controlObject):
            if attribute in cmds.attributeInfo(controlObject, enumerated=True):
                return 'enum'
            if attribute in cmds.attributeInfo(controlObject, bool=True):
                return 'bool'
            if attribute in cmds.attributeInfo(controlObject, allAttributes=True):
                return 'other'
        return False

    @classmethod
    def findMatchingObjectsInNamespace(cls, *args, **kwargs):
        node = False
        if 'node' in kwargs:
            node = kwargs.pop('node')
        namespaces = False
        if 'namespaces' in kwargs:
            namespaces = kwargs.pop('namespaces')
        matchingNodes = []
        nodeNamespace = Functions.getNamespaces(nodes=[node])[0]
        for ns in namespaces:
            potentialNode = node.replace(nodeNamespace, ns)
            if cmds.objExists(potentialNode):
                matchingNodes.append(potentialNode)

        return matchingNodes

    @classmethod
    def getNamespaces(cls, *args, **kwargs):
        nodes = False
        if 'nodes' in kwargs:
            nodes = kwargs.pop('nodes')
        namespaces = []
        if nodes:
            for n in nodes:
                n = n.split('|')[-1]
                n = n.split(':')
                del n[-1]
                n = ':'.join(n)
                namespaces.append(n)

        return namespaces

    @classmethod
    def setKeyType(cls, keyType, *args, **kwargs):
        outTangent = keyType
        inTangent = keyType
        selection = cmds.ls(sl=True)
        if keyType == 'auto' or keyType == 'spline' or keyType == 'clamped' or keyType == 'step' or keyType == 'linear' or keyType == 'flat' or keyType == 'plateau':
            if inTangent == 'step':
                inTangent = 'linear'
            mel.eval('keyTangent -global -itt {0};'.format(inTangent))
            mel.eval('keyTangent -global -ott {0};'.format(outTangent))
            if selection:
                cmds.keyTangent(selection, outTangentType=outTangent)
                if inTangent != 'step':
                    cmds.keyTangent(selection, inTangentType=inTangent)
        elif keyType == 'free':
            cmds.keyTangent(g=True, edit=True, weightedTangents=True)
            if selection:
                cmds.keyTangent(selection, animation='objects', edit=True, weightedTangents=True)
                cmds.keyTangent(selection, animation='objects', edit=True, weightLock=False)

    @classmethod
    def listAttributes(cls, node, *args, **kwargs):
        filterEnums = True
        if 'filterEnums' in kwargs:
            filterEnums = kwargs.pop('filterEnums')
        attributes = []
        keyableAttributes = cmds.listAttr(node, keyable=True, unlocked=True, scalar=True, visible=True, shortNames=True)
        if keyableAttributes:
            for a in keyableAttributes:
                try:
                    isEnum = False
                    if cmds.attributeQuery(a, node=node, enum=True):
                        isEnum = True
                    if filterEnums and isEnum:
                        continue
                except:
                    pass

                attributes.append(a)

        return attributes

    @classmethod
    def getRelativePosition(cls, node, attribute, time, *args, **kwargs):
        allKeys = cmds.keyframe(node, query=True, at=attribute)
        if allKeys:
            allKeys = sorted(allKeys)
            firstKeytime = allKeys[0]
            lastKeyTime = allKeys[-1]
            if time == firstKeytime:
                relativePosition = 'First'
                return relativePosition
            elif time == lastKeyTime:
                relativePosition = 'Last'
                return relativePosition
            elif time < firstKeytime:
                relativePosition = 'Before'
                return relativePosition
            elif time > lastKeyTime:
                relativePosition = 'After'
                return relativePosition
            elif time in allKeys:
                relativePosition = 'OnKey'
                return relativePosition
            else:
                relativePosition = 'InKeys'
                return relativePosition

    @classmethod
    def isOnKey(cls, node, attribute, time):
        allKeys = cmds.keyframe(node, query=True, at=attribute)
        if time in allKeys:
            return True
        else:
            return False

    @classmethod
    def getKeyFrameAtOffsetInfo(cls, node, attribute, offset, *args, **kwargs):
        offsetTime = False
        offsetValue = False
        currentFrame = cmds.currentTime(query=True)
        relativePosition = Functions.getRelativePosition(node, attribute, currentFrame)
        sourceKeys = cmds.keyframe(node, query=True, at=attribute)
        referenceKeys = list(sourceKeys)
        if currentFrame not in referenceKeys:
            referenceKeys.append(currentFrame)
            referenceKeys = sorted(referenceKeys)
        currentKeyIndex = referenceKeys.index(currentFrame)
        indexLookup = currentKeyIndex + offset
        indexLookup = int(Functions.clamp(indexLookup, 0, len(referenceKeys) - 1))
        offsetTime = referenceKeys[indexLookup]
        offsetTime = Functions.clamp(offsetTime, min(sourceKeys), max(sourceKeys))
        localIndex = sourceKeys.index(offsetTime)
        offsetTime = cmds.keyframe(node, query=True, at=attribute, index=(localIndex, localIndex))[0]
        offsetValue = cmds.getAttr('{0}.{1}'.format(node, attribute), time=offsetTime)
        return (offsetTime, offsetValue)

    @classmethod
    def getBoundingBoxSize(node, *args, **kwargs):
        radius = 0
        if cmds.objExists(node):
            objectType = cmds.objectType(node)
            if objectType == 'joint':
                radius = cmds.getAttr(node + '.radius') * 2
            else:
                boundingBox = cmds.exactWorldBoundingBox(node, ignoreInvisible=True)
                dimensions = [abs(boundingBox[0] - boundingBox[3]), abs(boundingBox[1] - boundingBox[4]), abs(boundingBox[2] - boundingBox[5])]
                radius = sum(dimensions) / 3
        if radius > 0.0001:
            return radius
        else:
            return 1

    @classmethod
    def getAverageBoundingBoxSize(cls, nodes, *args, **kwargs):
        averageSize = False
        if nodes:
            averageSize = 0
            runningSum = 0
            for n in nodes:
                runningSum += cls.getBoundingBoxSize(n)

            averageSize = runningSum / len(nodes)
        return averageSize

    @classmethod
    def getActiveCamera(cls, *args, **kwargs):
        modelPanel = cmds.getPanel(withFocus=True)
        cameraName = None
        cameraShape = None
        isCameraPanel = False
        try:
            cameraName = cmds.modelEditor(modelPanel, query=True, camera=True)
            if cmds.objectType(cameraName) == 'transform':
                shapeCheck = cmds.listRelatives(cameraName, shapes=True, fullPath=True)[0]
                if cmds.objectType(shapeCheck) == 'camera':
                    cameraShape = shapeCheck
            elif cmds.objectType(cameraName) == 'camera':
                cameraShape = cameraName
                cameraName = cmds.listRelatives(cameraShape, parent=True, fullPath=True)[0]
            if cmds.objectType(cameraShape) == 'camera':
                isCameraPanel = True
        except:
            pass

        return cameraName

    @classmethod
    def setVersion(cls, version):
        cls.version = version

    @classmethod
    def getVersion(cls):
        return cls.version

    @classmethod
    def loadDataFromFile(cls, filename, *args, **kwargs):
        data = None
        try:
            filePath = open(filename, 'r')
            data = json.loads(filePath.read())
            filePath.close()
        except:
            pass

        return data

    @classmethod
    def writeDataToFile(cls, filePath, dictionary):
        filePathRoot = os.path.split(filePath)[0]
        if not os.path.exists(filePathRoot):
            os.makedirs(filePathRoot)
        fileObject = open(filePath, 'w')
        data = json.dumps(dictionary, sort_keys=True, indent=4)
        fileObject.write(data)
        fileObject.close()

    @classmethod
    def clearPrefs(cls, *args, **kwargs):
        profile = False
        if 'profile' in kwargs:
            profile = kwargs.pop('profile')
        profilesData = cls.getProfilesData()
        profilesData[profile] = {}
        cls.setProfilesData(profilesData)
        widgetData = []
        cls.storePrefs(widgetData, profile=profile)

    @classmethod
    def retreivePrefs(cls, *args, **kwargs):
        profile = False
        if 'profile' in kwargs:
            profile = kwargs.pop('profile')
        try:
            data = cls.loadDataFromFile(cls.prefsFilepath)
            activeProfile = data['activeProfile']
            if profile:
                activeProfile = profile
            profilesData = data['data']
            cls.setActiveProfile(activeProfile)
            cls.setProfilesData(profilesData)
            widgetData = profilesData[activeProfile]['data']
            version = profilesData[activeProfile]['version']
            return (version, widgetData)
        except:
            return (False, False)

    @classmethod
    def storePrefs(cls, widgetData, *args, **kwargs):
        command = partial(cls.storePrefs_deferred, widgetData)
        cmds.evalDeferred(command)

    @classmethod
    def storePrefs_deferred(cls, widgetData, *args, **kwargs):
        profile = cls.getActiveProfile()
        if 'profile' in kwargs:
            profile = kwargs.pop('profile')
        profilesData = cls.getProfilesData()
        try:
            profilesData[profile]
        except:
            profilesData[profile] = {}

        try:
            profilesData[profile]['data']
        except Exception as e:
            print (868, e)
            print (863,
             'profilesData',
             type(profilesData),
             profilesData)
            print (863,
             'profilesData[profile]',
             type(profilesData[profile]),
             profilesData[profile])
            print (864,
             'profile',
             type(profile),
             profile)
            profilesData[profile]['data'] = {}

        profilesData[profile]['data'] = widgetData
        profilesData[profile]['version'] = cls.getVersion()
        cls.setProfilesData(profilesData)
        data = cls.loadDataFromFile(cls.prefsFilepath)
        try:
            data
        except:
            data = {}

        data['data'] = profilesData
        data['version'] = cls.getVersion()
        data['activeProfile'] = profile
        cls.writeDataToFile(cls.prefsFilepath, data)

    @classmethod
    def worldToLocalPoint(cls, point, node):
        matrix = cmds.getAttr(node + '.parentInverseMatrix')
        localPointX = point[0] * matrix[0] + point[1] * matrix[4] + point[2] * matrix[8] + matrix[12]
        localPointY = point[0] * matrix[1] + point[1] * matrix[5] + point[2] * matrix[9] + matrix[13]
        localPointZ = point[0] * matrix[2] + point[1] * matrix[6] + point[2] * matrix[10] + matrix[14]
        return [localPointX, localPointY, localPointZ]

    @classmethod
    def decompMatrix(cls, node, matrix):
        """
        Decomposes a MMatrix in new api. Returns an list of translation,rotation,scale in world space.
        """
        rotOrder = cmds.getAttr('{0}.rotateOrder'.format(node))
        mTransformMtx = OpenMaya.MTransformationMatrix(matrix)
        trans = mTransformMtx.translation(OpenMaya.MSpace.kWorld)
        eulerRot = mTransformMtx.rotation()
        eulerRot.reorderIt(rotOrder)
        angles = [ math.degrees(angle) for angle in (eulerRot.x, eulerRot.y, eulerRot.z) ]
        scale = mTransformMtx.scale(OpenMaya.MSpace.kWorld)
        return [trans.x, trans.y, trans.z] + angles + scale

    @classmethod
    def rekeyOnKeys(cls, *args, **kwargs):
        objects = None
        if 'objects' in kwargs:
            objects = kwargs.pop('objects')
        matchLast = False
        if 'matchLast' in kwargs:
            matchLast = kwargs.pop('matchLast')
        try:
            if objects:
                currentTime = cmds.currentTime(query=True)
                highlightedChannels = Functions.getSelectedChannels()
                if not highlightedChannels:
                    highlightedChannels = None
                specialKeyTimeTemplateObjects = objects
                keyTimeTemplateObjects = objects
                if matchLast:
                    specialKeyTimeTemplateObjects = objects[-1:]
                    keyTimeTemplateObjects = objects[-1:]
                specialKeyTickTimes = cls.getSpecialKeyTickTimes(objects=specialKeyTimeTemplateObjects)
                keyTimes = []
                keyTimes = cmds.keyframe(keyTimeTemplateObjects, query=True, attribute=highlightedChannels)
                if keyTimes:
                    keyTimes = list(set(keyTimes))
                allKeyTimes = []
                allKeyTimes = cmds.keyframe(objects, query=True, attribute=None)
                if allKeyTimes:
                    allKeyTimes = list(set(allKeyTimes))
                objectsToProcess = objects
                if matchLast:
                    if objectsToProcess and len(objectsToProcess) == 1:
                        objectsToProcess = objects
                    else:
                        objectsToProcess = objects[:-1]
                highlightedRange = cls.getHighlightedRange()
                if highlightedRange:
                    trimmed = []
                    for f in keyTimes:
                        if highlightedRange[0] <= f <= highlightedRange[1]:
                            trimmed.append(f)

                    keyTimes = sorted(trimmed)
                cls.suspendUI(True)
                for f in keyTimes:
                    cmds.currentTime(f, edit=True)
                    if matchLast or not highlightedChannels:
                        cmds.setKeyframe(objectsToProcess)
                    else:
                        cmds.setKeyframe(objectsToProcess, attribute=highlightedChannels)

                for f in specialKeyTickTimes:
                    cmds.keyframe(objectsToProcess, time=(f, f), tickDrawSpecial=True, animation='objects', attribute=highlightedChannels)

                if matchLast:
                    for f in allKeyTimes:
                        if f not in keyTimes:
                            cmds.cutKey(objectsToProcess, time=(f, f), clear=True)

                cmds.currentTime(currentTime, edit=True)
        finally:
            cls.suspendUI(False)

        return

    @classmethod
    def getSpecialKeyTickTimes(cls, *args, **kwargs):
        objects = None
        if 'objects' in kwargs:
            objects = kwargs.pop('objects')
        if objects:
            specialKeyTicks = []
            for s in objects:
                keyableAttributes = cmds.listAttr(s, keyable=True, unlocked=True, scalar=True, visible=True)
                if not keyableAttributes:
                    return specialKeyTicks
                for a in keyableAttributes:
                    attribute = '{0}.{1}'.format(s, a)
                    keyframeCount = cmds.keyframe(attribute, query=True)
                    if keyframeCount:
                        curveNode = cmds.keyframe(attribute, query=True, name=True)[0]
                        keyFrameList = cmds.keyframe(curveNode, query=True)
                        uncheckedFrames = list(set(keyFrameList) - set(specialKeyTicks))
                        for f in uncheckedFrames:
                            index = keyFrameList.index(f)
                            querySpecialKeyTick = cmds.getAttr('{0}.kyts[{1}]'.format(curveNode, index))
                            if querySpecialKeyTick:
                                specialKeyTicks.append(f)

            return specialKeyTicks
        else:
            return

    @classmethod
    def setKeyframe(cls, *args, **kwargs):
        objects = None
        if 'objects' in kwargs:
            objects = kwargs.pop('objects')
        special = None
        if 'special' in kwargs:
            special = kwargs.pop('special')
        useHighlighted = True
        if 'useHighlighted' in kwargs:
            useHighlighted = kwargs.pop('useHighlighted')
        highlightedChannels = False
        if useHighlighted:
            highlightedChannels = Functions.getSelectedChannels(objects)
        if objects:
            if highlightedChannels:
                cmds.setKeyframe(objects, attribute=highlightedChannels)
            else:
                cmds.setKeyframe(objects)
        if special:
            currentTime = cmds.currentTime(query=True)
            cmds.keyframe(objects, time=(currentTime, currentTime), tickDrawSpecial=True, animation='objects')
        return

    @classmethod
    def validateText(cls, text, *args, **kwargs):
        if not text:
            return False
        validCharacters = '-_.(){0}{1}'.format(string.ascii_letters, string.digits)
        validatedCharacters = []
        for c in text:
            if c == ' ':
                c = '_'
            if c in validCharacters:
                validatedCharacters.append(c)

        validatedText = ''.join(validatedCharacters)
        return validatedText

    @classmethod
    def getStringFromUser(cls):
        description = False
        result = cmds.promptDialog(title='Enter Text', message='Enter Text:', button=['OK', 'Cancel'], defaultButton='OK', cancelButton='Cancel', dismissString='Cancel', text='')
        if result == 'OK':
            query = cmds.promptDialog(query=True, text=True)
            validateText = Functions.validateText(query)
            if validateText:
                description = validateText
        return description

    @classmethod
    def getDescription(cls):
        description = False
        result = cmds.promptDialog(title='Share Folder Description', message='Enter Description:', button=['OK', 'Cancel'], defaultButton='OK', cancelButton='Cancel', dismissString='Cancel', text='')
        if result == 'OK':
            query = cmds.promptDialog(query=True, text=True)
            validateText = Functions.validateText(query)
            if validateText:
                description = validateText
        return description

    @classmethod
    def clamp(cls, n, minn, maxn):
        return max(min(maxn, n), minn)

    @classmethod
    def getSelectedChannels(cls, selection = False):
        if not selection:
            selection = cmds.ls(sl=True, type=['transform', 'joint'])
        if selection:
            selectedChannels = cmds.channelBox('mainChannelBox', query=True, selectedMainAttributes=True)
            if not selectedChannels:
                return None
            return selectedChannels
        else:
            return None

    @classmethod
    def suspendUI(cls, state, *args, **kwargs):
        try:
            cmds.undoInfo(stateWithoutFlush=False)
            cls.suspendUI_wrapped(state, *args, **kwargs)
        except Exception as e:
            print (Exception, e)
            cmds.warning('Suspend UI Failed')
        finally:
            cmds.undoInfo(stateWithoutFlush=True)

    @classmethod
    def suspendUI_wrapped(cls, state):
        if state == True:
            try:
                selected = cmds.ls(sl=True)
                allPanels = cmds.getPanel(type='modelPanel')
                cmds.select(clear=True)
                cls.suspendIsolatedObjects = {}
                for panel in allPanels:
                    viewSet = cmds.isolateSelect(panel, q=True, viewObjects=True)
                    setMembers = False
                    if viewSet:
                        setMembers = cmds.sets(viewSet, q=True)
                        cls.suspendIsolatedObjects[panel] = setMembers
                    cmds.isolateSelect(panel, state=1)

                cmds.select(selected)
                mel.eval('paneLayout -e -manage false $gMainPane')
            except Exception as e:
                print (1137, e)
                cmds.warning('Suspend UI Not Activating Properly Mate.')
                mel.eval('paneLayout -e -manage true $gMainPane')
                allPanels = cmds.getPanel(type='modelPanel')
                for panel in allPanels:
                    cmds.isolateSelect(panel, state=False)

        if state == False:
            mel.eval('paneLayout -e -manage true $gMainPane')
            allPanels = cmds.getPanel(type='modelPanel')
            for panel in allPanels:
                cmds.isolateSelect(panel, state=False)
                try:
                    if panel in cls.suspendIsolatedObjects.keys():
                        if cls.suspendIsolatedObjects[panel]:
                            cmds.isolateSelect(panel, state=True)
                            for n in cls.suspendIsolatedObjects[panel]:
                                cmds.isolateSelect(panel, addDagObject=n)

                except Exception as e:
                    print (1292, e)


class widget_base():
    """ Define Common Functions for widgets
    """
    instances = []

    def __init__(self, *args, **kwargs):
        parent = self.getWidgetParent()
        description = 'Inbetween'
        if 'description' in kwargs:
            description = kwargs.pop('description')
        expandedState = True
        if 'expandedState' in kwargs:
            expandedState = kwargs.pop('expandedState')
        self.instances.append(self)
        labelVisible = False
        collapsable = False
        collapse = False
        if not expandedState:
            labelVisible = True
            collapsable = True
            collapse = True
        self.mainContainer = cmds.frameLayout(parent=parent, labelVisible=labelVisible, collapsable=collapsable, collapse=collapse)
        cmds.frameLayout(self.mainContainer, edit=True, expandCommand=partial(self.expandMainContainer))
        formattingLayout = cmds.formLayout(parent=self.mainContainer)
        self.formLayout = cmds.formLayout(parent=formattingLayout, bgc=[0.95] * 3)
        spacerFormlayout = cmds.formLayout(parent=formattingLayout, height=2, bgc=[0.95] * 3)
        cmds.formLayout(formattingLayout, edit=True, attachForm=[(self.formLayout, 'top', 0)])
        cmds.formLayout(formattingLayout, edit=True, attachForm=[(self.formLayout, 'left', 0)])
        cmds.formLayout(formattingLayout, edit=True, attachNone=[(self.formLayout, 'bottom')])
        cmds.formLayout(formattingLayout, edit=True, attachForm=[(self.formLayout, 'right', 0)])
        cmds.formLayout(formattingLayout, edit=True, attachControl=[(spacerFormlayout,
          'top',
          0,
          self.formLayout)])
        cmds.formLayout(formattingLayout, edit=True, attachForm=[(spacerFormlayout, 'left', 0)])
        cmds.formLayout(formattingLayout, edit=True, attachNone=[(spacerFormlayout, 'bottom')])
        cmds.formLayout(formattingLayout, edit=True, attachForm=[(spacerFormlayout, 'right', 0)])
        popupMenu = cmds.popupMenu(parent=self.mainContainer)
        cmds.popupMenu(popupMenu, edit=True, postMenuCommand=partial(self.widgetMenu, parent=popupMenu))
        self.data = {}
        self.widgetType = ''
        self.widgetState = ''
        self.enableSlider = True

    @classmethod
    def clearInstances(cls):
        cls.instances = []

    def multiplierChangeUpdateText(self, *args, **kwargs):
        sliderWidget = False
        if 'sliderWidget' in kwargs:
            sliderWidget = kwargs.pop('sliderWidget')
        element = False
        if 'element' in kwargs:
            element = kwargs.pop('element')
        value = sliderWidget.getMultiplier()
        text = '{0:.2f}x'.format(value)
        self.setTextLabel(element, text)

    def setTextLabel(self, element, text, *args, **kwargs):
        cmds.text(element, edit=True, label=text)

    @classmethod
    def addItem(cls, addItem, *args, **kwargs):
        parent = cls.getWidgetParent()
        if addItem == 'inbetween':
            newItem = widget_tween(parent=parent)
        if addItem == 'extras':
            newItem = widget_extras(parent=parent)
        if addItem == 'worldSpace':
            newItem = widget_worldSpace(parent=parent)
        if addItem == 'curveOptions':
            newItem = widget_curveOptions(parent=parent)
        if addItem == 'snapshot':
            newItem = widget_snapshot(parent=parent)
        if addItem == 'principles':
            newItem = widget_principles(parent=parent)
        if addItem == 'classic':
            newItem = widget_classic(parent=parent)
        if addItem == 'tools':
            newItem = widget_tools(parent=parent)
        cls.storePrefs()
        window.resizeUI()

    @classmethod
    def getWidgetParent(cls, *args, **kwargs):
        try:
            cls.widgetParent
        except:
            cls.widgetParent = False

        return cls.widgetParent

    @classmethod
    def setWidgetParent(cls, parent, *args, **kwargs):
        cls.widgetParent = parent

    def addPostCommand(self, command, *args, **kwargs):
        try:
            self.postCommands
        except:
            self.postCommands = []

        if command:
            self.postCommands.append(command)

    def clearPostCommands(self, *args, **kwargs):
        self.postCommands = []

    def onPost(self, *args, **kwargs):
        try:
            self.postCommands
        except:
            self.postCommands = []

        for c in self.postCommands:
            c()

    def addPreCommand(self, command, *args, **kwargs):
        try:
            self.preCommands
        except:
            self.preCommands = []

        if command:
            self.preCommands.append(command)

    def clearPreCommands(self, *args, **kwargs):
        self.preCommands = []

    def onPre(self, *args, **kwargs):
        try:
            self.preCommands
        except:
            self.preCommands = []

        for c in self.preCommands:
            c()

    def addChangeCommand(self, command, *args, **kwargs):
        try:
            self.changeCommands
        except:
            self.changeCommands = []

        if command:
            self.changeCommands.append(command)

    def clearChangeCommands(self, *args, **kwargs):
        self.changeCommands = []

    def onChange(self, debug = False, *args, **kwargs):
        if debug:
            print (debug, len(self.changeCommands))
        try:
            self.changeCommands
        except Exception as e:
            self.changeCommands = []

        for c in self.changeCommands:
            c()

    def rekeyOnKeys(self, *args, **kwargs):
        matchLast = False
        if 'matchLast' in kwargs:
            matchLast = kwargs.pop('matchLast')
        objects = self.getSelected()
        Functions.rekeyOnKeys(objects=objects, matchLast=matchLast)

    def setKeyframe(self, *args, **kwargs):
        special = False
        if 'special' in kwargs:
            special = kwargs.pop('special')
        objects = self.getSelected()
        Functions.setKeyframe(objects=objects, special=special)

    def setKeysPopupMenu(self, *args, **kwargs):
        parent = False
        if 'parent' in kwargs:
            parent = kwargs.pop('parent')
        special = False
        if 'special' in kwargs:
            special = kwargs.pop('special')
        cmds.popupMenu(parent, edit=True, deleteAllItems=True)
        cmds.setParent(parent, menu=True)
        specialString = ''
        cmds.menuItem(parent=parent, label='Rekey Selection' + specialString, command=partial(self.rekeyOnKeys))
        cmds.menuItem(parent=parent, label='Rekey To Match Last Selected' + specialString, command=partial(self.rekeyOnKeys, matchLast=True))

    def expandMainContainer(self, *args, **kwargs):
        cmds.frameLayout(self.mainContainer, edit=True, labelVisible=False, collapsable=False, collapse=False)
        window.resizeUI()
        self.storePrefs()

    def moveWidget(self, direction, *args, **kwargs):
        index = self.getInstanceIndex()
        instances = self.getInstances()
        instancesCount = len(instances)
        newIndex = int(Functions.clamp(index + direction, 0, instancesCount))
        popped = instances.pop(index)
        instances.insert(newIndex, popped)
        self.setInstances(instances)
        self.storePrefs()
        currentProfile = Functions.getActiveProfile()
        self.switchToProfile(currentProfile)

    def collapseMainContainer(self, *args, **kwargs):
        cmds.frameLayout(self.mainContainer, edit=True, labelVisible=True, collapsable=True, collapse=True)
        window.resizeUI()
        self.storePrefs()

    def getWidgetExpandedState(self, *args, **kwargs):
        state = cmds.frameLayout(self.mainContainer, query=True, collapse=True)
        return not state

    def getInstanceIndex(self, *args, **kwargs):
        index = self.instances.index(self)
        return index

    def widgetMenu(self, *args, **kwargs):
        parent = False
        if 'parent' in kwargs:
            parent = kwargs.pop('parent')
        cmds.popupMenu(parent, edit=True, deleteAllItems=True)
        cmds.setParent(parent, menu=True)
        description = self.getDescription()
        toolsSubmenu = cmds.menuItem(parent=parent, subMenu=True, label='Tools')
        cmds.menuItem(parent=toolsSubmenu, label='Rekey Selection', command=partial(self.rekeyOnKeys))
        cmds.menuItem(parent=toolsSubmenu, label='Rekey To Match Last Selected', command=partial(self.rekeyOnKeys, matchLast=True))
        cmds.menuItem(parent=toolsSubmenu, divider=True)
        cmds.menuItem(parent=toolsSubmenu, label='Clean Subframe Keys', command=partial(self.cleanSubframeKeys))
        cmds.menuItem(parent=toolsSubmenu, label='Remove Boring Keys', command=partial(self.removeBoringKeys, regions=False))
        cmds.menuItem(parent=toolsSubmenu, divider=True)
        startTime, endTime = Functions.queryTimeRange()
        selected = cmds.ls(sl=True)
        label = 'Smash Bake: {0}-{1}'.format(startTime, endTime)
        cmds.menuItem(parent=toolsSubmenu, label=label, command=partial(Functions.smashBaker, selected, startTime, endTime))
        profilesMenu = cmds.menuItem(parent=parent, subMenu=True, label='Profiles')
        cmds.menuItem(profilesMenu, edit=True, postMenuCommand=partial(self.profilesMenuPostCommand, parent=profilesMenu))
        widgetCollapseState = self.getWidgetExpandedState()
        cmds.menuItem(parent=parent, label='/\\ (move up)', command=partial(self.moveWidget, -1))
        cmds.menuItem(parent=parent, label='\\/ (move down)', command=partial(self.moveWidget, 1))
        cmds.menuItem(parent=parent, label='Collapse Widget', command=partial(self.collapseMainContainer), enable=widgetCollapseState)
        cmds.menuItem(parent=parent, divider=True)
        addWidgetsSubmenu = cmds.menuItem(parent=parent, subMenu=True, label='Add Widget')
        cmds.menuItem(parent=addWidgetsSubmenu, label='Add Classic Widget', command=partial(self.addItem, 'classic'))
        cmds.menuItem(parent=addWidgetsSubmenu, label='Add Inbetween Widget', command=partial(self.addItem, 'inbetween'))
        cmds.menuItem(parent=addWidgetsSubmenu, label='Add World Space Widget', command=partial(self.addItem, 'worldSpace'))
        cmds.menuItem(parent=addWidgetsSubmenu, label='Add Extras Widget', command=partial(self.addItem, 'extras'))
        cmds.menuItem(parent=addWidgetsSubmenu, label='Add Snapshot Widget', command=partial(self.addItem, 'snapshot'))
        cmds.menuItem(parent=addWidgetsSubmenu, divider=True)
        cmds.menuItem(parent=addWidgetsSubmenu, label='Add Tools Widget', command=partial(self.addItem, 'tools'))
        cmds.menuItem(parent=addWidgetsSubmenu, label='Add Options Widget', command=partial(window.addItem, 'curveOptions'))
        cmds.menuItem(parent=addWidgetsSubmenu, label='Add Animation Principles', command=partial(window.addItem, 'principles'))
        cmds.menuItem(parent=parent, label='Remove Widget: ' + description, command=partial(self.removeWidget))
        cmds.menuItem(parent=parent, divider=True)
        advancedSubmenu = cmds.menuItem(parent=parent, subMenu=True, label='Advanced')
        storeWindowPosition = Prefs.getPrefsKey('storeWindowPosition')
        command = partial(self.toggleStoreWindowPosition)
        cmds.menuItem(parent=advancedSubmenu, label='Store Window Positions', command=command, checkBox=storeWindowPosition)
        cmds.menuItem(parent=advancedSubmenu, label='Resize UI', command=partial(window.resizeUI))
        activeProfile = Functions.getActiveProfile()
        cmds.menuItem(parent=advancedSubmenu, label='Reset "{0}" Prefs'.format(activeProfile), command=partial(window.resetPrefs, profile=activeProfile))
        cmds.menuItem(parent=advancedSubmenu, label='Print Widget Info', command=partial(self.printInfo))

    def toggleStoreWindowPosition(self, *args, **kwargs):
        state = args[0]
        Prefs.setPrefsKey('storeWindowPosition', state)

    def profilesMenuPostCommand(self, *args, **kwargs):
        parent = False
        if 'parent' in kwargs:
            parent = kwargs.pop('parent')
        cmds.popupMenu(parent, edit=True, deleteAllItems=True)
        cmds.menuItem(parent=parent, label='New Profile', command=partial(self.createNewProfile))
        cmds.menuItem(parent=parent, divider=True)
        currentProfile = Prefs.getPrefsKey('activeProfile')
        profiles = Prefs.listProfiles()
        for p in profiles:
            cmds.menuItem(parent=parent, label='Switch To: ' + p, enable=not p == currentProfile, command=partial(self.switchToProfile, p))

        cmds.menuItem(parent=parent, divider=True)
        profilesRemove = cmds.menuItem(parent=parent, subMenu=True, label='Remove Profile')
        for p in profiles:
            cmds.menuItem(parent=profilesRemove, label='Remove: ' + p, enable=not p == currentProfile, command=partial(self.removeProfile, p))

    def switchToProfile(self, profile, *args, **kwargs):
        command = partial(self.switchToProfile_deferred, profile)
        cmds.evalDeferred(command)

    def switchToProfile_deferred(self, profile, *args, **kwargs):
        instances = self.getInstances()
        self.clearWidgets(instances=instances)
        Prefs.setPrefsKey('activeProfile', profile)
        self.addWidgetsFromPrefs(profile=profile)

    @classmethod
    def addWidgetsFromPrefs(cls, *args, **kwargs):
        profile = False
        if 'profile' in kwargs:
            profile = kwargs.pop('profile')
        widgetData = Prefs.getProfileData(profile=profile)
        if not widgetData:
            widgetData = cls.getDefaultWidgetData()
        parent = cls.getWidgetParent()
        for w in widgetData:
            widgetDescription = w['description']
            widgetType = w['widgetType']
            widgetState = w['state']
            widgetExpandedState = True
            try:
                widgetExpandedState = w['expanded']
            except:
                pass

            if widgetType == 'inbetween':
                newItem = widget_tween(parent=parent, description=widgetDescription, expandedState=widgetExpandedState, stateData=widgetState)
            if widgetType == 'extras':
                newItem = widget_extras(parent=parent, description=widgetDescription, expandedState=widgetExpandedState, stateData=widgetState)
            if widgetType == 'worldSpace':
                newItem = widget_worldSpace(parent=parent, description=widgetDescription, expandedState=widgetExpandedState, stateData=widgetState)
            if widgetType == 'classic':
                newItem = widget_classic(parent=parent, description=widgetDescription, expandedState=widgetExpandedState, stateData=widgetState)
            if widgetType == 'curveOptions':
                newItem = widget_curveOptions(parent=parent, description=widgetDescription, expandedState=widgetExpandedState, stateData=widgetState)
            if widgetType == 'snapshot':
                newItem = widget_snapshot(parent=parent, description=widgetDescription, expandedState=widgetExpandedState, stateData=widgetState)
            if widgetType == 'principles':
                newItem = widget_principles(parent=parent, description=widgetDescription, expandedState=widgetExpandedState, stateData=widgetState)
            if widgetType == 'tools':
                newItem = widget_tools(parent=parent, description=widgetDescription, expandedState=widgetExpandedState, stateData=widgetState)

    @classmethod
    def getDefaultWidgetData(cls, *args, **kwargs):
        widgetData = []
        data = {}
        data['widgetType'] = 'principles'
        data['description'] = 'Animation Principles'
        data['expanded'] = False
        data['state'] = {}
        data['state']['pinState'] = False
        data['state']['bufferSelection'] = []
        data = {}
        data['widgetType'] = 'classic'
        data['description'] = 'Classic'
        data['expanded'] = True
        data['state'] = {}
        data['state']['pinState'] = False
        data['state']['bufferSelection'] = []
        widgetData.append(data)
        data = {}
        data['widgetType'] = 'inbetween'
        data['description'] = 'Inbetween'
        data['expanded'] = True
        data['state'] = {}
        data['state']['pinState'] = False
        data['state']['bufferSelection'] = []
        data = {}
        data['widgetType'] = 'extras'
        data['description'] = 'Extras'
        data['expanded'] = True
        data['state'] = {}
        data['state']['pinState'] = False
        data['state']['bufferSelection'] = []
        data = {}
        data['widgetType'] = 'worldSpace'
        data['description'] = 'World Space'
        data['expanded'] = False
        data['state'] = {}
        data['state']['pinState'] = False
        data['state']['bufferSelection'] = []
        data = {}
        data['widgetType'] = 'snapshot'
        data['description'] = 'Snapshot'
        data['expanded'] = False
        data['state'] = {}
        data['state']['pinState'] = False
        data['state']['bufferSelection'] = []
        data = {}
        data['widgetType'] = 'curveOptions'
        data['description'] = 'Curve Options'
        data['expanded'] = False
        data['state'] = {}
        data['state']['pinState'] = False
        data['state']['bufferSelection'] = []
        widgetData.append(data)
        data = {}
        data['widgetType'] = 'tools'
        data['description'] = 'Tools'
        data['expanded'] = False
        data['state'] = {}
        data['state']['pinState'] = False
        data['state']['bufferSelection'] = []
        return widgetData

    @classmethod
    def clearWidgets(cls, *args, **kwargs):
        instances = cls.getInstances()
        if 'instances' in kwargs:
            instances = kwargs.pop('instances')
        for i in instances:
            i.removeWidget(storePrefs=False)

    def removeProfile(self, profile, *args, **kwargs):
        Prefs.removeProfile(profile)
        self.storePrefs()

    def createNewProfile(self, *args, **kwargs):
        profile = Functions.getStringFromUser()
        if profile:
            profile = str(profile)
            data = self.getCurrentState()
            Prefs.setProfileData(profile=profile, profileData=data)
            self.storePrefs()

    def cleanSubframeKeys(self, *args, **kwargs):
        selection = self.getSelected()
        Functions.cleanSubframeKeys(selection=selection)

    def removeBoringKeys(self, *args, **kwargs):
        regions = False
        if 'regions' in kwargs:
            regions = kwargs.pop('regions')
        selection = self.getSelected()
        Functions.removeBoringKeys(selection=selection, regions=regions)

    def getMainContainer(self, *args, **kwargs):
        return self.mainContainer

    def removeWidget(self, *args, **kwargs):
        storePrefs = True
        if 'storePrefs' in kwargs:
            storePrefs = kwargs.pop('storePrefs')
        command = partial(self.removeWidget_deferred, storePrefs=storePrefs)
        cmds.evalDeferred(command)

    def removeWidget_deferred(self, storePrefs, *args, **kwargs):
        storePrefs = True
        if 'storePrefs' in kwargs:
            storePrefs = kwargs.pop('storePrefs')
        layout = self.getMainContainer()
        cmds.deleteUI(layout, layout=True)
        try:
            self.instances.remove(self)
        except:
            pass

        if storePrefs:
            self.storePrefs()
        window.resizeUI()

    @classmethod
    def getCurrentState(cls, *args, **kwargs):
        widgetList = []
        for instance in cls.getInstances():
            data = {}
            data['description'] = instance.getDescription()
            data['widgetType'] = instance.getType()
            data['state'] = instance.getState()
            data['expanded'] = instance.getWidgetExpandedState()
            widgetList.append(data)

        return widgetList

    def getState(self):
        """
        This will get overwritten to collect data specific to each widget
        """
        return {}

    def setState(self, stateData):
        """
        This will get overwritten to collect data specific to each widget
        """
        pass

    def getType(self):
        return self.widgetType

    @classmethod
    def printInfo(cls, *args, **kwargs):
        """ print info about the widgets
        """
        widgetData = cls.getCurrentState()
        print (175, 'widgetData')
        for w in widgetData:
            print (w)

    @classmethod
    def storePrefs(cls, *args, **kwargs):
        debugging = False
        if 'debugging' in kwargs:
            debugging = kwargs.pop('debugging')
        widgetData = cls.getCurrentState()
        Prefs.setProfileData(profileData=widgetData)

    @classmethod
    def setInstances(cls, instances):
        cls.instances = instances

    @classmethod
    def getInstances(cls):
        return cls.instances

    def setDescription(self, description):
        """
        This is for setting the description text in the widget, its optional
        """
        self.description = description
        try:
            self.descriptionWidget.overrideDescription(self.description)
        except:
            pass

        try:
            cmds.frameLayout(self.mainContainer, edit=True, label=self.description)
        except:
            pass

    def getDescription(self):
        try:
            self.description
        except:
            self.description = ''

        return self.description

    def getLayout(self):
        return self.formLayout

    def getLayoutWidth(self):
        return cmds.formLayout(self.formLayout, query=True, width=True)

    def setLayoutWidth(self, w):
        return cmds.formLayout(self.formLayout, edit=True, width=w)

    def getSelected(self):
        selection = []
        if self.getPinState():
            selection = self.getBufferSelection()
        else:
            selection = cmds.ls(sl=True, type=['transform', 'joint'], long=True)
        return selection

    def getSelectedChannels(self, *args, **kwargs):
        selection = []
        if self.getPinState():
            selection = self.getBufferChannels()
        if not selection:
            selection = Functions.getSelectedChannels(*args, **kwargs)
        return selection

    def setWidgetType(self, widgetType):
        self.widgetType = widgetType

    def pinSelectionPopupMenu(self, *args, **kwargs):
        parent = False
        if 'parent' in kwargs:
            parent = kwargs.pop('parent')
        cmds.popupMenu(parent, edit=True, deleteAllItems=True)
        cmds.setParent(parent, menu=True)
        state = self.getPinState()
        if state:
            bufferSelection = self.getBufferSelection()
            bufferCount = len(bufferSelection)
            storedChannels = self.getBufferChannels()
            storedChannelsString = ''
            storedChannelCount = 0
            if storedChannels:
                storedChannelsString = '], ['.join(storedChannels)
                storedChannelCount = len(storedChannels)
            cmds.menuItem(label='Info: {0} Stored Objects'.format(bufferCount), enable=False)
            cmds.menuItem(label='Info: {0} Stored Channels: [{1}]'.format(storedChannelCount, storedChannelsString), enable=False)
            cmds.menuItem(divider=True)
        count = 0
        selected = cmds.ls(sl=True)
        if selected:
            count = len(selected)
        cmds.menuItem(label='Add Selected {0} Object(s)'.format(count), enable=state, command=partial(self.modifySelectionBuffer, 'add'))
        cmds.menuItem(label='Remove Selected {0} Object(s)'.format(count), enable=state, command=partial(self.modifySelectionBuffer, 'remove'))
        cmds.menuItem(divider=True)
        cmds.menuItem(label='Set Highlighted Channels'.format(count), enable=state, command=partial(self.storeHighlightedChannels, 'add'))
        cmds.menuItem(divider=True)
        cmds.menuItem(label='Select Objects', enable=state, command=partial(self.selectObjects, forSelectedNamespace=False))
        cmds.menuItem(label='Select Objects For selection Namespace', enable=state, command=partial(self.selectObjects, forSelectedNamespace=True))

    def storeHighlightedChannels(self, *args, **kwargs):
        highlightedChannels = Functions.getSelectedChannels()
        self.setBufferChannels(highlightedChannels)
        self.storePrefs()

    def modifySelectionBuffer(self, action, *args, **kwargs):
        currentBuffer = self.getSelected()
        if action == 'add':
            currentBuffer = list(set(currentBuffer) | set(cmds.ls(sl=True)))
        elif action == 'remove':
            currentBuffer = list(set(currentBuffer) - set(cmds.ls(sl=True)))
        self.bufferSelection = currentBuffer
        try:
            selectionCount = len(self.bufferSelection)
            description = '{0} Objects'.format(str(selectionCount))
            self.pinSelectionToggle.overrideDescription(description)
        except:
            pass

        self.storePrefs()

    def onPinSelectionButton(self, state, *args, **kwargs):
        onInit = False
        if 'onInit' in kwargs:
            onInit = kwargs.pop('onInit')
        if state:
            self.setPinState(False)
            bufferSelection = self.getBufferSelection()
            if bufferSelection:
                try:
                    cmds.select(bufferSelection)
                except:
                    pass

            self.setBufferChannels([])
        else:
            self.setPinState(True)
            if not onInit:
                self.setBufferSelection(cmds.ls(sl=True))
            try:
                selectionCount = len(self.bufferSelection)
                description = '{0} Objects'.format(str(selectionCount))
                self.pinSelectionToggle.overrideDescription(description)
            except:
                pass

        self.storePrefs()

    def selectObjects(self, *args, **kwargs):
        forSelectedNamespace = False
        if 'forSelectedNamespace' in kwargs:
            forSelectedNamespace = kwargs.pop('forSelectedNamespace')
        toSelect = []
        if not forSelectedNamespace:
            toSelect = self.getSelected()
        elif forSelectedNamespace:
            selection = cmds.ls(sl=True)
            selectedNamespaces = set(Functions.getNamespaces(nodes=selection))
            bufferNodes = self.getSelected()
            bufferNamespaces = set(Functions.getNamespaces(nodes=bufferNodes))
            for bufferNode in bufferNodes:
                if not selection or selectedNamespaces == bufferNamespaces:
                    toSelect += [bufferNode]
                elif selectedNamespaces != bufferNamespaces:
                    toSelect += Functions.findMatchingObjectsInNamespace(node=bufferNode, namespaces=selectedNamespaces)

        cmds.select(clear=True)
        for s in toSelect:
            if cmds.objExists(s):
                cmds.select(s, add=True)

    def setPinState(self, state):
        self.pinState = state

    def getPinState(self):
        try:
            self.pinState
        except:
            self.pinState = False

        return self.pinState

    def setBufferSelection(self, selection):
        if selection:
            self.bufferSelection = selection

    def getBufferSelection(self):
        try:
            self.bufferSelection
        except:
            self.bufferSelection = []

        return self.bufferSelection

    def setBufferChannels(self, selection):
        self.bufferChannels = selection

    def getBufferChannels(self):
        try:
            self.bufferChannels
        except:
            self.bufferChannels = []

        return self.bufferChannels

    def onDescriptionChange(self, description, *args, **kwargs):
        self.setDescription(description)
        self.storePrefs()


class widget_tween(widget_base):

    def __init__(self, *args, **kwargs):
        parent = False
        if 'parent' in kwargs:
            parent = kwargs.pop('parent')
        description = 'Inbetween'
        if 'description' in kwargs:
            description = kwargs.pop('description')
        stateData = {'pinState': False,
         'bufferSelection': [],
         'useAllLayersState': True}
        if 'stateData' in kwargs:
            stateData = kwargs.pop('stateData')
        expandedState = True
        if 'expandedState' in kwargs:
            expandedState = kwargs.pop('expandedState')
        widget_base.__init__(self, parent=parent, description=description, expandedState=expandedState)
        self.setState(stateData)
        self.setupUI()
        self.setDescription(description)
        self.setWidgetType('inbetween')

    def setState(self, stateData):
        try:
            self.setPinState(stateData['pinState'])
        except:
            pass

        try:
            self.setBufferSelection(stateData['bufferSelection'])
        except:
            pass

        try:
            self.setUseAllLayersState(stateData['useAllLayersState'])
        except:
            pass

        try:
            self.setBufferChannels(stateData['bufferChannels'])
        except:
            pass

    def setUseAllLayersState(self, state):
        self.useAllLayersState = state

    def getUseAllLayersState(self):
        try:
            self.useAllLayersState
        except:
            self.useAllLayersState = True

        return self.useAllLayersState

    def setupUI(self):
        layoutContainer = self.getLayout()
        cmds.formLayout(layoutContainer, edit=True)
        buttonBGC = [0.95] * 3
        self.sliderTween = slider_tween(parent=layoutContainer)
        sliderTweenUI = self.sliderTween.getLayout()
        self.sliderTween.getSelected = self.getSelected
        self.sliderTween.getUseAllLayersState = self.getUseAllLayersState
        self.sliderTween.getSelectedChannels = self.getSelectedChannels
        changeCommand = partial(self.onDescriptionChange)
        collapseCommand = partial(self.collapseMainContainer)
        self.descriptionWidget = button_textToggle(parent=layoutContainer, description=self.getDescription(), collapseCommand=collapseCommand, changeCommand=changeCommand)
        descriptionWidgetLayout = self.descriptionWidget.getLayout()
        ADescription = 'Anim Layers'
        BDescription = 'Isolate Layer'
        ACommand = partial(self.onToggleLayersButton, True)
        BCommand = partial(self.onToggleLayersButton, False)
        startState = self.getUseAllLayersState()
        self.layerToggle = button_toggleSwitch(parent=layoutContainer, startState=startState, ADescription=ADescription, BDescription=BDescription, ACommand=ACommand, BCommand=BCommand)
        layerToggleButton = self.layerToggle.getLayout()
        startState = not self.getPinState()
        ADescription = 'Pin Selection'
        BDescription = 'Pinned'
        if not startState:
            try:
                selectionCount = len(self.bufferSelection)
                BDescription = '{0} Objects'.format(str(selectionCount))
            except:
                pass

        ACommand = partial(self.onPinSelectionButton, True)
        BCommand = partial(self.onPinSelectionButton, False)
        self.pinSelectionToggle = button_toggleSwitch(parent=layoutContainer, startState=startState, ADescription=ADescription, BDescription=BDescription, ACommand=ACommand, BCommand=BCommand)
        pinSelectionButton = self.pinSelectionToggle.getLayout()
        popupMenu = cmds.popupMenu(parent=pinSelectionButton)
        cmds.popupMenu(popupMenu, edit=True, postMenuCommand=partial(self.pinSelectionPopupMenu, parent=popupMenu))
        easyTweenButton = cmds.button(parent=layoutContainer, label='Easy Tween', width=5, height=22, command=partial(self.sliderTween.useSetValueCommand), bgc=buttonBGC)
        h, s, v = cmds.displayRGBColor('timeSliderKey', query=True, hueSaturationValue=True)
        keyframeColor_rgb = colorsys.hsv_to_rgb(h / 360, 0.5, 0.8)
        h, s, v = cmds.displayRGBColor('timeSliderTickDrawSpecial', query=True, hueSaturationValue=True)
        specialKeyframeColor_rgb = colorsys.hsv_to_rgb(h / 360, 0.5, 0.8)
        size = 22
        setKeyButton = cmds.button(parent=layoutContainer, command=partial(self.setKeyframe), annotation='Set Key on Objects', height=size, width=size, bgc=keyframeColor_rgb, label='')
        popupMenu = cmds.popupMenu(parent=setKeyButton)
        cmds.popupMenu(popupMenu, edit=True, postMenuCommand=partial(self.setKeysPopupMenu, parent=popupMenu, special=False))
        setSpecialKeyButton = cmds.button(parent=layoutContainer, command=partial(self.setKeyframe, special=True), annotation='Set Colored Key on Objects', height=size, width=size, bgc=specialKeyframeColor_rgb, label='')
        popupMenu = cmds.popupMenu(parent=setSpecialKeyButton)
        cmds.popupMenu(popupMenu, edit=True, postMenuCommand=partial(self.setKeysPopupMenu, parent=popupMenu, special=True))
        presetLayout = cmds.formLayout(parent=layoutContainer)
        value = 0
        value = value * 2 - 1
        presetButton1 = cmds.button(parent=presetLayout, annotation='Previous', label='Prev', width=5, command=partial(self.sliderTween.presetCommand, value), bgc=buttonBGC)
        value = 0.1
        value = value * 2 - 1
        presetButton2 = cmds.button(parent=presetLayout, annotation='1/10', label='', width=5, command=partial(self.sliderTween.presetCommand, value), bgc=buttonBGC)
        value = 0.25
        value = value * 2 - 1
        presetButton3 = cmds.button(parent=presetLayout, annotation='1/4', label='', width=5, command=partial(self.sliderTween.presetCommand, value), bgc=buttonBGC)
        value = 0.5
        value = value * 2 - 1
        presetButton4 = cmds.button(parent=presetLayout, annotation='Half', label='Half', width=5, command=partial(self.sliderTween.presetCommand, value), bgc=buttonBGC)
        value = 0.75
        value = value * 2 - 1
        presetButton5 = cmds.button(parent=presetLayout, annotation='3/4', label='', width=5, command=partial(self.sliderTween.presetCommand, value), bgc=buttonBGC)
        value = 0.9
        value = value * 2 - 1
        presetButton6 = cmds.button(parent=presetLayout, annotation='1/10', label='', width=5, command=partial(self.sliderTween.presetCommand, value), bgc=buttonBGC)
        value = 1
        value = value * 2 - 1
        presetButton7 = cmds.button(parent=presetLayout, annotation='Next', label='Next', width=5, command=partial(self.sliderTween.presetCommand, value), bgc=buttonBGC)
        padding = 1
        cmds.formLayout(presetLayout, edit=True, attachForm=[(presetButton1, 'top', padding)])
        cmds.formLayout(presetLayout, edit=True, attachPosition=[(presetButton1,
          'left',
          padding,
          0)])
        cmds.formLayout(presetLayout, edit=True, attachNone=[(presetButton1, 'bottom')])
        cmds.formLayout(presetLayout, edit=True, attachPosition=[(presetButton1,
          'right',
          padding,
          20)])
        cmds.formLayout(presetLayout, edit=True, attachForm=[(presetButton2, 'top', padding)])
        cmds.formLayout(presetLayout, edit=True, attachPosition=[(presetButton2,
          'left',
          padding,
          20)])
        cmds.formLayout(presetLayout, edit=True, attachNone=[(presetButton2, 'bottom')])
        cmds.formLayout(presetLayout, edit=True, attachPosition=[(presetButton2,
          'right',
          padding,
          30)])
        cmds.formLayout(presetLayout, edit=True, attachForm=[(presetButton3, 'top', padding)])
        cmds.formLayout(presetLayout, edit=True, attachPosition=[(presetButton3,
          'left',
          padding,
          30)])
        cmds.formLayout(presetLayout, edit=True, attachNone=[(presetButton3, 'bottom')])
        cmds.formLayout(presetLayout, edit=True, attachPosition=[(presetButton3,
          'right',
          padding,
          40)])
        cmds.formLayout(presetLayout, edit=True, attachForm=[(presetButton4, 'top', padding)])
        cmds.formLayout(presetLayout, edit=True, attachPosition=[(presetButton4,
          'left',
          padding,
          40)])
        cmds.formLayout(presetLayout, edit=True, attachNone=[(presetButton4, 'bottom')])
        cmds.formLayout(presetLayout, edit=True, attachPosition=[(presetButton4,
          'right',
          padding,
          60)])
        cmds.formLayout(presetLayout, edit=True, attachForm=[(presetButton5, 'top', padding)])
        cmds.formLayout(presetLayout, edit=True, attachPosition=[(presetButton5,
          'left',
          padding,
          60)])
        cmds.formLayout(presetLayout, edit=True, attachNone=[(presetButton5, 'bottom')])
        cmds.formLayout(presetLayout, edit=True, attachPosition=[(presetButton5,
          'right',
          padding,
          70)])
        cmds.formLayout(presetLayout, edit=True, attachForm=[(presetButton6, 'top', padding)])
        cmds.formLayout(presetLayout, edit=True, attachPosition=[(presetButton6,
          'left',
          padding,
          70)])
        cmds.formLayout(presetLayout, edit=True, attachNone=[(presetButton6, 'bottom')])
        cmds.formLayout(presetLayout, edit=True, attachPosition=[(presetButton6,
          'right',
          padding,
          80)])
        cmds.formLayout(presetLayout, edit=True, attachForm=[(presetButton7, 'top', padding)])
        cmds.formLayout(presetLayout, edit=True, attachPosition=[(presetButton7,
          'left',
          padding,
          80)])
        cmds.formLayout(presetLayout, edit=True, attachNone=[(presetButton7, 'bottom')])
        cmds.formLayout(presetLayout, edit=True, attachPosition=[(presetButton7,
          'right',
          padding,
          100)])
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(descriptionWidgetLayout, 'top', 0)])
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(descriptionWidgetLayout, 'left', 0)])
        cmds.formLayout(layoutContainer, edit=True, attachNone=[(descriptionWidgetLayout, 'bottom')])
        cmds.formLayout(layoutContainer, edit=True, attachControl=[(descriptionWidgetLayout,
          'right',
          0,
          layerToggleButton)])
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(pinSelectionButton, 'top', 0)])
        cmds.formLayout(layoutContainer, edit=True, attachNone=[(pinSelectionButton, 'left')])
        cmds.formLayout(layoutContainer, edit=True, attachNone=[(pinSelectionButton, 'bottom')])
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(pinSelectionButton, 'right', 0)])
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(layerToggleButton, 'top', 0)])
        cmds.formLayout(layoutContainer, edit=True, attachNone=[(layerToggleButton, 'left')])
        cmds.formLayout(layoutContainer, edit=True, attachNone=[(layerToggleButton, 'bottom')])
        cmds.formLayout(layoutContainer, edit=True, attachControl=[(layerToggleButton,
          'right',
          0,
          pinSelectionButton)])
        cmds.formLayout(layoutContainer, edit=True, attachControl=[(setKeyButton,
          'top',
          1,
          layerToggleButton)])
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(setKeyButton, 'left', 2)])
        cmds.formLayout(layoutContainer, edit=True, attachNone=[(setKeyButton, 'bottom')])
        cmds.formLayout(layoutContainer, edit=True, attachNone=[(setKeyButton, 'right')])
        cmds.formLayout(layoutContainer, edit=True, attachControl=[(setSpecialKeyButton,
          'top',
          1,
          pinSelectionButton)])
        cmds.formLayout(layoutContainer, edit=True, attachControl=[(setSpecialKeyButton,
          'left',
          2,
          setKeyButton)])
        cmds.formLayout(layoutContainer, edit=True, attachNone=[(setSpecialKeyButton, 'bottom')])
        cmds.formLayout(layoutContainer, edit=True, attachNone=[(setSpecialKeyButton, 'right')])
        cmds.formLayout(layoutContainer, edit=True, attachControl=[(easyTweenButton,
          'top',
          1,
          pinSelectionButton)])
        cmds.formLayout(layoutContainer, edit=True, attachControl=[(easyTweenButton,
          'left',
          2,
          setSpecialKeyButton)])
        cmds.formLayout(layoutContainer, edit=True, attachNone=[(easyTweenButton, 'bottom')])
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(easyTweenButton, 'right', 1)])
        cmds.formLayout(layoutContainer, edit=True, attachControl=[(sliderTweenUI,
          'top',
          5,
          easyTweenButton)])
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(sliderTweenUI, 'left', 0)])
        cmds.formLayout(layoutContainer, edit=True, attachNone=[(sliderTweenUI, 'bottom')])
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(sliderTweenUI, 'right', 0)])
        cmds.formLayout(layoutContainer, edit=True, attachControl=[(presetLayout,
          'top',
          5,
          sliderTweenUI)])
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(presetLayout, 'left', 0)])
        cmds.formLayout(layoutContainer, edit=True, attachNone=[(presetLayout, 'bottom')])
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(presetLayout, 'right', 0)])

    def getState(self):
        data = {}
        data['pinState'] = self.pinState
        data['bufferSelection'] = self.getBufferSelection()
        data['bufferChannels'] = self.getBufferChannels()
        data['useAllLayersState'] = self.useAllLayersState
        return data

    def onToggleLayersButton(self, state, *args, **kwargs):
        if state:
            self.useAllLayersState = True
        else:
            self.useAllLayersState = False
        self.storePrefs(debugging='onToggleLayersButton')


class widget_snapshot(widget_base):

    def __init__(self, *args, **kwargs):
        parent = False
        if 'parent' in kwargs:
            parent = kwargs.pop('parent')
        description = 'Snapshot'
        if 'description' in kwargs:
            description = kwargs.pop('description')
        stateData = {'pinState': False,
         'bufferSelection': [],
         'useAllLayersState': True}
        if 'stateData' in kwargs:
            stateData = kwargs.pop('stateData')
        expandedState = True
        if 'expandedState' in kwargs:
            expandedState = kwargs.pop('expandedState')
        widget_base.__init__(self, parent=parent, description=description, expandedState=expandedState)
        self.setState(stateData)
        self.setupUI()
        self.setDescription(description)
        self.setWidgetType('snapshot')
        self.setInitialSliderState()

    def setInitialSliderState(self):
        if self.getPinState():
            self.slider.clearData()
            data = self.getDataBuffer()
            self.slider.setSnapshotData(data)
            self.slider.setSliderState(True)
        else:
            self.slider.setSliderState(False)

    def setState(self, stateData):
        try:
            self.setPinState(stateData['pinState'])
        except:
            self.setPinState(False)

        try:
            self.setDataBuffer(stateData['bufferData'])
        except:
            self.setDataBuffer([])

        try:
            self.setBufferChannels(stateData['bufferChannels'])
        except:
            pass

    def getState(self):
        data = {}
        data['pinState'] = self.pinState
        data['bufferData'] = self.getDataBuffer()
        data['bufferChannels'] = self.getBufferChannels()
        return data

    def setDataBuffer(self, data):
        self.bufferData = data
        if data:
            selection = data.keys()
            self.setBufferSelection(selection)

    def getDataBuffer(self):
        try:
            self.bufferData
        except:
            self.bufferData = []

        return self.bufferData

    def setupUI(self):
        layoutContainer = self.getLayout()
        cmds.formLayout(layoutContainer, edit=True)
        buttonBGC = [0.95] * 3
        self.slider = slider_snapshot(parent=layoutContainer)
        sliderElement = self.slider.getLayout()
        self.slider.getSelected = self.getSelected
        self.slider.getSelectedChannels = self.getSelectedChannels
        height = 15
        value = 1
        value = value * 2 - 1
        applyFullButton = cmds.button(parent=layoutContainer, label='Appy Pose', width=5, height=height, command=partial(self.slider.presetCommand, value), bgc=buttonBGC)
        changeCommand = partial(self.onDescriptionChange)
        collapseCommand = partial(self.collapseMainContainer)
        self.descriptionWidget = button_textToggle(parent=layoutContainer, description=self.getDescription(), collapseCommand=collapseCommand, changeCommand=changeCommand)
        descriptionWidgetLayout = self.descriptionWidget.getLayout()
        startState = not self.getPinState()
        ADescription = 'Capture Pose'
        BDescription = 'Pose Stored'
        try:
            selectionCount = len(self.getDataBuffer())
            BDescription = 'Pose Stored, {0} Objects'.format(str(selectionCount))
        except:
            pass

        ACommand = partial(self.onPinSelectionButton, True)
        BCommand = partial(self.onPinSelectionButton, False)
        self.pinSelectionToggle = button_toggleSwitch(parent=layoutContainer, startState=startState, ADescription=ADescription, BDescription=BDescription, ACommand=ACommand, BCommand=BCommand)
        pinSelectionButton = self.pinSelectionToggle.getLayout()
        popupMenu = cmds.popupMenu(parent=pinSelectionButton)
        cmds.popupMenu(popupMenu, edit=True, postMenuCommand=partial(self.pinSelectionPopupMenu, parent=popupMenu))
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(descriptionWidgetLayout, 'top', 0)])
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(descriptionWidgetLayout, 'left', 0)])
        cmds.formLayout(layoutContainer, edit=True, attachNone=[(descriptionWidgetLayout, 'bottom')])
        cmds.formLayout(layoutContainer, edit=True, attachPosition=[(descriptionWidgetLayout,
          'right',
          0,
          33)])
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(pinSelectionButton, 'top', 0)])
        cmds.formLayout(layoutContainer, edit=True, attachControl=[(pinSelectionButton,
          'left',
          0,
          descriptionWidgetLayout)])
        cmds.formLayout(layoutContainer, edit=True, attachNone=[(pinSelectionButton, 'bottom')])
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(pinSelectionButton, 'right', 0)])
        cmds.formLayout(layoutContainer, edit=True, attachControl=[(sliderElement,
          'top',
          5,
          pinSelectionButton)])
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(sliderElement, 'left', 0)])
        cmds.formLayout(layoutContainer, edit=True, attachNone=[(sliderElement, 'bottom')])
        cmds.formLayout(layoutContainer, edit=True, attachPosition=[(sliderElement,
          'right',
          10,
          66)])
        cmds.formLayout(layoutContainer, edit=True, attachControl=[(applyFullButton,
          'top',
          5,
          pinSelectionButton)])
        cmds.formLayout(layoutContainer, edit=True, attachPosition=[(applyFullButton,
          'left',
          0,
          66)])
        cmds.formLayout(layoutContainer, edit=True, attachNone=[(applyFullButton, 'bottom')])
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(applyFullButton, 'right', 2)])

    def onPinSelectionButton(self, state, *args, **kwargs):
        onInit = False
        if 'onInit' in kwargs:
            onInit = kwargs.pop('onInit')
        if state:
            self.setPinState(False)
            self.slider.clearData()
            self.slider.setSliderState(False)
        else:
            self.slider.collectSnapshotData()
            data = self.slider.getSnapshotData()
            self.setDataBuffer(data)
            self.setPinState(True)
            self.slider.setSliderState(True)
            try:
                selectionCount = len(self.getDataBuffer())
                description = 'Pose Stored, {0} Objects'.format(str(selectionCount))
                self.pinSelectionToggle.overrideDescription(description)
            except Exception as e:
                print (1990, e)

        self.storePrefs(debugging='onPinSelectionButton')


class widget_extras(widget_base):

    def __init__(self, *args, **kwargs):
        parent = False
        if 'parent' in kwargs:
            parent = kwargs.pop('parent')
        description = 'extras'
        if 'description' in kwargs:
            description = kwargs.pop('description')
        stateData = {'pinState': False,
         'bufferSelection': [],
         'useAllLayersState': True}
        if 'stateData' in kwargs:
            stateData = kwargs.pop('stateData')
        expandedState = True
        if 'expandedState' in kwargs:
            expandedState = kwargs.pop('expandedState')
        widget_base.__init__(self, parent=parent, description=description, expandedState=expandedState)
        self.setState(stateData)
        self.setupUI()
        self.setDescription(description)
        self.setWidgetType('extras')

    def setState(self, stateData):
        try:
            self.setPinState(stateData['pinState'])
        except:
            pass

        try:
            self.setBufferSelection(stateData['bufferSelection'])
        except:
            pass

        try:
            self.setBufferChannels(stateData['bufferChannels'])
        except:
            pass

    def setupUI(self):
        layoutContainer = self.getLayout()
        buttonBGC = [0.95] * 3
        changeCommand = partial(self.onDescriptionChange)
        collapseCommand = partial(self.collapseMainContainer)
        self.descriptionWidget = button_textToggle(parent=layoutContainer, description=self.getDescription(), changeCommand=changeCommand, collapseCommand=collapseCommand, width=60)
        descriptionWidgetLayout = self.descriptionWidget.getLayout()
        startState = not self.getPinState()
        ADescription = 'Pin Selection'
        BDescription = 'Pinned'
        if not startState:
            try:
                selectionCount = len(self.bufferSelection)
                BDescription = '{0} Objects'.format(str(selectionCount))
            except:
                pass

        ACommand = partial(self.onPinSelectionButton, True)
        BCommand = partial(self.onPinSelectionButton, False)
        self.pinSelectionToggle = button_toggleSwitch(parent=layoutContainer, startState=startState, ADescription=ADescription, BDescription=BDescription, ACommand=ACommand, BCommand=BCommand)
        pinSelectionButton = self.pinSelectionToggle.getLayout()
        popupMenu = cmds.popupMenu(parent=pinSelectionButton)
        cmds.popupMenu(popupMenu, edit=True, postMenuCommand=partial(self.pinSelectionPopupMenu, parent=popupMenu))
        miniSlidersLayout = cmds.formLayout(parent=layoutContainer)
        size = 22
        sliderA = cmds.floatSlider(parent=miniSlidersLayout, width=5, min=-1, max=1, value=0, step=0.1, bgc=buttonBGC)
        sliderA_label = cmds.text(parent=miniSlidersLayout, label='Multiply', bgc=buttonBGC, height=size, width=5, align='center')
        sliderB_label = cmds.text(parent=miniSlidersLayout, label='PosePusher', bgc=buttonBGC, height=size, width=5, align='center')
        sliderC_label = cmds.text(parent=miniSlidersLayout, label='In<>Out', bgc=buttonBGC, height=size, width=5, align='center')
        self.posePusher = slider_PosePusher(parent=miniSlidersLayout)
        posePusherUI = self.posePusher.getLayout()
        self.posePusher.getSelected = self.getSelected
        self.posePusher.getSelectedChannels = self.getSelectedChannels
        command = partial(self.multiplierChangeUpdateText, sliderWidget=self.posePusher, element=sliderB_label)
        self.posePusher.addMultiplierChangeCommand(command)
        command = partial(self.setTextLabel, sliderB_label, 'PosePusher')
        self.posePusher.addMultiplierPostCommand(command)
        self.sliderInOut = slider_inOut(parent=miniSlidersLayout)
        sliderInOutUI = self.sliderInOut.getLayout()
        self.sliderInOut.getSelected = self.getSelected
        self.sliderInOut.getSelectedChannels = self.getSelectedChannels
        command = partial(self.multiplierChangeUpdateText, sliderWidget=self.sliderInOut, element=sliderC_label)
        self.sliderInOut.addMultiplierChangeCommand(command)
        command = partial(self.setTextLabel, sliderC_label, 'In<>Out')
        self.sliderInOut.addMultiplierPostCommand(command)
        self.sliderMultiply = slider_multiply(parent=miniSlidersLayout)
        sliderMultiplyUI = self.sliderMultiply.getLayout()
        self.sliderMultiply.getSelected = self.getSelected
        self.sliderMultiply.getSelectedChannels = self.getSelectedChannels
        command = partial(self.multiplierChangeUpdateText, sliderWidget=self.sliderMultiply, element=sliderA_label)
        self.sliderMultiply.addMultiplierChangeCommand(command)
        command = partial(self.setTextLabel, sliderA_label, 'Multiply')
        self.sliderMultiply.addMultiplierPostCommand(command)
        padding = 1
        cmds.formLayout(miniSlidersLayout, edit=True, attachForm=[(sliderA_label, 'top', padding)])
        cmds.formLayout(miniSlidersLayout, edit=True, attachPosition=[(sliderA_label,
          'left',
          padding,
          0)])
        cmds.formLayout(miniSlidersLayout, edit=True, attachNone=[(sliderA_label, 'bottom')])
        cmds.formLayout(miniSlidersLayout, edit=True, attachPosition=[(sliderA_label,
          'right',
          padding,
          33)])
        cmds.formLayout(miniSlidersLayout, edit=True, attachForm=[(sliderB_label, 'top', padding)])
        cmds.formLayout(miniSlidersLayout, edit=True, attachPosition=[(sliderB_label,
          'left',
          padding,
          34)])
        cmds.formLayout(miniSlidersLayout, edit=True, attachNone=[(sliderB_label, 'bottom')])
        cmds.formLayout(miniSlidersLayout, edit=True, attachPosition=[(sliderB_label,
          'right',
          padding,
          66)])
        cmds.formLayout(miniSlidersLayout, edit=True, attachForm=[(sliderC_label, 'top', padding)])
        cmds.formLayout(miniSlidersLayout, edit=True, attachPosition=[(sliderC_label,
          'left',
          padding,
          67)])
        cmds.formLayout(miniSlidersLayout, edit=True, attachNone=[(sliderC_label, 'bottom')])
        cmds.formLayout(miniSlidersLayout, edit=True, attachPosition=[(sliderC_label,
          'right',
          padding,
          100)])
        cmds.formLayout(miniSlidersLayout, edit=True, attachControl=[(sliderMultiplyUI,
          'top',
          0,
          sliderA_label)])
        cmds.formLayout(miniSlidersLayout, edit=True, attachPosition=[(sliderMultiplyUI,
          'left',
          padding,
          0)])
        cmds.formLayout(miniSlidersLayout, edit=True, attachNone=[(sliderMultiplyUI, 'bottom')])
        cmds.formLayout(miniSlidersLayout, edit=True, attachPosition=[(sliderMultiplyUI,
          'right',
          padding,
          33)])
        cmds.formLayout(miniSlidersLayout, edit=True, attachControl=[(posePusherUI,
          'top',
          0,
          sliderA_label)])
        cmds.formLayout(miniSlidersLayout, edit=True, attachPosition=[(posePusherUI,
          'left',
          padding,
          34)])
        cmds.formLayout(miniSlidersLayout, edit=True, attachNone=[(posePusherUI, 'bottom')])
        cmds.formLayout(miniSlidersLayout, edit=True, attachPosition=[(posePusherUI,
          'right',
          padding,
          66)])
        cmds.formLayout(miniSlidersLayout, edit=True, attachControl=[(sliderInOutUI,
          'top',
          0,
          sliderA_label)])
        cmds.formLayout(miniSlidersLayout, edit=True, attachPosition=[(sliderInOutUI,
          'left',
          padding,
          67)])
        cmds.formLayout(miniSlidersLayout, edit=True, attachNone=[(sliderInOutUI, 'bottom')])
        cmds.formLayout(miniSlidersLayout, edit=True, attachPosition=[(sliderInOutUI,
          'right',
          padding,
          100)])
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(pinSelectionButton, 'top', 0)])
        cmds.formLayout(layoutContainer, edit=True, attachNone=[(pinSelectionButton, 'left')])
        cmds.formLayout(layoutContainer, edit=True, attachNone=[(pinSelectionButton, 'bottom')])
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(pinSelectionButton, 'right', 0)])
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(descriptionWidgetLayout, 'top', 0)])
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(descriptionWidgetLayout, 'left', 0)])
        cmds.formLayout(layoutContainer, edit=True, attachNone=[(descriptionWidgetLayout, 'bottom')])
        cmds.formLayout(layoutContainer, edit=True, attachControl=[(descriptionWidgetLayout,
          'right',
          0,
          pinSelectionButton)])
        cmds.formLayout(layoutContainer, edit=True, attachControl=[(miniSlidersLayout,
          'top',
          2,
          descriptionWidgetLayout)])
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(miniSlidersLayout, 'left', 0)])
        cmds.formLayout(layoutContainer, edit=True, attachNone=[(miniSlidersLayout, 'bottom')])
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(miniSlidersLayout, 'right', 0)])

    def getState(self):
        data = {}
        data['pinState'] = self.pinState
        data['bufferSelection'] = self.getBufferSelection()
        data['bufferChannels'] = self.getBufferChannels()
        return data


class widget_tools(widget_base):

    def __init__(self, *args, **kwargs):
        parent = False
        if 'parent' in kwargs:
            parent = kwargs.pop('parent')
        description = 'tools'
        if 'description' in kwargs:
            description = kwargs.pop('description')
        stateData = {'pinState': False,
         'bufferSelection': [],
         'useAllLayersState': True}
        if 'stateData' in kwargs:
            stateData = kwargs.pop('stateData')
        expandedState = True
        if 'expandedState' in kwargs:
            expandedState = kwargs.pop('expandedState')
        widget_base.__init__(self, parent=parent, description=description, expandedState=expandedState)
        self.setState(stateData)
        self.setupUI()
        self.setDescription(description)
        self.setWidgetType('tools')
        self.refreshTimeRange()

    def setState(self, stateData):
        pass

    def setupUI(self):
        layoutContainer = self.getLayout()
        spacerHeight = 2
        columnLayout = cmds.columnLayout(parent=layoutContainer, adjustableColumn=True, columnAttach=['both', 1], rowSpacing=2)
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(columnLayout, 'top', 0)])
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(columnLayout, 'left', 0)])
        cmds.formLayout(layoutContainer, edit=True, attachNone=[(columnLayout, 'bottom')])
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(columnLayout, 'right', 0)])
        height = 18
        changeCommand = partial(self.onDescriptionChange)
        collapseCommand = partial(self.collapseMainContainer)
        self.descriptionWidget = button_textToggle(parent=columnLayout, description=self.getDescription(), collapseCommand=collapseCommand, changeCommand=changeCommand)
        cmds.button(parent=columnLayout, label='Rekey Selection', bgc=[0.6] * 3, height=height, command=partial(self.rekeyOnKeys))
        cmds.button(parent=columnLayout, label='Rekey Selection To Match Last Selected', bgc=[0.6] * 3, height=height, command=partial(self.rekeyOnKeys, matchLast=True))
        cmds.formLayout(parent=columnLayout, height=spacerHeight)
        cmds.button(parent=columnLayout, label='Clean Subframe Keys', bgc=[0.6] * 3, height=height, command=partial(self.cleanSubframeKeys))
        cmds.button(parent=columnLayout, label='Remove Boring Keys', bgc=[0.6] * 3, height=height, command=partial(self.removeBoringKeys, regions=False))
        cmds.formLayout(parent=columnLayout, height=spacerHeight)
        smashBakeLayout = cmds.formLayout(parent=columnLayout, width=5, bgc=[0.6] * 3, height=height)
        self.startFrameField = cmds.intField(parent=smashBakeLayout, width=5, bgc=[0.3] * 3, height=height)
        self.endFrameField = cmds.intField(parent=smashBakeLayout, width=5, bgc=[0.3] * 3, height=height)
        bakeButton = cmds.button(parent=smashBakeLayout, label='Smash Bake', width=5, height=height, command=partial(self.smashBakeButton))
        popupMenu = cmds.popupMenu(parent=smashBakeLayout)
        cmds.popupMenu(popupMenu, edit=True, button=3, postMenuCommand=partial(self.smashBakeOptionsPopup, parent=popupMenu))
        cmds.formLayout(smashBakeLayout, edit=True, attachForm=[(bakeButton, 'top', 0)])
        cmds.formLayout(smashBakeLayout, edit=True, attachForm=[(bakeButton, 'left', 0)])
        cmds.formLayout(smashBakeLayout, edit=True, attachNone=[(bakeButton, 'bottom')])
        cmds.formLayout(smashBakeLayout, edit=True, attachPosition=[(bakeButton,
          'right',
          0,
          50)])
        cmds.formLayout(smashBakeLayout, edit=True, attachForm=[(self.startFrameField, 'top', 0)])
        cmds.formLayout(smashBakeLayout, edit=True, attachControl=[(self.startFrameField,
          'left',
          0,
          bakeButton)])
        cmds.formLayout(smashBakeLayout, edit=True, attachNone=[(self.startFrameField, 'bottom')])
        cmds.formLayout(smashBakeLayout, edit=True, attachPosition=[(self.startFrameField,
          'right',
          0,
          75)])
        cmds.formLayout(smashBakeLayout, edit=True, attachForm=[(self.endFrameField, 'top', 0)])
        cmds.formLayout(smashBakeLayout, edit=True, attachControl=[(self.endFrameField,
          'left',
          0,
          self.startFrameField)])
        cmds.formLayout(smashBakeLayout, edit=True, attachNone=[(self.endFrameField, 'bottom')])
        cmds.formLayout(smashBakeLayout, edit=True, attachForm=[(self.endFrameField, 'right', 0)])
        cmds.formLayout(parent=columnLayout, height=spacerHeight)
        quickUndosLayout = cmds.formLayout(parent=columnLayout, width=5, bgc=[0.6] * 3, height=height)
        undoButton = cmds.button(parent=quickUndosLayout, label='Quick Undo', bgc=[0.8] * 3, height=height, command=partial(Functions.quickUndo))
        redoButton = cmds.button(parent=quickUndosLayout, label='Quick Redo', bgc=[0.4] * 3, height=height, command=partial(Functions.quickRedo))
        cmds.formLayout(quickUndosLayout, edit=True, attachForm=[(undoButton, 'top', 0)])
        cmds.formLayout(quickUndosLayout, edit=True, attachForm=[(undoButton, 'left', 0)])
        cmds.formLayout(quickUndosLayout, edit=True, attachNone=[(undoButton, 'bottom')])
        cmds.formLayout(quickUndosLayout, edit=True, attachPosition=[(undoButton,
          'right',
          0,
          50)])
        cmds.formLayout(quickUndosLayout, edit=True, attachForm=[(redoButton, 'top', 0)])
        cmds.formLayout(quickUndosLayout, edit=True, attachControl=[(redoButton,
          'left',
          0,
          undoButton)])
        cmds.formLayout(quickUndosLayout, edit=True, attachNone=[(redoButton, 'bottom')])
        cmds.formLayout(quickUndosLayout, edit=True, attachForm=[(redoButton, 'right', 0)])

    def onCollapseButtonPress(self, *args, **kwargs):
        cmds.frameLayout(self.collapseButton, edit=True, collapse=False)
        self.collapseMainContainer()

    def smashBakeButton(self, *args, **kwargs):
        startTime, endTime = Functions.queryTimeRange()
        try:
            startTime = cmds.intField(self.startFrameField, query=True, value=startTime)
            endTime = cmds.intField(self.endFrameField, query=True, value=endTime)
        except:
            pass

        selected = cmds.ls(sl=True)
        Functions.smashBaker(selected, startTime, endTime)

    def smashBakeOptionsPopup(self, *args, **kwargs):
        parent = False
        if 'parent' in kwargs:
            parent = kwargs.pop('parent')
        cmds.popupMenu(parent, edit=True, deleteAllItems=True)
        cmds.setParent(parent, menu=True)
        cmds.menuItem(parent=parent, label='Refresh Time Range', command=partial(self.refreshTimeRange))

    def refreshTimeRange(self, *args, **kwargs):
        checkHighlighted = False
        if 'checkHighlighted' in kwargs:
            checkHighlighted = kwargs.pop('checkHighlighted')
        startTime, endTime = Functions.queryTimeRange(checkHighlighted=checkHighlighted)
        cmds.intField(self.startFrameField, edit=True, value=startTime)
        cmds.intField(self.endFrameField, edit=True, value=endTime)


class widget_worldSpace(widget_base):

    def __init__(self, *args, **kwargs):
        parent = False
        if 'parent' in kwargs:
            parent = kwargs.pop('parent')
        description = 'World Space'
        if 'description' in kwargs:
            description = kwargs.pop('description')
        stateData = {'pinState': False,
         'bufferSelection': [],
         'useAllLayersState': True}
        if 'stateData' in kwargs:
            stateData = kwargs.pop('stateData')
        expandedState = True
        if 'expandedState' in kwargs:
            expandedState = kwargs.pop('expandedState')
        widget_base.__init__(self, parent=parent, description=description, expandedState=expandedState)
        self.setState(stateData)
        self.setupUI()
        self.setDescription(description)
        self.setWidgetType('worldSpace')

    def setState(self, stateData):
        try:
            self.setPinState(stateData['pinState'])
        except:
            pass

        try:
            self.setBufferSelection(stateData['bufferSelection'])
        except:
            pass

        try:
            self.setBufferChannels(stateData['bufferChannels'])
        except:
            pass

    def setupUI(self):
        layoutContainer = self.getLayout()
        cmds.formLayout(layoutContainer, edit=True)
        buttonBGC = [0.95] * 3
        self.sliderWorldSpace = slider_worldSpace(parent=layoutContainer)
        sliderWorldSpaceUI = self.sliderWorldSpace.getLayout()
        self.sliderWorldSpace.getSelected = self.getSelected
        self.sliderWorldSpace.getSelectedChannels = self.getSelectedChannels
        height = 15
        value = 0
        value = value * 2 - 1
        presetButton1 = cmds.button(parent=layoutContainer, annotation='Previous', label='Prev', width=5, height=height, command=partial(self.sliderWorldSpace.presetCommand, value), bgc=buttonBGC)
        value = 1
        value = value * 2 - 1
        presetButton2 = cmds.button(parent=layoutContainer, annotation='Next', label='Next', width=5, height=height, command=partial(self.sliderWorldSpace.presetCommand, value), bgc=buttonBGC)
        changeCommand = partial(self.onDescriptionChange)
        collapseCommand = partial(self.collapseMainContainer)
        self.descriptionWidget = button_textToggle(parent=layoutContainer, collapseCommand=collapseCommand, description=self.getDescription(), changeCommand=changeCommand)
        descriptionWidgetLayout = self.descriptionWidget.getLayout()
        startState = not self.getPinState()
        ADescription = 'Pin Selection'
        BDescription = 'Pinned'
        if not startState:
            try:
                selectionCount = len(self.bufferSelection)
                BDescription = '{0} Objects'.format(str(selectionCount))
            except:
                pass

        ACommand = partial(self.onPinSelectionButton, True)
        BCommand = partial(self.onPinSelectionButton, False)
        self.pinSelectionToggle = button_toggleSwitch(parent=layoutContainer, startState=startState, ADescription=ADescription, BDescription=BDescription, ACommand=ACommand, BCommand=BCommand)
        pinSelectionButton = self.pinSelectionToggle.getLayout()
        popupMenu = cmds.popupMenu(parent=pinSelectionButton)
        cmds.popupMenu(popupMenu, edit=True, postMenuCommand=partial(self.pinSelectionPopupMenu, parent=popupMenu))
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(descriptionWidgetLayout, 'top', 0)])
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(descriptionWidgetLayout, 'left', 0)])
        cmds.formLayout(layoutContainer, edit=True, attachNone=[(descriptionWidgetLayout, 'bottom')])
        cmds.formLayout(layoutContainer, edit=True, attachControl=[(descriptionWidgetLayout,
          'right',
          0,
          pinSelectionButton)])
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(pinSelectionButton, 'top', 0)])
        cmds.formLayout(layoutContainer, edit=True, attachNone=[(pinSelectionButton, 'left')])
        cmds.formLayout(layoutContainer, edit=True, attachNone=[(pinSelectionButton, 'bottom')])
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(pinSelectionButton, 'right', 0)])
        cmds.formLayout(layoutContainer, edit=True, attachControl=[(presetButton1,
          'top',
          5,
          descriptionWidgetLayout)])
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(presetButton1, 'left', 2)])
        cmds.formLayout(layoutContainer, edit=True, attachNone=[(presetButton1, 'bottom')])
        cmds.formLayout(layoutContainer, edit=True, attachPosition=[(presetButton1,
          'right',
          0,
          20)])
        cmds.formLayout(layoutContainer, edit=True, attachControl=[(presetButton2,
          'top',
          5,
          descriptionWidgetLayout)])
        cmds.formLayout(layoutContainer, edit=True, attachPosition=[(presetButton2,
          'left',
          0,
          80)])
        cmds.formLayout(layoutContainer, edit=True, attachNone=[(presetButton2, 'bottom')])
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(presetButton2, 'right', 2)])
        cmds.formLayout(layoutContainer, edit=True, attachControl=[(sliderWorldSpaceUI,
          'top',
          5,
          descriptionWidgetLayout)])
        cmds.formLayout(layoutContainer, edit=True, attachControl=[(sliderWorldSpaceUI,
          'left',
          5,
          presetButton1)])
        cmds.formLayout(layoutContainer, edit=True, attachNone=[(sliderWorldSpaceUI, 'bottom')])
        cmds.formLayout(layoutContainer, edit=True, attachControl=[(sliderWorldSpaceUI,
          'right',
          5,
          presetButton2)])

    def getState(self):
        data = {}
        data['pinState'] = self.pinState
        data['bufferSelection'] = self.getBufferSelection()
        data['bufferChannels'] = self.getBufferChannels()
        return data


class widget_classic(widget_base):

    def __init__(self, *args, **kwargs):
        parent = False
        if 'parent' in kwargs:
            parent = kwargs.pop('parent')
        description = 'Classic'
        if 'description' in kwargs:
            description = kwargs.pop('description')
        stateData = {'pinState': False,
         'bufferSelection': [],
         'useAllLayersState': True}
        if 'stateData' in kwargs:
            stateData = kwargs.pop('stateData')
        expandedState = True
        if 'expandedState' in kwargs:
            expandedState = kwargs.pop('expandedState')
        widget_base.__init__(self, parent=parent, description=description, expandedState=expandedState)
        self.setState(stateData)
        self.setupUI()
        self.setDescription(description)
        self.setWidgetType('classic')

    def setState(self, stateData):
        try:
            self.setPinState(stateData['pinState'])
        except:
            pass

        try:
            self.setBufferSelection(stateData['bufferSelection'])
        except:
            pass

        try:
            self.setUseAllLayersState(stateData['useAllLayersState'])
        except:
            pass

        try:
            self.setBufferChannels(stateData['bufferChannels'])
        except:
            pass

    def setUseAllLayersState(self, state):
        self.useAllLayersState = state

    def getUseAllLayersState(self):
        try:
            self.useAllLayersState
        except:
            self.useAllLayersState = True

        return self.useAllLayersState

    def setupUI(self):
        layoutContainer = self.getLayout()
        cmds.formLayout(layoutContainer, edit=True)
        buttonBGC = [0.95] * 3
        self.sliderTween = slider_tween(parent=layoutContainer)
        sliderTweenUI = self.sliderTween.getLayout()
        self.sliderTween.getSelected = self.getSelected
        self.sliderTween.getUseAllLayersState = self.getUseAllLayersState
        self.sliderTween.getSelectedChannels = self.getSelectedChannels
        changeCommand = partial(self.onDescriptionChange)
        collapseCommand = partial(self.collapseMainContainer)
        self.descriptionWidget = button_textToggle(parent=layoutContainer, description=self.getDescription(), collapseCommand=collapseCommand, changeCommand=changeCommand)
        descriptionWidgetLayout = self.descriptionWidget.getLayout()
        ADescription = 'Anim Layers'
        BDescription = 'Isolate Layer'
        ACommand = partial(self.onToggleLayersButton, True)
        BCommand = partial(self.onToggleLayersButton, False)
        startState = self.getUseAllLayersState()
        self.layerToggle = button_toggleSwitch(parent=layoutContainer, startState=startState, ADescription=ADescription, BDescription=BDescription, ACommand=ACommand, BCommand=BCommand)
        layerToggleButton = self.layerToggle.getLayout()
        startState = not self.getPinState()
        ADescription = 'Pin Selection'
        BDescription = 'Pinned'
        if not startState:
            try:
                selectionCount = len(self.bufferSelection)
                BDescription = '{0} Objects'.format(str(selectionCount))
            except:
                pass

        ACommand = partial(self.onPinSelectionButton, True)
        BCommand = partial(self.onPinSelectionButton, False)
        self.pinSelectionToggle = button_toggleSwitch(parent=layoutContainer, startState=startState, ADescription=ADescription, BDescription=BDescription, ACommand=ACommand, BCommand=BCommand)
        pinSelectionButton = self.pinSelectionToggle.getLayout()
        popupMenu = cmds.popupMenu(parent=pinSelectionButton)
        cmds.popupMenu(popupMenu, edit=True, postMenuCommand=partial(self.pinSelectionPopupMenu, parent=popupMenu))
        easyTweenButton = cmds.button(parent=layoutContainer, label='Easy Tween', width=5, height=22, command=partial(self.sliderTween.useSetValueCommand), bgc=buttonBGC)
        h, s, v = 360.0, 0.8105263113975525, 0.49662160873413086
        try:
            h, s, v = cmds.displayRGBColor('timeSliderKey', query=True, hueSaturationValue=True)
        except:
            try:
                h, s, v = cmds.displayRGBColor('timeControlKey', query=True, hueSaturationValue=True)
            except:
                pass

        keyframeColor_rgb = colorsys.hsv_to_rgb(h / 360, 0.5, 0.8)
        h, s, v = 123.47547149658203, 0.6543209552764893, 0.8100000023841858
        try:
            h, s, v = cmds.displayRGBColor('timeControlTickDrawSpecial', query=True, hueSaturationValue=True)
        except:
            try:
                h, s, v = cmds.displayRGBColor('timeSliderTickDrawSpecial', query=True, hueSaturationValue=True)
            except:
                pass

        specialKeyframeColor_rgb = colorsys.hsv_to_rgb(h / 360, 0.5, 0.8)
        size = 22
        setKeyButton = cmds.button(parent=layoutContainer, command=partial(self.setKeyframe), annotation='Set Key on Objects', height=size, width=size, bgc=keyframeColor_rgb, label='')
        popupMenu = cmds.popupMenu(parent=setKeyButton)
        cmds.popupMenu(popupMenu, edit=True, postMenuCommand=partial(self.setKeysPopupMenu, parent=popupMenu, special=False))
        setSpecialKeyButton = cmds.button(parent=layoutContainer, command=partial(self.setKeyframe, special=True), annotation='Set Colored Key on Objects', height=size, width=size, bgc=specialKeyframeColor_rgb, label='')
        popupMenu = cmds.popupMenu(parent=setSpecialKeyButton)
        cmds.popupMenu(popupMenu, edit=True, postMenuCommand=partial(self.setKeysPopupMenu, parent=popupMenu, special=True))
        presetLayout = cmds.formLayout(parent=layoutContainer)
        value = 0
        value = value * 2 - 1
        presetButton1 = cmds.button(parent=presetLayout, annotation='Previous', label='Prev', width=5, command=partial(self.sliderTween.presetCommand, value), bgc=buttonBGC)
        value = 0.1
        value = value * 2 - 1
        presetButton2 = cmds.button(parent=presetLayout, annotation='1/10', label='', width=5, command=partial(self.sliderTween.presetCommand, value), bgc=buttonBGC)
        value = 0.25
        value = value * 2 - 1
        presetButton3 = cmds.button(parent=presetLayout, annotation='1/4', label='', width=5, command=partial(self.sliderTween.presetCommand, value), bgc=buttonBGC)
        value = 0.5
        value = value * 2 - 1
        presetButton4 = cmds.button(parent=presetLayout, annotation='Half', label='Half', width=5, command=partial(self.sliderTween.presetCommand, value), bgc=buttonBGC)
        value = 0.75
        value = value * 2 - 1
        presetButton5 = cmds.button(parent=presetLayout, annotation='3/4', label='', width=5, command=partial(self.sliderTween.presetCommand, value), bgc=buttonBGC)
        value = 0.9
        value = value * 2 - 1
        presetButton6 = cmds.button(parent=presetLayout, annotation='1/10', label='', width=5, command=partial(self.sliderTween.presetCommand, value), bgc=buttonBGC)
        value = 1
        value = value * 2 - 1
        presetButton7 = cmds.button(parent=presetLayout, annotation='Next', label='Next', width=5, command=partial(self.sliderTween.presetCommand, value), bgc=buttonBGC)
        padding = 1
        cmds.formLayout(presetLayout, edit=True, attachForm=[(presetButton1, 'top', padding)])
        cmds.formLayout(presetLayout, edit=True, attachPosition=[(presetButton1,
          'left',
          padding,
          0)])
        cmds.formLayout(presetLayout, edit=True, attachNone=[(presetButton1, 'bottom')])
        cmds.formLayout(presetLayout, edit=True, attachPosition=[(presetButton1,
          'right',
          padding,
          20)])
        cmds.formLayout(presetLayout, edit=True, attachForm=[(presetButton2, 'top', padding)])
        cmds.formLayout(presetLayout, edit=True, attachPosition=[(presetButton2,
          'left',
          padding,
          20)])
        cmds.formLayout(presetLayout, edit=True, attachNone=[(presetButton2, 'bottom')])
        cmds.formLayout(presetLayout, edit=True, attachPosition=[(presetButton2,
          'right',
          padding,
          30)])
        cmds.formLayout(presetLayout, edit=True, attachForm=[(presetButton3, 'top', padding)])
        cmds.formLayout(presetLayout, edit=True, attachPosition=[(presetButton3,
          'left',
          padding,
          30)])
        cmds.formLayout(presetLayout, edit=True, attachNone=[(presetButton3, 'bottom')])
        cmds.formLayout(presetLayout, edit=True, attachPosition=[(presetButton3,
          'right',
          padding,
          40)])
        cmds.formLayout(presetLayout, edit=True, attachForm=[(presetButton4, 'top', padding)])
        cmds.formLayout(presetLayout, edit=True, attachPosition=[(presetButton4,
          'left',
          padding,
          40)])
        cmds.formLayout(presetLayout, edit=True, attachNone=[(presetButton4, 'bottom')])
        cmds.formLayout(presetLayout, edit=True, attachPosition=[(presetButton4,
          'right',
          padding,
          60)])
        cmds.formLayout(presetLayout, edit=True, attachForm=[(presetButton5, 'top', padding)])
        cmds.formLayout(presetLayout, edit=True, attachPosition=[(presetButton5,
          'left',
          padding,
          60)])
        cmds.formLayout(presetLayout, edit=True, attachNone=[(presetButton5, 'bottom')])
        cmds.formLayout(presetLayout, edit=True, attachPosition=[(presetButton5,
          'right',
          padding,
          70)])
        cmds.formLayout(presetLayout, edit=True, attachForm=[(presetButton6, 'top', padding)])
        cmds.formLayout(presetLayout, edit=True, attachPosition=[(presetButton6,
          'left',
          padding,
          70)])
        cmds.formLayout(presetLayout, edit=True, attachNone=[(presetButton6, 'bottom')])
        cmds.formLayout(presetLayout, edit=True, attachPosition=[(presetButton6,
          'right',
          padding,
          80)])
        cmds.formLayout(presetLayout, edit=True, attachForm=[(presetButton7, 'top', padding)])
        cmds.formLayout(presetLayout, edit=True, attachPosition=[(presetButton7,
          'left',
          padding,
          80)])
        cmds.formLayout(presetLayout, edit=True, attachNone=[(presetButton7, 'bottom')])
        cmds.formLayout(presetLayout, edit=True, attachPosition=[(presetButton7,
          'right',
          padding,
          100)])
        miniSlidersLayout = cmds.formLayout(parent=layoutContainer)
        sliderA = cmds.floatSlider(parent=miniSlidersLayout, width=5, min=-1, max=1, value=0, step=0.1, bgc=buttonBGC)
        sliderA_label = cmds.text(parent=miniSlidersLayout, label='Multiply', bgc=buttonBGC, height=size, width=5, align='center')
        sliderB_label = cmds.text(parent=miniSlidersLayout, label='PosePusher', bgc=buttonBGC, height=size, width=5, align='center')
        sliderC_label = cmds.text(parent=miniSlidersLayout, label='In<>Out', bgc=buttonBGC, height=size, width=5, align='center')
        self.posePusher = slider_PosePusher(parent=miniSlidersLayout)
        posePusherUI = self.posePusher.getLayout()
        self.posePusher.getSelected = self.getSelected
        self.posePusher.getSelectedChannels = self.getSelectedChannels
        command = partial(self.multiplierChangeUpdateText, sliderWidget=self.posePusher, element=sliderB_label)
        self.posePusher.addMultiplierChangeCommand(command)
        command = partial(self.setTextLabel, sliderB_label, 'PosePusher')
        self.posePusher.addMultiplierPostCommand(command)
        self.sliderInOut = slider_inOut(parent=miniSlidersLayout)
        sliderInOutUI = self.sliderInOut.getLayout()
        self.sliderInOut.getSelected = self.getSelected
        self.sliderInOut.getSelectedChannels = self.getSelectedChannels
        command = partial(self.multiplierChangeUpdateText, sliderWidget=self.sliderInOut, element=sliderC_label)
        self.sliderInOut.addMultiplierChangeCommand(command)
        command = partial(self.setTextLabel, sliderC_label, 'In<>Out')
        self.sliderInOut.addMultiplierPostCommand(command)
        self.sliderMultiply = slider_multiply(parent=miniSlidersLayout)
        sliderMultiplyUI = self.sliderMultiply.getLayout()
        self.sliderMultiply.getSelected = self.getSelected
        self.sliderMultiply.getSelectedChannels = self.getSelectedChannels
        command = partial(self.multiplierChangeUpdateText, sliderWidget=self.sliderMultiply, element=sliderA_label)
        self.sliderMultiply.addMultiplierChangeCommand(command)
        command = partial(self.setTextLabel, sliderA_label, 'Multiply')
        self.sliderMultiply.addMultiplierPostCommand(command)
        padding = 1
        cmds.formLayout(miniSlidersLayout, edit=True, attachForm=[(sliderA_label, 'top', padding)])
        cmds.formLayout(miniSlidersLayout, edit=True, attachPosition=[(sliderA_label,
          'left',
          padding,
          0)])
        cmds.formLayout(miniSlidersLayout, edit=True, attachNone=[(sliderA_label, 'bottom')])
        cmds.formLayout(miniSlidersLayout, edit=True, attachPosition=[(sliderA_label,
          'right',
          padding,
          33)])
        cmds.formLayout(miniSlidersLayout, edit=True, attachForm=[(sliderB_label, 'top', padding)])
        cmds.formLayout(miniSlidersLayout, edit=True, attachPosition=[(sliderB_label,
          'left',
          padding,
          34)])
        cmds.formLayout(miniSlidersLayout, edit=True, attachNone=[(sliderB_label, 'bottom')])
        cmds.formLayout(miniSlidersLayout, edit=True, attachPosition=[(sliderB_label,
          'right',
          padding,
          66)])
        cmds.formLayout(miniSlidersLayout, edit=True, attachForm=[(sliderC_label, 'top', padding)])
        cmds.formLayout(miniSlidersLayout, edit=True, attachPosition=[(sliderC_label,
          'left',
          padding,
          67)])
        cmds.formLayout(miniSlidersLayout, edit=True, attachNone=[(sliderC_label, 'bottom')])
        cmds.formLayout(miniSlidersLayout, edit=True, attachPosition=[(sliderC_label,
          'right',
          padding,
          100)])
        cmds.formLayout(miniSlidersLayout, edit=True, attachControl=[(sliderMultiplyUI,
          'top',
          0,
          sliderA_label)])
        cmds.formLayout(miniSlidersLayout, edit=True, attachPosition=[(sliderMultiplyUI,
          'left',
          padding,
          0)])
        cmds.formLayout(miniSlidersLayout, edit=True, attachNone=[(sliderMultiplyUI, 'bottom')])
        cmds.formLayout(miniSlidersLayout, edit=True, attachPosition=[(sliderMultiplyUI,
          'right',
          padding,
          33)])
        cmds.formLayout(miniSlidersLayout, edit=True, attachControl=[(posePusherUI,
          'top',
          0,
          sliderA_label)])
        cmds.formLayout(miniSlidersLayout, edit=True, attachPosition=[(posePusherUI,
          'left',
          padding,
          34)])
        cmds.formLayout(miniSlidersLayout, edit=True, attachNone=[(posePusherUI, 'bottom')])
        cmds.formLayout(miniSlidersLayout, edit=True, attachPosition=[(posePusherUI,
          'right',
          padding,
          66)])
        cmds.formLayout(miniSlidersLayout, edit=True, attachControl=[(sliderInOutUI,
          'top',
          0,
          sliderA_label)])
        cmds.formLayout(miniSlidersLayout, edit=True, attachPosition=[(sliderInOutUI,
          'left',
          padding,
          67)])
        cmds.formLayout(miniSlidersLayout, edit=True, attachNone=[(sliderInOutUI, 'bottom')])
        cmds.formLayout(miniSlidersLayout, edit=True, attachPosition=[(sliderInOutUI,
          'right',
          padding,
          100)])
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(descriptionWidgetLayout, 'top', 0)])
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(descriptionWidgetLayout, 'left', 0)])
        cmds.formLayout(layoutContainer, edit=True, attachNone=[(descriptionWidgetLayout, 'bottom')])
        cmds.formLayout(layoutContainer, edit=True, attachControl=[(descriptionWidgetLayout,
          'right',
          0,
          layerToggleButton)])
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(pinSelectionButton, 'top', 0)])
        cmds.formLayout(layoutContainer, edit=True, attachNone=[(pinSelectionButton, 'left')])
        cmds.formLayout(layoutContainer, edit=True, attachNone=[(pinSelectionButton, 'bottom')])
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(pinSelectionButton, 'right', 0)])
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(layerToggleButton, 'top', 0)])
        cmds.formLayout(layoutContainer, edit=True, attachNone=[(layerToggleButton, 'left')])
        cmds.formLayout(layoutContainer, edit=True, attachNone=[(layerToggleButton, 'bottom')])
        cmds.formLayout(layoutContainer, edit=True, attachControl=[(layerToggleButton,
          'right',
          0,
          pinSelectionButton)])
        cmds.formLayout(layoutContainer, edit=True, attachControl=[(setKeyButton,
          'top',
          1,
          layerToggleButton)])
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(setKeyButton, 'left', 2)])
        cmds.formLayout(layoutContainer, edit=True, attachNone=[(setKeyButton, 'bottom')])
        cmds.formLayout(layoutContainer, edit=True, attachNone=[(setKeyButton, 'right')])
        cmds.formLayout(layoutContainer, edit=True, attachControl=[(setSpecialKeyButton,
          'top',
          1,
          pinSelectionButton)])
        cmds.formLayout(layoutContainer, edit=True, attachControl=[(setSpecialKeyButton,
          'left',
          2,
          setKeyButton)])
        cmds.formLayout(layoutContainer, edit=True, attachNone=[(setSpecialKeyButton, 'bottom')])
        cmds.formLayout(layoutContainer, edit=True, attachNone=[(setSpecialKeyButton, 'right')])
        cmds.formLayout(layoutContainer, edit=True, attachControl=[(easyTweenButton,
          'top',
          1,
          pinSelectionButton)])
        cmds.formLayout(layoutContainer, edit=True, attachControl=[(easyTweenButton,
          'left',
          2,
          setSpecialKeyButton)])
        cmds.formLayout(layoutContainer, edit=True, attachNone=[(easyTweenButton, 'bottom')])
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(easyTweenButton, 'right', 1)])
        cmds.formLayout(layoutContainer, edit=True, attachControl=[(sliderTweenUI,
          'top',
          5,
          easyTweenButton)])
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(sliderTweenUI, 'left', 0)])
        cmds.formLayout(layoutContainer, edit=True, attachNone=[(sliderTweenUI, 'bottom')])
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(sliderTweenUI, 'right', 0)])
        cmds.formLayout(layoutContainer, edit=True, attachControl=[(presetLayout,
          'top',
          5,
          sliderTweenUI)])
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(presetLayout, 'left', 0)])
        cmds.formLayout(layoutContainer, edit=True, attachNone=[(presetLayout, 'bottom')])
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(presetLayout, 'right', 0)])
        cmds.formLayout(layoutContainer, edit=True, attachControl=[(miniSlidersLayout,
          'top',
          5,
          presetLayout)])
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(miniSlidersLayout, 'left', 0)])
        cmds.formLayout(layoutContainer, edit=True, attachNone=[(miniSlidersLayout, 'bottom')])
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(miniSlidersLayout, 'right', 0)])

    def getState(self):
        data = {}
        data['pinState'] = self.pinState
        data['bufferSelection'] = self.getBufferSelection()
        data['bufferChannels'] = self.getBufferChannels()
        data['useAllLayersState'] = self.useAllLayersState
        return data

    def onToggleLayersButton(self, state, *args, **kwargs):
        if state:
            self.useAllLayersState = True
        else:
            self.useAllLayersState = False
        self.storePrefs(debugging='onToggleLayersButton')


class widget_curveOptions(widget_base):

    def __init__(self, *args, **kwargs):
        parent = False
        if 'parent' in kwargs:
            parent = kwargs.pop('parent')
        description = 'Curve Options'
        if 'description' in kwargs:
            description = kwargs.pop('description')
        stateData = {'pinState': False,
         'bufferSelection': [],
         'useAllLayersState': True}
        if 'stateData' in kwargs:
            stateData = kwargs.pop('stateData')
        expandedState = True
        if 'expandedState' in kwargs:
            expandedState = kwargs.pop('expandedState')
        widget_base.__init__(self, parent=parent, description=description, expandedState=expandedState)
        self.setState(stateData)
        self.setupUI()
        self.setDescription(description)
        self.setWidgetType('curveOptions')

    def setupUI(self):
        layoutContainer = self.getLayout()
        cmds.formLayout(layoutContainer, edit=True)
        buttonBGC = [0.95] * 3
        curveOptionButtons = []
        buttonInfo = 'CollapseButton'
        curveOptionButtons.append(buttonInfo)
        buttonInfo = {}
        buttonInfo['image'] = 'autoTangent.xpm'
        buttonInfo['command'] = partial(Functions.setKeyType, 'auto')
        buttonInfo['description'] = 'set to auto tangents'
        curveOptionButtons.append(buttonInfo)
        buttonInfo = {}
        buttonInfo['image'] = 'splineTangent.xpm'
        buttonInfo['command'] = partial(Functions.setKeyType, 'spline')
        buttonInfo['description'] = 'set to spline tangents'
        curveOptionButtons.append(buttonInfo)
        buttonInfo = {}
        buttonInfo['image'] = 'clampedTangent.xpm'
        buttonInfo['command'] = partial(Functions.setKeyType, 'clamped')
        buttonInfo['description'] = 'set to clamped tangents'
        curveOptionButtons.append(buttonInfo)
        buttonInfo = {}
        buttonInfo['image'] = 'linearTangent.xpm'
        buttonInfo['command'] = partial(Functions.setKeyType, 'linear')
        buttonInfo['description'] = 'set to linear tangents'
        curveOptionButtons.append(buttonInfo)
        buttonInfo = {}
        buttonInfo['image'] = 'flatTangent.xpm'
        buttonInfo['command'] = partial(Functions.setKeyType, 'flat')
        buttonInfo['description'] = 'set to flat tangents'
        curveOptionButtons.append(buttonInfo)
        buttonInfo = {}
        buttonInfo['image'] = 'stepTangent.xpm'
        buttonInfo['command'] = partial(Functions.setKeyType, 'step')
        buttonInfo['description'] = 'set to step tangents'
        curveOptionButtons.append(buttonInfo)
        buttonInfo = {}
        buttonInfo['image'] = 'plateauTangent.xpm'
        buttonInfo['command'] = partial(Functions.setKeyType, 'plateau')
        buttonInfo['description'] = 'set to plateau tangents'
        curveOptionButtons.append(buttonInfo)
        buttonInfo = {}
        buttonInfo['image'] = 'freeTangentWeight.xpm'
        buttonInfo['command'] = partial(Functions.setKeyType, 'free')
        buttonInfo['description'] = 'set to free tangents handles'
        curveOptionButtons.append(buttonInfo)
        buttonObjects = []
        iconSize = 23
        for buttonInfo in curveOptionButtons:
            if buttonInfo == 'CollapseButton':
                command = partial(self.onCollapseButtonPress)
                color = [1] * 3
                self.collapseButton = cmds.button(parent=layoutContainer, label='-', height=iconSize, width=iconSize, command=command, bgc=color, annotation='* Click To Collapse Widget')
                buttonObjects.append(self.collapseButton)
            else:
                buttonImage = buttonInfo['image']
                buttonCommand = buttonInfo['command']
                buttonAnnotation = buttonInfo['description']
                try:
                    newButton = cmds.iconTextButton(parent=layoutContainer, image1=buttonImage, width=iconSize, height=iconSize, command=buttonCommand, ann=buttonAnnotation)
                    buttonObjects.append(newButton)
                except:
                    pass

        buttonCount = len(buttonObjects)
        for i, b in enumerate(buttonObjects):
            leftOffset = i * 100 / buttonCount
            cmds.formLayout(layoutContainer, edit=True, attachForm=[(b, 'top', 0)])
            cmds.formLayout(layoutContainer, edit=True, attachPosition=[(b,
              'left',
              0,
              leftOffset)])
            cmds.formLayout(layoutContainer, edit=True, attachNone=[(b, 'bottom')])
            cmds.formLayout(layoutContainer, edit=True, attachNone=[(b, 'right')])

    def onCollapseButtonPress(self, *args, **kwargs):
        self.collapseMainContainer()


class widget_principles(widget_base):

    def __init__(self, *args, **kwargs):
        parent = False
        if 'parent' in kwargs:
            parent = kwargs.pop('parent')
        description = 'Principles of Animation'
        if 'description' in kwargs:
            description = kwargs.pop('description')
        stateData = {'pinState': False,
         'bufferSelection': [],
         'useAllLayersState': True}
        if 'stateData' in kwargs:
            stateData = kwargs.pop('stateData')
        expandedState = True
        if 'expandedState' in kwargs:
            expandedState = kwargs.pop('expandedState')
        widget_base.__init__(self, parent=parent, description=description, expandedState=expandedState)
        self.setState(stateData)
        self.setupUI()
        self.setDescription(description)
        self.setWidgetType('principles')

    def setupUI(self):
        layoutContainer = self.getLayout()
        infoText = 'Welcome To whisKEY Pro\n\n'
        infoText += '* Right click anywhere to check out the main menu.\n'
        infoText += '\n'
        infoText += 'Principles of Animation'
        infoText += '\n'
        infoText += "1 .Squash'n stretch\n"
        infoText += '2 .Anticipation\n'
        infoText += '3 .Staging\n'
        infoText += '4 .Straight ahead and pose to pose\n'
        infoText += '5 .Follow through and overlap\n'
        infoText += '6 .Spacing\n'
        infoText += '7 .Arcs\n'
        infoText += '8 .Secondary action\n'
        infoText += '9 .Timing\n'
        infoText += '10.Exaggeration\n'
        infoText += '11.Solid drawing\n'
        infoText += '12.Appeal\n'
        infoText += '\n'
        infoText += '\n'
        infoText += 'And dont forget,\n'
        infoText += '      ____ \n'
        infoText += '     |    | ebLabs \n'
        infoText += '     |    | whisKEY Pro\n'
        infoText += '     |____| \n'
        infoText += '     |    | (C)Eric Bates\n'
        infoText += '     (    ) 2015\n'
        infoText += '     )    ( eblabs-tech.com\n'
        infoText += "   .'      `. \n"
        infoText += '  /          \\\n'
        infoText += ' |------------|\n'
        infoText += ' |JACK DANIELS|\n'
        infoText += ' |    ----    |\n'
        infoText += ' |   (No.7)   |\n'
        infoText += ' |    ----    |\n'
        infoText += ' | Tennessee  |\n'
        infoText += ' |  WHISKEY   |\n'
        infoText += ' |  40% Vol.  |\n'
        infoText += ' |------------|\n'
        infoText += ' |____________|\n'
        infoText += '\n'
        self.infoBox = cmds.scrollField(parent=layoutContainer, wordWrap=True, editable=False, text=infoText)
        changeCommand = partial(self.onDescriptionChange)
        collapseCommand = partial(self.collapseMainContainer)
        self.descriptionWidget = button_textToggle(parent=layoutContainer, description=self.getDescription(), collapseCommand=collapseCommand, changeCommand=changeCommand)
        descriptionWidgetLayout = self.descriptionWidget.getLayout()
        cmds.formLayout(layoutContainer, edit=True, height=100)
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(descriptionWidgetLayout, 'top', 0)])
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(descriptionWidgetLayout, 'left', 0)])
        cmds.formLayout(layoutContainer, edit=True, attachNone=[(descriptionWidgetLayout, 'bottom')])
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(descriptionWidgetLayout, 'right', 0)])
        cmds.formLayout(layoutContainer, edit=True, attachControl=[(self.infoBox,
          'top',
          0,
          descriptionWidgetLayout)])
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(self.infoBox, 'left', 0)])
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(self.infoBox, 'bottom', 0)])
        cmds.formLayout(layoutContainer, edit=True, attachForm=[(self.infoBox, 'right', 0)])


class button_toggleSwitch():
    """
    button_toggleSwitch(parent = None, ADescription = '', BDescription = '', ACommand = '', BCommand = '', startState = True)
    """

    def __init__(self, *args, **kwargs):
        state = True
        parent = None
        if 'parent' in kwargs:
            parent = kwargs.pop('parent')
        startState = True
        if 'startState' in kwargs:
            startState = kwargs.pop('startState')
        ADescription = ''
        if 'ADescription' in kwargs:
            ADescription = kwargs.pop('ADescription')
        BDescription = ''
        if 'BDescription' in kwargs:
            BDescription = kwargs.pop('BDescription')
        ACommand = False
        if 'ACommand' in kwargs:
            ACommand = kwargs.pop('ACommand')
        BCommand = False
        if 'BCommand' in kwargs:
            BCommand = kwargs.pop('BCommand')
        width = 75
        if 'width' in kwargs:
            width = kwargs.pop('width')
        height = 18
        if 'height' in kwargs:
            height = kwargs.pop('height')
        if parent:
            cmds.setParent(parent)
        description = ADescription
        self.form = cmds.formLayout(parent=parent, height=height)
        self.toggleButton = cmds.button(recomputeSize=False, width=width, height=1, command=partial(self.pressButton, ADescription, BDescription, ACommand, BCommand))
        self.setState(startState)
        self.pressButton = self.pressButton(ADescription, BDescription, ACommand, BCommand, onInit=True)
        cmds.formLayout(self.form, edit=True, attachForm=[(self.toggleButton, 'top', 0)])
        cmds.formLayout(self.form, edit=True, attachForm=[(self.toggleButton, 'left', 0)])
        cmds.formLayout(self.form, edit=True, attachForm=[(self.toggleButton, 'bottom', 0)])
        cmds.formLayout(self.form, edit=True, attachForm=[(self.toggleButton, 'right', 0)])
        return

    def pressButton(self, ADescription, BDescription, ACommand, BCommand, *args, **kwargs):
        onInit = False
        if 'onInit' in kwargs:
            onInit = kwargs.pop('onInit')
        state = self.getState()
        color = []
        if state:
            color = [0.7, 0.7, 0.7]
            description = ADescription
            command = ACommand
        if not state:
            color = [0.2, 0.2, 0.2]
            description = BDescription
            command = BCommand
        cmds.button(self.toggleButton, edit=True, bgc=color, label=description)
        self.setState(not state)
        if not onInit:
            if command:
                command(onInit=onInit)

    def overrideDescription(self, description, *args, **kwargs):
        cmds.button(self.toggleButton, edit=True, label=description)

    def setState(self, state, *args, **kwargs):
        self.state = state

    def getState(self, *args, **kwargs):
        return self.state

    def getLayout(self, *args, **kwargs):
        return self.form


class button_textToggle():

    def __init__(self, *args, **kwargs):
        parent = None
        if 'parent' in kwargs:
            parent = kwargs.pop('parent')
        self.description = ''
        if 'description' in kwargs:
            self.description = kwargs.pop('description')
        changeCommand = False
        if 'changeCommand' in kwargs:
            changeCommand = kwargs.pop('changeCommand')
        collapseCommand = False
        if 'collapseCommand' in kwargs:
            collapseCommand = kwargs.pop('collapseCommand')
        width = 75
        if 'width' in kwargs:
            width = kwargs.pop('width')
        height = 18
        if 'height' in kwargs:
            height = kwargs.pop('height')
        if parent:
            cmds.setParent(parent)
        self.form = cmds.formLayout(parent=parent, height=height)
        command = partial(partial(self.onCollapseButtonPress, collapseCommand))
        color = [1] * 3
        self.collapseButton = cmds.button(parent=self.form, label='-', height=height, width=height, command=command, bgc=color, annotation='* Click To Collapse Widget')
        self.button = cmds.button(parent=self.form, label=self.description, bgc=[1] * 3, command=partial(self.onButtonPress), height=1)
        self.textField = cmds.textField(parent=self.form, text=self.description, bgc=[0.3] * 3, visible=False, height=1)
        cmds.textField(self.textField, edit=True, alwaysInvokeEnterCommandOnReturn=True)
        cmds.textField(self.textField, edit=True, changeCommand=partial(self.onTextChange, changeCommand=changeCommand))
        cmds.textField(self.textField, edit=True, enterCommand=partial(self.onTextChange, changeCommand=changeCommand))
        cmds.formLayout(self.form, edit=True, attachForm=[(self.collapseButton, 'top', 0)])
        cmds.formLayout(self.form, edit=True, attachForm=[(self.collapseButton, 'left', 0)])
        cmds.formLayout(self.form, edit=True, attachForm=[(self.collapseButton, 'bottom', 0)])
        cmds.formLayout(self.form, edit=True, attachNone=[(self.collapseButton, 'right')])
        cmds.formLayout(self.form, edit=True, attachForm=[(self.button, 'top', 0)])
        cmds.formLayout(self.form, edit=True, attachControl=[(self.button,
          'left',
          0,
          self.collapseButton)])
        cmds.formLayout(self.form, edit=True, attachForm=[(self.button, 'bottom', 0)])
        cmds.formLayout(self.form, edit=True, attachForm=[(self.button, 'right', 0)])
        cmds.formLayout(self.form, edit=True, attachForm=[(self.textField, 'top', 0)])
        cmds.formLayout(self.form, edit=True, attachControl=[(self.textField,
          'left',
          0,
          self.collapseButton)])
        cmds.formLayout(self.form, edit=True, attachForm=[(self.textField, 'bottom', 0)])
        cmds.formLayout(self.form, edit=True, attachForm=[(self.textField, 'right', 0)])
        return

    def onCollapseButtonPress(self, collapseCommand, *args, **kwargs):
        if collapseCommand:
            try:
                collapseCommand()
            except Exception as e:
                print (3915, e)

    def onButtonPress(self, *args, **kwargs):
        cmds.button(self.button, edit=True, visible=False)
        cmds.textField(self.textField, edit=True, visible=True)
        cmds.setFocus(self.textField)

    def onTextChange(self, *args, **kwargs):
        changeCommand = False
        if 'changeCommand' in kwargs:
            changeCommand = kwargs.pop('changeCommand')
        self.description = cmds.textField(self.textField, query=True, text=True)
        self.description = self.validateText(self.description)
        hideCommnad = partial(cmds.textField, self.textField, edit=True, visible=False)
        cmds.evalDeferred(hideCommnad)
        cmds.button(self.button, edit=True, visible=True)
        cmds.button(self.button, edit=True, label=self.description)
        cmds.textField(self.textField, edit=True, visible=True)
        if changeCommand:
            changeCommand(self.description)

    def getLayout(self, *args, **kwargs):
        return self.form

    def getDescription(self):
        return self.description

    def overrideDescription(self, description, *args, **kwargs):
        self.description = description
        cmds.textField(self.textField, edit=True, text=self.description)
        cmds.button(self.button, edit=True, label=self.description)
        hideCommnad = partial(cmds.textField, self.textField, edit=True, visible=False)
        cmds.evalDeferred(hideCommnad)
        cmds.button(self.button, edit=True, visible=True)

    @classmethod
    def validateText(cls, text, *args, **kwargs):
        if not text:
            return False
        validCharacters = ' -_.(){0}{1}'.format(string.ascii_letters, string.digits)
        validatedCharacters = []
        for c in text:
            if c in validCharacters:
                validatedCharacters.append(c)

        validatedText = ''.join(validatedCharacters)
        return validatedText


class slider_base():
    """ Define Common Functions for sliders
    """
    instances = []

    def __init__(self, *args, **kwargs):
        parent = False
        if 'parent' in kwargs:
            parent = kwargs.pop('parent')
        sliderType = 'sliderType'
        if 'sliderType' in kwargs:
            sliderType = kwargs.pop('sliderType')
        self.showMultiplier = False
        if 'showMultiplier' in kwargs:
            self.showMultiplier = kwargs.pop('showMultiplier')
        self.setMultiplier(1.0)
        self.instances.append(self)
        self.setSliderType(sliderType)
        self.formLayout = cmds.formLayout(parent=parent, bgc=[0.95] * 3)
        buttonBGC = [0.95] * 3
        self.slider = cmds.floatSlider(parent=self.formLayout, width=5, min=-1, max=1, value=0, step=0.1, dragCommand=partial(self.slider_realtime_modifiers, fromCurrentValue=True), changeCommand=partial(self.slider_realtime_finish_modifiers), bgc=buttonBGC)
        if self.showMultiplier:
            popupMenu = cmds.popupMenu(parent=self.slider)
            cmds.popupMenu(popupMenu, edit=True, postMenuCommand=partial(self.multiplierPopupMenu, parent=popupMenu))
        cmds.formLayout(self.formLayout, edit=True, attachForm=[(self.slider, 'top', 0)])
        cmds.formLayout(self.formLayout, edit=True, attachForm=[(self.slider, 'left', 0)])
        cmds.formLayout(self.formLayout, edit=True, attachForm=[(self.slider, 'bottom', 0)])
        cmds.formLayout(self.formLayout, edit=True, attachForm=[(self.slider, 'right', 0)])
        self.enableSlider = True

    @classmethod
    def clearInstances(cls):
        cls.instances = []

    def setSliderState(self, state, *args, **kwargs):
        cmds.floatSlider(self.slider, edit=True, enable=state)

    def multiplierPopupMenu(self, *args, **kwargs):
        parent = False
        if 'parent' in kwargs:
            parent = kwargs.pop('parent')
        cmds.popupMenu(parent, edit=True, deleteAllItems=True)
        cmds.setParent(parent, menu=True)
        multiplier = self.getMultiplier()
        powerMessage = 'Current Power: x{0:.2f}'.format(round(multiplier, 2))
        cmds.menuItem(parent=parent, label=powerMessage)
        cmds.menuItem(parent=parent, label='Increase Power', command=partial(self.increaseMultiplier))
        cmds.menuItem(parent=parent, label='Decrease Power', command=partial(self.decreaseMultiplier))
        cmds.menuItem(parent=parent, label='Reset Power', command=partial(self.resetMultiplier))

    def increaseMultiplier(self, *args, **kwargs):
        self.multiplier = self.multiplier * 2
        if self.multiplier == 0:
            self.multiplier = 1

    def decreaseMultiplier(self, *args, **kwargs):
        self.multiplier = self.multiplier / 2
        if self.multiplier == 0:
            self.multiplier = 1

    def resetMultiplier(self, value, *args, **kwargs):
        self.multiplier = 1

    def setMultiplier(self, value, *args, **kwargs):
        self.multiplier = value

    def getMultiplier(self, *args, **kwargs):
        try:
            self.multiplier
        except:
            self.multiplier = 1

        return self.multiplier

    def useSetValueCommand(self, *args, **kwargs):
        try:
            self.slider_realtime(useSetValue=True)
        except Exception as e:
            print (444, Exception, e)
        finally:
            self.slider_realtime_finish()

    def presetCommand(self, value, *args, **kwargs):
        try:
            self.slider_realtime(overrideRatio=value)
        except Exception as e:
            print (444, Exception, e)
        finally:
            self.slider_realtime_finish()

    def getBufferSelection(self):
        try:
            self.bufferSelection
        except:
            self.bufferSelection = []

        return self.bufferSelection

    def setBufferSelection(self, selection):
        if selection:
            self.bufferSelection = selection

    def getSelectedChannels(self, *args, **kwargs):
        """
        overwrite this in widgets if needed
        """
        selection = Functions.getSelectedChannels(*args, **kwargs)
        return selection

    def getSelected(self):
        selection = []
        if self.pinState:
            selection = self.bufferSelection
        else:
            selection = cmds.ls(sl=True, type=['transform', 'joint'])
        return selection

    def setBufferChannels(self, selection):
        self.bufferChannels = selection

    def getBufferChannels(self):
        try:
            self.bufferChannels
        except:
            self.bufferChannels = []

        return self.bufferChannels

    def setPinState(self, state):
        self.pinState = state

    def getPinState(self):
        try:
            self.pinState
        except:
            self.pinState = False

        return self.pinState

    def setUseAllLayersState(self, state):
        self.useAllLayersState = state

    def getUseAllLayersState(self):
        try:
            self.useAllLayersState
        except:
            self.useAllLayersState = True

        return self.useAllLayersState

    def addPostCommand(self, command, *args, **kwargs):
        try:
            self.postCommands
        except:
            self.postCommands = []

        if command:
            self.postCommands.append(command)

    def clearPostCommands(self, *args, **kwargs):
        self.postCommands = []

    def onPost(self, *args, **kwargs):
        try:
            self.postCommands
        except:
            self.postCommands = []

        for c in self.postCommands:
            c()

    def addPreCommand(self, command, *args, **kwargs):
        try:
            self.preCommands
        except:
            self.preCommands = []

        if command:
            self.preCommands.append(command)

    def clearPreCommands(self, *args, **kwargs):
        self.preCommands = []

    def onPre(self, *args, **kwargs):
        try:
            self.preCommands
        except:
            self.preCommands = []

        for c in self.preCommands:
            c()

    def addChangeCommand(self, command, *args, **kwargs):
        try:
            self.changeCommands
        except:
            self.changeCommands = []

        if command:
            self.changeCommands.append(command)

    def clearChangeCommands(self, *args, **kwargs):
        self.changeCommands = []

    def onChange(self, debug = False, *args, **kwargs):
        if debug:
            print (debug, len(self.changeCommands))
        try:
            self.multiplierChangeCommands
        except Exception as e:
            self.multiplierChangeCommands = []

        for c in self.multiplierChangeCommands:
            c()

    def addMultiplierChangeCommand(self, command, *args, **kwargs):
        try:
            self.multiplierChangeCommands
        except:
            self.multiplierChangeCommands = []

        if command:
            self.multiplierChangeCommands.append(command)

    def clearMultiplierChangeCommands(self, *args, **kwargs):
        self.multiplierChangeCommands = []

    def onMultiplierChange(self, debug = False, *args, **kwargs):
        if debug:
            print (debug, len(self.multiplierChangeCommands))
        try:
            self.multiplierChangeCommands
        except Exception as e:
            self.multiplierChangeCommands = []

        value = self.getSliderValue()
        for c in self.multiplierChangeCommands:
            c(value)

    def addMultiplierPostCommand(self, command, *args, **kwargs):
        try:
            self.multiplierPostCommands
        except:
            self.multiplierPostCommands = []

        if command:
            self.multiplierPostCommands.append(command)

    def clearMultiplierPostCommands(self, *args, **kwargs):
        self.multiplierPostCommands = []

    def onMultiplierPost(self, debug = False, *args, **kwargs):
        if debug:
            print (debug, len(self.multiplierPostCommands))
        try:
            self.multiplierPostCommands
        except Exception as e:
            self.multiplierPostCommands = []

        value = self.getSliderValue()
        for c in self.multiplierPostCommands:
            c(value)

    def getSliderType(self):
        return self.sliderType

    def getLayout(self):
        return self.formLayout

    def collectData(self):
        """
        This will get overwritten to collect data specific to each widget
        """
        pass

    def clearData(self):
        self.data = {}

    def getSliderValue(self):
        """
        return the slider value
        """
        value = cmds.floatSlider(self.slider, query=True, value=True)
        return value

    def slider_exec(self, *args, **kwargs):
        """
        This will perform the actual execution of the data and slider
        """
        useSetValue = False
        if 'useSetValue' in kwargs:
            useSetValue = kwargs.pop('useSetValue')
        overrideRatio = False
        if 'overrideRatio' in kwargs:
            overrideRatio = kwargs.pop('overrideRatio')
        fromCurrentValue = False
        if 'fromCurrentValue' in kwargs:
            fromCurrentValue = kwargs.pop('fromCurrentValue')
        data = self.data
        if data:
            sliderValue = self.getSliderValue()
            if type(overrideRatio) != bool:
                sliderValue = overrideRatio
            sliderValue = Functions.clamp(sliderValue, -1, 1)
            sliderPos = Functions.clamp(sliderValue, 0, 1)
            sliderNeg = abs(Functions.clamp(sliderValue, -1, 0))
            ratio = (sliderValue + 1) / 2
            ratioInverted = 1 - ratio
            sliderMult = 1.0
            for a in data.keys():
                isBoring = True
                try:
                    isBoring = data[a]['isBoring']
                except:
                    pass

                if not isBoring:
                    isIgnored = data[a]['isIgnored']
                    if not isIgnored:
                        prevValue = data[a]['prevValue']
                        nextValue = data[a]['nextValue']
                        currentValue = data[a]['currentValue']
                        setValue = data[a]['setValue']
                        attributeType = data[a]['type']
                        newValue = 0
                        if useSetValue:
                            newValue = setValue
                        elif attributeType != 'enum':
                            if fromCurrentValue:
                                newValue = currentValue + (prevValue - currentValue) * sliderNeg + (nextValue - currentValue) * sliderPos
                            else:
                                newValue = prevValue * ratioInverted + nextValue * ratio
                        elif fromCurrentValue:
                            if sliderValue > 0.5:
                                newValue = nextValue
                            elif sliderValue < -0.5:
                                newValue = prevValue
                            else:
                                newValue = currentValue
                        elif sliderValue >= 0:
                            newValue = nextValue
                        elif sliderValue < 0:
                            newValue = prevValue
                        else:
                            newValue = currentValue
                        if newValue != currentValue:
                            cmds.setAttr(a, newValue, clamp=True)

    def slider_realtime_modifiers(self, *args, **kwargs):
        try:
            self.modifierChecked
        except:
            self.modifierChecked = False

        if not self.modifierChecked:
            self.mods = cmds.getModifiers()
            self.modifierChecked = True
        if self.showMultiplier and self.mods & 4 > 0:
            self.editMultiplier_realtime()
        else:
            self.slider_realtime(*args, **kwargs)

    def slider_realtime(self, *args, **kwargs):
        useSetValue = False
        if 'useSetValue' in kwargs:
            useSetValue = kwargs.pop('useSetValue')
        overrideRatio = False
        if 'overrideRatio' in kwargs:
            overrideRatio = kwargs.pop('overrideRatio')
        fromCurrentValue = False
        if 'fromCurrentValue' in kwargs:
            fromCurrentValue = kwargs.pop('fromCurrentValue')
        self.slider_realtime_standard(useSetValue=useSetValue, overrideRatio=overrideRatio, fromCurrentValue=fromCurrentValue)

    def slider_realtime_finish_modifiers(self, *args, **kwargs):
        self.modifierChecked = False
        if self.showMultiplier and self.mods & 4 > 0:
            self.editMultiplier_finish()
        else:
            self.slider_realtime_finish(*args, **kwargs)

    def editMultiplier_realtime(self, *args, **kwargs):
        value = ((self.getSliderValue() + 1) / 2) ** 2 * 10
        self.setMultiplier(value)
        self.onMultiplierChange()

    def editMultiplier_finish(self, *args, **kwargs):
        self.resetSlider()
        self.onMultiplierPost()

    def slider_realtime_finish(self, *args, **kwargs):
        self.slider_realtime_finish_standard()

    def slider_realtime_standard(self, *args, **kwargs):
        """
        This will be the main realtime slider system
        """
        useSetValue = False
        if 'useSetValue' in kwargs:
            useSetValue = kwargs.pop('useSetValue')
        overrideRatio = False
        if 'overrideRatio' in kwargs:
            overrideRatio = kwargs.pop('overrideRatio')
        fromCurrentValue = False
        if 'fromCurrentValue' in kwargs:
            fromCurrentValue = kwargs.pop('fromCurrentValue')
        try:
            self.isFirstLoop
        except:
            self.isFirstLoop = True

        if self.enableSlider:
            if self.isFirstLoop:
                cmds.undoInfo(openChunk=True)
                self.autoKeyState = cmds.autoKeyframe(query=True, state=True)
                cmds.autoKeyframe(edit=True, state=False)
                self.isFirstLoop = False
                self.collectData()
            self.slider_exec(useSetValue=useSetValue, overrideRatio=overrideRatio, fromCurrentValue=fromCurrentValue)

    def slider_realtime_finish_standard(self, *args, **kwargs):
        """
        This will close the realtime slider functionality
        """
        self.isFirstLoop = True
        if self.autoKeyState:
            self.keyAll()
            cmds.autoKeyframe(edit=True, state=True)
        cmds.undoInfo(closeChunk=True)
        self.resetSlider()

    def keyAll(self, *args, **kwargs):
        keyableList = list(self.data.keys())
        if keyableList:
            cmds.setKeyframe(keyableList)

    def resetSlider(self):
        cmds.floatSlider(self.slider, edit=True, value=0)

    def setSliderType(self, sliderType):
        self.sliderType = sliderType


class slider_tween(slider_base):

    def __init__(self, *args, **kwargs):
        parent = False
        if 'parent' in kwargs:
            parent = kwargs.pop('parent')
        sliderType = 'tweenSlider'
        slider_base.__init__(self, parent=parent, sliderType=sliderType)

    def collectData(self):
        """
        structure
        object.attribute
                     >prevValue
                     >nextValue
                     >currentValue
                     >type
                     >setValue
                     >isBoring
                     >isIgnored
        
        """
        cmds.waitCursor(state=True)
        data = {}
        try:
            selection = self.getSelected()
            selectedChannels = self.getSelectedChannels(selection=selection)
            currentTime = cmds.currentTime(query=True)
            for s in selection:
                keyableAttributes = Functions.listAttributes(s)
                if keyableAttributes:
                    for a in keyableAttributes:
                        if selectedChannels and a in selectedChannels or not selectedChannels:
                            attribute = '{0}.{1}'.format(s, a)
                            data[attribute] = {}
                            keyFrameCount = cmds.keyframe(attribute, query=True, keyframeCount=True)
                            isBoring = False
                            if not keyFrameCount >= 2:
                                isBoring = True
                            if not isBoring:
                                currentValue = cmds.getAttr(attribute, time=currentTime)
                                prevKeyFrame = cmds.findKeyframe(s, which='previous', at=a)
                                nextKeyFrame = cmds.findKeyframe(s, which='next', at=a)
                                prevValue = cmds.getAttr(attribute, t=prevKeyFrame)
                                nextValue = cmds.getAttr(attribute, t=nextKeyFrame)
                                if prevValue == nextValue == currentValue:
                                    isBoring = True
                                if not isBoring:
                                    minTime = prevKeyFrame
                                    maxTime = nextKeyFrame
                                    midTime = Functions.clamp(currentTime, minTime, maxTime)
                                    timeRange = maxTime - minTime
                                    ratio = 0.5
                                    if timeRange != 0:
                                        ratio = (midTime - minTime) / (maxTime - minTime)
                                    ratioInverted = 1 - ratio
                                    setValue = prevValue * ratioInverted + nextValue * ratio
                                    isIgnored = False
                                    data[attribute]['prevValue'] = prevValue
                                    data[attribute]['nextValue'] = nextValue
                                    data[attribute]['currentValue'] = currentValue
                                    data[attribute]['type'] = Functions.getAttributeType(s, a)
                                    data[attribute]['setValue'] = setValue
                                    data[attribute]['isBoring'] = isBoring
                                    data[attribute]['isIgnored'] = isIgnored

        except Exception as e:
            print (traceback.format_exc())
            print (1146, Exception, e)
        finally:
            self.data = data
            cmds.waitCursor(state=False)

    def slider_realtime(self, *args, **kwargs):
        useSetValue = False
        if 'useSetValue' in kwargs:
            useSetValue = kwargs.pop('useSetValue')
        overrideRatio = False
        if 'overrideRatio' in kwargs:
            overrideRatio = kwargs.pop('overrideRatio')
        fromCurrentValue = False
        if 'fromCurrentValue' in kwargs:
            fromCurrentValue = kwargs.pop('fromCurrentValue')
        if self.getUseAllLayersState():
            self.slider_realtime_standard(useSetValue=useSetValue, overrideRatio=overrideRatio, fromCurrentValue=fromCurrentValue)
        else:
            self.slider_realtime_layers(useSetValue=useSetValue, overrideRatio=overrideRatio, fromCurrentValue=fromCurrentValue)

    def slider_realtime_finish(self, *args, **kwargs):
        if self.getUseAllLayersState():
            self.slider_realtime_finish_standard()
        else:
            self.slider_realtime_finish_layers()

    def slider_realtime_layers(self, *args, **kwargs):
        """
        This will be the main realtime slider system
        """
        useSetValue = False
        if 'useSetValue' in kwargs:
            useSetValue = kwargs.pop('useSetValue')
        overrideRatio = False
        if 'overrideRatio' in kwargs:
            overrideRatio = kwargs.pop('overrideRatio')
        fromCurrentValue = False
        if 'fromCurrentValue' in kwargs:
            fromCurrentValue = kwargs.pop('fromCurrentValue')
        try:
            self.isFirstLoop
        except:
            self.isFirstLoop = True

        if self.enableSlider:
            if self.isFirstLoop:
                cmds.undoInfo(openChunk=True)
                self.autoKeyState = cmds.autoKeyframe(query=True, state=True)
                cmds.autoKeyframe(edit=True, state=False)
                self.isFirstLoop = False
                self.collectData_layers()
            self.slider_exec_layers(useSetValue=useSetValue, overrideRatio=overrideRatio, fromCurrentValue=fromCurrentValue)

    def slider_realtime_finish_layers(self, *args, **kwargs):
        """
        This will close the realtime slider functionality
        """
        self.isFirstLoop = True
        if self.autoKeyState:
            self.keyAll()
            cmds.autoKeyframe(edit=True, state=True)
        cmds.undoInfo(closeChunk=True)
        self.resetSlider()

    def collectData_layers(self):
        """
        structure, list of actual anim curve nodes
        object_attribute
                     >prevValue
                     >nextValue
                     >currentValue
                     >setValue
                     >isBoring
                     >isIgnored
        
        """
        cmds.waitCursor(state=True)
        data = {}
        try:
            selection = self.getSelected()
            selectedChannels = self.getSelectedChannels(selection=selection)
            currentTime = cmds.currentTime(query=True)
            for s in selection:
                keyableAttributes = Functions.listAttributes(s)
                for a in keyableAttributes:
                    if selectedChannels and a in selectedChannels or not selectedChannels:
                        attribute = '{0}.{1}'.format(s, a)
                        curveNode = cmds.keyframe(attribute, query=True, name=True)[0]
                        curveNode_output = '{0}.{1}'.format(curveNode, 'output')
                        data[curveNode] = {}
                        isBoring = False
                        if curveNode:
                            keyFrameCount = cmds.keyframe(curveNode, query=True, keyframeCount=True)
                            if not keyFrameCount >= 2:
                                isBoring = True
                            if not isBoring:
                                currentValue = cmds.getAttr(curveNode_output, time=currentTime)
                                prevKeyFrame = cmds.findKeyframe(curveNode, which='previous')
                                nextKeyFrame = cmds.findKeyframe(curveNode, which='next')
                                prevValue = cmds.getAttr(curveNode_output, t=prevKeyFrame)
                                nextValue = cmds.getAttr(curveNode_output, t=nextKeyFrame)
                                if prevValue == nextValue == currentValue:
                                    isBoring = True
                                if not isBoring:
                                    minTime = prevKeyFrame
                                    maxTime = nextKeyFrame
                                    midTime = Functions.clamp(currentTime, minTime, maxTime)
                                    ratio = (midTime - minTime) / (maxTime - minTime)
                                    ratioInverted = 1 - ratio
                                    setValue = prevValue * ratioInverted + nextValue * ratio
                                    isIgnored = False
                                    keyTimeList = cmds.keyframe(curveNode, query=True)
                                    if currentTime not in keyTimeList:
                                        cmds.setKeyframe(curveNode)
                                    keyTimeList = cmds.keyframe(curveNode, query=True)
                                    index = keyTimeList.index(currentTime)
                                    data[curveNode]['index'] = index
                                    data[curveNode]['prevValue'] = prevValue
                                    data[curveNode]['nextValue'] = nextValue
                                    data[curveNode]['currentValue'] = currentValue
                                    data[curveNode]['type'] = Functions.getAttributeType(s, a)
                                    data[curveNode]['setValue'] = setValue
                                    data[curveNode]['isBoring'] = isBoring
                                    data[curveNode]['isIgnored'] = isIgnored

        except Exception as e:
            print (565, Exception, e)
        finally:
            self.data = data
            cmds.waitCursor(state=False)

    def slider_exec_layers(self, *args, **kwargs):
        """
        This will perform the actual execution of the data and slider
        """
        useSetValue = False
        if 'useSetValue' in kwargs:
            useSetValue = kwargs.pop('useSetValue')
        overrideRatio = False
        if 'overrideRatio' in kwargs:
            overrideRatio = kwargs.pop('overrideRatio')
        fromCurrentValue = False
        if 'fromCurrentValue' in kwargs:
            fromCurrentValue = kwargs.pop('fromCurrentValue')
        sliderValue = self.getSliderValue()
        if overrideRatio:
            sliderValue = overrideRatio
        sliderValue = Functions.clamp(sliderValue, -1, 1)
        sliderPos = Functions.clamp(sliderValue, 0, 1)
        sliderNeg = abs(Functions.clamp(sliderValue, -1, 0))
        ratio = (sliderValue + 1) / 2
        ratioInverted = 1 - ratio
        sliderMult = 1.0
        data = self.data
        currentTime = cmds.currentTime(query=True)
        if data:
            for curveNode in data.keys():
                isBoring = True
                try:
                    isBoring = data[curveNode]['isBoring']
                except:
                    pass

                if not isBoring:
                    isIgnored = data[curveNode]['isIgnored']
                    if not isIgnored:
                        prevValue = data[curveNode]['prevValue']
                        nextValue = data[curveNode]['nextValue']
                        currentValue = data[curveNode]['currentValue']
                        setValue = data[curveNode]['setValue']
                        index = data[curveNode]['index']
                        attributeType = data[curveNode]['type']
                        newValue = 0
                        if useSetValue:
                            newValue = setValue
                        elif attributeType != 'enum':
                            if fromCurrentValue:
                                newValue = currentValue + (prevValue - currentValue) * sliderNeg + (nextValue - currentValue) * sliderPos
                            else:
                                newValue = prevValue * ratioInverted + nextValue * ratio
                        elif fromCurrentValue:
                            if sliderValue > 0.5:
                                newValue = nextValue
                            elif sliderValue < -0.5:
                                newValue = prevValue
                            else:
                                newValue = currentValue
                        elif sliderValue >= 0:
                            newValue = nextValue
                        elif sliderValue < 0:
                            newValue = prevValue
                        else:
                            newValue = currentValue
                        if newValue != currentValue:
                            cmds.setAttr('{0}.keyTimeValue[{1}].keyValue'.format(curveNode, index), newValue)


class slider_snapshot(slider_base):

    def __init__(self, *args, **kwargs):
        parent = False
        if 'parent' in kwargs:
            parent = kwargs.pop('parent')
        sliderType = 'snapshotSlider'
        slider_base.__init__(self, parent=parent, sliderType=sliderType)
        cmds.floatSlider(self.slider, edit=True, min=0, max=1)

    def collectData(self):
        """
        rebuild new data from snapshot data
        """
        data = {}
        snapshotData = self.getSnapshotData()
        if snapshotData:
            selection = cmds.ls(sl=True)
            selectedNamespaces = set(Functions.getNamespaces(nodes=selection))
            snapshotDataNodes = snapshotData.keys()
            snapShotDataNamespaceList = set(Functions.getNamespaces(nodes=snapshotDataNodes))
            remapLookup = {}
            for snapshotNode in snapshotDataNodes:
                remapLookup[snapshotNode] = []
                if not selection or selectedNamespaces == snapShotDataNamespaceList:
                    remapLookup[snapshotNode] = [snapshotNode]
                elif selectedNamespaces != snapShotDataNamespaceList:
                    remapLookup[snapshotNode] = Functions.findMatchingObjectsInNamespace(node=snapshotNode, namespaces=selectedNamespaces)

            cmds.waitCursor(state=True)
            data = {}
            try:
                selection = cmds.ls(sl=True)
                selectedChannels = self.getSelectedChannels(selection=selection)
                currentTime = cmds.currentTime(query=True)
                for snapshotNode in remapLookup.keys():
                    for s in remapLookup[snapshotNode]:
                        keyableAttributes = Functions.listAttributes(s, filterEnums=False)
                        snapshotDataAttributes = snapshotData[snapshotNode].keys()
                        commonAttributes = list(set(keyableAttributes) & set(snapshotDataAttributes))
                        if commonAttributes:
                            for a in commonAttributes:
                                if selectedChannels and a in selectedChannels or not selectedChannels:
                                    attribute = '{0}.{1}'.format(s, a)
                                    data[attribute] = {}
                                    isBoring = False
                                    if not isBoring:
                                        currentValue = cmds.getAttr(attribute, time=currentTime)
                                        prevValue = False
                                        nextValue = snapshotData[snapshotNode][a]['nextValue']
                                        if currentValue == nextValue:
                                            isBoring = True
                                        if not isBoring:
                                            setValue = False
                                            isIgnored = False
                                            data[attribute]['prevValue'] = prevValue
                                            data[attribute]['nextValue'] = nextValue
                                            data[attribute]['currentValue'] = currentValue
                                            data[attribute]['type'] = Functions.getAttributeType(s, a)
                                            data[attribute]['setValue'] = setValue
                                            data[attribute]['isBoring'] = isBoring
                                            data[attribute]['isIgnored'] = isIgnored

            except Exception as e:
                print (4255, Exception, e)
            finally:
                self.data = data
                cmds.waitCursor(state=False)

    def collectSnapshotData(self):
        """
        object
                >attribute
                     >prevValue
                     >nextValue
                     >currentValue
                     >setValue
                     >isBoring
                     >isIgnored
        
        """
        cmds.waitCursor(state=True)
        data = {}
        try:
            selection = self.getSelected()
            if selection:
                selectedChannels = self.getSelectedChannels(selection=selection)
                currentTime = cmds.currentTime(query=True)
                for s in selection:
                    data[s] = {}
                    keyableAttributes = Functions.listAttributes(s, filterEnums=False)
                    if keyableAttributes:
                        for a in keyableAttributes:
                            if selectedChannels and a in selectedChannels or not selectedChannels:
                                attribute = '{0}.{1}'.format(s, a)
                                data[s][a] = {}
                                isBoring = False
                                if not isBoring:
                                    currentValue = False
                                    prevKeyFrame = False
                                    nextKeyFrame = cmds.findKeyframe(s, which='next', at=a)
                                    prevValue = False
                                    nextValue = cmds.getAttr(attribute, t=currentTime)
                                    if not isBoring:
                                        setValue = False
                                        isIgnored = False
                                        data[s][a]['prevValue'] = prevValue
                                        data[s][a]['nextValue'] = nextValue
                                        data[s][a]['currentValue'] = currentValue
                                        data[s][a]['setValue'] = setValue
                                        data[s][a]['isBoring'] = isBoring
                                        data[s][a]['isIgnored'] = isIgnored

        except Exception as e:
            print (4937, e)
        finally:
            self.setSnapshotData(data)
            cmds.waitCursor(state=False)

    def setSnapshotData(self, data):
        self.snapShotData = data

    def getSnapshotData(self):
        try:
            self.snapShotData
        except:
            self.snapShotData = {}

        return self.snapShotData


class slider_worldSpace(slider_base):

    def __init__(self, *args, **kwargs):
        parent = False
        if 'parent' in kwargs:
            parent = kwargs.pop('parent')
        sliderType = 'tweenSlider'
        slider_base.__init__(self, parent=parent, sliderType=sliderType)

    def collectData(self):
        """
        structure
        object.attribute
                     >prevValue
                     >nextValue
                     >currentValue
                     >type
                     >setValue
                     >isBoring
                     >isIgnored
        
        """
        cmds.waitCursor(state=True)
        data = {}
        try:
            selection = self.getSelected()
            selectedChannels = self.getSelectedChannels(selection=selection)
            currentTime = cmds.currentTime(query=True)
            translateAttributes = ['tx', 'ty', 'tz']
            rotateAttributes = ['rx', 'ry', 'rz']
            transformAttributes = translateAttributes + rotateAttributes
            if selection:
                for s in selection:
                    keyableAttributes = Functions.listAttributes(s)
                    isBoring = False
                    for a in transformAttributes:
                        attribute = '{0}.{1}'.format(s, a)
                        keyFrameCount = cmds.keyframe(attribute, query=True, keyframeCount=True)
                        isBoring = True
                        if keyFrameCount and keyFrameCount >= 1:
                            isBoring = False
                            break

                    if not isBoring:
                        prevKeyFrame = cmds.findKeyframe(s, which='previous', at=transformAttributes)
                        nextKeyFrame = cmds.findKeyframe(s, which='next', at=transformAttributes)
                        prevKeyFrame = min(prevKeyFrame, currentTime)
                        nextKeyFrame = max(nextKeyFrame, currentTime)
                        prev_worldMatrix = OpenMaya.MMatrix(cmds.getAttr(s + '.worldMatrix', time=prevKeyFrame))
                        curr_worldMatrix = OpenMaya.MMatrix(cmds.getAttr(s + '.worldMatrix', time=currentTime))
                        next_worldMatrix = OpenMaya.MMatrix(cmds.getAttr(s + '.worldMatrix', time=nextKeyFrame))
                        current_ParentMatrix = OpenMaya.MMatrix(cmds.getAttr(s + '.parentInverseMatrix', time=currentTime))
                        prev_localMatrix = prev_worldMatrix * current_ParentMatrix
                        curr_localMatrix = curr_worldMatrix * current_ParentMatrix
                        next_localMatrix = next_worldMatrix * current_ParentMatrix
                        prev_localValues = Functions.decompMatrix(s, prev_localMatrix)
                        curr_localValues = Functions.decompMatrix(s, curr_localMatrix)
                        next_localValues = Functions.decompMatrix(s, next_localMatrix)
                        for i, a in enumerate(transformAttributes):
                            if a in keyableAttributes:
                                if selectedChannels and a in selectedChannels or not selectedChannels:
                                    if not prev_localValues[i] == curr_localValues[i] == next_localValues[i]:
                                        attribute = '{0}.{1}'.format(s, a)
                                        data[attribute] = {}
                                        prevValue = prev_localValues[i]
                                        currValue = curr_localValues[i]
                                        nextValue = next_localValues[i]
                                        minTime = prevKeyFrame
                                        maxTime = nextKeyFrame
                                        midTime = Functions.clamp(currentTime, minTime, maxTime)
                                        ratio = (midTime - minTime) / (maxTime - minTime)
                                        ratioInverted = 1 - ratio
                                        setValue = prevValue * ratioInverted + nextValue * ratio
                                        isIgnored = False
                                        data[attribute]['prevValue'] = prevValue
                                        data[attribute]['nextValue'] = nextValue
                                        data[attribute]['currentValue'] = currValue
                                        data[attribute]['type'] = False
                                        data[attribute]['setValue'] = setValue
                                        data[attribute]['isBoring'] = isBoring
                                        data[attribute]['isIgnored'] = isIgnored

        except Exception as e:
            print (traceback.format_exc())
            print (5495, Exception, e)
            cmds.select(clear=True)
        finally:
            self.data = data
            cmds.waitCursor(state=False)


class slider_inOut(slider_base):

    def __init__(self, *args, **kwargs):
        parent = False
        if 'parent' in kwargs:
            parent = kwargs.pop('parent')
        sliderType = 'inOutSlider'
        showMultiplier = True
        slider_base.__init__(self, parent=parent, sliderType=sliderType, showMultiplier=showMultiplier)
        self.setMultiplier(1.0)

    def collectData(self):
        """
        structure
        object.attribute
                     >prevValue
                     >nextValue
                     >currentValue
                     >type
                     >setValue
                     >isBoring
                     >isIgnored
        
        """
        cmds.waitCursor(state=True)
        data = {}
        multiplier = self.getMultiplier() * 3
        try:
            selection = self.getSelected()
            activeCamera = Functions.getActiveCamera()
            selectedChannels = self.getSelectedChannels(selection=selection)
            limitedAttributes = ['tx', 'ty', 'tz']
            averageBoundingBoxSize = Functions.getAverageBoundingBoxSize(selection) * multiplier
            if selection and activeCamera:
                worldMatrixCamera = OpenMaya.MMatrix(cmds.getAttr(activeCamera + '.worldMatrix'))
                worldSpaceCamera = Functions.decompMatrix(activeCamera, worldMatrixCamera)
                for s in selection:
                    keyableAttributes_raw = Functions.listAttributes(s)
                    keyableAttributes = list(set(keyableAttributes_raw) & set(limitedAttributes))
                    if selectedChannels:
                        keyableAttributes = list(set(keyableAttributes) & set(selectedChannels))
                    if keyableAttributes:
                        isBoring = False
                        worldMatrix = OpenMaya.MMatrix(cmds.getAttr(s + '.worldMatrix'))
                        worldSpaceVectorCurrent = OpenMaya.MVector(Functions.decompMatrix(s, worldMatrix)[:3])
                        cameraVector = OpenMaya.MVector(worldSpaceVectorCurrent[0] - worldSpaceCamera[0], worldSpaceVectorCurrent[1] - worldSpaceCamera[1], worldSpaceVectorCurrent[2] - worldSpaceCamera[2])
                        cameraVector = cameraVector.normal() * averageBoundingBoxSize
                        worldSpaceVectorIn = worldSpaceVectorCurrent + cameraVector
                        worldSpaceVectorOut = worldSpaceVectorCurrent - cameraVector
                        attribute = '{0}.{1}'.format(s, 'tx')
                        localSpaceCurrentX = cmds.getAttr(attribute)
                        attribute = '{0}.{1}'.format(s, 'ty')
                        localSpaceCurrentY = cmds.getAttr(attribute)
                        attribute = '{0}.{1}'.format(s, 'tz')
                        localSpaceCurrentZ = cmds.getAttr(attribute)
                        localSpaceCurrent = [localSpaceCurrentX, localSpaceCurrentY, localSpaceCurrentZ]
                        localSpaceCurrent = Functions.worldToLocalPoint(worldSpaceVectorCurrent, s)
                        localSpaceIn = Functions.worldToLocalPoint(worldSpaceVectorIn, s)
                        localSpaceOut = Functions.worldToLocalPoint(worldSpaceVectorOut, s)
                        for a in keyableAttributes:
                            indexLookup = limitedAttributes.index(a)
                            prevValue = localSpaceIn[indexLookup]
                            currValue = localSpaceCurrent[indexLookup]
                            nextValue = localSpaceOut[indexLookup]
                            if not prevValue == currValue == nextValue:
                                attribute = '{0}.{1}'.format(s, a)
                                data[attribute] = {}
                                setValue = 0
                                isIgnored = False
                                data[attribute]['prevValue'] = prevValue
                                data[attribute]['nextValue'] = nextValue
                                data[attribute]['currentValue'] = currValue
                                data[attribute]['type'] = False
                                data[attribute]['setValue'] = setValue
                                data[attribute]['isBoring'] = isBoring
                                data[attribute]['isIgnored'] = isIgnored

        except Exception as e:
            print (traceback.format_exc())
            print (5633, Exception, e)
        finally:
            self.data = data
            cmds.waitCursor(state=False)


class slider_PosePusher(slider_base):

    def __init__(self, *args, **kwargs):
        parent = False
        if 'parent' in kwargs:
            parent = kwargs.pop('parent')
        sliderType = 'posePusherSlider'
        showMultiplier = True
        slider_base.__init__(self, parent=parent, sliderType=sliderType, showMultiplier=showMultiplier)
        self.setMultiplier(1.0)

    def collectData(self):
        """
        structure
        object.attribute
                     >prevValue
                     >nextValue
                     >currentValue
                     >type                                          
                     >setValue
                     >isBoring
                     >isIgnored
        
        """
        cmds.waitCursor(state=True)
        data = {}
        multiplier = self.getMultiplier() * 5
        try:
            selection = self.getSelected()
            selectedChannels = self.getSelectedChannels(selection=selection)
            currentTime = cmds.currentTime(query=True)
            for s in selection:
                keyableAttributes = Functions.listAttributes(s)
                if keyableAttributes:
                    for a in keyableAttributes:
                        if selectedChannels and a in selectedChannels or not selectedChannels:
                            attribute = '{0}.{1}'.format(s, a)
                            data[attribute] = {}
                            keyFrameCount = cmds.keyframe(attribute, query=True, keyframeCount=True)
                            isBoring = False
                            if not keyFrameCount >= 2:
                                isBoring = True
                            if not isBoring:
                                currentValue = cmds.getAttr(attribute, time=currentTime)
                                midValue = float(currentValue)
                                midTime = currentTime
                                previousLookup = -1
                                nextLookup = 1
                                midLookup = False
                                relativePosition = Functions.getRelativePosition(s, a, currentTime)
                                if relativePosition == 'Before':
                                    midLookup = 1
                                    previousLookup = 1
                                    nextLookup = 2
                                if relativePosition == 'After':
                                    midLookup = -1
                                    previousLookup = -2
                                    nextLookup = -1
                                prevKeyTime, prevValueRaw = Functions.getKeyFrameAtOffsetInfo(s, a, previousLookup)
                                nextKeyTime, nextValueRaw = Functions.getKeyFrameAtOffsetInfo(s, a, nextLookup)
                                if midLookup:
                                    midTime, midValue = Functions.getKeyFrameAtOffsetInfo(s, a, midLookup)
                                PrevNormalizeKeyFrame = abs(midTime - prevKeyTime)
                                if PrevNormalizeKeyFrame == 0:
                                    PrevNormalizeKeyFrame = 1
                                NextNormalizeKeyFrame = abs(nextKeyTime - midTime)
                                if NextNormalizeKeyFrame == 0:
                                    NextNormalizeKeyFrame = 1
                                prevValue = midValue + (midValue - nextValueRaw) / NextNormalizeKeyFrame * multiplier
                                nextValue = midValue + (midValue - prevValueRaw) / PrevNormalizeKeyFrame * multiplier
                                if prevValue == nextValue == currentValue:
                                    isBoring = True
                                if not isBoring:
                                    setValue = 0
                                    isIgnored = False
                                    data[attribute]['prevValue'] = prevValue
                                    data[attribute]['nextValue'] = nextValue
                                    data[attribute]['currentValue'] = currentValue
                                    data[attribute]['type'] = Functions.getAttributeType(s, a)
                                    data[attribute]['setValue'] = setValue
                                    data[attribute]['isBoring'] = isBoring
                                    data[attribute]['isIgnored'] = isIgnored

        except Exception as e:
            print (1146, Exception, e)
        finally:
            self.data = data
            cmds.waitCursor(state=False)


class slider_multiply(slider_base):

    def __init__(self, *args, **kwargs):
        parent = False
        if 'parent' in kwargs:
            parent = kwargs.pop('parent')
        sliderType = 'multiplySlider'
        showMultiplier = True
        slider_base.__init__(self, parent=parent, sliderType=sliderType, showMultiplier=showMultiplier)
        self.setMultiplier(1.0)

    def collectData(self):
        """
        structure
        object.attribute
                     >prevValue
                     >nextValue
                     >currentValue
                     >type
                     >setValue
                     >isBoring
                     >isIgnored
        
        """
        cmds.waitCursor(state=True)
        data = {}
        multiplier = self.getMultiplier() * 2
        try:
            selection = self.getSelected()
            selectedChannels = self.getSelectedChannels(selection=selection)
            limitedAttributes = ['tx',
             'ty',
             'tz',
             'rx',
             'ry',
             'rz']
            blackListAttributes = ['sx',
             'sy',
             'sz',
             'v']
            currentTime = cmds.currentTime(query=True)
            for s in selection:
                keyableAttributes = []
                if selectedChannels:
                    keyableAttributes = list(set(selectedChannels))
                else:
                    keyableAttributes_raw = Functions.listAttributes(s)
                    keyableAttributes = list(set(keyableAttributes_raw) & set(limitedAttributes))
                if keyableAttributes:
                    for a in keyableAttributes:
                        attribute = '{0}.{1}'.format(s, a)
                        data[attribute] = {}
                        isBoring = False
                        if not isBoring:
                            currentValue = cmds.getAttr(attribute, time=currentTime)
                            prevValue = 0
                            nextValue = currentValue * multiplier
                            if prevValue == nextValue == currentValue:
                                isBoring = True
                            if not isBoring:
                                setValue = 0
                                isIgnored = False
                                data[attribute]['prevValue'] = prevValue
                                data[attribute]['nextValue'] = nextValue
                                data[attribute]['currentValue'] = currentValue
                                data[attribute]['type'] = False
                                data[attribute]['setValue'] = setValue
                                data[attribute]['isBoring'] = isBoring
                                data[attribute]['isIgnored'] = isIgnored

        except Exception as e:
            print (1146, Exception, e)
        finally:
            self.data = data
            cmds.waitCursor(state=False)

    def slider_realtime(self, *args, **kwargs):
        useSetValue = False
        if 'useSetValue' in kwargs:
            useSetValue = kwargs.pop('useSetValue')
        overrideRatio = False
        if 'overrideRatio' in kwargs:
            overrideRatio = kwargs.pop('overrideRatio')
        fromCurrentValue = False
        if 'fromCurrentValue' in kwargs:
            fromCurrentValue = kwargs.pop('fromCurrentValue')
        mods = cmds.getModifiers()
        isCtrl = mods & 4 > 0
        isShift = mods & 1 > 0
        isAlt = mods & 8 > 0
        if self.getUseAllLayersState():
            self.slider_realtime_standard(useSetValue=useSetValue, overrideRatio=overrideRatio, fromCurrentValue=fromCurrentValue)
        else:
            self.slider_realtime_layers(useSetValue=useSetValue, overrideRatio=overrideRatio, fromCurrentValue=fromCurrentValue)

    def slider_realtime_finish(self, *args, **kwargs):
        if self.getUseAllLayersState():
            self.slider_realtime_finish_standard()
        else:
            self.slider_realtime_finish_layers()


class Hotkeys(object):

    @classmethod
    def autoInbetween(cls):
        cls.inbetween(0, useSetValue=True)

    @classmethod
    def inbetween(cls, valueVar, useSetValue = False, fromCurrentValue = False):
        """
        This will perform the actual execution of the data and slider
        """
        data = cls.collectData()
        if data:
            sliderValue = float(valueVar)
            sliderValue = Functions.clamp(sliderValue, -1, 1)
            sliderPos = Functions.clamp(sliderValue, 0, 1)
            sliderNeg = abs(Functions.clamp(sliderValue, -1, 0))
            ratio = (sliderValue + 1) / 2
            ratioInverted = 1 - ratio
            for a in data.keys():
                isBoring = True
                try:
                    isBoring = data[a]['isBoring']
                except:
                    pass

                if not isBoring:
                    isIgnored = data[a]['isIgnored']
                    if not isIgnored:
                        prevValue = data[a]['prevValue']
                        nextValue = data[a]['nextValue']
                        currentValue = data[a]['currentValue']
                        setValue = data[a]['setValue']
                        attributeType = data[a]['type']
                        isOnKey = data[a]['onKey']
                        fromCurrentValue = False
                        if isOnKey and not ratio == 0.5:
                            fromCurrentValue = True
                        newValue = 0
                        if useSetValue:
                            newValue = setValue
                        elif attributeType != 'enum':
                            if fromCurrentValue:
                                newValue = currentValue + (prevValue - currentValue) * sliderNeg + (nextValue - currentValue) * sliderPos
                            else:
                                newValue = prevValue * ratioInverted + nextValue * ratio
                        elif fromCurrentValue:
                            if sliderValue > 0.5:
                                newValue = nextValue
                            elif sliderValue < -0.5:
                                newValue = prevValue
                            else:
                                newValue = currentValue
                        elif sliderValue >= 0:
                            newValue = nextValue
                        elif sliderValue < 0:
                            newValue = prevValue
                        else:
                            newValue = currentValue
                        if newValue != currentValue:
                            cmds.setAttr(a, newValue, clamp=True)

    @classmethod
    def collectData(cls):
        """
        structure
        object.attribute
                     >prevValue
                     >nextValue
                     >currentValue
                     >type
                     >setValue
                     >isBoring
                     >isIgnored
        
        """
        cmds.waitCursor(state=True)
        data = {}
        try:
            selection = cmds.ls(sl=True, type=['transform', 'joint'], long=True)
            selectedChannels = Functions.getSelectedChannels()
            currentTime = cmds.currentTime(query=True)
            for s in selection:
                keyableAttributes = Functions.listAttributes(s)
                if keyableAttributes:
                    for a in keyableAttributes:
                        if selectedChannels and a in selectedChannels or not selectedChannels:
                            attribute = '{0}.{1}'.format(s, a)
                            data[attribute] = {}
                            keyFrameCount = cmds.keyframe(attribute, query=True, keyframeCount=True)
                            isBoring = False
                            if not keyFrameCount >= 2:
                                isBoring = True
                            if not isBoring:
                                currentValue = cmds.getAttr(attribute, time=currentTime)
                                prevKeyFrame = cmds.findKeyframe(s, which='previous', at=a)
                                nextKeyFrame = cmds.findKeyframe(s, which='next', at=a)
                                prevValue = cmds.getAttr(attribute, t=prevKeyFrame)
                                nextValue = cmds.getAttr(attribute, t=nextKeyFrame)
                                if prevValue == nextValue == currentValue:
                                    isBoring = True
                                if not isBoring:
                                    minTime = prevKeyFrame
                                    maxTime = nextKeyFrame
                                    midTime = Functions.clamp(currentTime, minTime, maxTime)
                                    timeRange = maxTime - minTime
                                    ratio = 0.5
                                    if timeRange != 0:
                                        ratio = (midTime - minTime) / (maxTime - minTime)
                                    ratioInverted = 1 - ratio
                                    setValue = prevValue * ratioInverted + nextValue * ratio
                                    isIgnored = False
                                    data[attribute]['onKey'] = Functions.isOnKey(s, a, currentTime)
                                    data[attribute]['prevValue'] = prevValue
                                    data[attribute]['nextValue'] = nextValue
                                    data[attribute]['currentValue'] = currentValue
                                    data[attribute]['type'] = Functions.getAttributeType(s, a)
                                    data[attribute]['setValue'] = setValue
                                    data[attribute]['isBoring'] = isBoring
                                    data[attribute]['isIgnored'] = isIgnored

        except Exception as e:
            print (traceback.format_exc())
            print (1146, Exception, e)
        finally:
            cmds.waitCursor(state=False)
            return data