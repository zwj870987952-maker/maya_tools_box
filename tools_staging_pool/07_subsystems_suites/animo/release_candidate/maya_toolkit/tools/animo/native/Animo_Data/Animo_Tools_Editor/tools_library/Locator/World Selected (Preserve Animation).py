import maya.cmds as cmds

def smart_constraint_mo_off(ctrl=None, object=None):
    transAttr = None
    rotAttr = None
    scaleAttr = None
    translate=True
    rotate=True
    scale=False
    maintainOffset=False 

    if translate:
        transAttr = cmds.listAttr(object, keyable=True, unlocked=True, string='translate*')     
    if rotate:
        rotAttr = cmds.listAttr(object, keyable=True, unlocked=True, string='rotate*')      
    if scale:
        scaleAttr = cmds.listAttr(object, keyable=True, unlocked=True, string='scale*')     

    rotSkip = []
    transSkip = []

    for axis in ['x','y','z']:
        if transAttr and not 'translate'+axis.upper() in transAttr:
            transSkip.append(axis)
        if rotAttr and not 'rotate'+axis.upper() in rotAttr:
            rotSkip.append(axis)

    if not transSkip:
        transSkip = 'none'
    if not rotSkip:
        rotSkip = 'none'

    constraints = []
    if rotAttr and transAttr and rotSkip == 'none' and transSkip == 'none':
        constraints.append(cmds.parentConstraint(ctrl, object, maintainOffset=maintainOffset))
    else:
        if transAttr:
            constraints.append(cmds.pointConstraint(ctrl, object, skip=transSkip, maintainOffset=maintainOffset))
        if rotAttr:
            constraints.append(cmds.orientConstraint(ctrl, object, skip=rotSkip, maintainOffset=maintainOffset))



def is_object_referenced(obj_name):
    """
    Check if the given object (by name) is referenced in Maya.

    Args:
        obj_name (str): The name of the object to check.

    Returns:
        bool: True if the object is referenced, False if not.
        None: If the object does not exist.
    """
    if not cmds.objExists(obj_name):
        cmds.warning(f"Object '{obj_name}' does not exist.")
        return None
    
    return cmds.referenceQuery(obj_name, isNodeReferenced=True)





def esn_convert_to_world():

    sel = cmds.ls(sl=True)
    
    temp_ctrls = []
    for s in sel:
        if not is_object_referenced(s):
            temp_ctrls.append(s)


    if temp_ctrls:

        con_list = []
        loc_list = []    
        for obj in temp_ctrls:

         
            loc  = cmds.spaceLocator(n = obj + "_temp_loc")[0]
            loc_list.append(loc)
            con = cmds.parentConstraint(obj, loc, mo=False)[0]
            con_list.append(con)
            
        

        minT = cmds.playbackOptions(q=True, min=True)
        maxT = cmds.playbackOptions(q=True, max=True)
        eval_mode = cmds.evaluationManager(q=True, mode=True)

        try:
            cmds.refresh(suspend=True)
            cmds.evaluationManager(mode="off")

            try:
                cmds.bakeResults(loc_list, sm=True, t=(minT,maxT), pok=True) 
                cmds.delete(con_list)
                try:
                    cmds.parent(sel, world=True)
                except:
                    pass

            except Exception as e:
                return   

            
            
            obj_list = []
            for loc in loc_list:
                obj = loc.split("_temp_loc")[0] 
                obj_list.append(obj)
                smart_constraint_mo_off(loc, obj)
                
                
                        
            cmds.bakeResults(obj_list, sm=True, t=(minT,maxT), pok=True)
            cmds.delete(loc_list)
            
            cmds.select(temp_ctrls)  

        finally:
            cmds.refresh(suspend=False)
            cmds.evaluationManager(mode=eval_mode[0])
        
       
                                 
                                        
    if not temp_ctrls:
        if is_object_referenced(s):
            
            cmds.confirmDialog(
                title='Warning',
                message='You have selected referenced objects.\nPlease make temp controls first and then apply the parent space.',
                button=['OK'],
                defaultButton='OK',
                icon='warning'
            )            
            
            return          
            
        
        
           
        
esn_convert_to_world()