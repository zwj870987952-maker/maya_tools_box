import os
import glob
import sys
import tempfile
from pathlib import Path
import maya.cmds as cmds
import importlib.util
from PIL import Image

# 0. Clean cached modules
for mod in list(sys.modules):
    if 'kf_animrig_ikfk' in mod:
        del sys.modules[mod]

# 1. Clean previous scene nodes
for ref in cmds.file(query=True, reference=True) or []:
    try:
        cmds.file(ref, removeReference=True)
    except Exception:
        pass

for n in cmds.ls('pelvis_root*', 'kfrig:*', 'kf_test_cam*', 'camera*', type='transform'):
    if cmds.objExists(n):
        try:
            cmds.delete(n)
        except Exception:
            pass

# 2. Build Symmetrical Skeletal Chains & KF Rig Controls in a temp file to reference
tmp_dir = tempfile.gettempdir()
rig_file = (Path(tmp_dir) / 'kf_rig_arm.ma').as_posix()

# Setup rig elements in fresh temporary context
cmds.file(new=True, force=True)
cmds.currentUnit(angle='deg', linear='cm')

# Symmetrical skeletal chains
root = cmds.joint(name='pelvis_root', position=[0, 10, 0])
l_sh = cmds.joint(name='L_shoulder', position=[2, 10, 0])
l_el = cmds.joint(name='L_elbow', position=[5, 10, -0.5])
l_wr = cmds.joint(name='L_wrist', position=[8, 10, 0])

cmds.select(root)
r_sh = cmds.joint(name='R_shoulder', position=[-2, 10, 0])
r_el = cmds.joint(name='R_elbow', position=[-5, 10, -0.5])
r_wr = cmds.joint(name='R_wrist', position=[-8, 10, 0])

# KF standard naming controls for Left Arm
ctrl_hand = cmds.createNode('transform', name='CTRL_L_Hand')
cmds.setAttr(ctrl_hand + '.translate', 8, 10, 0)

ctrl_pole = cmds.createNode('transform', name='CTRL_L_ElbowPole')
cmds.setAttr(ctrl_pole + '.translate', 5, 10, -4)

ctrl_fk_sh = cmds.createNode('transform', name='CTRL_FK_L_Shoulder')
cmds.setAttr(ctrl_fk_sh + '.translate', 2, 10, 0)

ctrl_fk_el = cmds.createNode('transform', name='CTRL_FK_L_Elbow')
cmds.setAttr(ctrl_fk_el + '.translate', 5, 10, -0.5)

ctrl_fk_wr = cmds.createNode('transform', name='CTRL_FK_L_Wrist')
cmds.setAttr(ctrl_fk_wr + '.translate', 8, 10, 0)

# Save to rig file
cmds.file(rename=rig_file)
cmds.file(save=True, type='mayaAscii', force=True)

# Now in fresh scene, reference the rig file
cmds.file(new=True, force=True)
cmds.file(rig_file, reference=True, namespace='kfrig')

ref_hand = 'kfrig:CTRL_L_Hand'
ref_pole = 'kfrig:CTRL_L_ElbowPole'
ref_fk_sh = 'kfrig:CTRL_FK_L_Shoulder'
ref_fk_el = 'kfrig:CTRL_FK_L_Elbow'
ref_fk_wr = 'kfrig:CTRL_FK_L_Wrist'

# Add keyframe dynamic animation on FK controls across 1-36 frames
cmds.playbackOptions(minTime=1, maxTime=36, animationStartTime=1, animationEndTime=36)
cmds.currentTime(1)
cmds.setKeyframe(ref_fk_sh, attribute='rotateZ', value=-15, time=1)
cmds.setKeyframe(ref_fk_el, attribute='rotateY', value=20, time=1)
cmds.setKeyframe(ref_fk_wr, attribute='rotateZ', value=-10, time=1)

cmds.setKeyframe(ref_fk_sh, attribute='rotateZ', value=35, time=18)
cmds.setKeyframe(ref_fk_el, attribute='rotateY', value=-35, time=18)
cmds.setKeyframe(ref_fk_wr, attribute='rotateZ', value=20, time=18)

cmds.setKeyframe(ref_fk_sh, attribute='rotateZ', value=-15, time=36)
cmds.setKeyframe(ref_fk_el, attribute='rotateY', value=20, time=36)
cmds.setKeyframe(ref_fk_wr, attribute='rotateZ', value=-10, time=36)

# 3. Create camera
cam_node, cam_shape = cmds.camera(position=[0, 10, 26], rotation=[0, 0, 0])
panels = cmds.getPanel(type='modelPanel') or ['modelPanel4']
panel = panels[0]
cmds.modelPanel(panel, edit=True, camera=cam_node)
cmds.viewFit(cam_node, all=True)

# 4. Load KFAnimRigTool and execute IK/FK matching and baking
rc_path = Path(r"c:\Users\zhongweijie\Documents\GitHub\maya_tools_box\tools_staging_pool\01_animation\kf_animrig_ikfk\release_candidate").resolve()
spec = importlib.util.spec_from_file_location('kf_loader', rc_path / 'launch_candidate.py')
loader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(loader)
tool = loader.load_tool()

# Inspect
insp_res = tool.run(action='inspect', control=ref_hand)
print("Inspect success:", insp_res.success)

# Bake IK to FK across 1-36
bake_res = tool.run(action='bake_ik_to_fk', control=ref_hand, start=1, end=36, allow_reference_edits=True)
print("Bake IK to FK success:", bake_res.success)
print("Baked keyframes count on hand:", cmds.keyframe(ref_hand, query=True, keyframeCount=True) or 0)

# Test Undo / Redo
cmds.undo()
print("Undo tested successfully. Hand keys count:", cmds.keyframe(ref_hand, query=True, keyframeCount=True) or 0)
cmds.redo()
print("Redo tested successfully. Hand keys count:", cmds.keyframe(ref_hand, query=True, keyframeCount=True) or 0)

# 5. Playblast capture
cmds.viewFit(cam_node, all=True)
out_dir = Path(r"C:\Users\zhongweijie\.gemini\antigravity\brain\f8152522-dcb3-4911-9254-38b4c32bd26d\snapshots\kf_animrig_anim_seq")
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
    target_gif_snap = Path(r"C:\Users\zhongweijie\.gemini\antigravity\brain\f8152522-dcb3-4911-9254-38b4c32bd26d\snapshots\kf_animrig_ikfk_joint_animation.gif")
    target_gif_root = Path(r"C:\Users\zhongweijie\.gemini\antigravity\brain\f8152522-dcb3-4911-9254-38b4c32bd26d\kf_animrig_ikfk_joint_animation.gif")
    
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
for ref in cmds.file(query=True, reference=True) or []:
    try:
        cmds.file(ref, removeReference=True)
    except Exception:
        pass

for n in cmds.ls(cam_node, type='transform'):
    if cmds.objExists(n):
        try:
            cmds.delete(n)
        except Exception:
            pass
try:
    if os.path.exists(rig_file):
        os.remove(rig_file)
except Exception:
    pass
print("Scene cleaned up successfully.")
