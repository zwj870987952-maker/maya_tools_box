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
    if 'keyframe_reduction' in mod:
        del sys.modules[mod]

# 1. Clean previous scene nodes
for n in cmds.ls('pelvis_root*', 'kr_test_cam*', type='transform'):
    if cmds.objExists(n):
        try:
            cmds.delete(n)
        except Exception:
            pass

# Ensure units and undo
cmds.currentUnit(angle='deg', linear='cm')
cmds.undoInfo(state=True)
cmds.autoKeyframe(state=False)

# 2. Build Symmetrical Skeletal Joint Chains
cmds.select(clear=True)
root = cmds.joint(name='pelvis_root', position=[0, 10, 0])

l_sh = cmds.joint(name='L_shoulder', position=[2, 10, 0])
l_el = cmds.joint(name='L_elbow', position=[5, 10, -0.5])
l_wr = cmds.joint(name='L_wrist', position=[8, 10, 0])

cmds.select(root)
r_sh = cmds.joint(name='R_shoulder', position=[-2, 10, 0])
r_el = cmds.joint(name='R_elbow', position=[-5, 10, -0.5])
r_wr = cmds.joint(name='R_wrist', position=[-8, 10, 0])

all_joints = [root, l_sh, l_el, l_wr, r_sh, r_el, r_wr]

# 3. Create dense baked motion on all joints (frame 1 to 36, 1 key per frame)
cmds.playbackOptions(minTime=1, maxTime=36, animationStartTime=1, animationEndTime=36)

for frame in range(1, 37):
    t = frame / 36.0 * 2.0 * math.pi
    # Root sway
    cmds.setKeyframe(root, attribute='translateY', value=10.0 + 1.2 * math.sin(t * 2), time=frame)
    cmds.setKeyframe(root, attribute='translateX', value=1.5 * math.sin(t), time=frame)
    cmds.setKeyframe(root, attribute='rotateY', value=15.0 * math.sin(t), time=frame)
    
    # Left arm swinging
    cmds.setKeyframe(l_sh, attribute='rotateZ', value=-20.0 + 25.0 * math.sin(t), time=frame)
    cmds.setKeyframe(l_sh, attribute='rotateY', value=15.0 * math.cos(t), time=frame)
    cmds.setKeyframe(l_el, attribute='rotateY', value=35.0 + 20.0 * math.sin(t + 0.5), time=frame)
    cmds.setKeyframe(l_wr, attribute='rotateZ', value=-10.0 + 15.0 * math.sin(t + 1.0), time=frame)
    
    # Right arm swinging symmetrically
    cmds.setKeyframe(r_sh, attribute='rotateZ', value=20.0 - 25.0 * math.sin(t), time=frame)
    cmds.setKeyframe(r_sh, attribute='rotateY', value=-15.0 * math.cos(t), time=frame)
    cmds.setKeyframe(r_el, attribute='rotateY', value=-35.0 - 20.0 * math.sin(t + 0.5), time=frame)
    cmds.setKeyframe(r_wr, attribute='rotateZ', value=10.0 - 15.0 * math.sin(t + 1.0), time=frame)

# Gather all created animCurves
curves = []
for j in all_joints:
    for attr in ('translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ'):
        c = cmds.listConnections(f'{j}.{attr}', source=True, destination=False)
        if c:
            curves.append(c[0])

print(f"Total curves created: {len(curves)}")
initial_key_counts = {c: cmds.keyframe(c, query=True, keyframeCount=True) for c in curves}
total_initial_keys = sum(initial_key_counts.values())
print(f"Total initial baked keys across all curves: {total_initial_keys}")

# 4. Load Candidate Tool
rc_path = Path(r"c:\Users\zhongweijie\Documents\GitHub\maya_tools_box\tools_staging_pool\01_animation\maya_keyframe_reduction\release_candidate\launch_candidate.py")
tool = runpy.run_path(str(rc_path))['load_tool']()

# 5. Run Keyframe Reduction
result = tool.run(
    curves=curves,
    error=0.08,
    step=1.0,
    weightedTangents=True,
    tangentSplitAuto=True
)
print("KeyframeReduction result:", result.success, result.message)

reduced_key_counts = {c: cmds.keyframe(c, query=True, keyframeCount=True) for c in curves}
total_reduced_keys = sum(reduced_key_counts.values())
reduction_pct = (1.0 - float(total_reduced_keys) / float(total_initial_keys)) * 100.0
print(f"Total keys after reduction: {total_reduced_keys} (Reduction: {reduction_pct:.1f}%)")

# 6. Test Undo
cmds.undo()
undone_counts = sum(cmds.keyframe(c, query=True, keyframeCount=True) for c in curves)
print(f"Total keys after Undo: {undone_counts} (Expected: {total_initial_keys})")

# Re-apply reduction for playblast
result = tool.run(
    curves=curves,
    error=0.08,
    step=1.0,
    weightedTangents=True,
    tangentSplitAuto=True
)
print("Re-applied reduction for playblast capture.")

# 7. Setup camera for playblast
cam_name = 'kr_test_cam'
if cmds.objExists(cam_name):
    cmds.delete(cam_name)
cam_node, cam_shape = cmds.camera(name=cam_name)
cmds.setAttr(cam_node + '.translate', 0, 10, 30)
cmds.setAttr(cam_node + '.rotate', 0, 0, 0)
cmds.lookThru('modelPanel4', cam_node)

# Set display
cmds.modelEditor('modelPanel4', edit=True, displayAppearance='wireframe', joints=True)

# 8. Playblast sequence
out_dir = Path(r"C:\Users\zhongweijie\.gemini\antigravity\brain\f8152522-dcb3-4911-9254-38b4c32bd26d\snapshots\keyframe_reduction_anim_seq")
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

# 9. Assemble looping GIF
png_files = sorted(glob.glob(str(out_dir / "frame.*.png")))
print(f"Captured {len(png_files)} frames.")
if png_files:
    frames = [Image.open(f) for f in png_files]
    target_gif_snap = Path(r"C:\Users\zhongweijie\.gemini\antigravity\brain\f8152522-dcb3-4911-9254-38b4c32bd26d\snapshots\keyframe_reduction_joint_animation.gif")
    target_gif_root = Path(r"C:\Users\zhongweijie\.gemini\antigravity\brain\f8152522-dcb3-4911-9254-38b4c32bd26d\keyframe_reduction_joint_animation.gif")
    
    frames[0].save(
        target_gif_snap,
        save_all=True,
        append_images=frames[1:],
        duration=41,
        loop=0
    )
    shutil.copy2(target_gif_snap, target_gif_root)
    print("GIF saved to:", target_gif_root)

# 10. Clean up scene
for n in cmds.ls(root, cam_node, type='transform'):
    if cmds.objExists(n):
        try:
            cmds.delete(n)
        except Exception:
            pass
print("Scene cleaned up successfully.")
