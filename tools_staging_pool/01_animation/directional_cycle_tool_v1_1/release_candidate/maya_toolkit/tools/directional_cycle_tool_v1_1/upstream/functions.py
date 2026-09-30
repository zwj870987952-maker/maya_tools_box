import maya.cmds as cmds

##########################
# Back
##########################
def run_back(Selection, Bake=False, FeetNumber = 2, CorrectionLoc = False):
    
    if check_for_animlayer():
        pass
    else:
        return

    LayerName = "Back"
    start_time = cmds.playbackOptions(q=True, min=True)
    end_time = cmds.playbackOptions(q=True, max=True)
    print(start_time, end_time)


    MasterCtrl = Selection[0]
    Feet = []
    for i in range(FeetNumber):
        if i < len(Selection) - 4:
            Feet.append(Selection[i+1])
    MainBody = Selection[FeetNumber+1]
    UpperBody = Selection[FeetNumber+2]
    Head = Selection[FeetNumber+3]

    Loc_Feet = []
    for foot in Feet:
        Loc_Foot = cmds.spaceLocator(n=f"Loc_Feet_{foot}")
        Loc_Feet.append(Loc_Foot[0])
    Loc_HeadAim = cmds.spaceLocator(n=f"Loc_Aim_{Head}")
    cmds.move(0,100,500, Loc_HeadAim, r=True, ws=True)

    Constrains = []
    for i, foot in enumerate(Feet):
        Constrain = cmds.parentConstraint(foot, Loc_Feet[i], mo=False)
        Constrains.append(Constrain)
    cmds.bakeResults(Loc_Feet, sm=True, t=(start_time, end_time))
    cmds.delete(Constrains[0])

    cmds.aimConstraint(Loc_HeadAim, Head, mo=True)
    for i, foot in enumerate(Feet):
        cmds.parentConstraint(Loc_Feet[i], foot, mo=False)

    print("Pelvis setup")
    pelvis_setup(MainBody)
    
    print("Feet setup")
    for obj in Loc_Feet:
        print(obj)
        try:
            cmds.select(obj)
            Keyframes = cmds.keyframe(obj, query=True, timeChange=True)
            FirstKey = min(Keyframes)
            LastKey = max(Keyframes)

            TimePivot = FirstKey + ((LastKey - FirstKey)/2)

            cmds.scaleKey(obj, time = (FirstKey, LastKey), timeScale = -1, timePivot=TimePivot)
        except:
            warning_popup(f"Warning: No keys found for {obj}.\nRetry with the BaseAnimation layer selected.")
            print(f"No keys for {obj}")

        
    if CorrectionLoc:
        create_correction_locators(Loc_Feet)

    if Bake:
        ControllerToBake = Feet + [MainBody, Head]
        LocToDelete = Loc_Feet + Loc_HeadAim
        create_animlayer(LayerName, ControllerToBake)
        cmds.select(ControllerToBake)
        cmds.bakeResults(t=(start_time-1,end_time), dl=LayerName)
        cmds.delete(LocToDelete)
        cmds.animLayer(LayerName, edit=True, o=True)
        try:
            cmds.delete("Loc_Master_Correction")
        except:
            pass

def pelvis_setup(Controller):
    LayerName = "Back_Pelvis"
    start_time = cmds.playbackOptions(q=True, min=True)

    if not cmds.animLayer(LayerName, query=True, exists=True):
         cmds.animLayer(LayerName)

    cmds.select(Controller)
    cmds.animLayer(LayerName, edit=True, addSelectedObjects=True)

    CurrentTranslate = cmds.getAttr(f"{Controller}.translateY")
    CurrenRotate = cmds.getAttr(f"{Controller}.rotateX")

    cmds.setKeyframe(f"{Controller}.translateY", al=LayerName, time=start_time, value=CurrentTranslate-10)
    cmds.setKeyframe(f"{Controller}.rotateX", al=LayerName, time=start_time, value=CurrenRotate*-1)


##########################
# Left Right
##########################
def run_side(Right = False, Angle = 45, Selection = None, Bake = False, FeetNumber = 2, CorrectionLoc = False, CounterRotation = False):

    if check_for_animlayer():
        pass
    else:
        return
    
    RotateMain = Angle
    RotateLoc = 90
    LayerName = "Left"


    if Right:
        RotateMain = -RotateMain
        RotateLoc = -RotateLoc
        LayerName = "Right"

    start_time = cmds.playbackOptions(q=True, min=True)
    end_time = cmds.playbackOptions(q=True, max=True)

    MasterCtrl = Selection[0]
    Feet = []
    for i in range(FeetNumber):
        if i < len(Selection) - 4:
            Feet.append(Selection[i+1])
    MainBody = Selection[FeetNumber+1]
    UpperBody = Selection[FeetNumber+2]
    Head = Selection[FeetNumber+3]

    Loc_Master = cmds.spaceLocator(n=f"Loc_{MasterCtrl}")
    Loc_FeetMaster = cmds.spaceLocator(n="Loc_AutoMoveset")
    Loc_Feet = []
    for foot in Feet:
        Loc_Foot = cmds.spaceLocator(n=f"Loc_{foot}")
        Loc_Feet.append(Loc_Foot[0])
    Loc_HeadAim = cmds.spaceLocator(n=f"Loc_Aim_{Head}")
    cmds.move(0,100,500, Loc_HeadAim, r=True, ws=True)

    cmds.parentConstraint(Loc_Master, MasterCtrl, mo=True)
    for loc_foot in Loc_Feet:
        cmds.parent(loc_foot, Loc_FeetMaster)

    Constrains = []
    for i, foot in enumerate(Feet):
        Constrain = cmds.parentConstraint(foot, Loc_Feet[i], mo=False)
        Constrains.append(Constrain)
    

    cmds.bakeResults(Loc_Feet, sm=True, t=(start_time, end_time))
    cmds.delete(Constrains[0])

    cmds.aimConstraint(Loc_HeadAim, Head, mo=True)
    cmds.rotate(0,RotateMain,0, Loc_Master, r=True, ws=True)
    cmds.rotate(0,RotateLoc,0, Loc_FeetMaster, r=True, ws=True)

    for i, foot in enumerate(Feet):
        cmds.pointConstraint(Loc_Feet[i], foot, mo=False)

    if CorrectionLoc or CounterRotation:
        create_correction_locators(Loc_Feet, RotateLoc, RotateMain, CorrectionLoc,CounterRotation)

    if Bake:
        create_animlayer(LayerName, Selection)
        cmds.select(Selection)
        cmds.bakeResults(t=(start_time,end_time), dl=LayerName)
        cmds.delete(Loc_Master + Loc_FeetMaster + Loc_Feet + Loc_HeadAim)
        cmds.animLayer(LayerName, edit=True, o=True)
        try:
            cmds.delete("Loc_Master_Correction")
        except:
            pass

    cmds.select(Selection)



##########################
# Utility
##########################

def warning_popup(Message=""):
    cmds.confirmDialog(
        title="Warning",
        message=Message,
        button=["OK"],
        defaultButton="OK",
        icon="warning"
    )

def create_animlayer(Name = "", Controllers = None):

    if cmds.objExists(Name) and cmds.nodeType(Name) == "animLayer":
        cmds.delete(Name)

    cmds.select(Controllers)
    cmds.animLayer(Name, aso=True)

def check_for_animlayer():

    try:
        RootLayer = cmds.animLayer(query=True, root=True)
        Value = cmds.animLayer(RootLayer, query=True, selected=True)
    except:
        return True

    if Value:
        cmds.animLayer(RootLayer, edit=True, selected=True)
    else:
        warning_popup(f"Please select the {RootLayer} layer")

    return Value

def check_controller_number(Selection, RequiredNumber):
    if Selection == None:
        warning_popup("No controller saved\nPlease select and save your controllers")
        print("No controller saved")
        return True
    elif len(Selection) < RequiredNumber:
        warning_popup("Not enough controllers saved\nPlease select and save your controllers")
        print("Not enough controllers saved")
        return True
    elif len(Selection) > RequiredNumber:
        warning_popup("Too many controllers saved\nPlease select and save your controllers")
        print("Too many controllers saved")
        return True
    else:
        return False

def create_correction_locators(Selection, MainRotation = 0, FeetAngle = 0, KeepCorrection = True, CounterRotation = False):
    CorrectionLocatorList = []
    TempMotionLocatorList = []
    TempPositionLocatorList = []
    ConstrainList = []

    CounterRotationValue = FeetAngle-MainRotation

    start_time = cmds.playbackOptions(q=True, min=True)
    end_time = cmds.playbackOptions(q=True, max=True)
    
    cmds.bakeResults(Selection, sm=True, t=(start_time, end_time))

    Loc_MasterCorrection = cmds.spaceLocator(n="Loc_Master_Correction")
    RotationLocator = cmds.spaceLocator(n="Master_CorrectionLoc")

    for obj in Selection:
        # Create correction locator (the one that will be visible)
        CorrectionLoc = cmds.spaceLocator(n=f"CorrectionLoc_{obj}")
        CorrectionLocatorList.append(CorrectionLoc[0])
        cmds.parent(CorrectionLoc, Loc_MasterCorrection)
        cmds.setAttr(f"{CorrectionLoc[0]}Shape.localScaleX", 30)
        cmds.setAttr(f"{CorrectionLoc[0]}Shape.localScaleY", 30)
        cmds.setAttr(f"{CorrectionLoc[0]}Shape.localScaleZ", 30)
        # Match transform to the new cycle locator
        cmds.matchTransform(CorrectionLoc, obj, pos=True, rot=False, scale=False)
        cmds.move(2, CorrectionLoc, y=True, a=True)

        # Create temp Position locator
        TempPosLoc = cmds.spaceLocator(n=f"Temp_Pos_{obj}")
        TempPositionLocatorList.append(TempPosLoc[0])
        cmds.parent(TempPosLoc, RotationLocator)
        cmds.matchTransform(TempPosLoc, CorrectionLoc, pos=True, rot=False, scale=False)

        # Create temp motion locator
        TempMotionLoc = cmds.spaceLocator(n=f"Temp_Motion_Loc_{obj}")
        TempMotionLocatorList.append(TempMotionLoc[0])
        cmds.parent(TempMotionLoc, CorrectionLoc)
        Temp_Constrain = cmds.parentConstraint(obj, TempMotionLoc, mo=False)
        ConstrainList.append(Temp_Constrain)

    # Bake the feet'smotion to the temp locator
    cmds.bakeResults(TempMotionLocatorList, sm=True, t=(start_time, end_time))
    cmds.delete(ConstrainList[0])

    # Parent the temp motion to the correction locator and parent constraint back the feet to the temp motion
    # Bake everything back to the feet and delete the temp motion
    for i, obj in enumerate(Selection):
        cmds.parent(obj, CorrectionLocatorList[i])
        cmds.parentConstraint(TempMotionLocatorList[i], obj, mo=False)
    
    cmds.bakeResults(Selection, sm=True, t=(start_time, end_time))
    cmds.delete(TempMotionLocatorList)

    # Rotate the rotation locator to offset the correction locator to the temp position locator
    if CounterRotation:
        cmds.rotate(0,CounterRotationValue,0, RotationLocator, r=True, ws=True)

        for i, obj in enumerate(CorrectionLocatorList):
            cmds.matchTransform(obj, TempPositionLocatorList[i], pos=True, rot=False, scale=False)

    if not KeepCorrection:
        cmds.bakeResults(Selection, sm=True, t=(start_time, end_time))
        # cmds.delete(Loc_MasterCorrection)
    
    cmds.delete(TempPositionLocatorList, RotationLocator)

    

    