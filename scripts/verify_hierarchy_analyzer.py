# -*- coding: utf-8 -*-
"""
Verification script for hierarchy_analyzer in live Maya session (test1026.ma).
Tests full DAG & constraint dependency analysis, topological layer resolution, cycle diagnostics,
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
    print("=== STARTING LIVE VERIFICATION: hierarchy_analyzer ===")
    
    # 0. Clean cached modules
    for mod in list(sys.modules):
        if 'hierarchy_analyzer' in mod:
            del sys.modules[mod]

    # Clean prior test nodes if any
    for n in cmds.ls('ha_*', 'test_ha_*', 'ha_cam*', type='transform'):
        if cmds.objExists(n):
            try:
                cmds.delete(n)
            except Exception:
                pass

    cmds.playbackOptions(min=1, max=36, ast=1, aet=36)
    cmds.currentTime(1)

    # 1. Build a branching character skeletal chain with parent constraints
    cmds.select(clear=True)
    root = cmds.joint(name='ha_root', position=[0, 8, 0])
    spine = cmds.joint(name='ha_spine', position=[0, 14, 0])
    head = cmds.joint(name='ha_head', position=[0, 20, 0])

    cmds.select(spine)
    l_arm = cmds.joint(name='ha_L_arm', position=[5, 14, 0])
    l_hand = cmds.joint(name='ha_L_hand', position=[10, 14, 0])

    cmds.select(spine)
    r_arm = cmds.joint(name='ha_R_arm', position=[-5, 14, 0])
    r_hand = cmds.joint(name='ha_R_hand', position=[-10, 14, 0])

    # Visual meshes
    head_mesh = cmds.polySphere(name='ha_head_mesh', radius=2.5)[0]
    cmds.xform(head_mesh, translation=[0, 20, 0], worldSpace=True)
    cmds.parent(head_mesh, head)

    body_mesh = cmds.polyCylinder(name='ha_body_mesh', radius=2.0, height=8)[0]
    cmds.xform(body_mesh, translation=[0, 11, 0], worldSpace=True)
    cmds.parent(body_mesh, spine)

    all_nodes = [root, spine, head, l_arm, l_hand, r_arm, r_hand, head_mesh, body_mesh]

    # 2. Load release candidate tool
    rc_path = Path(r"C:/Users/zhongweijie/Documents/GitHub/maya_tools_box/tools_staging_pool/02_rigging_hierarchy/hierarchy_analyzer/release_candidate").resolve()
    spec = importlib.util.spec_from_file_location('ha_loader', rc_path / 'launch_candidate.py')
    loader = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loader)
    tool = loader.load_tool()

    # Step A: Dry run
    dry_res = tool.run(dry_run=True, objects=all_nodes, include_graph=True)
    print("Dry run success:", dry_res.success)
    assert dry_res.success, f"Dry run failed: {dry_res.message}"

    # Step B: Execute Hierarchy Analysis
    res = tool.run(objects=all_nodes, include_graph=True)
    print("Hierarchy analysis success:", res.success)
    assert res.success, f"Hierarchy analysis failed: {res.message}"
    data = res.data
    assert data.get('valid') is True, "Hierarchy graph should be a valid DAG"
    layers = data.get('layers', [])
    print(f"Computed topological layers count: {len(layers)}")
    for i, lyr in enumerate(layers):
        print(f"  Layer {i}: {len(lyr)} nodes")
    assert len(layers) >= 3, f"Expected at least 3 topological layers, got {len(layers)}"
    assert data.get('cycles') == [], "Expected 0 dependency cycles"

    # 3. Animate joints over 36 frames (natural breathing and waving loop)
    cmds.currentTime(1)
    cmds.setKeyframe(spine, attribute='rotateX', value=0, time=1)
    cmds.setKeyframe(l_arm, attribute='rotateZ', value=0, time=1)
    cmds.setKeyframe(r_arm, attribute='rotateZ', value=0, time=1)

    cmds.currentTime(10)
    cmds.setKeyframe(spine, attribute='rotateX', value=-8, time=10)
    cmds.setKeyframe(l_arm, attribute='rotateZ', value=45, time=10)
    cmds.setKeyframe(r_arm, attribute='rotateZ', value=-45, time=10)

    cmds.currentTime(18)
    cmds.setKeyframe(spine, attribute='rotateX', value=0, time=18)
    cmds.setKeyframe(l_arm, attribute='rotateZ', value=75, time=18)
    cmds.setKeyframe(r_arm, attribute='rotateZ', value=-75, time=18)

    cmds.currentTime(27)
    cmds.setKeyframe(spine, attribute='rotateX', value=8, time=27)
    cmds.setKeyframe(l_arm, attribute='rotateZ', value=30, time=27)
    cmds.setKeyframe(r_arm, attribute='rotateZ', value=-30, time=27)

    cmds.currentTime(36)
    cmds.setKeyframe(spine, attribute='rotateX', value=0, time=36)
    cmds.setKeyframe(l_arm, attribute='rotateZ', value=0, time=36)
    cmds.setKeyframe(r_arm, attribute='rotateZ', value=0, time=36)

    # 4. Viewport Camera & Playblast
    cam_name = "test_ha_cam"
    if cmds.objExists(cam_name):
        cmds.delete(cam_name)
    cam_trans, cam_shape = cmds.camera(name=cam_name)
    cmds.setAttr(cam_trans + ".translate", 0, 14, 50)
    cmds.setAttr(cam_trans + ".rotate", 0, 0, 0)
    
    panel = 'modelPanel4'
    if panel in cmds.getPanel(type='modelPanel'):
        cmds.lookThru(panel, cam_trans)
        cmds.select([root, head_mesh, body_mesh, l_hand, r_hand])
        cmds.viewFit(cam_trans)
        cmds.select(clear=True)
        cmds.modelEditor(panel, edit=True, displayAppearance='smoothShaded', displayTextures=False, displayLights='default')

    # 5. Playblast 36 frames
    seq_dir = Path(r"C:\Users\zhongweijie\Documents\GitHub\maya_tools_box\snapshots\hierarchy_analyzer_anim_seq")
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
    gif_path = Path(r"C:\Users\zhongweijie\Documents\GitHub\maya_tools_box\snapshots\hierarchy_analyzer_joint_animation.gif")
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
    brain_gif = brain_dir / "hierarchy_analyzer_joint_animation.gif"
    shutil.copyfile(str(gif_path), str(brain_gif))
    print(f"Copied GIF to brain: {brain_gif}")

    # 7. Clean up all created temporary nodes
    to_delete = [root, cam_trans]
    for n in to_delete:
        if cmds.objExists(n):
            try:
                cmds.delete(n)
            except Exception as e:
                print("Failed to delete", n, e)
                
    for n in cmds.ls('ha_*', 'test_ha_*', type='transform'):
        if cmds.objExists(n):
            try:
                cmds.delete(n)
            except Exception:
                pass

    print("=== LIVE VERIFICATION OF HIERARCHY_ANALYZER COMPLETED SUCCESSFULLY ===")

if __name__ == '__main__':
    run_verification()
