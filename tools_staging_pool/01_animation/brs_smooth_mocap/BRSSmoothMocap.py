import urllib,os
import maya.cmds as cmds
import maya.mel as mel

def formatPath(path):
    path = path.replace("/", os.sep)
    path = path.replace("\\", os.sep)
    return path

mayaAppDir = formatPath(mel.eval('getenv MAYA_APP_DIR'))
scriptsDir = formatPath(mayaAppDir + os.sep + 'scripts')

"""
BRS Loc Transfer
"""
snapLocName = 'BRSSnapLoc'
try:
    script = open(scriptsDir + os.sep + 'BRSLocTransfer.py', 'r')
except:
    cmds.error('can\'t found \"BRSLocTransfer.py\"')
else:
    exec (script.read())
    script.close()

"""
BRS Smooth Keys
"""
def valueAverage (attrName,keyframeList):
    new_keyframeList = []
    new_valueList = []
    for i in range(len(keyframeList)):
        if not keyframeList[i] in [keyframeList[0],keyframeList[-1]]:
            new_keyframeList.append(keyframeList[i])
            
            valuePrev = cmds.keyframe(attrName,q=True,vc=True,t=(keyframeList[i-1],))[0]
            valueCur = cmds.keyframe(attrName,q=True,vc=True,t=(keyframeList[i],))[0]
            valueNext = cmds.keyframe(attrName,q=True,vc=True,t=(keyframeList[i+1],))[0]
            
            average = (valuePrev+valueCur+valueNext)/3
            new_valueList.append(average)
            
    zipKeyValue = zip(new_keyframeList,new_valueList)
    
    for kv in zipKeyValue:
        #print(kv)
        cmds.setKeyframe(attrName, time=(kv[0],), value=kv[1])
    
def BRSSmoothKeys (*_):
    attrList = cmds.keyframe(q=True,name=True)
    for attrName in attrList:
        #print (attrName)
        keyframeList = cmds.keyframe(attrName,q=True,sl=True)
        #print (keyframeList)
        
        if keyframeList == None:
            pass
        elif len(keyframeList) >= 3 :
            valueAverage(attrName,keyframeList)

"""
BRS Mocap
"""
def BRSSmoothMocap(rootJoint,smoothStrength = 3):
    jointSelect = cmds.listRelatives(rootJoint,allDescendents=True)
    jointSelect.append(rootJoint)
    cmds.select(jointSelect)
    
    objectToLocatorSnap(toGroup=False,forceConstraint=False)
    
    locList = []
    for n in jointSelect:
        if cmds.objectType(n,isType='joint') and cmds.keyframe(n,q=True) != None:
            locList.append('_'.join([n,snapLocName]))
    cmds.select(locList)
    
    cmds.selectKey(clear=True)
    for loc in locList:
        cmds.selectKey(loc+'.tx',add=True)
        cmds.selectKey(loc+'.ty',add=True)
        cmds.selectKey(loc+'.tz',add=True)
        cmds.selectKey(loc+'.rx',add=True)
        cmds.selectKey(loc+'.ry',add=True)
        cmds.selectKey(loc+'.rz',add=True)
    
    print ('BRS Smooth Keyframe..')
    
    gMainProgressBar = mel.eval('$tmp = $gMainProgressBar');
    cmds.progressBar( gMainProgressBar,
    				edit=True,
    				beginProgress=True,
    				isInterruptable=False,
    				status='BRS Smooth Keyframe..',
    				maxValue=smoothStrength )
    				
    for i in range(smoothStrength-1):
        cmds.progressBar(gMainProgressBar, edit=True, step=1)
        BRSSmoothKeys()
        
    cmds.progressBar(gMainProgressBar, edit=True, endProgress=True)
    
    keyframeList = cmds.keyframe(locList,q=True,sl=True)
    bakeKey(jointSelect,keyframeList,inTimeline=False)
    cmds.delete(locList)
    print ('Smooth Mocap is Done!')
    
selection = cmds.ls(sl=True)
if len(selection) != 0 and cmds.objectType(selection[0],isType='joint'):
    result = cmds.confirmDialog( title='BRS Smooth Mocap', message='BRS Smooth Mocap\nRoot Joint Selected is \"{}\" '.format(selection[0]), button=['Yes','No'], defaultButton='Yes', cancelButton='No', dismissString='No' )
    if result == 'Yes':
        BRSSmoothMocap(selection[0],smoothStrength = 3)
else:
    cmds.warning( 'Select Root Joint.' )
    cmds.confirmDialog( title='Error', message='Please select root joint', button=['Close'])
cmds.deleteUI('BRSLOCTRANSFER')