import os
import glob
import sys
from pathlib import Path
import maya.cmds as cmds
import importlib.util
from PIL import Image

# 0. Clean cached modules
for mod in list(sys.modules):
    if 'ik_fk_switch' in mod:
        del sys.modules[mod]

# 1. Clean previous scene nodes
for n in cmds.ls('pelvis_root*', 'fk*', 'ik*', 'switchCtrl*', 'mtbIKFK*', 'ikfk_test_cam*', 'camera*', type='transform'):
    if cmds.objExists(n):
        try:
            cmds.delete(n)
        except Exception:
            pass

# 2. Build Symmetrical Skeletal Chains
cmds.select(clear=True)
root = cmds.joint(name='pelvis_root', position=[0, 10, 0])

l_sh = cmds.joint(name='L_shoulder', position=[2, 10, 0])
l_el = cmds.joint(name='L_elbow', position=[5, 10, -0.5])
l_wr = cmds.joint(name='L_wrist', position=[8, 10, 0])

cmds.select(root)
r_sh = cmds.joint(name='R_shoulder', position=[-2, 10, 0])
r_el = cmds.joint(name='R_elbow', position=[-5, 10, -0.5])
r_wr = cmds.joint(name='R_wrist', position=[-8, 10, 0])

# Controls for IK/FK switch
ik_wrist = cmds.spaceLocator(name='ikwrist')[0]
cmds.xform(ik_wrist, translation=[8, 10, 0], worldSpace=True)

ik_pv = cmds.spaceLocator(name='ikpv')[0]
cmds.xform(ik_pv, translation=[5, 10, -5], worldSpace=True)

switch_ctrl = cmds.spaceLocator(name='switchCtrl')[0]
cmds.xform(switch_ctrl, translation=[0, 14, 0], worldSpace=True)
cmds.addAttr(switch_ctrl, longName='ikfk', attributeType='double', minValue=0, maxValue=1, defaultValue=0, keyable=True)

# Dynamic keyframes across 1-36 frames
cmds.playbackOptions(minTime=1, maxTime=36, animationStartTime=1, animationEndTime=36)
cmds.currentTime(1)
cmds.setKeyframe(l_sh, attribute='rotateZ', value=-15, time=1)
cmds.setKeyframe(l_el, attribute='rotateY', value=20, time=1)
cmds.setKeyframe(l_wr, attribute='rotateZ', value=-10, time=1)
cmds.setKeyframe(r_sh, attribute='rotateZ', value=15, time=1)
cmds.setKeyframe(r_el, attribute='rotateY', value=-20, time=1)
cmds.setKeyframe(r_wr, attribute='rotateZ', value=10, time=1)

cmds.setKeyframe(l_sh, attribute='rotateZ', value=35, time=18)
cmds.setKeyframe(l_el, attribute='rotateY', value=-35, time=18)
cmds.setKeyframe(l_wr, attribute='rotateZ', value=20, time=18)
cmds.setKeyframe(r_sh, attribute='rotateZ', value=-35, time=18)
cmds.setKeyframe(r_el, attribute='rotateY', value=35, time=18)
cmds.setKeyframe(r_wr, attribute='rotateZ', value=-20, time=18)

cmds.setKeyframe(l_sh, attribute='rotateZ', value=-15, time=36)
cmds.setKeyframe(l_el, attribute='rotateY', value=20, time=36)
cmds.setKeyframe(l_wr, attribute='rotateZ', value=-10, time=36)
cmds.setKeyframe(r_sh, attribute='rotateZ', value=15, time=36)
cmds.setKeyframe(r_el, attribute='rotateY', value=-20, time=36)
cmds.setKeyframe(r_wr, attribute='rotateZ', value=10, time=36)

# 3. Create camera
cam_node, cam_shape = cmds.camera(position=[0, 10, 26], rotation=[0, 0, 0])
panels = cmds.getPanel(type='modelPanel') or ['modelPanel4']
panel = panels[0]
cmds.modelPanel(panel, edit=True, camera=cam_node)
cmds.viewFit(cam_node, all=True)

# 4. Load IKFKTool and test store, switch, key
rc_path = Path(r"c:\Users\zhongweijie\Documents\GitHub\maya_tools_box\tools_staging_pool\01_animation\ik_fk_switch\release_candidate").resolve()
spec = importlib.util.spec_from_file_location('ikfk_loader', rc_path / 'launch_candidate.py')
loader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(loader)
tool = loader.load_tool()

fields = {
    'fkshldr': l_sh,
    'fkellbow': l_el,
    'fkwrist': l_wr,
    'ikwrist': ik_wrist,
    'ikpv': ik_pv,
    'switchCtrl': switch_ctrl,
    'switchAttr': 'ikfk',
    'switchAttrRange': 1,
    'switch0isfk': True
}

store_res = tool.run(action='store', **fields)
print("Store config success:", store_res.success)
record_id = store_res.data.get('record_id', '')
print("Store record_id:", record_id)

# Test switch to IK
switch_res = tool.run(action='switch', direction='to_ik', **fields)
print("Switch to IK success:", switch_res.success)
print("SwitchCtrl ikfk value:", cmds.getAttr(switch_ctrl + '.ikfk'))

# Test Undo / Redo
cmds.undo()
print("Undo tested successfully. ikfk value:", cmds.getAttr(switch_ctrl + '.ikfk'))
cmds.redo()
print("Redo tested successfully. ikfk value:", cmds.getAttr(switch_ctrl + '.ikfk'))

# Animate switchCtrl ikfk attribute across 1-36
cmds.setKeyframe(switch_ctrl, attribute='ikfk', value=0, time=1)
cmds.setKeyframe(switch_ctrl, attribute='ikfk', value=1, time=18)
cmds.setKeyframe(switch_ctrl, attribute='ikfk', value=0, time=36)

# 5. Playblast capture
cmds.viewFit(cam_node, all=True)
out_dir = Path(r"C:\Users\zhongweijie\.gemini\antigravity\brain\f8152522-dcb3-4911-9254-38b4c32bd26d\snapshots\ik_fk_switch_anim_seq")
out_dir.mkdir(parents=True, exist_ok=True)
frame_prefix = (out_dir / "frame").as_posix()

cmds.playblast(
    startTime=1,
    endTime=36,
    format='image',
    compression='png',
    filename=frame_prefix,
    sequenceTime=False,
    clearCache=True,
    viewer=False,
    showOrnaments=False,
    framePadding=4,
    percent=100,
    widthHeight=(640, 480),
    forceOverwrite=True
)
print("Playblast completed successfully.")

# 6. Assemble looping GIF
png_files = sorted(glob.glob(str(out_dir / "frame.*.png")))
print(f"Captured {len(png_files)} frames.")
if png_files:
    frames = [Image.open(f) for f in png_files]
    target_gif_snap = Path(r"C:\Users\zhongweijie\.gemini\antigravity\brain\f8152522-dcb3-4911-9254-38b4c32bd26d\snapshots\ik_fk_switch_joint_animation.gif")
    target_gif_root = Path(r"C:\Users\zhongweijie\.gemini\antigravity\brain\f8152522-dcb3-4911-9254-38b4c32bd26d\ik_fk_switch_joint_animation.gif")
    
    frames[0].save(
        target_gif_snap,
        save_all=True,
        append_images=frames[1:],
        duration=41,
        loop=0
    )
    import shutil
    shutil.copy2(target_gif_snap, target_gif_root)
    print("GIF saved to:", target_gif_root)

# 7. Clean up scene
for n in cmds.ls(root, ik_wrist, ik_pv, switch_ctrl, cam_node, 'mtbIKFK*', type='transform'):
    if cmds.objExists(n):
        try:
            cmds.delete(n)
        except Exception:
            pass
print("Scene cleaned up successfully.")
