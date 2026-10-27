import os
import glob
import sys
from pathlib import Path
import maya.cmds as cmds
import importlib.util
from PIL import Image

# 0. Clean previous scene nodes
for n in cmds.ls('src_*', 'tgt_*', 'retarget_test_cam*', 'camera*', type='transform'):
    if cmds.objExists(n):
        try:
            cmds.delete(n)
        except Exception:
            pass

# 1. Build Source Skeletal Chain (Driver)
cmds.select(clear=True)
src_root = cmds.joint(name='src_root', position=[0, 10, 0])

src_l_sh = cmds.joint(name='src_L_shoulder', position=[2, 10, 0])
src_l_el = cmds.joint(name='src_L_elbow', position=[5, 10, -0.5])
src_l_wr = cmds.joint(name='src_L_wrist', position=[8, 10, 0])

cmds.select(src_root)
src_r_sh = cmds.joint(name='src_R_shoulder', position=[-2, 10, 0])
src_r_el = cmds.joint(name='src_R_elbow', position=[-5, 10, -0.5])
src_r_wr = cmds.joint(name='src_R_wrist', position=[-8, 10, 0])

# Add keyframe animation on Source
cmds.playbackOptions(minTime=1, maxTime=36, animationStartTime=1, animationEndTime=36)
cmds.currentTime(1)
cmds.setKeyframe(src_l_sh, attribute='rotateZ', value=0, time=1)
cmds.setKeyframe(src_l_el, attribute='rotateZ', value=0, time=1)
cmds.setKeyframe(src_r_sh, attribute='rotateZ', value=0, time=1)
cmds.setKeyframe(src_r_el, attribute='rotateZ', value=0, time=1)

cmds.setKeyframe(src_l_sh, attribute='rotateZ', value=55, time=18)
cmds.setKeyframe(src_l_el, attribute='rotateZ', value=-70, time=18)
cmds.setKeyframe(src_r_sh, attribute='rotateZ', value=-55, time=18)
cmds.setKeyframe(src_r_el, attribute='rotateZ', value=70, time=18)

cmds.setKeyframe(src_l_sh, attribute='rotateZ', value=0, time=36)
cmds.setKeyframe(src_l_el, attribute='rotateZ', value=0, time=36)
cmds.setKeyframe(src_r_sh, attribute='rotateZ', value=0, time=36)
cmds.setKeyframe(src_r_el, attribute='rotateZ', value=0, time=36)

# 2. Build Target Skeletal Chain (Receiver) with Spatial Offset
cmds.select(clear=True)
tgt_root = cmds.joint(name='tgt_root', position=[0, 7, -6])

tgt_l_sh = cmds.joint(name='tgt_L_shoulder', position=[2.5, 7, -6])
tgt_l_el = cmds.joint(name='tgt_L_elbow', position=[6, 7, -6.5])
tgt_l_wr = cmds.joint(name='tgt_L_wrist', position=[9.5, 7, -6])

cmds.select(tgt_root)
tgt_r_sh = cmds.joint(name='tgt_R_shoulder', position=[-2.5, 7, -6])
tgt_r_el = cmds.joint(name='tgt_R_elbow', position=[-6, 7, -6.5])
tgt_r_wr = cmds.joint(name='tgt_R_wrist', position=[-9.5, 7, -6])

# 3. Load AnimationRetargetTool and test align + bake
rc_path = Path(r"c:\Users\zhongweijie\Documents\GitHub\maya_tools_box\tools_staging_pool\01_animation\animation_retarget\release_candidate").resolve()
spec = importlib.util.spec_from_file_location('retarget_loader', rc_path / 'launch_candidate.py')
loader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(loader)
tool = loader.load_tool()

pairs = [
    {'source': src_l_sh, 'target': tgt_l_sh, 'modes': {'translate': 'constraint', 'rotate': 'constraint'}},
    {'source': src_l_el, 'target': tgt_l_el, 'modes': {'rotate': 'constraint'}},
    {'source': src_l_wr, 'target': tgt_l_wr, 'modes': {'rotate': 'constraint'}},
    {'source': src_r_sh, 'target': tgt_r_sh, 'modes': {'translate': 'constraint', 'rotate': 'constraint'}},
    {'source': src_r_el, 'target': tgt_r_el, 'modes': {'rotate': 'constraint'}},
    {'source': src_r_wr, 'target': tgt_r_wr, 'modes': {'rotate': 'constraint'}},
]

align_res = tool.run(action='align', pairs=pairs)
print("Align success:", align_res.success, "data:", align_res.data)

# Test Undo / Redo on align
cmds.undo()
print("Undo tested, constraints removed:", not any(cmds.ls('*Constraint*', type='constraint')))
cmds.redo()
print("Redo tested, constraints restored:", any(cmds.ls('*Constraint*', type='constraint')))

# Bake retargeted animation onto target joints
bake_res = tool.run(action='bake', pairs=pairs, start=1, end=36, smart=False)
print("Bake success:", bake_res.success)

# 4. Camera framing and playblast
cam_node, cam_shape = cmds.camera(position=[0, 8, 30], rotation=[-5, 0, 0])
panels = cmds.getPanel(type='modelPanel') or ['modelPanel4']
panel = panels[0]
cmds.modelPanel(panel, edit=True, camera=cam_node)
cmds.viewFit(cam_node, all=True)

out_dir = Path(r"C:\Users\zhongweijie\.gemini\antigravity\brain\f8152522-dcb3-4911-9254-38b4c32bd26d\snapshots\retarget_anim_seq")
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

# 5. Assemble looping GIF
png_files = sorted(glob.glob(str(out_dir / "frame.*.png")))
print(f"Captured {len(png_files)} frames.")
if png_files:
    frames = [Image.open(f) for f in png_files]
    target_gif_snap = Path(r"C:\Users\zhongweijie\.gemini\antigravity\brain\f8152522-dcb3-4911-9254-38b4c32bd26d\snapshots\animation_retarget_joint_animation.gif")
    target_gif_root = Path(r"C:\Users\zhongweijie\.gemini\antigravity\brain\f8152522-dcb3-4911-9254-38b4c32bd26d\animation_retarget_joint_animation.gif")
    
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

# 6. Clean up scene
for n in cmds.ls(src_root, tgt_root, cam_node, '*retarget*', type='transform'):
    if cmds.objExists(n):
        try:
            cmds.delete(n)
        except Exception:
            pass
print("Scene cleaned up successfully.")
