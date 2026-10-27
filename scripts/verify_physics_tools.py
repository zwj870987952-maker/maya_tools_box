import os
import glob
import sys
import math
import shutil
from pathlib import Path
import maya.cmds as cmds
import runpy
from PIL import Image

# 0. Clean cached modules
for mod in list(sys.modules):
    if 'physics_tools' in mod:
        del sys.modules[mod]

# 1. Clean previous scene nodes
for n in cmds.ls('pelvis_root*', 'pt_test_cam*', 'mtkPhysics_*', type='transform'):
    if cmds.objExists(n):
        try:
            cmds.delete(n)
        except Exception:
            pass

cmds.currentUnit(angle='deg', linear='cm')
cmds.undoInfo(state=True)
cmds.autoKeyframe(state=False)

# 2. Build Symmetrical Skeletal Joint Chains with Wrist Controls
cmds.select(clear=True)
root = cmds.joint(name='pelvis_root', position=[0, 10, 0])

l_sh = cmds.joint(name='L_shoulder', position=[2, 10, 0])
l_el = cmds.joint(name='L_elbow', position=[5, 10, -0.5])
l_wr = cmds.joint(name='L_wrist', position=[8, 10, 0])

cmds.select(root)
r_sh = cmds.joint(name='R_shoulder', position=[-2, 10, 0])
r_el = cmds.joint(name='R_elbow', position=[-5, 10, -0.5])
r_wr = cmds.joint(name='R_wrist', position=[-8, 10, 0])

l_wr_ctrl = cmds.circle(name='L_wrist_ctrl', radius=1.2, normal=[1, 0, 0], ch=False)[0]
cmds.delete(cmds.parentConstraint(l_wr, l_wr_ctrl))
cmds.parentConstraint(l_wr_ctrl, l_wr, maintainOffset=True)

r_wr_ctrl = cmds.circle(name='R_wrist_ctrl', radius=1.2, normal=[1, 0, 0], ch=False)[0]
cmds.delete(cmds.parentConstraint(r_wr, r_wr_ctrl))
cmds.parentConstraint(r_wr_ctrl, r_wr, maintainOffset=True)

# 3. Dynamic Keyframes across 1-36 frames
cmds.playbackOptions(minTime=1, maxTime=36, animationStartTime=1, animationEndTime=36)

for frame in range(1, 37):
    t = frame / 36.0 * 2.0 * math.pi
    cmds.setKeyframe(root, attribute='translateY', value=10.0 + 1.2 * math.sin(t * 2), time=frame)
    cmds.setKeyframe(root, attribute='translateX', value=1.5 * math.sin(t), time=frame)
    cmds.setKeyframe(root, attribute='rotateY', value=15.0 * math.sin(t), time=frame)
    
    cmds.setKeyframe(l_sh, attribute='rotateZ', value=-20.0 + 25.0 * math.sin(t), time=frame)
    cmds.setKeyframe(l_wr_ctrl, attribute='translateY', value=10.0 + 3.0 * math.sin(t), time=frame)
    cmds.setKeyframe(l_wr_ctrl, attribute='translateX', value=8.0 + 2.0 * math.cos(t), time=frame)
    
    cmds.setKeyframe(r_sh, attribute='rotateZ', value=20.0 - 25.0 * math.sin(t), time=frame)
    cmds.setKeyframe(r_wr_ctrl, attribute='translateY', value=10.0 + 3.0 * math.sin(t), time=frame)
    cmds.setKeyframe(r_wr_ctrl, attribute='translateX', value=-8.0 - 2.0 * math.cos(t), time=frame)

# 4. Load Physics Tools Tool
rc_path = Path(r"c:\Users\zhongweijie\Documents\GitHub\maya_tools_box\tools_staging_pool\01_animation\physics_tools\release_candidate\launch_candidate.py")
tool = runpy.run_path(str(rc_path))['load_tool']()

# Test Inspect
inspect_res = tool.run(action='inspect')
print("Inspect result:", inspect_res.success)

# 5. Invoke toLocator procedure on L_wrist_ctrl across frames 1..36
loc_res = tool.run(action='invoke', procedure='toLocator', targets=[l_wr_ctrl], frame_range=[1, 36])
print("toLocator result:", loc_res.success, loc_res.message, loc_res.data)
print("toLocator errors:", loc_res.errors)

# Test Undo
cmds.undo()
print("Undo toLocator succeeded.")

# Re-apply toLocator for visual demonstration in playblast
loc_res = tool.run(action='invoke', procedure='toLocator', targets=[l_wr_ctrl], frame_range=[1, 36])
print("Re-applied toLocator for playblast.")

# 6. Setup camera for playblast
cam_name = 'pt_test_cam'
if cmds.objExists(cam_name):
    cmds.delete(cam_name)
cam_node, cam_shape = cmds.camera(name=cam_name)
cmds.setAttr(cam_node + '.translate', 0, 10, 32)
cmds.setAttr(cam_node + '.rotate', 0, 0, 0)
cmds.lookThru('modelPanel4', cam_node)

# Set display
cmds.modelEditor('modelPanel4', edit=True, displayAppearance='wireframe', joints=True, locators=True, nurbsCurves=True)

# 7. Playblast sequence
out_dir = Path(r"C:\Users\zhongweijie\.gemini\antigravity\brain\f8152522-dcb3-4911-9254-38b4c32bd26d\snapshots\physics_tools_anim_seq")
if out_dir.exists():
    shutil.rmtree(out_dir)
out_dir.mkdir(parents=True, exist_ok=True)

prefix = str(out_dir / "frame")
cmds.currentTime(1)
cmds.playblast(
    format='image',
    filename=prefix,
    sequenceTime=0,
    clearCache=True,
    viewer=False,
    showOrnaments=False,
    fp=4,
    percent=100,
    compression='png',
    quality=100,
    widthHeight=[640, 480],
    startTime=1,
    endTime=36,
    forceOverwrite=True
)
print("Playblast completed.")

# 8. Assemble looping GIF
png_files = sorted(glob.glob(str(out_dir / "frame.*.png")))
print(f"Captured {len(png_files)} frames.")
if png_files:
    frames = [Image.open(f) for f in png_files]
    target_gif_snap = Path(r"C:\Users\zhongweijie\.gemini\antigravity\brain\f8152522-dcb3-4911-9254-38b4c32bd26d\snapshots\physics_tools_joint_animation.gif")
    target_gif_root = Path(r"C:\Users\zhongweijie\.gemini\antigravity\brain\f8152522-dcb3-4911-9254-38b4c32bd26d\physics_tools_joint_animation.gif")
    
    frames[0].save(
        target_gif_snap,
        save_all=True,
        append_images=frames[1:],
        duration=41,
        loop=0
    )
    shutil.copy2(target_gif_snap, target_gif_root)
    print("GIF saved to:", target_gif_root)

# 9. Clean up scene
tool.run(action='cleanup_session')
for n in cmds.ls(root, l_wr_ctrl, r_wr_ctrl, cam_node, type='transform'):
    if cmds.objExists(n):
        try:
            cmds.delete(n)
        except Exception:
            pass
print("Scene cleaned up successfully.")
