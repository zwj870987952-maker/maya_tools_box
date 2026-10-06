import maya.cmds as cmds
import maya.mel as mel

def clean_keys_interactive():
    try:
        if cmds.objExists("esn_time_null"):
            try:
                cmds.delete("esn_time_null")
            except:
                pass
        
        sel = cmds.ls(sl=True)
        if not sel:
            return
            
        null = cmds.spaceLocator(name="esn_time_null")[0]
        cmds.hide()
        cmds.select(null)
        
        def removeKeys():
            try:
                cmds.undoInfo(openChunk=True)
                
                playBackSlider = mel.eval('$animBot_playBackSliderPython=$gPlayBackSlider')
                timeRange = cmds.timeControl(playBackSlider, query=True, rangeArray=True)
                min_time = cmds.playbackOptions(q=True, min=True)
                max_time = cmds.playbackOptions(q=True, max=True)
                StartRange = timeRange[0]
                EndRange = timeRange[1] - 1
                StartRange = int(StartRange)
                EndRange = int(EndRange)

                if (EndRange - StartRange) == 0:
                    selKeys = cmds.keyframe(sel, q=True, t=(min_time, max_time))
                    if selKeys:
                        selKeys = list(set(selKeys))
                        selKeys.sort()
                    else:
                        selKeys = []
                
                    LOCkeys = cmds.keyframe("esn_time_null", q=True, t=(min_time, max_time))
                    if LOCkeys:
                        LOCkeys = list(set(LOCkeys))
                        LOCkeys.sort()
                    else:
                        LOCkeys = []
                else:
                    selKeys = cmds.keyframe(sel, q=True, t=(StartRange, EndRange))
                    if selKeys:
                        selKeys = list(set(selKeys))
                        selKeys.sort()
                    else:
                        selKeys = []
                
                    LOCkeys = cmds.keyframe("esn_time_null", q=True, t=(StartRange, EndRange))
                    if LOCkeys:
                        LOCkeys = list(set(LOCkeys))
                        LOCkeys.sort()
                    else:
                        LOCkeys = []

                if LOCkeys:
                    cmds.setKeyframe(sel, i=True, t=LOCkeys)
                    
                    for key in selKeys:
                        if key not in LOCkeys:
                            cmds.cutKey(sel, t=(key, key))
                
                try:
                    cmds.delete("esn_time_null")
                except:
                    pass
                
                cmds.select(sel)
                
            except Exception as e:
                try:
                    if cmds.objExists("esn_time_null"):
                        cmds.delete("esn_time_null")
                    cmds.select(sel)
                except:
                    pass
            finally:
                cmds.undoInfo(closeChunk=True)
        
        cmds.scriptJob(runOnce=True, killWithScene=True, event=["SelectionChanged", removeKeys])
        
    except Exception as e:
        try:
            if cmds.objExists("esn_time_null"):
                cmds.delete("esn_time_null")
        except:
            pass

clean_keys_interactive()
