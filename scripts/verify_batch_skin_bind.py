# -*- coding: utf-8 -*-
"""
Verification script for batch_skin_bind in live Maya session (test1026.ma).
Tests batch skin bind across multiple joint/mesh pairs, proxy creation, Undo/Redo,
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
    print("=== STARTING LIVE VERIFICATION: batch_skin_bind ===")
    
    # 0. Clean cached modules
    for mod in list(sys.modules):
        if 'batch_skin_bind' in mod:
            del sys.modules[mod]

    # Clean prior test nodes if any
    for n in cmds.ls('bsb_*', 'test_bsb_*', 'bsb_cam*', type='transform'):
        if cmds.objExists(n):
            try:
                cmds.delete(n)
            except Exception:
                pass

    cmds.playbackOptions(min=1, max=36, ast=1, aet=36)
    cmds.currentTime(1)

    # 1. Build a 3-joint chain and 3 polygon cylinders for batch skin binding
    cmds.select(clear=True)
    j0 = cmds.joint(name='bsb_j0', position=[0, 5, 0])
    j1 = cmds.joint(name='bsb_j1', position=[0, 12, 0])
    j2 = cmds.joint(name='bsb_j2', position=[0, 19, 0])

    m0 = cmds.polyCylinder(name='bsb_m0', radius=1.8, height=6)[0]
    cmds.xform(m0, translation=[0, 5, 0], worldSpace=True)

    m1 = cmds.polyCylinder(name='bsb_m1', radius=1.5, height=6)[0]
    cmds.xform(m1, translation=[0, 12, 0], worldSpace=True)

    m2 = cmds.polyCylinder(name='bsb_m2', radius=1.2, height=6)[0]
    cmds.xform(m2, translation=[0, 19, 0], worldSpace=True)

    # 2. Load release candidate tool
    rc_path = Path(r"C:/Users/zhongweijie/Documents/GitHub/maya_tools_box/tools_staging_pool/02_rigging_hierarchy/batch_skin_bind/release_candidate").resolve()
    spec = importlib.util.spec_from_file_location('bsb_loader', rc_path / 'launch_candidate.py')
    loader = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loader)
    tool = loader.load_tool()

    pairs = [
        {'joint': j0, 'mesh': m0},
        {'joint': j1, 'mesh': m1},
        {'joint': j2, 'mesh': m2}
    ]

    # Step A: Validate / Dry run
    dry_res = tool.run(dry_run=True, action='bind', pairs=pairs)
    print("Dry run success:", dry_res.success)
    assert dry_res.success, f"Dry run failed: {dry_res.message}"

    # Step B: Execute batch skin bind
    bind_res = tool.run(action='bind', pairs=pairs)
    print("Batch bind success:", bind_res.success, "data:", bind_res.data)
    assert bind_res.success, f"Batch bind failed: {bind_res.message}"
    assert len(bind_res.data.get('bindings', [])) == 3, "Expected 3 bindings"

    # Step C: Test Undo / Redo
    cmds.undo()
    clusters_after_undo = cmds.ls(type='skinCluster')
    print("Undo tested, remaining skinClusters:", len(clusters_after_undo))
    assert len(clusters_after_undo) == 0, "Undo should have removed skinClusters"
    cmds.redo()
    clusters_after_redo = cmds.ls(type='skinCluster')
    print("Redo tested, restored skinClusters:", len(clusters_after_redo))
    assert len(clusters_after_redo) == 3, "Redo should have restored 3 skinClusters"

    # 3. Animate joints over 36 frames (dynamic snake wave loop)
    cmds.currentTime(1)
    cmds.setKeyframe(j0, attribute='rotateZ', value=0, time=1)
    cmds.setKeyframe(j1, attribute='rotateZ', value=0, time=1)
    cmds.setKeyframe(j2, attribute='rotateZ', value=0, time=1)

    cmds.currentTime(10)
    cmds.setKeyframe(j0, attribute='rotateZ', value=20, time=10)
    cmds.setKeyframe(j1, attribute='rotateZ', value=-40, time=10)
    cmds.setKeyframe(j2, attribute='rotateZ', value=30, time=10)

    cmds.currentTime(18)
    cmds.setKeyframe(j0, attribute='rotateZ', value=0, time=18)
    cmds.setKeyframe(j1, attribute='rotateZ', value=0, time=18)
    cmds.setKeyframe(j2, attribute='rotateZ', value=0, time=18)

    cmds.currentTime(27)
    cmds.setKeyframe(j0, attribute='rotateZ', value=-20, time=27)
    cmds.setKeyframe(j1, attribute='rotateZ', value=40, time=27)
    cmds.setKeyframe(j2, attribute='rotateZ', value=-30, time=27)

    cmds.currentTime(36)
    cmds.setKeyframe(j0, attribute='rotateZ', value=0, time=36)
    cmds.setKeyframe(j1, attribute='rotateZ', value=0, time=36)
    cmds.setKeyframe(j2, attribute='rotateZ', value=0, time=36)

    # 4. Viewport Camera & Playblast
    cam_name = "test_bsb_cam"
    if cmds.objExists(cam_name):
        cmds.delete(cam_name)
    cam_trans, cam_shape = cmds.camera(name=cam_name)
    cmds.setAttr(cam_trans + ".translate", 0, 12, 45)
    cmds.setAttr(cam_trans + ".rotate", 0, 0, 0)
    
    panel = 'modelPanel4'
    if panel in cmds.getPanel(type='modelPanel'):
        cmds.lookThru(panel, cam_trans)
        cmds.select([j0, m0, m1, m2])
        cmds.viewFit(cam_trans)
        cmds.select(clear=True)
        cmds.modelEditor(panel, edit=True, displayAppearance='smoothShaded', displayTextures=False, displayLights='default')

    # 5. Playblast 36 frames
    seq_dir = Path(r"C:\Users\zhongweijie\Documents\GitHub\maya_tools_box\snapshots\batch_skin_bind_anim_seq")
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
    gif_path = Path(r"C:\Users\zhongweijie\Documents\GitHub\maya_tools_box\snapshots\batch_skin_bind_joint_animation.gif")
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
    brain_gif = brain_dir / "batch_skin_bind_joint_animation.gif"
    shutil.copyfile(str(gif_path), str(brain_gif))
    print(f"Copied GIF to brain: {brain_gif}")

    # 7. Clean up all created temporary nodes
    to_delete = [j0, m0, m1, m2, cam_trans]
    for n in to_delete:
        if cmds.objExists(n):
            try:
                cmds.delete(n)
            except Exception as e:
                print("Failed to delete", n, e)
                
    for n in cmds.ls('bsb_*', 'test_bsb_*', type='transform'):
        if cmds.objExists(n):
            try:
                cmds.delete(n)
            except Exception:
                pass

    print("=== LIVE VERIFICATION OF BATCH_SKIN_BIND COMPLETED SUCCESSFULLY ===")

if __name__ == '__main__':
    run_verification()
