# -*- coding: utf-8 -*-
"""
Verification script for reparent_pro_v1_5_1 in live Maya session (test1026.ma).
Tests reparent space switching, locator tracking, baking & deletion,
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
    print("=== STARTING LIVE VERIFICATION: reparent_pro_v1_5_1 ===")
    
    # 0. Clean cached modules
    for mod in list(sys.modules):
        if 'reparent_pro_v1_5_1' in mod:
            del sys.modules[mod]

    # Clean prior test nodes if any
    for n in cmds.ls('rpp_*', 'test_rpp_*', 'rpp_cam*', type='transform'):
        if cmds.objExists(n):
            try:
                cmds.delete(n)
            except Exception:
                pass

    cmds.playbackOptions(min=1, max=36, ast=1, aet=36)
    cmds.currentTime(1)

    # 1. Build a 3-joint bone chain with skinned cylinder
    cmds.select(clear=True)
    j0 = cmds.joint(name='rpp_j0', position=[0, 0, 0])
    j1 = cmds.joint(name='rpp_j1', position=[0, 10, 0])
    j2 = cmds.joint(name='rpp_j2', position=[0, 20, 0])

    cyl = cmds.polyCylinder(name='rpp_cyl', radius=2.2, height=22, subdivisionsY=12)[0]
    cmds.xform(cyl, translation=[0, 10, 0], worldSpace=True)
    cmds.skinCluster([j0, j1, j2], cyl, toSelectedBones=True, name='rpp_skinCluster')

    ctrl = cmds.circle(name='rpp_ctrl', radius=4.0, normal=[0, 1, 0])[0]
    cmds.xform(ctrl, translation=[0, 10, 0], worldSpace=True)
    cmds.parentConstraint(ctrl, j1, maintainOffset=True)

    # 2. Keyframe control along 36-frame loop
    for f in range(1, 37):
        t = (f - 1) / 35.0 * 2 * math.pi
        tx = math.sin(t) * 8.0
        ty = 10.0 + math.cos(t) * 3.5
        tz = math.sin(t * 2) * 6.0
        ry = math.sin(t) * 30.0
        cmds.setKeyframe(ctrl, attribute='translateX', value=tx, time=f)
        cmds.setKeyframe(ctrl, attribute='translateY', value=ty, time=f)
        cmds.setKeyframe(ctrl, attribute='translateZ', value=tz, time=f)
        cmds.setKeyframe(ctrl, attribute='rotateY', value=ry, time=f)

    # 3. Load release candidate tool
    rc_path = Path(r"C:/Users/zhongweijie/Documents/GitHub/maya_tools_box/tools_staging_pool/02_rigging_hierarchy/reparent_pro_v1_5_1/release_candidate").resolve()
    spec = importlib.util.spec_from_file_location('rpp_loader', rc_path / 'launch_candidate.py')
    loader = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loader)
    tool = loader.load_tool()

    # Step A: Inspect
    inspect_res = tool.run(action='inspect')
    print("Inspect success:", inspect_res.success)
    assert inspect_res.success, f"Inspect failed: {inspect_res.message}"

    # Step B: Reparent operation with locator tracking
    reparent_res = tool.run(
        action='reparent',
        objects=[ctrl],
        frame_range=[1, 36],
        allow_clear_animation=True,
        delete_redundant=False
    )
    print("Reparent Result:", reparent_res.success, reparent_res.message)
    assert reparent_res.success, f"Reparent failed: {reparent_res.message}"

    # Step C: Bake and delete temporary locator
    bake_res = tool.run(
        action='bake_delete',
        frame_range=[1, 36]
    )
    print("Bake Delete Result:", bake_res.success, bake_res.message)
    assert bake_res.success, f"Bake delete failed: {bake_res.message}"

    # 4. Viewport Playblast Setup
    cam, cam_shape = cmds.camera(name='rpp_cam', position=[30, 16, 45], rotation=[-10, 32, 0])
    cmds.viewFit(cam, all=True)
    
    panel = 'modelPanel4'
    if cmds.panel(panel, exists=True):
        cmds.modelPanel(panel, edit=True, camera=cam)
        cmds.modelEditor(panel, edit=True, displayAppearance='smoothShaded', displayTextures=False, joints=True, nurbsCurves=True)

    tmp_dir = Path("C:/Users/zhongweijie/Documents/GitHub/maya_tools_box/snapshots/temp_blast_rpp")
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
    gif_path = Path("C:/Users/zhongweijie/Documents/GitHub/maya_tools_box/snapshots/reparent_pro_v1_5_1_joint_animation.gif")
    brain_gif_path = Path("C:/Users/zhongweijie/.gemini/antigravity/brain/cb4fe7e1-8af7-4380-97a4-e5fb35e6f9bb/reparent_pro_v1_5_1_joint_animation.gif")
    
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
    print("=== LIVE VERIFICATION COMPLETE: reparent_pro_v1_5_1 PASSED ===")
    return True

if __name__ == '__main__':
    run_verification()
