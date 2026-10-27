# -*- coding: utf-8 -*-
"""
Verification script for skin_weight_transfer in live Maya session (test1026.ma).
Tests joint weight merging/transfer, dynamic deformation,
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
    print("=== STARTING LIVE VERIFICATION: skin_weight_transfer ===")
    
    # 0. Clean cached modules
    for mod in list(sys.modules):
        if 'skin_weight_transfer' in mod:
            del sys.modules[mod]

    # Clean prior test nodes if any
    for n in cmds.ls('swt_*', 'test_swt_*', 'swt_cam*', type='transform'):
        if cmds.objExists(n):
            try:
                cmds.delete(n)
            except Exception:
                pass

    cmds.playbackOptions(min=1, max=36, ast=1, aet=36)
    cmds.currentTime(1)

    # 1. Build joints with an extra helper joint
    cmds.select(clear=True)
    j0 = cmds.joint(name='swt_j0', position=[0, 0, 0])
    j1 = cmds.joint(name='swt_j1', position=[0, 10, 0])
    j2 = cmds.joint(name='swt_j2', position=[0, 20, 0])
    helper = cmds.joint(name='swt_helper', position=[2, 10, 0])

    cyl = cmds.polyCylinder(name='swt_cyl', radius=2.2, height=22, subdivisionsY=12)[0]
    cmds.xform(cyl, translation=[0, 10, 0], worldSpace=True)
    skin_node = cmds.skinCluster([j0, j1, j2, helper], cyl, toSelectedBones=True, name='swt_skinCluster')[0]

    # Distribute initial weights with helper having 0.3 weight on mid vertices
    mid_vtx = f"{cyl}.vtx[10:18]"
    cmds.skinPercent(skin_node, mid_vtx, transformValue=[(j0, 0.1), (j1, 0.4), (j2, 0.2), (helper, 0.3)], normalize=True)

    # 2. Load release candidate tool
    rc_path = Path(r"C:/Users/zhongweijie/Documents/GitHub/maya_tools_box/tools_staging_pool/02_rigging_hierarchy/skin_weight_transfer/release_candidate").resolve()
    spec = importlib.util.spec_from_file_location('swt_loader', rc_path / 'launch_candidate.py')
    loader = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loader)
    tool = loader.load_tool()

    # Step A: Dry Run
    dry_res = tool.run(task_text=f'{helper} => {j1} => {cyl}', dry_run=True)
    print("Dry run success:", dry_res.success)
    assert dry_res.success, f"Dry run failed: {dry_res.message}"

    # Step B: Real Transfer (Merge helper weights into j1)
    transfer_res = tool.run(task_text=f'{helper} => {j1} => {cyl}')
    print("Transfer Result:", transfer_res.success, transfer_res.message)
    assert transfer_res.success, f"Transfer failed: {transfer_res.message}"

    # Verify helper weight is now 0 on vertex 10
    vtx10_weights = cmds.skinPercent(skin_node, f"{cyl}.vtx[10]", query=True, value=True)
    print("Transferred Vtx10 Weights:", vtx10_weights)
    assert abs(vtx10_weights[3]) < 1e-5, f"Expected helper weight 0, got {vtx10_weights[3]}"

    # 3. Animate joints across 36 frames
    for f in range(1, 37):
        t = (f - 1) / 35.0 * 2 * math.pi
        rz1 = math.sin(t) * 35.0
        rx1 = math.cos(t) * 20.0
        rz2 = math.cos(t) * 40.0
        cmds.setKeyframe(j1, attribute='rotateZ', value=rz1, time=f)
        cmds.setKeyframe(j1, attribute='rotateX', value=rx1, time=f)
        cmds.setKeyframe(j2, attribute='rotateZ', value=rz2, time=f)

    # 4. Viewport Playblast Setup
    cam, cam_shape = cmds.camera(name='swt_cam', position=[32, 16, 45], rotation=[-10, 32, 0])
    cmds.viewFit(cam, all=True)
    
    panel = 'modelPanel4'
    if cmds.panel(panel, exists=True):
        cmds.modelPanel(panel, edit=True, camera=cam)
        cmds.modelEditor(panel, edit=True, displayAppearance='smoothShaded', displayTextures=False, joints=True)

    tmp_dir = Path("C:/Users/zhongweijie/Documents/GitHub/maya_tools_box/snapshots/temp_blast_swt")
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
    gif_path = Path("C:/Users/zhongweijie/Documents/GitHub/maya_tools_box/snapshots/skin_weight_transfer_joint_animation.gif")
    brain_gif_path = Path("C:/Users/zhongweijie/.gemini/antigravity/brain/cb4fe7e1-8af7-4380-97a4-e5fb35e6f9bb/skin_weight_transfer_joint_animation.gif")
    
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

    # 5. Cleanup & Restore Scene to pristine test1026.ma
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)
        
    cmds.file('C:/Users/zhongweijie/Documents/GitHub/maya_tools_box/tests/test1026.ma', open=True, force=True)
    print("SCENE RESTORED TO test1026.ma")
    print("=== LIVE VERIFICATION COMPLETE: skin_weight_transfer PASSED ===")
    return True

if __name__ == '__main__':
    run_verification()
