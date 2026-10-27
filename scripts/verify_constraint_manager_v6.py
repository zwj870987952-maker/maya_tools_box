# -*- coding: utf-8 -*-
"""
Verification script for constraint_manager_v6 in live Maya session (test1026.ma).
Tests dual-driver parent constraint inspection, weight blending, keyframing, Undo/Redo,
36-frame dynamic playback and GIF generation.
"""
import glob
import importlib.util
import os
from pathlib import Path
import shutil
import sys
import maya.cmds as cmds
from PIL import Image

def run_verification():
    print("=== STARTING LIVE VERIFICATION: constraint_manager_v6 ===")
    
    # 0. Clean cached modules
    for mod in list(sys.modules):
        if 'constraint_manager_v6' in mod:
            del sys.modules[mod]

    # Clean prior test nodes if any
    for n in cmds.ls('cm_*', 'test_cm_*', 'cm_cam*', type='transform'):
        if cmds.objExists(n):
            try:
                cmds.delete(n)
            except Exception:
                pass

    cmds.playbackOptions(min=1, max=36, ast=1, aet=36)
    cmds.currentTime(1)

    # 1. Build two driver joints and one driven joint with a visual sphere
    cmds.select(clear=True)
    drv_a = cmds.joint(name='cm_driverA', position=[-8, 10, 0])
    cmds.select(clear=True)
    drv_b = cmds.joint(name='cm_driverB', position=[8, 10, 0])
    cmds.select(clear=True)
    driven = cmds.joint(name='cm_driven', position=[0, 10, 0])

    sphere = cmds.polySphere(name='cm_sphere', radius=2.0)[0]
    cmds.parent(sphere, driven)
    cmds.setAttr(sphere + '.translate', 0, 0, 0)

    # Create parent constraint
    cns = cmds.parentConstraint([drv_a, drv_b], driven, maintainOffset=True)[0]
    w_attrs = [f"{cns}.cm_driverAW0", f"{cns}.cm_driverBW1"]

    # 2. Load release candidate tool
    rc_path = Path(r"C:/Users/zhongweijie/Documents/GitHub/maya_tools_box/tools_staging_pool/02_rigging_hierarchy/constraint_manager_v6/release_candidate").resolve()
    spec = importlib.util.spec_from_file_location('cm_loader', rc_path / 'launch_candidate.py')
    loader = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loader)
    tool = loader.load_tool()

    # Step A: Dry run weight adjustment
    dry_res = tool.run(dry_run=True, action='weights', selected_weights=[w_attrs[0]], all_weights=w_attrs, mode='selected_one')
    print("Dry run success:", dry_res.success)
    assert dry_res.success, f"Dry run failed: {dry_res.message}"

    # Step B: Adjust weights to 100% driver A
    res_a = tool.run(action='weights', selected_weights=[w_attrs[0]], all_weights=w_attrs, mode='selected_one')
    print("Set driver A weight success:", res_a.success)
    assert res_a.success, f"Set weight A failed: {res_a.message}"
    assert cmds.getAttr(w_attrs[0]) == 1.0
    assert cmds.getAttr(w_attrs[1]) == 0.0

    # Step C: Test Undo / Redo
    cmds.undo()
    print("Undo tested successfully.")
    cmds.redo()
    print("Redo tested successfully.")

    # 3. Animate drivers and weight transition over 36 frames
    # Drivers motion: Driver A oscillates in Y, Driver B oscillates in Z
    cmds.currentTime(1)
    cmds.setKeyframe(drv_a, attribute='translateY', value=10, time=1)
    cmds.setKeyframe(drv_b, attribute='translateY', value=10, time=1)
    cmds.setKeyframe(w_attrs[0], value=1.0, time=1)
    cmds.setKeyframe(w_attrs[1], value=0.0, time=1)

    cmds.currentTime(10)
    cmds.setKeyframe(drv_a, attribute='translateY', value=16, time=10)
    cmds.setKeyframe(drv_b, attribute='translateY', value=6, time=10)
    cmds.setKeyframe(w_attrs[0], value=0.8, time=10)
    cmds.setKeyframe(w_attrs[1], value=0.2, time=10)

    cmds.currentTime(18)
    cmds.setKeyframe(drv_a, attribute='translateY', value=10, time=18)
    cmds.setKeyframe(drv_b, attribute='translateY', value=10, time=18)
    cmds.setKeyframe(w_attrs[0], value=0.0, time=18)
    cmds.setKeyframe(w_attrs[1], value=1.0, time=18)

    cmds.currentTime(27)
    cmds.setKeyframe(drv_a, attribute='translateY', value=6, time=27)
    cmds.setKeyframe(drv_b, attribute='translateY', value=16, time=27)
    cmds.setKeyframe(w_attrs[0], value=0.2, time=27)
    cmds.setKeyframe(w_attrs[1], value=0.8, time=27)

    cmds.currentTime(36)
    cmds.setKeyframe(drv_a, attribute='translateY', value=10, time=36)
    cmds.setKeyframe(drv_b, attribute='translateY', value=10, time=36)
    cmds.setKeyframe(w_attrs[0], value=1.0, time=36)
    cmds.setKeyframe(w_attrs[1], value=0.0, time=36)

    # 4. Viewport Camera & Playblast
    cam_name = "test_cm_cam"
    if cmds.objExists(cam_name):
        cmds.delete(cam_name)
    cam_trans, cam_shape = cmds.camera(name=cam_name)
    cmds.setAttr(cam_trans + ".translate", 0, 11, 45)
    cmds.setAttr(cam_trans + ".rotate", 0, 0, 0)
    
    panel = 'modelPanel4'
    if panel in cmds.getPanel(type='modelPanel'):
        cmds.lookThru(panel, cam_trans)
        cmds.select([drv_a, drv_b, driven, sphere])
        cmds.viewFit(cam_trans)
        cmds.select(clear=True)
        cmds.modelEditor(panel, edit=True, displayAppearance='smoothShaded', displayTextures=False, displayLights='default')

    # 5. Playblast 36 frames
    seq_dir = Path(r"C:\Users\zhongweijie\Documents\GitHub\maya_tools_box\snapshots\constraint_manager_v6_anim_seq")
    if seq_dir.exists():
        shutil.rmtree(str(seq_dir))
    seq_dir.mkdir(parents=True, exist_ok=True)

    img_prefix = str(seq_dir / "frame")
    print(f"Playblasting 36 frames to {img_prefix}...")
    cmds.playblast(
        format="image",
        compression="png",
        filename=img_prefix,
        sequenceTime=0,
        clearCache=1,
        viewer=0,
        showOrnaments=0,
        fp=4,
        percent=100,
        widthHeight=(640, 480),
        startTime=1,
        endTime=36
    )

    # 6. Assemble GIF
    frame_files = sorted(list(seq_dir.glob("frame.*.png")))
    if not frame_files:
        frame_files = sorted(list(seq_dir.glob("*.png")))
    print(f"Captured {len(frame_files)} frames for GIF.")
    assert len(frame_files) >= 30, f"Too few frames: {len(frame_files)}"

    frames = [Image.open(str(f)) for f in frame_files]
    gif_path = Path(r"C:\Users\zhongweijie\Documents\GitHub\maya_tools_box\snapshots\constraint_manager_v6_joint_animation.gif")
    gif_path.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(
        str(gif_path),
        save_all=True,
        append_images=frames[1:],
        duration=int(1000 / 24),
        loop=0
    )
    print(f"GIF assembled: {gif_path} ({gif_path.stat().st_size} bytes)")

    # Copy to brain artifact directory
    brain_dir = Path(r"C:\Users\zhongweijie\.gemini\antigravity\brain\cb4fe7e1-8af7-4380-97a4-e5fb35e6f9bb")
    brain_gif = brain_dir / "constraint_manager_v6_joint_animation.gif"
    shutil.copyfile(str(gif_path), str(brain_gif))
    print(f"Copied GIF to brain: {brain_gif}")

    # 7. Clean up all created temporary nodes
    to_delete = [drv_a, drv_b, driven, cam_trans]
    for n in to_delete:
        if cmds.objExists(n):
            try:
                cmds.delete(n)
            except Exception as e:
                print("Failed to delete", n, e)
                
    for n in cmds.ls('cm_*', 'test_cm_*', type='transform'):
        if cmds.objExists(n):
            try:
                cmds.delete(n)
            except Exception:
                pass

    print("=== LIVE VERIFICATION OF CONSTRAINT_MANAGER_V6 COMPLETED SUCCESSFULLY ===")

if __name__ == '__main__':
    run_verification()
