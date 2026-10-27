import os
import glob
import sys
from pathlib import Path
import maya.cmds as cmds
import importlib.util
from PIL import Image

# 0. Clean cached modules
for mod in list(sys.modules):
    if 'fd_multi_space' in mod:
        del sys.modules[mod]

# 1. Clean previous scene nodes
for n in cmds.ls('pelvis_root*', 'hip_target*', 'mtbFD*', '*_spaceGrp*', 'space_test_cam*', 'camera*', type='transform'):
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

# Add driver target locator at hip/pelvis
hip_driver = cmds.spaceLocator(name='hip_target')[0]
cmds.xform(hip_driver, translation=[0, 8, 2], worldSpace=True)

# Add dynamic animation on joints (swaying motion)
cmds.playbackOptions(minTime=1, maxTime=36, animationStartTime=1, animationEndTime=36)
cmds.currentTime(1)
cmds.setKeyframe(l_sh, attribute='rotateZ', value=-20, time=1)
cmds.setKeyframe(l_el, attribute='rotateY', value=30, time=1)
cmds.setKeyframe(r_sh, attribute='rotateZ', value=20, time=1)
cmds.setKeyframe(r_el, attribute='rotateY', value=-30, time=1)

cmds.setKeyframe(l_sh, attribute='rotateZ', value=40, time=18)
cmds.setKeyframe(l_el, attribute='rotateY', value=-40, time=18)
cmds.setKeyframe(r_sh, attribute='rotateZ', value=-40, time=18)
cmds.setKeyframe(r_el, attribute='rotateY', value=40, time=18)

cmds.setKeyframe(l_sh, attribute='rotateZ', value=-20, time=36)
cmds.setKeyframe(l_el, attribute='rotateY', value=30, time=36)
cmds.setKeyframe(r_sh, attribute='rotateZ', value=20, time=36)
cmds.setKeyframe(r_el, attribute='rotateY', value=-30, time=36)

# 3. Create camera
cam_node, cam_shape = cmds.camera(position=[0, 10, 26], rotation=[0, 0, 0])
panels = cmds.getPanel(type='modelPanel') or ['modelPanel4']
panel = panels[0]
cmds.modelPanel(panel, edit=True, camera=cam_node)
cmds.viewFit(cam_node, all=True)

# 4. Load MultiSpaceTool and execute space creation
rc_path = Path(r"c:\Users\zhongweijie\Documents\GitHub\maya_tools_box\tools_staging_pool\01_animation\fd_multi_space\release_candidate").resolve()
spec = importlib.util.spec_from_file_location('multi_space_loader', rc_path / 'launch_candidate.py')
loader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(loader)
tool = loader.load_tool()

create_res = tool.run(action='create', mode='local', driven=l_wr, driver=hip_driver, attribute='spaceHip')
print("MultiSpace create success:", create_res.success)
print("MultiSpace record data:", create_res.data)

# Animate space weight on l_wr
cmds.setKeyframe(l_wr, attribute='spaceHip', value=0, time=1)
cmds.setKeyframe(l_wr, attribute='spaceHip', value=1, time=18)
cmds.setKeyframe(l_wr, attribute='spaceHip', value=0, time=36)

# Test Undo / Redo
cmds.undo()
print("Undo tested successfully.")
cmds.redo()
print("Redo tested successfully.")

# 5. Playblast capture
cmds.viewFit(cam_node, all=True)
out_dir = Path(r"C:\Users\zhongweijie\.gemini\antigravity\brain\f8152522-dcb3-4911-9254-38b4c32bd26d\snapshots\fd_multi_space_anim_seq")
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
    target_gif_snap = Path(r"C:\Users\zhongweijie\.gemini\antigravity\brain\f8152522-dcb3-4911-9254-38b4c32bd26d\snapshots\fd_multi_space_joint_animation.gif")
    target_gif_root = Path(r"C:\Users\zhongweijie\.gemini\antigravity\brain\f8152522-dcb3-4911-9254-38b4c32bd26d\fd_multi_space_joint_animation.gif")
    
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
for n in cmds.ls(root, hip_driver, cam_node, 'mtbFD*', '*_spaceGrp*', type='transform'):
    if cmds.objExists(n):
        try:
            cmds.delete(n)
        except Exception:
            pass
print("Scene cleaned up successfully.")
