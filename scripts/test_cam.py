import maya.cmds as cmds
cam = 'mirror_test_cam'
for c in cmds.ls('mirror_test_cam*', type='transform'):
    try:
        cmds.delete(c)
    except Exception:
        pass
cam_node, cam_shape = cmds.camera(position=[0, 10, 24], rotation=[-5, 0, 0])
panels = cmds.getPanel(type='modelPanel') or ['modelPanel4']
panel = panels[0]
cmds.modelPanel(panel, edit=True, camera=cam_node)
cmds.viewFit(cam_node, all=True)
print("Camera assigned successfully:", cam_node)
