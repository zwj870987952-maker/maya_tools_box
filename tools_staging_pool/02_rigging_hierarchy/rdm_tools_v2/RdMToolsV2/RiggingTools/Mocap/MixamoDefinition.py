import pymel.core as pm
from maya import cmds
import maya.mel as mel

cmds.playbackOptions( minTime=-10 )
cmds.currentTime( -10 )

pm.select('mixamorig:Hips', 'mixamorig:Spine', 'mixamorig:Spine1', 'mixamorig:Spine2', 'mixamorig:Neck', 'mixamorig:Head', 'mixamorig:HeadTop_End', 'mixamorig:LeftShoulder', 'mixamorig:LeftArm', 'mixamorig:LeftForeArm', 'mixamorig:LeftHand', 'mixamorig:LeftHandThumb1', 'mixamorig:LeftHandThumb2', 'mixamorig:LeftHandThumb3', 'mixamorig:LeftHandThumb4', 'mixamorig:LeftHandIndex1', 'mixamorig:LeftHandIndex2', 'mixamorig:LeftHandIndex3', 'mixamorig:LeftHandIndex4', 'mixamorig:LeftHandMiddle1', 'mixamorig:LeftHandMiddle2', 'mixamorig:LeftHandMiddle3', 'mixamorig:LeftHandMiddle4', 'mixamorig:LeftHandRing1', 'mixamorig:LeftHandRing2', 'mixamorig:LeftHandRing3', 'mixamorig:LeftHandRing4', 'mixamorig:RightShoulder', 'mixamorig:RightArm', 'mixamorig:RightForeArm', 'mixamorig:RightHand', 'mixamorig:RightHandThumb1', 'mixamorig:RightHandThumb2', 'mixamorig:RightHandThumb3', 'mixamorig:RightHandThumb4', 'mixamorig:RightHandIndex1', 'mixamorig:RightHandIndex2', 'mixamorig:RightHandIndex3', 'mixamorig:RightHandIndex4', 'mixamorig:RightHandMiddle1', 'mixamorig:RightHandMiddle2', 'mixamorig:RightHandMiddle3', 'mixamorig:RightHandMiddle4', 'mixamorig:RightHandRing1', 'mixamorig:RightHandRing2', 'mixamorig:RightHandRing3', 'mixamorig:RightHandRing4', 'mixamorig:LeftUpLeg', 'mixamorig:LeftLeg', 'mixamorig:LeftFoot', 'mixamorig:LeftToeBase', 'mixamorig:LeftToe_End', 'mixamorig:RightUpLeg', 'mixamorig:RightLeg', 'mixamorig:RightFoot', 'mixamorig:RightToeBase', 'mixamorig:RightToe_End', r=1)

for i in cmds.ls(sl = True):
    cmds.setAttr(str(i)+'.rotateX', 0)
    cmds.setAttr(str(i)+'.rotateY', 0)
    cmds.setAttr(str(i)+'.rotateZ', 0)

#/////////////////////////////////
#    Custom Rig Definition     //
#///////////////////////////////

#Spine
if pm.objExists("mixamorig:Hips"):
    pm.mel.setCharacterObject("mixamorig:Hips", "Character1", 1, 0)
    pm.mel.setCharacterObject("mixamorig:Spine", "Character1", 8, 0)
    pm.mel.setCharacterObject("mixamorig:Spine1", "Character1", 23, 0)
    pm.mel.setCharacterObject("mixamorig:Spine2", "Character1", 24, 0)


#Clavicles
if pm.objExists("mixamorig:LeftShoulder"):
    pm.mel.setCharacterObject("mixamorig:LeftShoulder", "Character1", 18, 0)
    pm.mel.setCharacterObject("mixamorig:RightShoulder", "Character1", 19, 0)


#Arms
if pm.objExists("mixamorig:LeftArm"):
	pm.mel.setCharacterObject("mixamorig:LeftArm", "Character1", 9, 0)
	pm.mel.setCharacterObject("mixamorig:RightArm", "Character1", 12, 0)


#ForeArm
if pm.objExists("mixamorig:LeftForeArm"):
	pm.mel.setCharacterObject("mixamorig:LeftForeArm", "Character1", 10, 0)
	pm.mel.setCharacterObject("mixamorig:RightForeArm", "Character1", 13, 0)

	

#Palm
if pm.objExists("mixamorig:LeftHand"):
	pm.mel.setCharacterObject("mixamorig:LeftHand", "Character1", 11, 0)
	pm.mel.setCharacterObject("mixamorig:RightHand", "Character1", 14, 0)
	

#Thumb
if pm.objExists("mixamorig:LeftHandThumb1"):
	pm.mel.setCharacterObject("mixamorig:LeftHandThumb1", "Character1", 50, 0)
	pm.mel.setCharacterObject("mixamorig:RightHandThumb1", "Character1", 74, 0)
	pm.mel.setCharacterObject("mixamorig:LeftHandThumb2", "Character1", 51, 0)
	pm.mel.setCharacterObject("mixamorig:RightHandThumb2", "Character1", 75, 0)
	pm.mel.setCharacterObject("mixamorig:LeftHandThumb3", "Character1", 52, 0)
	pm.mel.setCharacterObject("mixamorig:RightHandThumb3", "Character1", 76, 0)
	

#Index 
if pm.objExists("mixamorig:LeftHandIndex1"):

	pm.mel.setCharacterObject("mixamorig:LeftHandIndex1", "Character1", 54, 0)
	pm.mel.setCharacterObject("mixamorig:RightHandIndex1", "Character1", 78, 0)
	pm.mel.setCharacterObject("mixamorig:LeftHandIndex2", "Character1", 55, 0)
	pm.mel.setCharacterObject("mixamorig:RightHandIndex2", "Character1", 79, 0)
	pm.mel.setCharacterObject("mixamorig:LeftHandIndex3", "Character1", 56, 0)
	pm.mel.setCharacterObject("mixamorig:RightHandIndex3", "Character1", 80, 0)
	

#Middle
if pm.objExists("LeftHandMiddle1"):

	pm.mel.setCharacterObject("mixamorig:LeftHandMiddle1", "Character1", 58, 0)
	pm.mel.setCharacterObject("mixamorig:RightHandMiddle1", "Character1", 82, 0)
	pm.mel.setCharacterObject("mixamorig:LeftHandMiddle2", "Character1", 59, 0)
	pm.mel.setCharacterObject("mixamorig:RightHandMiddle2", "Character1", 83, 0)
	pm.mel.setCharacterObject("mixamorig:LeftHandMiddle3", "Character1", 60, 0)
	pm.mel.setCharacterObject("mixamorig:RightHandMiddle3", "Character1", 84, 0)
	

#Ring
if pm.objExists("mixamorig:LeftHandRing2"):

	pm.mel.setCharacterObject("mixamorig:LeftHandRing2", "Character1", 62, 0)
	pm.mel.setCharacterObject("mixamorig:RightHandRing1", "Character1", 86, 0)
	pm.mel.setCharacterObject("mixamorig:LeftHandRing3", "Character1", 63, 0)
	pm.mel.setCharacterObject("mixamorig:RightHandRing2", "Character1", 87, 0)
	pm.mel.setCharacterObject("mixamorig:LeftHandRing4", "Character1", 64, 0)
	pm.mel.setCharacterObject("mixamorig:RightHandRing3", "Character1", 88, 0)
	

#Pinky
if pm.objExists("mixamorig:RightHandPinky3"):

	pm.mel.setCharacterObject("mixamorig:LeftHandPinky1", "Character1", 66, 0)
	pm.mel.setCharacterObject("mixamorig:RightHandPinky1", "Character1", 90, 0)
	pm.mel.setCharacterObject("mixamorig:LeftHandPinky2", "Character1", 67, 0)
	pm.mel.setCharacterObject("mixamorig:RightHandPinky2", "Character1", 91, 0)
	pm.mel.setCharacterObject("mixamorig:LeftHandPinky3", "Character1", 68, 0)
	pm.mel.setCharacterObject("mixamorig:RightHandPinky3", "Character1", 92, 0)
	

#Head Neck
if pm.objExists("mixamorig:Neck"):
	pm.mel.setCharacterObject("mixamorig:Neck", "Character1", 20, 0)
	pm.mel.setCharacterObject("mixamorig:Head", "Character1", 15, 0)
	

#Legs
if pm.objExists("mixamorig:LeftUpLeg"):
	pm.mel.setCharacterObject("mixamorig:LeftUpLeg", "Character1", 2, 0)
	pm.mel.setCharacterObject("mixamorig:RightUpLeg", "Character1", 5, 0)
	

#Knee
if pm.objExists("mixamorig:LeftLeg"):
	pm.mel.setCharacterObject("mixamorig:LeftLeg", "Character1", 3, 0)
	pm.mel.setCharacterObject("mixamorig:RightLeg", "Character1", 6, 0)
	

#Ankle Ball
if pm.objExists("mixamorig:LeftFoot"):
	pm.mel.setCharacterObject("mixamorig:LeftFoot", "Character1", 4, 0)
	pm.mel.setCharacterObject("mixamorig:RightFoot", "Character1", 7, 0)
	pm.mel.setCharacterObject("mixamorig:LeftToeBase", "Character1", 16, 0)
	pm.mel.setCharacterObject("mixamorig:RightToeBase", "Character1", 17, 0)
	
	
	