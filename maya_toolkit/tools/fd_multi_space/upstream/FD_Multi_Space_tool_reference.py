# This script is owned by Filippo Dattola. All Rights Reserved 2023. 
# If a commercial Studios wishes to use it, please contact me at dattolafilippo@gmail.com for permission and further detail

# This a MULTI-SPACE tool for Python 2.x and above

import maya.cmds as mc
import sys

obj1_list = []
obj2_list = []
window = "MultiSpaceToolWindow"

def create_ui():
    if mc.window(window, exists=True):
        mc.deleteUI(window, window=True)

    mc.window(window, title="Multi-Space Tool - Reference", widthHeight=(380, 150))
    mc.columnLayout(adjustableColumn=True)
    mc.separator(height=10)
    attribute_field = mc.textFieldGrp("attribute_field", label="New Attribute name:", adjustableColumn=True)
    mc.separator(height=15)
    mc.button(label="1 - Select a control, type a name and click here", command=driven_obj)
    mc.separator(height=10)
    mc.button(label="2 - Select a control to Connect to and click here", command=driver_obj)
    mc.separator(height=10)
    mc.button(label="3 - Execute", bgc=[.8, .5, 0], command=connect_objs)
    mc.showWindow(window)


def driven_obj(*args):
    obj1 = mc.ls(sl=True)
    attribute_textfield = mc.textFieldGrp("attribute_field", query=True, text=True)  
    if obj1 and attribute_textfield:
        obj1_list[:] = []  
        obj1_list.append(obj1)

        # Add the attribute to the selected object
        if mc.objExists(obj1[0]):
            mc.addAttr(obj1[0], ln=attribute_textfield, at="double", min=0, max=1, dv=0, keyable=True)
            mc.refresh() 
            print("New attribute '{}' added to '{}'".format(attribute_textfield, obj1[0]))
        else:
            print("The object '{}' does not exist.".format(obj1[0]))
    else:
        mc.warning("Enter a valid name for the attribute and make sure you have a selection.")

    return obj1, attribute_textfield


def driver_obj(*args):
    obj2 = mc.ls(sl=True)
    if obj1_list and obj2:
        obj2_list[:] = []  

        # Get the parent node of the first selected object
        parent_node = mc.listRelatives(obj1_list[0][0], parent=True, fullPath=True)

        if not parent_node:
            print("The object '{}' has no parent node. Unable to proceed.".format(obj1_list[0][0]))
            return

        #print("Using parent node '{}' as the control node.".format(parent_node[0]))

        # Create a parentConstraint with mo=1 option between the parent node and obj2
        constraint_name = "{}_parentConstraint1".format(obj1_list[0][0])  # Modify this line
        mc.parentConstraint(obj2[0], parent_node[0], name=constraint_name, mo=1)

        # Get the created Parent Constraint node
        parent_constraint_node = mc.listRelatives(parent_node[0], type='parentConstraint')[0]
        obj2_list.append(parent_constraint_node)  # Add the Parent Constraint node to the list

        #print("Created parentConstraint '{}' between '{}' and parent node '{}'".format(constraint_name, obj2[0], parent_node[0]))
    else:
        mc.warning("Make sure you have a selection for the Connect to control")

    return obj2


def connect_objs(*args):
    full_name_list = obj1_list + obj2_list
    #print('Full name list:', full_name_list)

    if len(obj1_list) >= 1 and len(obj2_list) >= 1:
        obj1 = obj1_list[-1][0]
        obj2 = obj2_list[-1]  

        attrib_obj1 = mc.listAttr(obj1)
        attrib_obj2 = mc.listAttr(obj2)

        #print("The attributes of {0} are: {1}".format(obj1, attrib_obj1))
        #print("The attributes of {0} are: {1}".format(obj2, attrib_obj2))


        if attrib_obj1 and attrib_obj2:
            src_attr = "{}.{}".format(obj1, attrib_obj1[-1])
            dest_attr = "{}.{}".format(obj2, attrib_obj2[-1])
            mc.connectAttr(src_attr, dest_attr, force=True)
            #print("Connected attribute '{}' of '{}' to '{}' of '{}'".format(src_attr, obj1, dest_attr, obj2))
            sys.stdout.write('New space added!')
        else:
            print("The objects do not have attributes.")
    else:
        mc.warning("Make sure you completed the 2 steps above.")


create_ui()
