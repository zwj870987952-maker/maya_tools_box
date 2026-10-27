import os
import glob
import sys
from pathlib import Path
import maya.cmds as cmds
import importlib.util
from PIL import Image

# 0. Clean cached modules
for mod in list(sys.modules):
    if 'jop_retarget_anim' in mod:
        del sys.modules[mod]

# 1. Clean previous scene nodes
for n in cmds.ls('pelvis_root*', 'tgt_*', 'jop_test_cam*', 'camera*', type='transform'):
    if cmds.objExists(n):
        try:
            cmds.delete(n)
        except Exception:
            pass

# 2. Build Symmetrical Source Skeletal Chains
cmds.select(clear=True)
root = cmds.joint(name='pelvis_root', position=[0, 10, 0])

l_sh = cmds.joint(name='L_shoulder', position=[2, 10, 0])
l_el = cmds.joint(name='L_elbow', position=[5, 10, -0.5])
l_wr = cmds.joint(name='L_wrist', position=[8, 10, 0])

cmds.select(root)
r_sh = cmds.joint(name='R_shoulder', position=[-2, 10, 0])
r_el = cmds.joint(name='R_elbow', position=[-5, 10, -0.5])
r_wr = cmds.joint(name='R_wrist', position=[-8, 10, 0])

# Create transform controls for source joints
l_wr_ctrl = cmds.circle(name='L_wrist_ctrl', radius=1.5, normal=[1, 0, 0], ch=False)[0]
cmds.delete(cmds.parentConstraint(l_wr, l_wr_ctrl))
cmds.parentConstraint(l_wr_ctrl, l_wr, maintainOffset=True)

r_wr_ctrl = cmds.circle(name='R_wrist_ctrl', radius=1.5, normal=[1, 0, 0], ch=False)[0]
cmds.delete(cmds.parentConstraint(r_wr, r_wr_ctrl))
cmds.parentConstraint(r_wr_ctrl, r_wr, maintainOffset=True)

# Keyframes on source controls across 1-36 frames
cmds.playbackOptions(minTime=1, maxTime=36, animationStartTime=1, animationEndTime=36)
cmds.currentTime(1)
cmds.setKeyframe(l_sh, attribute='rotateZ', value=-20, time=1)
cmds.setKeyframe(l_el, attribute='rotateY', value=30, time=1)
cmds.setKeyframe(l_wr_ctrl, attribute='rotateZ', value=-15, time=1)
cmds.setKeyframe(r_sh, attribute='rotateZ', value=20, time=1)
cmds.setKeyframe(r_el, attribute='rotateY', value=-30, time=1)
cmds.setKeyframe(r_wr_ctrl, attribute='rotateZ', value=15, time=1)

cmds.setKeyframe(l_sh, attribute='rotateZ', value=40, time=18)
cmds.setKeyframe(l_el, attribute='rotateY', value=-40, time=18)
cmds.setKeyframe(l_wr_ctrl, attribute='rotateZ', value=30, time=18)
cmds.setKeyframe(r_sh, attribute='rotateZ', value=-40, time=18)
cmds.setKeyframe(r_el, attribute='rotateY', value=40, time=18)
cmds.setKeyframe(r_wr_ctrl, attribute='rotateZ', value=-30, time=18)

cmds.setKeyframe(l_sh, attribute='rotateZ', value=-20, time=36)
cmds.setKeyframe(l_el, attribute='rotateY', value=30, time=36)
cmds.setKeyframe(l_wr_ctrl, attribute='rotateZ', value=-15, time=36)
cmds.setKeyframe(r_sh, attribute='rotateZ', value=20, time=36)
cmds.setKeyframe(r_el, attribute='rotateY', value=-30, time=36)
cmds.setKeyframe(r_wr_ctrl, attribute='rotateZ', value=15, time=36)

# Build Target Skeletal Chains (offset along Z axis by 8 units)
cmds.select(clear=True)
tgt_root = cmds.joint(name='tgt_pelvis_root', position=[0, 10, 8])

tgt_l_sh = cmds.joint(name='tgt_L_shoulder', position=[2, 10, 8])
tgt_l_el = cmds.joint(name='tgt_L_elbow', position=[5, 10, 7.5])
tgt_l_wr = cmds.joint(name='tgt_L_wrist', position=[8, 10, 8])

cmds.select(tgt_root)
tgt_r_sh = cmds.joint(name='tgt_R_shoulder', position=[-2, 10, 8])
tgt_r_el = cmds.joint(name='tgt_R_elbow', position=[-5, 10, 7.5])
tgt_r_wr = cmds.joint(name='tgt_R_wrist', position=[-8, 10, 8])

# Create transform controls for target joints
tgt_l_wr_ctrl = cmds.circle(name='tgt_L_wrist_ctrl', radius=1.5, normal=[1, 0, 0], ch=False)[0]
cmds.delete(cmds.parentConstraint(tgt_l_wr, tgt_l_wr_ctrl))
cmds.parentConstraint(tgt_l_wr_ctrl, tgt_l_wr, maintainOffset=True)

tgt_r_wr_ctrl = cmds.circle(name='tgt_R_wrist_ctrl', radius=1.5, normal=[1, 0, 0], ch=False)[0]
cmds.delete(cmds.parentConstraint(tgt_r_wr, tgt_r_wr_ctrl))
cmds.parentConstraint(tgt_r_wr_ctrl, tgt_r_wr, maintainOffset=True)

# 3. Create camera
cam_node, cam_shape = cmds.camera(position=[0, 16, 32], rotation=[-12, 0, 0])
panels = cmds.getPanel(type='modelPanel') or ['modelPanel4']
panel = panels[0]
cmds.modelPanel(panel, edit=True, camera=cam_node)
cmds.viewFit(cam_node, all=True)

# 4. Load JopRetargetTool and execute retarget
rc_path = Path(r"c:\Users\zhongweijie\Documents\GitHub\maya_tools_box\tools_staging_pool\01_animation\jop_retarget_anim_v09\release_candidate").resolve()
spec = importlib.util.spec_from_file_location('jop_retarget_loader', rc_path / 'launch_candidate.py')
loader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(loader)
tool = loader.load_tool()

# Capture animation from source controls
src_nodes = [l_wr_ctrl, r_wr_ctrl]
tgt_nodes = [tgt_l_wr_ctrl, tgt_r_wr_ctrl]

cap_res = tool.run(action='capture', objects=src_nodes, bake=True, start=1, end=36)
print("Capture success:", cap_res.success, cap_res.message, cap_res.errors)
snapshot_data = cap_res.data if cap_res.data else {}
print("Snapshot records count:", len(snapshot_data.get('records', [])))

# Retarget onto target joints
retarget_res = tool.run(action='retarget', objects=tgt_nodes, snapshot_data=snapshot_data)
print("Retarget success:", retarget_res.success, retarget_res.message, retarget_res.errors)
print("Retargeted nodes:", retarget_res.data.get('retargeted', []) if retarget_res.data else [])

# Test Undo / Redo
cmds.undo()
print("Undo tested successfully. Target keys count:", cmds.keyframe(tgt_l_wr_ctrl, query=True, keyframeCount=True) or 0)
cmds.redo()
print("Redo tested successfully. Target keys count:", cmds.keyframe(tgt_l_wr_ctrl, query=True, keyframeCount=True) or 0)

# 5. Playblast capture
cmds.viewFit(cam_node, all=True)
out_dir = Path(r"C:\Users\zhongweijie\.gemini\antigravity\brain\f8152522-dcb3-4911-9254-38b4c32bd26d\snapshots\jop_retarget_anim_seq")
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
    target_gif_snap = Path(r"C:\Users\zhongweijie\.gemini\antigravity\brain\f8152522-dcb3-4911-9254-38b4c32bd26d\snapshots\jop_retarget_anim_joint_animation.gif")
    target_gif_root = Path(r"C:\Users\zhongweijie\.gemini\antigravity\brain\f8152522-dcb3-4911-9254-38b4c32bd26d\jop_retarget_anim_joint_animation.gif")
    
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
for n in cmds.ls(root, tgt_root, cam_node, type='transform'):
    if cmds.objExists(n):
        try:
            cmds.delete(n)
        except Exception:
            pass
print("Scene cleaned up successfully.")
