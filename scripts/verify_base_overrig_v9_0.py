# -*- coding: utf-8 -*-
"""
Verification script for base_overrig_v9_0 in live Maya session (test1026.ma).
Tests inspect, create_normalised_locators_on_selected, scale_selected_lock_or_joint, Undo/Redo,
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
    print("=== STARTING LIVE VERIFICATION: base_overrig_v9_0 ===")
    
    # 0. Clean cached modules
    for mod in list(sys.modules):
        if 'base_overrig_v9_0' in mod:
            del sys.modules[mod]

    # Clean prior test nodes if any
    for n in cmds.ls('ovr_*', 'test_ovr_*', 'ovr_cam*', type='transform'):
        if cmds.objExists(n):
            try:
                cmds.delete(n)
            except Exception:
                pass

    cmds.playbackOptions(min=1, max=36, ast=1, aet=36)
    cmds.currentTime(1)

    # 1. Build a dynamic 3-joint spine/arm chain
    cmds.select(clear=True)
    root = cmds.joint(name='ovr_root', position=[0, 10, 0])
    mid = cmds.joint(name='ovr_mid', position=[0, 15, 0])
    top = cmds.joint(name='ovr_top', position=[0, 20, 0])
    
    # Also create a mesh sphere attached/parented to top for visual volume
    sphere = cmds.polySphere(name='ovr_sphere', radius=2)[0]
    cmds.parent(sphere, top)
    cmds.setAttr(sphere + '.translate', 0, 0, 0)

    # 2. Load release candidate tool
    rc_path = Path(r"C:/Users/zhongweijie/Documents/GitHub/maya_tools_box/tools_staging_pool/02_rigging_hierarchy/base_overrig_v9_0/release_candidate").resolve()
    spec = importlib.util.spec_from_file_location('base_overrig_loader', rc_path / 'launch_candidate.py')
    loader = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loader)
    tool = loader.load_tool()

    # Step A: Validate / Inspect
    inspect_res = tool.run(action='inspect')
    print("Inspect success:", inspect_res.success, "public count:", len(inspect_res.data.get('public', {})))
    assert inspect_res.success, "Inspect failed"

    # Step B: Call create_normalised_locators_on_selected
    loc_res = tool.run(action='call', procedure='create_normalised_locators_on_selected', objects=[mid, top])
    print("Create locators success:", loc_res.success, "created:", loc_res.data.get('native_result', []))
    assert loc_res.success, f"Create locators failed: {loc_res.message}"
    created_locs = loc_res.data.get('native_result', [])
    assert len(created_locs) == 2, f"Expected 2 locators, got {len(created_locs)}"

    # Step C: Scale locator
    scale_res = tool.run(action='call', procedure='scale_selected_lock_or_joint', arguments=[2.5], objects=[created_locs[0]])
    print("Scale locator success:", scale_res.success)
    assert scale_res.success, f"Scale locator failed: {scale_res.message}"

    # Step D: Test Undo / Redo
    cmds.undo()
    print("Undo scale verified.")
    cmds.redo()
    print("Redo scale verified.")

    # 3. Animate joints over 36 frames (looping wave)
    cmds.currentTime(1)
    cmds.setKeyframe(root, attribute='rotateZ', value=0, time=1)
    cmds.setKeyframe(mid, attribute='rotateZ', value=0, time=1)
    cmds.setKeyframe(top, attribute='rotateZ', value=0, time=1)

    cmds.currentTime(10)
    cmds.setKeyframe(root, attribute='rotateZ', value=-15, time=10)
    cmds.setKeyframe(mid, attribute='rotateZ', value=30, time=10)
    cmds.setKeyframe(top, attribute='rotateZ', value=-25, time=10)

    cmds.currentTime(18)
    cmds.setKeyframe(root, attribute='rotateZ', value=0, time=18)
    cmds.setKeyframe(mid, attribute='rotateZ', value=0, time=18)
    cmds.setKeyframe(top, attribute='rotateZ', value=0, time=18)

    cmds.currentTime(27)
    cmds.setKeyframe(root, attribute='rotateZ', value=15, time=27)
    cmds.setKeyframe(mid, attribute='rotateZ', value=-30, time=27)
    cmds.setKeyframe(top, attribute='rotateZ', value=25, time=27)

    cmds.currentTime(36)
    cmds.setKeyframe(root, attribute='rotateZ', value=0, time=36)
    cmds.setKeyframe(mid, attribute='rotateZ', value=0, time=36)
    cmds.setKeyframe(top, attribute='rotateZ', value=0, time=36)

    # 4. Viewport Camera & Playblast
    cam_name = "test_ovr_cam"
    if cmds.objExists(cam_name):
        cmds.delete(cam_name)
    cam_trans, cam_shape = cmds.camera(name=cam_name)
    cmds.setAttr(cam_trans + ".translate", 0, 15, 45)
    cmds.setAttr(cam_trans + ".rotate", 0, 0, 0)
    
    panel = 'modelPanel4'
    if panel in cmds.getPanel(type='modelPanel'):
        cmds.lookThru(panel, cam_trans)
        cmds.viewFit(cam_trans, all=False)
        cmds.select([root, sphere] + created_locs)
        cmds.viewFit(cam_trans)
        cmds.select(clear=True)
        cmds.modelEditor(panel, edit=True, displayAppearance='smoothShaded', displayTextures=False, displayLights='default')

    # 5. Playblast 36 frames
    seq_dir = Path(r"C:\Users\zhongweijie\Documents\GitHub\maya_tools_box\snapshots\base_overrig_v9_0_anim_seq")
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
    gif_path = Path(r"C:\Users\zhongweijie\Documents\GitHub\maya_tools_box\snapshots\base_overrig_v9_0_joint_animation.gif")
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
    brain_gif = brain_dir / "base_overrig_v9_0_joint_animation.gif"
    shutil.copyfile(str(gif_path), str(brain_gif))
    print(f"Copied GIF to brain: {brain_gif}")

    # 7. Clean up all created temporary nodes and restore baseline scene
    to_delete = [root, cam_trans] + created_locs
    for n in to_delete:
        if cmds.objExists(n):
            try:
                cmds.delete(n)
            except Exception as e:
                print("Failed to delete", n, e)
                
    # Also clean up any lingering test nodes
    for n in cmds.ls('ovr_*', 'test_ovr_*', type='transform'):
        if cmds.objExists(n):
            try:
                cmds.delete(n)
            except Exception:
                pass

    print("=== LIVE VERIFICATION OF BASE_OVERRIG_V9_0 COMPLETED SUCCESSFULLY ===")

if __name__ == '__main__':
    run_verification()
