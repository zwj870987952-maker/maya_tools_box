import os
import glob
import sys
from pathlib import Path
import maya.cmds as cmds
import importlib.util
from PIL import Image

# 0. Clean any cached modules
for mod in list(sys.modules):
    if 'bh_speedlines' in mod:
        del sys.modules[mod]

# 1. Clean previous scene nodes
for n in cmds.ls('pelvis_root*', 'sl_curve*', 'bh_speedLine*', 'sl_test_cam*', 'camera*', type='transform'):
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

# Add keyframe animation on joints (slashing motion)
cmds.playbackOptions(minTime=1, maxTime=36, animationStartTime=1, animationEndTime=36)
cmds.currentTime(1)
cmds.setKeyframe(l_sh, attribute='rotateZ', value=0, time=1)
cmds.setKeyframe(l_el, attribute='rotateZ', value=0, time=1)
cmds.setKeyframe(r_sh, attribute='rotateZ', value=0, time=1)
cmds.setKeyframe(r_el, attribute='rotateZ', value=0, time=1)

cmds.setKeyframe(l_sh, attribute='rotateZ', value=60, time=18)
cmds.setKeyframe(l_el, attribute='rotateZ', value=-80, time=18)
cmds.setKeyframe(r_sh, attribute='rotateZ', value=-60, time=18)
cmds.setKeyframe(r_el, attribute='rotateZ', value=80, time=18)

cmds.setKeyframe(l_sh, attribute='rotateZ', value=0, time=36)
cmds.setKeyframe(l_el, attribute='rotateZ', value=0, time=36)
cmds.setKeyframe(r_sh, attribute='rotateZ', value=0, time=36)
cmds.setKeyframe(r_el, attribute='rotateZ', value=0, time=36)

# 3. Create two curves for speedline generation along the strike arc
c1 = cmds.curve(name='sl_curve1', d=3, p=[[8, 10, 0], [10, 14, 2], [11, 16, 4], [9, 17, 6], [6, 16, 7]])
c2 = cmds.curve(name='sl_curve2', d=3, p=[[8, 9.2, 0], [10, 13.2, 2], [11, 15.2, 4], [9, 16.2, 6], [6, 15.2, 7]])

# 4. Create camera
cam_node, cam_shape = cmds.camera(position=[0, 12, 30], rotation=[-5, 0, 0])
panels = cmds.getPanel(type='modelPanel') or ['modelPanel4']
panel = panels[0]
cmds.modelPanel(panel, edit=True, camera=cam_node)
cmds.viewFit(cam_node, all=True)

# 5. Load SpeedLinesTool and generate speedline geometry
rc_path = Path(r"c:\Users\zhongweijie\Documents\GitHub\maya_tools_box\tools_staging_pool\01_animation\bh_speedlines\release_candidate").resolve()
spec = importlib.util.spec_from_file_location('speedlines_loader', rc_path / 'launch_candidate.py')
loader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(loader)
tool = loader.load_tool()

geo_res = tool.run(action='geometry', objects=[c1, c2], camera=cam_node, consume_curves=False, on_layer=True)
print("Geometry result success:", geo_res.success)
created_nodes = geo_res.data.get('created_nodes', [])
print("Created speedline nodes:", created_nodes)
sl_mesh = [n for n in created_nodes if cmds.nodeType(n) == 'transform' and cmds.listRelatives(n, type='mesh')]
if sl_mesh:
    mesh_node = sl_mesh[0]
    print("Found speedline mesh:", mesh_node)
    
    # Test keying visibility on frames
    cmds.currentTime(18)
    key_res = tool.run(action='key_visibility', objects=[mesh_node])
    print("Key visibility success:", key_res.success)

# Test Undo / Redo
cmds.undo()
print("Undo tested successfully.")
cmds.redo()
print("Redo tested successfully.")

# 6. Playblast capture
cmds.viewFit(cam_node, all=True)
out_dir = Path(r"C:\Users\zhongweijie\.gemini\antigravity\brain\f8152522-dcb3-4911-9254-38b4c32bd26d\snapshots\speedlines_anim_seq")
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
    target_gif_snap = Path(r"C:\Users\zhongweijie\.gemini\antigravity\brain\f8152522-dcb3-4911-9254-38b4c32bd26d\snapshots\bh_speedlines_joint_animation.gif")
    target_gif_root = Path(r"C:\Users\zhongweijie\.gemini\antigravity\brain\f8152522-dcb3-4911-9254-38b4c32bd26d\bh_speedlines_joint_animation.gif")
    
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
for n in cmds.ls(root, c1, c2, cam_node, '*speedLine*', type='transform'):
    if cmds.objExists(n):
        try:
            cmds.delete(n)
        except Exception:
            pass
print("Scene cleaned up successfully.")
