
import maya.cmds as cmds
import maya.mel as mel

sel = cmds.ls(sl=True)

if len(sel)==0:
    sys.exit()

sel = cmds.ls(sl=True)
if len(sel)==1:
    cmds.warning("Please select at least 2 objects.")
    sys.exit()

def esn_alignObjects():

    CT = cmds.currentTime(q=1)
    sel.pop(-1)
    
    playBackSlider = mel.eval('$animBot_playBackSliderPython=$gPlayBackSlider')
    timeRange = cmds.timeControl(playBackSlider, query=True, rangeArray=True)
    StartRange = timeRange[0]
    EndRange = timeRange[1] - 1
    StartRange = int(StartRange)
    EndRange = int(EndRange)
    keys = cmds.keyframe(q=1, t=(StartRange, EndRange))
    firstSel = cmds.ls(sl=True)[0]
    
    if EndRange-StartRange==0:
        cmds.matchTransform(pos=1, rot=1)  
        if keys==None:
            cmds.matchTransform(pos=1, rot=1)
        else:
            pass    
            
    else:     
        keys = set(keys)
        cmds.refresh(suspend=True)
        cmds.evaluationManager(mode="off")
        for key in keys:
            cmds.currentTime(key)
            cmds.matchTransform(pos=1, rot=1)
            cmds.setKeyframe(sel, at= ('tx', 'ty', 'tz', 'rx', 'ry', 'rz'))
        cmds.currentTime(CT)
    cmds.select(firstSel)  
    cmds.refresh(suspend=False)
    cmds.evaluationManager(mode="parallel")          
esn_alignObjects()