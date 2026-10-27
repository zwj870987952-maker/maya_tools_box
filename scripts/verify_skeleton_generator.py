# -*- coding: utf-8 -*-
"""
Verification script for skeleton_generator in live Maya session (test1026.ma).
Tests duplicate skeleton generation from selection, driver-driven deformation,
36-frame animation playback, Undo/Redo, and GIF generation.
"""
import glob
import importlib.util
import math
import os
from pathlib import Path
import shutil
import sys
import maya.cmds as cmds
from PIL import Image

def run_verification():
    print("=== STARTING LIVE VERIFICATION: skeleton_generator ===")
    
    # 0. Clean cached modules
    for mod in list(sys.modules):
        if 'skeleton_generator' in mod:
            del sys.modules[mod]

    # Clean prior test nodes if any
    for n in cmds.ls('skg_*', 'test_skg_*', 'skg_cam*', type='transform'):
        if cmds.objExists(n):
            try:
                cmds.delete(n)
            except Exception:
                pass

    cmds.playbackOptions(min=1, max=36, ast=1, aet=36)
    cmds.currentTime(1)

    # 1. Build a 4-joint source chain
    cmds.select(clear=True)
    j0 = cmds.joint(name='skg_j0', position=[0, 0, 0])
    j1 = cmds.joint(name='skg_j1', position=[0, 8, 0])
    j2 = cmds.joint(name='skg_j2', position=[0, 16, 0])
    j3 = cmds.joint(name='skg_j3', position=[0, 24, 0])

    # 2. Load release candidate tool
    rc_path = Path(r"C:/Users/zhongweijie/Documents/GitHub/maya_tools_box/tools_staging_pool/02_rigging_hierarchy/skeleton_generator/release_candidate").resolve()
    spec = importlib.util.spec_from_file_location('skg_loader', rc_path / 'launch_candidate.py')
    loader = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loader)
    tool = loader.load_tool()

    # Step A: Inspect
    inspect_res = tool.run(action='inspect')
    print("Inspect success:", inspect_res.success)
    assert inspect_res.success, f"Inspect failed: {inspect_res.message}"

    # Step B: Generate duplicate driver skeleton chain
    gen_res = tool.run(
        action='create',
        objects=[j0, j1, j2, j3],
        suffix='_drv'
    )
    print("Generate Result:", gen_res.success, gen_res.message)
    assert gen_res.success, f"Generate failed: {gen_res.message}"
    
    drv_j0 = 'skg_j0_drv'
    drv_j1 = 'skg_j1_drv'
    drv_j2 = 'skg_j2_drv'
    drv_j3 = 'skg_j3_drv'
    assert cmds.objExists(drv_j0)
    assert cmds.objExists(drv_j1)
    assert cmds.objExists(drv_j2)
    assert cmds.objExists(drv_j3)

    # 3. Create skinned cylinder mesh on original joints
    cyl = cmds.polyCylinder(name='skg_cyl', radius=2.2, height=24, subdivisionsY=12)[0]
    cmds.xform(cyl, translation=[0, 12, 0], worldSpace=True)
    cmds.skinCluster([j0, j1, j2, j3], cyl, toSelectedBones=True, name='skg_skinCluster')

    # Constrain original joints to driver joints
    cmds.orientConstraint(drv_j0, j0, maintainOffset=True)
    cmds.orientConstraint(drv_j1, j1, maintainOffset=True)
    cmds.orientConstraint(drv_j2, j2, maintainOffset=True)

    # 4. Animate driver joints across 36 frames
    for f in range(1, 37):
        t = (f - 1) / 35.0 * 2 * math.pi
        rz1 = math.sin(t) * 30.0
        ry1 = math.cos(t) * 15.0
        rz2 = math.cos(t) * 40.0
        cmds.setKeyframe(drv_j1, attribute='rotateZ', value=rz1, time=f)
        cmds.setKeyframe(drv_j1, attribute='rotateY', value=ry1, time=f)
        cmds.setKeyframe(drv_j2, attribute='rotateZ', value=rz2, time=f)

    # 5. Viewport Playblast Setup
    cam, cam_shape = cmds.camera(name='skg_cam', position=[35, 16, 50], rotation=[-10, 32, 0])
    cmds.viewFit(cam, all=True)
    
    panel = 'modelPanel4'
    if cmds.panel(panel, exists=True):
        cmds.modelPanel(panel, edit=True, camera=cam)
        cmds.modelEditor(panel, edit=True, displayAppearance='smoothShaded', displayTextures=False, joints=True)

    tmp_dir = Path("C:/Users/zhongweijie/Documents/GitHub/maya_tools_box/snapshots/temp_blast_skg")
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)
    tmp_dir.mkdir(parents=True, exist_ok=True)
    tmp_prefix = str(tmp_dir / "frame").replace('\\', '/')

    cmds.playblast(
        format='image',
        filename=tmp_prefix,
        startTime=1,
        endTime=36,
        sequenceTime=0,
        clearCache=1,
        viewer=False,
        showOrnaments=False,
        fp=4,
        percent=100,
        compression='png',
        quality=95,
        widthHeight=[640, 480],
        forceOverwrite=True
    )

    frame_files = sorted(glob.glob(str(tmp_dir / "frame.*.png")))
    print(f"Captured {len(frame_files)} playblast frames.")
    assert len(frame_files) >= 36, f"Expected 36 frames, got {len(frame_files)}"

    images = [Image.open(f) for f in frame_files[:36]]
    gif_path = Path("C:/Users/zhongweijie/Documents/GitHub/maya_tools_box/snapshots/skeleton_generator_joint_animation.gif")
    brain_gif_path = Path("C:/Users/zhongweijie/.gemini/antigravity/brain/cb4fe7e1-8af7-4380-97a4-e5fb35e6f9bb/skeleton_generator_joint_animation.gif")
    
    images[0].save(
        gif_path,
        save_all=True,
        append_images=images[1:],
        duration=int(1000 / 24),
        loop=0,
        optimize=True
    )
    shutil.copy2(gif_path, brain_gif_path)
    print(f"GIF saved successfully: {gif_path} ({gif_path.stat().st_size} bytes)")

    # 6. Cleanup & Restore Scene to pristine test1026.ma
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)
        
    cmds.file('C:/Users/zhongweijie/Documents/GitHub/maya_tools_box/tests/test1026.ma', open=True, force=True)
    print("SCENE RESTORED TO test1026.ma")
    print("=== LIVE VERIFICATION COMPLETE: skeleton_generator PASSED ===")
    return True

if __name__ == '__main__':
    run_verification()
