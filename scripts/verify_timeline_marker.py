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
    if 'timeline_marker' in mod:
        del sys.modules[mod]

# 1. Clean previous scene nodes
for n in cmds.ls('pelvis_root*', 'tm_test_cam*', type='transform'):
    if cmds.objExists(n):
        try:
            cmds.delete(n)
        except Exception:
            pass

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

# 3. Create Dynamic Animation Keyframes on Joint Chains across 1-36 frames
cmds.playbackOptions(minTime=1, maxTime=36, animationStartTime=1, animationEndTime=36)

# Frame 1: Rest pose
cmds.setKeyframe(root, attribute='translateY', value=10.0, time=1)
cmds.setKeyframe(l_sh, attribute='rotateZ', value=-15.0, time=1)
cmds.setKeyframe(l_el, attribute='rotateY', value=20.0, time=1)
cmds.setKeyframe(r_sh, attribute='rotateZ', value=15.0, time=1)
cmds.setKeyframe(r_el, attribute='rotateY', value=-20.0, time=1)

# Frame 12: Punch Contact (Left punch extended forward, Right arm pulled back)
cmds.setKeyframe(root, attribute='translateY', value=9.2, time=12)
cmds.setKeyframe(root, attribute='rotateY', value=25.0, time=12)
cmds.setKeyframe(l_sh, attribute='rotateZ', value=-5.0, time=12)
cmds.setKeyframe(l_sh, attribute='rotateY', value=-45.0, time=12)
cmds.setKeyframe(l_el, attribute='rotateY', value=5.0, time=12)
cmds.setKeyframe(r_sh, attribute='rotateZ', value=30.0, time=12)
cmds.setKeyframe(r_sh, attribute='rotateY', value=40.0, time=12)
cmds.setKeyframe(r_el, attribute='rotateY', value=-85.0, time=12)

# Frame 24: Block Passing (Left arm curled in defense, Right arm countering)
cmds.setKeyframe(root, attribute='translateY', value=10.5, time=24)
cmds.setKeyframe(root, attribute='rotateY', value=-20.0, time=24)
cmds.setKeyframe(l_sh, attribute='rotateZ', value=-25.0, time=24)
cmds.setKeyframe(l_sh, attribute='rotateY', value=35.0, time=24)
cmds.setKeyframe(l_el, attribute='rotateY', value=75.0, time=24)
cmds.setKeyframe(r_sh, attribute='rotateZ', value=10.0, time=24)
cmds.setKeyframe(r_sh, attribute='rotateY', value=-35.0, time=24)
cmds.setKeyframe(r_el, attribute='rotateY', value=-15.0, time=24)

# Frame 36: Recoil / Rest pose return
cmds.setKeyframe(root, attribute='translateY', value=10.0, time=36)
cmds.setKeyframe(root, attribute='rotateY', value=0.0, time=36)
cmds.setKeyframe(l_sh, attribute='rotateZ', value=-15.0, time=36)
cmds.setKeyframe(l_sh, attribute='rotateY', value=20.0, time=36)
cmds.setKeyframe(l_el, attribute='rotateY', value=20.0, time=36)
cmds.setKeyframe(r_sh, attribute='rotateZ', value=15.0, time=36)
cmds.setKeyframe(r_sh, attribute='rotateY', value=-20.0, time=36)
cmds.setKeyframe(r_el, attribute='rotateY', value=-20.0, time=36)

# 4. Load Timeline Marker Tool
rc_path = Path(r"c:\Users\zhongweijie\Documents\GitHub\maya_tools_box\tools_staging_pool\01_animation\maya_timeline_marker\release_candidate\launch_candidate.py")
tool = runpy.run_path(str(rc_path))['load_tool']()

# Clear any pre-existing markers
tool.run(action='clear')

# 5. Add Key Poses Markers on the Timeline
markers_to_add = [
    (1, [0, 255, 0], "Pose: 起始站立 (Rest)"),
    (12, [255, 50, 50], "Pose: 挥拳出击 (Punch Contact)"),
    (24, [50, 120, 255], "Pose: 招架回防 (Block Passing)"),
    (36, [255, 215, 0], "Pose: 缓冲收势 (Recoil)"),
]

for frame, color, comment in markers_to_add:
    res = tool.run(action='add', frames=[frame], color=color, comment=comment)
    print(f"Added marker at frame {frame}: success={res.success}")

# 6. Inspect Markers
inspect_res = tool.run(action='inspect')
print("Inspect result count:", inspect_res.data['count'])
print("Inspect frames:", inspect_res.data['markers']['frames'])
print("Inspect comments:", inspect_res.data['markers']['comments'])

# 7. Test Undo
cmds.undo()
inspect_undo = tool.run(action='inspect')
print(f"Count after single undo: {inspect_undo.data['count']} (Undid frame 36)")

# Test Redo
cmds.redo()
inspect_redo = tool.run(action='inspect')
print(f"Count after redo: {inspect_redo.data['count']}")

# 8. Camera setup for playblast
cam_name = 'tm_test_cam'
if cmds.objExists(cam_name):
    cmds.delete(cam_name)
cam_node, cam_shape = cmds.camera(name=cam_name)
cmds.setAttr(cam_node + '.translate', 0, 10, 30)
cmds.setAttr(cam_node + '.rotate', 0, 0, 0)
cmds.lookThru('modelPanel4', cam_node)

# Set display
cmds.modelEditor('modelPanel4', edit=True, displayAppearance='wireframe', joints=True)

# 9. Playblast sequence
out_dir = Path(r"C:\Users\zhongweijie\.gemini\antigravity\brain\f8152522-dcb3-4911-9254-38b4c32bd26d\snapshots\timeline_marker_anim_seq")
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

# 10. Assemble looping GIF
png_files = sorted(glob.glob(str(out_dir / "frame.*.png")))
print(f"Captured {len(png_files)} frames.")
if png_files:
    frames = [Image.open(f) for f in png_files]
    target_gif_snap = Path(r"C:\Users\zhongweijie\.gemini\antigravity\brain\f8152522-dcb3-4911-9254-38b4c32bd26d\snapshots\timeline_marker_joint_animation.gif")
    target_gif_root = Path(r"C:\Users\zhongweijie\.gemini\antigravity\brain\f8152522-dcb3-4911-9254-38b4c32bd26d\timeline_marker_joint_animation.gif")
    
    frames[0].save(
        target_gif_snap,
        save_all=True,
        append_images=frames[1:],
        duration=41,
        loop=0
    )
    shutil.copy2(target_gif_snap, target_gif_root)
    print("GIF saved to:", target_gif_root)

# 11. Clean up scene
for n in cmds.ls(root, cam_node, type='transform'):
    if cmds.objExists(n):
        try:
            cmds.delete(n)
        except Exception:
            pass
tool.run(action='clear')
print("Scene cleaned up successfully.")
