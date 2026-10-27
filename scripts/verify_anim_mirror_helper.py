import os
import glob
from pathlib import Path
import maya.cmds as cmds
import importlib.util
from PIL import Image

# 1. Clean previous scene nodes
for n in cmds.ls('pelvis_root*', '*mirror*', '*MIRR*', 'camera*', type='transform'):
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

# 3. Add keyframe animation on left arm joints
cmds.playbackOptions(minTime=1, maxTime=36, animationStartTime=1, animationEndTime=36)
cmds.currentTime(1)
cmds.setKeyframe(l_sh, attribute='rotateZ', value=0, time=1)
cmds.setKeyframe(l_el, attribute='rotateZ', value=0, time=1)

cmds.setKeyframe(l_sh, attribute='rotateZ', value=50, time=18)
cmds.setKeyframe(l_el, attribute='rotateZ', value=-65, time=18)

cmds.setKeyframe(l_sh, attribute='rotateZ', value=0, time=36)
cmds.setKeyframe(l_el, attribute='rotateZ', value=0, time=36)

# 4. Load tool and test create_system
rc_path = Path(r"c:\Users\zhongweijie\Documents\GitHub\maya_tools_box\tools_staging_pool\01_animation\anim_mirror_helper_v1_1\release_candidate").resolve()
spec = importlib.util.spec_from_file_location('mirror_loader', rc_path / 'launch_candidate.py')
loader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(loader)
tool = loader.load_tool()

load_res = tool.run(action='load')
print("Load success:", load_res.success)

cmds.select([l_sh, l_el, l_wr])
create_res = tool.run(action='create_system', arguments={'mirror_axis': 'x', 'offset': 0.0, 'cycled': 0})
print("Create system success:", create_res.success)

# Attach pairs to right arm
cmds.select([l_sh, r_sh, l_el, r_el, l_wr, r_wr])
attach_res = tool.run(action='attach_pairs', arguments={'type': 'parent', 'offset': 0})
print("Attach pairs success:", attach_res.success)

# 5. Playblast capture
cam_node, cam_shape = cmds.camera(position=[0, 10, 24], rotation=[-5, 0, 0])
panels = cmds.getPanel(type='modelPanel') or ['modelPanel4']
panel = panels[0]
cmds.modelPanel(panel, edit=True, camera=cam_node)
cmds.viewFit(cam_node, all=True)

out_dir = Path(r"C:\Users\zhongweijie\.gemini\antigravity\brain\f8152522-dcb3-4911-9254-38b4c32bd26d\snapshots\mirror_anim_seq")
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
    target_gif_snap = Path(r"C:\Users\zhongweijie\.gemini\antigravity\brain\f8152522-dcb3-4911-9254-38b4c32bd26d\snapshots\anim_mirror_helper_joint_animation.gif")
    target_gif_root = Path(r"C:\Users\zhongweijie\.gemini\antigravity\brain\f8152522-dcb3-4911-9254-38b4c32bd26d\anim_mirror_helper_joint_animation.gif")
    
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

# 7. Clean up scene test nodes
for n in cmds.ls(root, cam_node, '*mirror*', '*MIRR*', type='transform'):
    if cmds.objExists(n):
        try:
            cmds.delete(n)
        except Exception:
            pass
print("Scene cleaned up successfully.")
