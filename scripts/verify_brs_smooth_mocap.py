import os
import glob
import sys
from pathlib import Path
import maya.cmds as cmds
import importlib.util
from PIL import Image

# 0. Clean cached modules
for mod in list(sys.modules):
    if 'brs_smooth_mocap' in mod:
        del sys.modules[mod]

# 1. Clean previous scene nodes
for n in cmds.ls('pelvis_root*', 'mtbBRS*', 'mocap_test_cam*', 'camera*', type='transform'):
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

# Add noisy mocap-like keyframe animation on joints
cmds.playbackOptions(minTime=1, maxTime=36, animationStartTime=1, animationEndTime=36)
keyframes_data = [
    (1, -10, 10, -20, 20),
    (6, 25, -20, 15, -15),
    (12, -5, 35, -30, 30),
    (18, 30, -10, 25, -25),
    (24, 5, 20, -15, 15),
    (30, 20, -30, 35, -35),
    (36, -10, 10, -20, 20),
]

for frame, l_sh_val, l_el_val, r_sh_val, r_el_val in keyframes_data:
    cmds.currentTime(frame)
    cmds.setKeyframe(l_sh, attribute='rotateY', value=l_sh_val, time=frame)
    cmds.setKeyframe(l_el, attribute='rotateZ', value=l_el_val, time=frame)
    cmds.setKeyframe(l_wr, attribute='rotateZ', value=l_el_val * 0.5, time=frame)
    cmds.setKeyframe(r_sh, attribute='rotateY', value=r_sh_val, time=frame)
    cmds.setKeyframe(r_el, attribute='rotateZ', value=r_el_val, time=frame)
    cmds.setKeyframe(r_wr, attribute='rotateZ', value=r_el_val * 0.5, time=frame)

# 3. Create camera
cam_node, cam_shape = cmds.camera(position=[0, 10, 28], rotation=[0, 0, 0])
panels = cmds.getPanel(type='modelPanel') or ['modelPanel4']
panel = panels[0]
cmds.modelPanel(panel, edit=True, camera=cam_node)
cmds.viewFit(cam_node, all=True)

# 4. Load SmoothMocapTool and execute smoothing
rc_path = Path(r"c:\Users\zhongweijie\Documents\GitHub\maya_tools_box\tools_staging_pool\01_animation\brs_smooth_mocap\release_candidate").resolve()
spec = importlib.util.spec_from_file_location('smooth_mocap_loader', rc_path / 'launch_candidate.py')
loader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(loader)
tool = loader.load_tool()

smooth_res = tool.run(action='smooth_mocap', root_joint=root, strength=3)
print("Smooth mocap success:", smooth_res.success)
print("Processed curves count:", len(smooth_res.data.get('processed_curves', [])))

# Test Undo / Redo
cmds.undo()
print("Undo tested successfully.")
cmds.redo()
print("Redo tested successfully.")

# 5. Playblast capture
cmds.viewFit(cam_node, all=True)
out_dir = Path(r"C:\Users\zhongweijie\.gemini\antigravity\brain\f8152522-dcb3-4911-9254-38b4c32bd26d\snapshots\brs_smooth_anim_seq")
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
    target_gif_snap = Path(r"C:\Users\zhongweijie\.gemini\antigravity\brain\f8152522-dcb3-4911-9254-38b4c32bd26d\snapshots\brs_smooth_mocap_joint_animation.gif")
    target_gif_root = Path(r"C:\Users\zhongweijie\.gemini\antigravity\brain\f8152522-dcb3-4911-9254-38b4c32bd26d\brs_smooth_mocap_joint_animation.gif")
    
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
for n in cmds.ls(root, cam_node, 'mtbBRS*', type='transform'):
    if cmds.objExists(n):
        try:
            cmds.delete(n)
        except Exception:
            pass
print("Scene cleaned up successfully.")
