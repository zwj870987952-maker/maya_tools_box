import os
import glob
import sys
import shutil
from pathlib import Path
import maya.cmds as cmds
import runpy
from PIL import Image

# 0. Clean cached modules
for mod in list(sys.modules):
    if 'lock_to_world' in mod:
        del sys.modules[mod]

# 1. Clean previous scene nodes
for n in cmds.ls('body_ctrl*', 'pelvis_root*', 'lock_test_cam*', type='transform'):
    if cmds.objExists(n):
        try:
            cmds.delete(n)
        except Exception:
            pass

# Ensure deg/cm and undo
cmds.currentUnit(angle='deg', linear='cm')
cmds.undoInfo(state=True)
cmds.autoKeyframe(state=False)

# 2. Build Symmetrical Skeletal Joint Chains with Moving Body Parent
body_ctrl = cmds.circle(name='body_ctrl', radius=3.0, normal=[0, 1, 0], ch=False)[0]

cmds.select(clear=True)
root = cmds.joint(name='pelvis_root', position=[0, 10, 0])
cmds.parent(root, body_ctrl)

l_sh = cmds.joint(name='L_shoulder', position=[2, 10, 0])
l_el = cmds.joint(name='L_elbow', position=[5, 10, -0.5])
l_wr = cmds.joint(name='L_wrist', position=[8, 10, 0])

cmds.select(root)
r_sh = cmds.joint(name='R_shoulder', position=[-2, 10, 0])
r_el = cmds.joint(name='R_elbow', position=[-5, 10, -0.5])
r_wr = cmds.joint(name='R_wrist', position=[-8, 10, 0])

# Controls
l_wr_ctrl = cmds.circle(name='L_wrist_ctrl', radius=1.2, normal=[1, 0, 0], ch=False)[0]
cmds.delete(cmds.parentConstraint(l_wr, l_wr_ctrl))
cmds.parent(l_wr_ctrl, body_ctrl)
cmds.parentConstraint(l_wr_ctrl, l_wr, maintainOffset=True)

r_wr_ctrl = cmds.circle(name='R_wrist_ctrl', radius=1.2, normal=[1, 0, 0], ch=False)[0]
cmds.delete(cmds.parentConstraint(r_wr, r_wr_ctrl))
cmds.parent(r_wr_ctrl, body_ctrl)
cmds.parentConstraint(r_wr_ctrl, r_wr, maintainOffset=True)

# 3. Dynamic Keyframes across 1-36 frames on body_ctrl
cmds.playbackOptions(minTime=1, maxTime=36, animationStartTime=1, animationEndTime=36)

keyframes_body = [
    (1, 0.0, 10.0, 0.0, 0.0, 0.0, 0.0),
    (9, -3.0, 9.0, 2.0, 0.0, -15.0, 5.0),
    (18, 0.0, 11.0, -1.0, 0.0, 10.0, -5.0),
    (27, 3.5, 9.5, 2.5, 0.0, 20.0, 8.0),
    (36, 0.0, 10.0, 0.0, 0.0, 0.0, 0.0),
]

for frame, tx, ty, tz, rx, ry, rz in keyframes_body:
    cmds.setKeyframe(body_ctrl, attribute='translateX', value=tx, time=frame)
    cmds.setKeyframe(body_ctrl, attribute='translateY', value=ty, time=frame)
    cmds.setKeyframe(body_ctrl, attribute='translateZ', value=tz, time=frame)
    cmds.setKeyframe(body_ctrl, attribute='rotateX', value=rx, time=frame)
    cmds.setKeyframe(body_ctrl, attribute='rotateY', value=ry, time=frame)
    cmds.setKeyframe(body_ctrl, attribute='rotateZ', value=rz, time=frame)

# Also add subtle arm movement
for frame, l_rz, r_rz in [(1, -15, 15), (18, -35, 35), (36, -15, 15)]:
    cmds.setKeyframe(l_sh, attribute='rotateZ', value=l_rz, time=frame)
    cmds.setKeyframe(r_sh, attribute='rotateZ', value=r_rz, time=frame)

# 4. Load Candidate Tool
rc_path = Path(r"c:\Users\zhongweijie\Documents\GitHub\maya_tools_box\tools_staging_pool\01_animation\lock_to_world\release_candidate\launch_candidate.py")
tool = runpy.run_path(str(rc_path))['load_tool']()

# Record world position of L_wrist_ctrl at frame 10 and 20 before lock
cmds.currentTime(10)
pos10_before = cmds.xform(l_wr_ctrl, query=True, worldSpace=True, translation=True)
cmds.currentTime(20)
pos20_before = cmds.xform(l_wr_ctrl, query=True, worldSpace=True, translation=True)
print("Before lock - Frame 10:", pos10_before)
print("Before lock - Frame 20:", pos20_before)

# 5. Lock L_wrist_ctrl to world space during frames 10..25
lock_res = tool.run(objects=[l_wr_ctrl], start=10, end=25)
print("Lock result:", lock_res.success, lock_res.message, lock_res.data)
print("Undo item name:", cmds.undoInfo(query=True, undoName=True))

# Check world position after lock
cmds.currentTime(10)
pos10_after = cmds.xform(l_wr_ctrl, query=True, worldSpace=True, translation=True)
cmds.currentTime(20)
pos20_after = cmds.xform(l_wr_ctrl, query=True, worldSpace=True, translation=True)
cmds.currentTime(25)
pos25_after = cmds.xform(l_wr_ctrl, query=True, worldSpace=True, translation=True)
print("After lock - Frame 10:", pos10_after)
print("After lock - Frame 20:", pos20_after)
print("After lock - Frame 25:", pos25_after)

# Verify world fixity: pos10 and pos20 should be virtually identical
diff = sum(abs(a - b) for a, b in zip(pos10_after, pos20_after))
print("Position difference frame 10 vs 20 after lock:", diff)

# Test Undo: Undo the tool
# Check keys on L_wrist_ctrl
keys_locked = cmds.keyframe(l_wr_ctrl, query=True, timeChange=True) or []
print(f"Keys on L_wrist_ctrl when locked: {len(keys_locked)}")
cmds.undo()
keys_undone = cmds.keyframe(l_wr_ctrl, query=True, timeChange=True) or []
print(f"Keys on L_wrist_ctrl after undo: {len(keys_undone)}")
# Verify keys removed by undo
if len(keys_undone) == 0:
    print("Undo verified cleanly: all baked keys reverted!")

# Re-apply lock for playblast
lock_res = tool.run(objects=[l_wr_ctrl], start=10, end=25)
print("Re-applied lock for playblast demonstration.")

# 6. Setup camera for playblast
cam_name = 'lock_test_cam'
if cmds.objExists(cam_name):
    cmds.delete(cam_name)
cam_node, cam_shape = cmds.camera(name=cam_name)
cmds.setAttr(cam_node + '.translate', 0, 11, 35)
cmds.setAttr(cam_node + '.rotate', -5, 0, 0)
cmds.lookThru('modelPanel4', cam_node)

# Set display: wireframe, joints, curves
cmds.modelEditor('modelPanel4', edit=True, displayAppearance='wireframe', joints=True, nurbsCurves=True)

# 7. Playblast sequence
out_dir = Path(r"C:\Users\zhongweijie\.gemini\antigravity\brain\f8152522-dcb3-4911-9254-38b4c32bd26d\snapshots\lock_to_world_anim_seq")
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
    target_gif_snap = Path(r"C:\Users\zhongweijie\.gemini\antigravity\brain\f8152522-dcb3-4911-9254-38b4c32bd26d\snapshots\lock_to_world_joint_animation.gif")
    target_gif_root = Path(r"C:\Users\zhongweijie\.gemini\antigravity\brain\f8152522-dcb3-4911-9254-38b4c32bd26d\lock_to_world_joint_animation.gif")
    
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
for n in cmds.ls(body_ctrl, cam_node, type='transform'):
    if cmds.objExists(n):
        try:
            cmds.delete(n)
        except Exception:
            pass
print("Scene cleaned up successfully.")
