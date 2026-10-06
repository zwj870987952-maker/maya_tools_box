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
    if not cmds.objExists(obj_name):
        cmds.warning(f"Object '{obj_name}' does not exist.")
        return None
    
    return cmds.referenceQuery(obj_name, isNodeReferenced=True)


def get_children_of_parent(parent_name):
    if not cmds.objExists(parent_name):
        cmds.warning(f"Object '{parent_name}' does not exist in the scene.")
        return []
    
    children = cmds.listRelatives(parent_name, allDescendents=True, type='transform', fullPath=False) or []
    return children


def make_scale_non_keyable_force(objects=None):
    if objects is None:
        objects = cmds.ls(selection=True)
        if not objects:
            cmds.warning("No objects selected.")
            return
    
    for obj in objects:
        for axis in ['X', 'Y', 'Z']:
            attr = f"{obj}.scale{axis}"
            if cmds.objExists(attr):
                was_hidden = not cmds.getAttr(attr, channelBox=True)
                
                if cmds.getAttr(attr, lock=True):
                    cmds.setAttr(attr, lock=False)
                    
                if cmds.getAttr(attr, channelBox=False):
                    cmds.setAttr(attr, channelBox=False)                    
                
                cmds.setAttr(attr, keyable=False)
                

                cmds.setAttr(attr, channelBox=False)



def esn_convert_to_parent():

    sel = cmds.ls(sl=True)
    
    if len(sel) == 1:
        
        cmds.confirmDialog(
            title='Warning',
            message='Please select at least two objects to create a parent space.\nMake sure to select the child objects first, then the parent last.',
            button=['OK'],
            defaultButton='OK',
            icon='warning'
        )        
        return
    
    if sel:
        parent_obj = sel[-1]
        sel.pop(-1)
        children = sel
        for child in children: 
            more_children = get_children_of_parent(child)   
            if more_children:
                for child in more_children:
                    children.append(child)    
        
        for s in children:
            if is_object_referenced(s):                
                cmds.confirmDialog(
                    title='Warning',
                    message='You have selected referenced objects.\nPlease make temp controls first and then apply the parent space.',
                    button=['OK'],
                    defaultButton='OK',
                    icon='warning'
                )        
                return                
    
        con_list = []
        loc_list = []    

        minT = cmds.playbackOptions(q=True, min=True)
        maxT = cmds.playbackOptions(q=True, max=True)
        eval_mode = cmds.evaluationManager(q=True, mode=True)

        try:
            cmds.refresh(suspend=True)
            cmds.evaluationManager(mode="off")

            try:

                for child in children:

                 
                    loc  = cmds.spaceLocator(n = child + "_temp_loc")[0]
                    loc_list.append(loc)
                    con = cmds.parentConstraint(child, loc, mo=False)[0]
                    con_list.append(con)
          
                    
                
                cmds.bakeResults(loc_list, sm=True, t=(minT,maxT), pok=True) 
                cmds.delete(con_list)

            except Exception as e:
                return 
            
            
            try:
                make_scale_non_keyable_force(children)           
            except:
                pass
            

            try:
                cmds.parent(children, parent_obj)
            except:
                pass
            
            
            try:        
            
                obj_list = []
                for loc in loc_list:
                    obj = loc.split("_temp_loc")[0] 
                    obj_list.append(obj)
                    smart_constraint_mo_off(loc, obj)
                    
                    
                            
                cmds.bakeResults(obj_list, sm=True, t=(minT,maxT), pok=True)
                cmds.delete(loc_list)
                
                cmds.select(sel)
                

                        
            except Exception as e:
                return 

        finally:
            cmds.refresh(suspend=False)
            cmds.evaluationManager(mode=eval_mode[0])


            
            
            
esn_convert_to_parent()