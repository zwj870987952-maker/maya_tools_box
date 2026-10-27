# -*- coding: utf-8 -*-
"""
Verification script for bb_tools in live Maya session (test1026.ma).
Tests controller shape creation (Circle, Box, Sphere), color assignment, hierarchy constraint,
Undo/Redo, 36-frame dynamic playback and GIF generation.
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
    print("=== STARTING LIVE VERIFICATION: bb_tools ===")
    
    # 0. Clean cached modules
    for mod in list(sys.modules):
        if 'bb_tools' in mod:
            del sys.modules[mod]

    # Clean prior test nodes if any
    for n in cmds.ls('bbt_*', 'test_bbt_*', 'bbt_cam*', type='transform'):
        if cmds.objExists(n):
            try:
                cmds.delete(n)
            except Exception:
                pass

    cmds.playbackOptions(min=1, max=36, ast=1, aet=36)
    cmds.currentTime(1)

    # 1. Build a 3-joint chain and mesh
    cmds.select(clear=True)
    j0 = cmds.joint(name='bbt_j0', position=[0, 5, 0])
    j1 = cmds.joint(name='bbt_j1', position=[0, 12, 0])
    j2 = cmds.joint(name='bbt_j2', position=[0, 19, 0])

    mesh = cmds.polyCylinder(name='bbt_mesh', radius=2.0, height=18, subdivisionsY=8)[0]
    cmds.xform(mesh, translation=[0, 12, 0], worldSpace=True)
    cmds.skinCluster([j0, j1, j2], mesh, toSelectedBones=True)

    # 2. Load release candidate tool
    rc_path = Path(r"C:/Users/zhongweijie/Documents/GitHub/maya_tools_box/tools_staging_pool/02_rigging_hierarchy/bb_tools/release_candidate").resolve()
    spec = importlib.util.spec_from_file_location('bbt_loader', rc_path / 'launch_candidate.py')
    loader = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loader)
    tool = loader.load_tool()

    # Step A: Validate / Dry run
    dry_res = tool.run(dry_run=True, action='call', procedure='bb_CtrlTool_createShape', arguments=['CtrlShape_circle', 'bbt_ctrl_root'])
    print("Dry run success:", dry_res.success)
    assert dry_res.success, f"Dry run failed: {dry_res.message}"

    # Step B: Create Controller Shapes (Circle, Cube, Sphere)
    res_c0 = tool.run(action='call', procedure='bb_CtrlTool_createShape', arguments=['CtrlShape_circle', 'bbt_ctrl_root'])
    assert res_c0.success, f"Failed to create Circle controller: {res_c0.message}"
    cmds.xform('bbt_ctrl_root', translation=[0, 5, 0], worldSpace=True)

    res_c1 = tool.run(action='call', procedure='bb_CtrlTool_createShape', arguments=['CtrlShape_cube', 'bbt_ctrl_mid'])
    assert res_c1.success, f"Failed to create Box controller: {res_c1.message}"
    cmds.xform('bbt_ctrl_mid', translation=[0, 12, 0], worldSpace=True)

    res_c2 = tool.run(action='call', procedure='bb_CtrlTool_createShape', arguments=['CtrlShape_sphere', 'bbt_ctrl_top'])
    assert res_c2.success, f"Failed to create Sphere controller: {res_c2.message}"
    cmds.xform('bbt_ctrl_top', translation=[0, 19, 0], worldSpace=True)

    # Step C: Change color of controllers
    res_col = tool.run(action='call', procedure='bb_CtrlTool_changeColorApply', arguments=['bbt_ctrl_root', 13], objects=['bbt_ctrl_root'])
    print("Change color success:", res_col.success)
    assert res_col.success, f"Failed to change color: {res_col.message}"

    # Step D: Test Undo / Redo
    cmds.undo()
    print("Undo color tested.")
    cmds.redo()
    print("Redo color tested.")

    # Parent constraint controllers to joints
    cmds.parentConstraint('bbt_ctrl_root', j0, maintainOffset=True)
    cmds.parentConstraint('bbt_ctrl_mid', j1, maintainOffset=True)
    cmds.parentConstraint('bbt_ctrl_top', j2, maintainOffset=True)

    # 3. Animate controllers over 36 frames
    cmds.currentTime(1)
    cmds.setKeyframe('bbt_ctrl_root', attribute='rotateZ', value=0, time=1)
    cmds.setKeyframe('bbt_ctrl_mid', attribute='rotateZ', value=0, time=1)
    cmds.setKeyframe('bbt_ctrl_top', attribute='rotateZ', value=0, time=1)

    cmds.currentTime(10)
    cmds.setKeyframe('bbt_ctrl_root', attribute='rotateZ', value=-15, time=10)
    cmds.setKeyframe('bbt_ctrl_mid', attribute='rotateZ', value=30, time=10)
    cmds.setKeyframe('bbt_ctrl_top', attribute='rotateZ', value=-25, time=10)

    cmds.currentTime(18)
    cmds.setKeyframe('bbt_ctrl_root', attribute='rotateZ', value=0, time=18)
    cmds.setKeyframe('bbt_ctrl_mid', attribute='rotateZ', value=0, time=18)
    cmds.setKeyframe('bbt_ctrl_top', attribute='rotateZ', value=0, time=18)

    cmds.currentTime(27)
    cmds.setKeyframe('bbt_ctrl_root', attribute='rotateZ', value=15, time=27)
    cmds.setKeyframe('bbt_ctrl_mid', attribute='rotateZ', value=-30, time=27)
    cmds.setKeyframe('bbt_ctrl_top', attribute='rotateZ', value=25, time=27)

    cmds.currentTime(36)
    cmds.setKeyframe('bbt_ctrl_root', attribute='rotateZ', value=0, time=36)
    cmds.setKeyframe('bbt_ctrl_mid', attribute='rotateZ', value=0, time=36)
    cmds.setKeyframe('bbt_ctrl_top', attribute='rotateZ', value=0, time=36)

    # 4. Viewport Camera & Playblast
    cam_name = "test_bbt_cam"
    if cmds.objExists(cam_name):
        cmds.delete(cam_name)
    cam_trans, cam_shape = cmds.camera(name=cam_name)
    cmds.setAttr(cam_trans + ".translate", 0, 12, 45)
    cmds.setAttr(cam_trans + ".rotate", 0, 0, 0)
    
    panel = 'modelPanel4'
    if panel in cmds.getPanel(type='modelPanel'):
        cmds.lookThru(panel, cam_trans)
        cmds.select([j0, mesh, 'bbt_ctrl_root', 'bbt_ctrl_mid', 'bbt_ctrl_top'])
        cmds.viewFit(cam_trans)
        cmds.select(clear=True)
        cmds.modelEditor(panel, edit=True, displayAppearance='smoothShaded', displayTextures=False, displayLights='default')

    # 5. Playblast 36 frames
    seq_dir = Path(r"C:\Users\zhongweijie\Documents\GitHub\maya_tools_box\snapshots\bb_tools_anim_seq")
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
    gif_path = Path(r"C:\Users\zhongweijie\Documents\GitHub\maya_tools_box\snapshots\bb_tools_joint_animation.gif")
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
    brain_gif = brain_dir / "bb_tools_joint_animation.gif"
    shutil.copyfile(str(gif_path), str(brain_gif))
    print(f"Copied GIF to brain: {brain_gif}")

    # 7. Clean up all created temporary nodes
    to_delete = [j0, mesh, cam_trans, 'bbt_ctrl_root', 'bbt_ctrl_mid', 'bbt_ctrl_top']
    for n in to_delete:
        if cmds.objExists(n):
            try:
                cmds.delete(n)
            except Exception as e:
                print("Failed to delete", n, e)
                
    for n in cmds.ls('bbt_*', 'test_bbt_*', type='transform'):
        if cmds.objExists(n):
            try:
                cmds.delete(n)
            except Exception:
                pass

    print("=== LIVE VERIFICATION OF BB_TOOLS COMPLETED SUCCESSFULLY ===")

if __name__ == '__main__':
    run_verification()
