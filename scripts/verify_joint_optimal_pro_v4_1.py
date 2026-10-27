# -*- coding: utf-8 -*-
"""
Verification script for joint_optimal_pro_v4_1 in live Maya session (test1026.ma).
Tests joint optimization procedures (radius, color override, display handles), Undo/Redo,
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
    print("=== STARTING LIVE VERIFICATION: joint_optimal_pro_v4_1 ===")
    
    # 0. Clean cached modules
    for mod in list(sys.modules):
        if 'joint_optimal_pro_v4_1' in mod:
            del sys.modules[mod]

    # Clean prior test nodes if any
    for n in cmds.ls('jop_*', 'test_jop_*', 'jop_cam*', type='transform'):
        if cmds.objExists(n):
            try:
                cmds.delete(n)
            except Exception:
                pass

    cmds.playbackOptions(min=1, max=36, ast=1, aet=36)
    cmds.currentTime(1)

    # 1. Build a 4-joint spine/leg chain with attached geometry volumes
    cmds.select(clear=True)
    j0 = cmds.joint(name='jop_j0', position=[0, 4, 0])
    j1 = cmds.joint(name='jop_j1', position=[0, 10, 0])
    j2 = cmds.joint(name='jop_j2', position=[0, 16, 0])
    j3 = cmds.joint(name='jop_j3', position=[0, 22, 0])

    sph = cmds.polySphere(name='jop_sphere', radius=2.2)[0]
    cmds.xform(sph, translation=[0, 22, 0], worldSpace=True)
    cmds.parent(sph, j3)

    cyl = cmds.polyCylinder(name='jop_cyl', radius=1.6, height=12)[0]
    cmds.xform(cyl, translation=[0, 10, 0], worldSpace=True)
    cmds.parent(cyl, j1)

    # 2. Load release candidate tool
    rc_path = Path(r"C:/Users/zhongweijie/Documents/GitHub/maya_tools_box/tools_staging_pool/02_rigging_hierarchy/joint_optimal_pro_v4_1/release_candidate").resolve()
    spec = importlib.util.spec_from_file_location('jop_loader', rc_path / 'launch_candidate.py')
    loader = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loader)
    tool = loader.load_tool()
    mod_pkg = tool.__class__.__module__.rsplit('.', 1)[0]
    runtime = __import__(mod_pkg + '.runtime', fromlist=['runtime'])

    # Step A: Validate / Inspect
    inspect_res = tool.run(action='inspect')
    print("Inspect success:", inspect_res.success, "public procedures count:", len(inspect_res.data.get('public', {})))
    assert inspect_res.success, "Inspect failed"

    # Step B: Optimize joint radius via native procedure
    res_rad = tool.run(action='call', procedure=runtime.RADIUS, arguments=[2.2], objects=[j0, j1, j2, j3])
    print("Optimize radius success:", res_rad.success)
    assert res_rad.success, f"Radius optimize failed: {res_rad.message}"
    assert cmds.getAttr(j0 + '.radius') == 2.2

    # Step C: Optimize joint color override
    res_col = tool.run(action='call', procedure=runtime.COLOR, arguments=[18], objects=[j0, j1])
    print("Optimize color success:", res_col.success)
    assert res_col.success, f"Color optimize failed: {res_col.message}"
    assert cmds.getAttr(j0 + '.overrideColor') == 18

    # Step D: Test Undo / Redo
    cmds.undo()
    print("Undo color tested, reverted color:", cmds.getAttr(j0 + '.overrideColor'))
    cmds.redo()
    print("Redo color tested, restored color:", cmds.getAttr(j0 + '.overrideColor'))

    # Step E: Enable display handles
    res_hdl = tool.run(action='call', procedure=runtime.HANDLE, arguments=[1], objects=[j2, j3])
    assert res_hdl.success, f"Handle optimize failed: {res_hdl.message}"

    # 3. Animate joints over 36 frames (smooth spiral wave loop)
    cmds.currentTime(1)
    for j in [j0, j1, j2, j3]:
        cmds.setKeyframe(j, attribute='rotateZ', value=0, time=1)
        cmds.setKeyframe(j, attribute='rotateY', value=0, time=1)

    cmds.currentTime(10)
    cmds.setKeyframe(j0, attribute='rotateZ', value=-10, time=10)
    cmds.setKeyframe(j1, attribute='rotateZ', value=25, time=10)
    cmds.setKeyframe(j2, attribute='rotateZ', value=-20, time=10)
    cmds.setKeyframe(j3, attribute='rotateZ', value=15, time=10)
    cmds.setKeyframe(j1, attribute='rotateY', value=20, time=10)

    cmds.currentTime(18)
    for j in [j0, j1, j2, j3]:
        cmds.setKeyframe(j, attribute='rotateZ', value=0, time=18)
        cmds.setKeyframe(j, attribute='rotateY', value=0, time=18)

    cmds.currentTime(27)
    cmds.setKeyframe(j0, attribute='rotateZ', value=10, time=27)
    cmds.setKeyframe(j1, attribute='rotateZ', value=-25, time=27)
    cmds.setKeyframe(j2, attribute='rotateZ', value=20, time=27)
    cmds.setKeyframe(j3, attribute='rotateZ', value=-15, time=27)
    cmds.setKeyframe(j1, attribute='rotateY', value=-20, time=27)

    cmds.currentTime(36)
    for j in [j0, j1, j2, j3]:
        cmds.setKeyframe(j, attribute='rotateZ', value=0, time=36)
        cmds.setKeyframe(j, attribute='rotateY', value=0, time=36)

    # 4. Viewport Camera & Playblast
    cam_name = "test_jop_cam"
    if cmds.objExists(cam_name):
        cmds.delete(cam_name)
    cam_trans, cam_shape = cmds.camera(name=cam_name)
    cmds.setAttr(cam_trans + ".translate", 0, 14, 50)
    cmds.setAttr(cam_trans + ".rotate", 0, 0, 0)
    
    panel = 'modelPanel4'
    if panel in cmds.getPanel(type='modelPanel'):
        cmds.lookThru(panel, cam_trans)
        cmds.select([j0, sph, cyl])
        cmds.viewFit(cam_trans)
        cmds.select(clear=True)
        cmds.modelEditor(panel, edit=True, displayAppearance='smoothShaded', displayTextures=False, displayLights='default')

    # 5. Playblast 36 frames
    seq_dir = Path(r"C:\Users\zhongweijie\Documents\GitHub\maya_tools_box\snapshots\joint_optimal_pro_v4_1_anim_seq")
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
    gif_path = Path(r"C:\Users\zhongweijie\Documents\GitHub\maya_tools_box\snapshots\joint_optimal_pro_v4_1_joint_animation.gif")
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
    brain_gif = brain_dir / "joint_optimal_pro_v4_1_joint_animation.gif"
    shutil.copyfile(str(gif_path), str(brain_gif))
    print(f"Copied GIF to brain: {brain_gif}")

    # 7. Clean up all created temporary nodes
    to_delete = [j0, cam_trans]
    for n in to_delete:
        if cmds.objExists(n):
            try:
                cmds.delete(n)
            except Exception as e:
                print("Failed to delete", n, e)
                
    for n in cmds.ls('jop_*', 'test_jop_*', type='transform'):
        if cmds.objExists(n):
            try:
                cmds.delete(n)
            except Exception:
                pass

    print("=== LIVE VERIFICATION OF JOINT_OPTIMAL_PRO_V4_1 COMPLETED SUCCESSFULLY ===")

if __name__ == '__main__':
    run_verification()
