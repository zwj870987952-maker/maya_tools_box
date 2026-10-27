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
    if 'pose_matcher' in mod:
        del sys.modules[mod]

# 1. Clean previous scene nodes
for n in cmds.ls('src_pelvis*', 'tgt_pelvis*', 'pm_test_cam*', type='transform'):
    if cmds.objExists(n):
        try:
            cmds.delete(n)
        except Exception:
            pass

cmds.currentUnit(angle='deg', linear='cm')
cmds.undoInfo(state=True)
cmds.autoKeyframe(state=False)

# 2. Build Symmetrical Source Skeletal Joint Chains
cmds.select(clear=True)
src_root = cmds.joint(name='src_pelvis', position=[0, 10, -5])

src_l_sh = cmds.joint(name='src_L_shoulder', position=[2, 10, -5])
src_l_el = cmds.joint(name='src_L_elbow', position=[5, 10, -5.5])
src_l_wr = cmds.joint(name='src_L_wrist', position=[8, 10, -5])

cmds.select(src_root)
src_r_sh = cmds.joint(name='src_R_shoulder', position=[-2, 10, -5])
src_r_el = cmds.joint(name='src_R_elbow', position=[-5, 10, -5.5])
src_r_wr = cmds.joint(name='src_R_wrist', position=[-8, 10, -5])

# Build Symmetrical Target Skeletal Joint Chains (offset forward Z=5, in T-pose without keys)
cmds.select(clear=True)
tgt_root = cmds.joint(name='tgt_pelvis', position=[0, 10, 5])

tgt_l_sh = cmds.joint(name='tgt_L_shoulder', position=[2, 10, 5])
tgt_l_el = cmds.joint(name='tgt_L_elbow', position=[5, 10, 5])
tgt_l_wr = cmds.joint(name='tgt_L_wrist', position=[8, 10, 5])

cmds.select(tgt_root)
tgt_r_sh = cmds.joint(name='tgt_R_shoulder', position=[-2, 10, 5])
tgt_r_el = cmds.joint(name='tgt_R_elbow', position=[-5, 10, 5])
tgt_r_wr = cmds.joint(name='tgt_R_wrist', position=[-8, 10, 5])

# 3. Dynamic Keyframes on Source Skeleton across 1-36 frames
cmds.playbackOptions(minTime=1, maxTime=36, animationStartTime=1, animationEndTime=36)

for frame in range(1, 37):
    t = frame / 36.0 * 2.0 * math.pi
    cmds.setKeyframe(src_root, attribute='translateY', value=10.0 + 1.2 * math.sin(t * 2), time=frame)
    cmds.setKeyframe(src_root, attribute='rotateY', value=20.0 * math.sin(t), time=frame)
    cmds.setKeyframe(src_l_sh, attribute='rotateZ', value=-20.0 + 35.0 * math.sin(t), time=frame)
    cmds.setKeyframe(src_l_el, attribute='rotateY', value=30.0 + 30.0 * math.sin(t + 0.5), time=frame)
    cmds.setKeyframe(src_r_sh, attribute='rotateZ', value=20.0 - 35.0 * math.sin(t), time=frame)
    cmds.setKeyframe(src_r_el, attribute='rotateY', value=-30.0 - 30.0 * math.sin(t + 0.5), time=frame)

# 4. Load Pose Matcher Tool
rc_path = Path(r"c:\Users\zhongweijie\Documents\GitHub\maya_tools_box\tools_staging_pool\01_animation\pose_matcher\release_candidate\launch_candidate.py")
tool = runpy.run_path(str(rc_path))['load_tool']()

# Map child joints (elbows and wrists drive the orientation of shoulders and elbows)
joint_map = {
    'src_L_elbow': 'tgt_L_elbow',
    'src_L_wrist': 'tgt_L_wrist',
    'src_R_elbow': 'tgt_R_elbow',
    'src_R_wrist': 'tgt_R_wrist',
}

# 5. Align Target Skeleton to Source at Frame 18
cmds.currentTime(18)
align_res = tool.run(action='align', source_root=src_root, target_root=tgt_root, joint_map=joint_map)
print("Align result:", align_res.success, align_res.message, align_res.data)

# Test Undo
cmds.undo()
print("Undo align verified.")

# Re-apply Align
align_res = tool.run(action='align', source_root=src_root, target_root=tgt_root, joint_map=joint_map)
print("Re-applied Align for visual comparison.")

# 6. Setup camera for playblast (framing both source and target skeletons side by side)
cam_name = 'pm_test_cam'
if cmds.objExists(cam_name):
    cmds.delete(cam_name)
cam_node, cam_shape = cmds.camera(name=cam_name)
cmds.setAttr(cam_node + '.translate', 0, 15, 38)
cmds.setAttr(cam_node + '.rotate', -12, 0, 0)
cmds.lookThru('modelPanel4', cam_node)

# Set display
cmds.modelEditor('modelPanel4', edit=True, displayAppearance='wireframe', joints=True)

# 7. Playblast sequence
out_dir = Path(r"C:\Users\zhongweijie\.gemini\antigravity\brain\f8152522-dcb3-4911-9254-38b4c32bd26d\snapshots\pose_matcher_anim_seq")
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
    target_gif_snap = Path(r"C:\Users\zhongweijie\.gemini\antigravity\brain\f8152522-dcb3-4911-9254-38b4c32bd26d\snapshots\pose_matcher_joint_animation.gif")
    target_gif_root = Path(r"C:\Users\zhongweijie\.gemini\antigravity\brain\f8152522-dcb3-4911-9254-38b4c32bd26d\pose_matcher_joint_animation.gif")
    
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
for n in cmds.ls(src_root, tgt_root, cam_node, type='transform'):
    if cmds.objExists(n):
        try:
            cmds.delete(n)
        except Exception:
            pass
print("Scene cleaned up successfully.")
