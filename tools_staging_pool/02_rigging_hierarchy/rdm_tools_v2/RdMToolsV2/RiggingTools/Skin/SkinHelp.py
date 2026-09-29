from maya import cmds
import pymel.core as pm
import maya.mel as mel

def helpSkin(rotation = 60):
    
    cmds.undoInfo(openChunk=True)   

    cmds.playbackOptions(max=180, min=1)
    ctrl = cmds.ls(sl = True)[0]
    
    cmds.currentTime(1)
    cmds.setAttr(str(ctrl) + '.rotateZ', 0)
    cmds.setKeyframe(str(ctrl) + '.rotate')
    
    cmds.currentTime(20)
    cmds.setAttr(str(ctrl) + '.rotateZ', rotation)
    cmds.setKeyframe(str(ctrl) + '.rotate')
    
    cmds.currentTime(40)
    cmds.setAttr(str(ctrl) + '.rotateZ', -rotation)
    cmds.setKeyframe(str(ctrl) + '.rotate')
    
    cmds.currentTime(60)
    cmds.setAttr(str(ctrl) + '.rotateZ', 0)
    cmds.setKeyframe(str(ctrl) + '.rotate')
    
    cmds.currentTime(60)
    cmds.setAttr(str(ctrl) + '.rotateY', 0)
    cmds.setKeyframe(str(ctrl) + '.rotate')
    
    cmds.currentTime(80)
    cmds.setAttr(str(ctrl) + '.rotateY', rotation)
    cmds.setKeyframe(str(ctrl) + '.rotate')
    
    cmds.currentTime(100)
    cmds.setAttr(str(ctrl) + '.rotateY', -rotation)
    cmds.setKeyframe(str(ctrl) + '.rotate')
    
    cmds.currentTime(120)
    cmds.setAttr(str(ctrl) + '.rotateY', 0)
    cmds.setKeyframe(str(ctrl) + '.rotate')
    
    cmds.currentTime(120)
    cmds.setAttr(str(ctrl) + '.rotateX', 0)
    cmds.setKeyframe(str(ctrl) + '.rotate')
    
    cmds.currentTime(140)
    cmds.setAttr(str(ctrl) + '.rotateX', rotation)
    cmds.setKeyframe(str(ctrl) + '.rotate')
    
    cmds.currentTime(160)
    cmds.setAttr(str(ctrl) + '.rotateX', -rotation)
    cmds.setKeyframe(str(ctrl) + '.rotate')
    
    cmds.currentTime(180)
    cmds.setAttr(str(ctrl) + '.rotateX', 0)
    cmds.setKeyframe(str(ctrl) + '.rotate')

    cmds.undoInfo(closeChunk=True)   


def cleanHelp():
    
    cmds.undoInfo(openChunk=True)   
    ctrl = cmds.ls(sl = True)[0]


    mel.eval('CBdeleteConnection "'+str(ctrl)+'.rx";')
    mel.eval('CBdeleteConnection "'+str(ctrl)+'.ry";')
    mel.eval('CBdeleteConnection "'+str(ctrl)+'.rz";')
    
    #cmds.disconnectAttr(cmds.listConnections (str(ctrl)+'.rotateX', p =True)[0],str(ctrl)+ '.rotateX')
    #cmds.disconnectAttr(cmds.listConnections (str(ctrl)+'.rotateY', p =True)[0],str(ctrl)+ '.rotateY')
    #cmds.disconnectAttr(cmds.listConnections (str(ctrl)+'.rotateZ', p =True)[0],str(ctrl)+ '.rotateZ')
    
    cmds.setAttr(str(ctrl)+ '.rx', 0)
    cmds.setAttr(str(ctrl)+ '.ry', 0)
    cmds.setAttr(str(ctrl)+ '.rz', 0)

    cmds.currentTime(1)

    cmds.undoInfo(closeChunk=True)   

'''

helpSkin(rotation = 60)
cleanHelp()

'''

