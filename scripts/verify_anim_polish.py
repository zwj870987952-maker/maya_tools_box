import os
import glob
import sys
from pathlib import Path
import maya.cmds as cmds
import importlib.util
from PIL import Image

# 0. Clean any cached modules
for mod in list(sys.modules):
    if 'anim_polish' in mod or 'animPolish' in mod:
        del sys.modules[mod]

# 1. Clean previous scene nodes
for n in cmds.ls('pelvis_root*', 'arm_mesh*', 'polish_test_cam*', 'camera*', type='transform'):
    if cmds.objExists(n):
        try:
            cmds.delete(n)
        except Exception:
            pass

# 2. Build symmetrical joint chains
cmds.select(clear=True)
root = cmds.joint(name='pelvis_root', position=[0, 10, 0])

l_sh = cmds.joint(name='L_shoulder', position=[2, 10, 0])
l_el = cmds.joint(name='L_elbow', position=[5, 10, -0.5])
l_wr = cmds.joint(name='L_wrist', position=[8, 10, 0])

cmds.select(root)
r_sh = cmds.joint(name='R_shoulder', position=[-2, 10, 0])
r_el = cmds.joint(name='R_elbow', position=[-5, 10, -0.5])
r_wr = cmds.joint(name='R_wrist', position=[-8, 10, 0])

# 3. Add keyframe animation on arm joints
cmds.playbackOptions(minTime=1, maxTime=36, animationStartTime=1, animationEndTime=36)
cmds.currentTime(1)
cmds.setKeyframe(l_sh, attribute='rotateZ', value=0, time=1)
cmds.setKeyframe(l_el, attribute='rotateZ', value=0, time=1)
cmds.setKeyframe(r_sh, attribute='rotateZ', value=0, time=1)
cmds.setKeyframe(r_el, attribute='rotateZ', value=0, time=1)

cmds.setKeyframe(l_sh, attribute='rotateZ', value=50, time=18)
cmds.setKeyframe(l_el, attribute='rotateZ', value=-65, time=18)
cmds.setKeyframe(r_sh, attribute='rotateZ', value=-50, time=18)
cmds.setKeyframe(r_el, attribute='rotateZ', value=65, time=18)

cmds.setKeyframe(l_sh, attribute='rotateZ', value=0, time=36)
cmds.setKeyframe(l_el, attribute='rotateZ', value=0, time=36)
cmds.setKeyframe(r_sh, attribute='rotateZ', value=0, time=36)
cmds.setKeyframe(r_el, attribute='rotateZ', value=0, time=36)

# 4. Create cylinder meshes for the arms and skin them to the joints
cyl_l = cmds.polyCylinder(name='arm_mesh_L', radius=0.8, height=6, subdivisionsY=10, axis=[1, 0, 0])[0]
cmds.move(5, 10, 0, cyl_l)
cmds.skinCluster([l_sh, l_el, l_wr], cyl_l, toSelectedBones=True)

cyl_r = cmds.polyCylinder(name='arm_mesh_R', radius=0.8, height=6, subdivisionsY=10, axis=[1, 0, 0])[0]
cmds.move(-5, 10, 0, cyl_r)
cmds.skinCluster([r_sh, r_el, r_wr], cyl_r, toSelectedBones=True)

# 5. Load AnimPolishTool and run growShrink / iron on the meshes
rc_path = Path(r"c:\Users\zhongweijie\Documents\GitHub\maya_tools_box\tools_staging_pool\01_animation\anim_polish_premium_v1_23\release_candidate").resolve()
spec = importlib.util.spec_from_file_location('polish_loader', rc_path / 'launch_candidate.py')
loader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(loader)
tool = loader.load_tool()

# Test growShrink on left arm mesh
gs_res = tool.run(action='invoke', function='growShrink.run', arguments={'geo': cyl_l})
print("GrowShrink result success:", gs_res.success)
if cmds.objExists(cyl_l + '.growShrink_1'):
    cmds.setKeyframe(cyl_l, attribute='growShrink_1', value=0.0, time=1)
    cmds.setKeyframe(cyl_l, attribute='growShrink_1', value=1.5, time=18)
    cmds.setKeyframe(cyl_l, attribute='growShrink_1', value=0.0, time=36)

# Test iron on right arm mesh
iron_res = tool.run(action='invoke', function='iron.run', arguments={'geo': cyl_r, 'its': 2})
print("Iron result success:", iron_res.success)

# Test Undo/Redo on iron
cmds.undo()
print("Undo tested, iron_1 exists:", cmds.objExists(cyl_r + '.iron_1'))
cmds.redo()
print("Redo tested, iron_1 exists:", cmds.objExists(cyl_r + '.iron_1'))
if cmds.objExists(cyl_r + '.iron_1'):
    cmds.setKeyframe(cyl_r, attribute='iron_1', value=0.0, time=1)
    cmds.setKeyframe(cyl_r, attribute='iron_1', value=1.0, time=18)
    cmds.setKeyframe(cyl_r, attribute='iron_1', value=0.0, time=36)

# 6. Camera framing and playblast
cam_node, cam_shape = cmds.camera(position=[0, 10, 24], rotation=[-5, 0, 0])
panels = cmds.getPanel(type='modelPanel') or ['modelPanel4']
panel = panels[0]
cmds.modelPanel(panel, edit=True, camera=cam_node)
cmds.viewFit(cam_node, all=True)

out_dir = Path(r"C:\Users\zhongweijie\.gemini\antigravity\brain\f8152522-dcb3-4911-9254-38b4c32bd26d\snapshots\polish_anim_seq")
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

# 7. Assemble looping GIF
png_files = sorted(glob.glob(str(out_dir / "frame.*.png")))
print(f"Captured {len(png_files)} frames.")
if png_files:
    frames = [Image.open(f) for f in png_files]
    target_gif_snap = Path(r"C:\Users\zhongweijie\.gemini\antigravity\brain\f8152522-dcb3-4911-9254-38b4c32bd26d\snapshots\anim_polish_premium_joint_animation.gif")
    target_gif_root = Path(r"C:\Users\zhongweijie\.gemini\antigravity\brain\f8152522-dcb3-4911-9254-38b4c32bd26d\anim_polish_premium_joint_animation.gif")
    
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

# 8. Clean up scene
for n in cmds.ls(root, cyl_l, cyl_r, cam_node, type='transform'):
    if cmds.objExists(n):
        try:
            cmds.delete(n)
        except Exception:
            pass
print("Scene cleaned up successfully.")
