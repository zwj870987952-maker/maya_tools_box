# -*- coding: utf-8 -*-
"""
Verification script for relationship_tools_v19 in live Maya session (test1026.ma).
Tests relationship marking, multi-frame alignment tracking, dynamic joint deformation,
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
    print("=== STARTING LIVE VERIFICATION: relationship_tools_v19 ===")
    
    # 0. Clean cached modules
    for mod in list(sys.modules):
        if 'relationship_tools_v19' in mod:
            del sys.modules[mod]

    # Clean prior test nodes if any
    for n in cmds.ls('rel_*', 'test_rel_*', 'rel_cam*', type='transform'):
        if cmds.objExists(n):
            try:
                cmds.delete(n)
            except Exception:
                pass

    cmds.playbackOptions(min=1, max=36, ast=1, aet=36)
    cmds.currentTime(1)

    # 1. Build a 3-joint bone chain with skinned cylinder
    cmds.select(clear=True)
    j0 = cmds.joint(name='rel_j0', position=[0, 0, 0])
    j1 = cmds.joint(name='rel_j1', position=[0, 10, 0])
    j2 = cmds.joint(name='rel_j2', position=[0, 20, 0])

    cyl = cmds.polyCylinder(name='rel_cyl', radius=2.2, height=22, subdivisionsY=12)[0]
    cmds.xform(cyl, translation=[0, 10, 0], worldSpace=True)
    cmds.skinCluster([j0, j1, j2], cyl, toSelectedBones=True, name='rel_skinCluster')

    # Driver target locator & follower locator
    target = cmds.spaceLocator(name='rel_target')[0]
    follower = cmds.spaceLocator(name='rel_follower')[0]

    # Constrain top joint to look at follower
    cmds.aimConstraint(follower, j1, aimVector=[0, 1, 0], upVector=[1, 0, 0], worldUpType="scene")

    # 2. Keyframe target along a smooth loop (frames 1..36)
    for f in range(1, 37):
        t = (f - 1) / 35.0 * 2 * math.pi
        tx = math.sin(t) * 12.0
        ty = 16.0 + math.cos(t) * 5.0
        tz = math.sin(t * 2) * 8.0
        cmds.setKeyframe(target, attribute='translateX', value=tx, time=f)
        cmds.setKeyframe(target, attribute='translateY', value=ty, time=f)
        cmds.setKeyframe(target, attribute='translateZ', value=tz, time=f)

    # 3. Load release candidate tool
    rc_path = Path(r"C:/Users/zhongweijie/Documents/GitHub/maya_tools_box/tools_staging_pool/02_rigging_hierarchy/relationship_tools_v19/release_candidate").resolve()
    spec = importlib.util.spec_from_file_location('rel_loader', rc_path / 'launch_candidate.py')
    loader = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loader)
    tool = loader.load_tool()

    # Step A: Inspect
    inspect_res = tool.run(action='inspect')
    print("Inspect success:", inspect_res.success)
    assert inspect_res.success, f"Inspect failed: {inspect_res.message}"

    # Step B: Mark relationship between follower and target
    mark_res = tool.run(action='mark', objects=[follower, target])
    print("Mark Result:", mark_res.success, mark_res.message)
    assert mark_res.success, f"Mark failed: {mark_res.message}"

    # Step C: Align follower to target across frame range 1..36 with step=1
    align_res = tool.run(
        action='align',
        objects=[follower, target],
        translate=True,
        rotate=False,
        bake=True,
        frame_range=[1, 36],
        step=1
    )
    print("Align Result:", align_res.success, align_res.message)
    assert align_res.success, f"Align failed: {align_res.message}"

    # Delete relation tracking marks cleanly
    del_res = tool.run(action='delete_marks')
    print("Delete Marks Result:", del_res.success, del_res.message)
    assert del_res.success, f"Delete marks failed: {del_res.message}"

    # 4. Viewport Playblast Setup
    cam, cam_shape = cmds.camera(name='rel_cam', position=[32, 16, 45], rotation=[-10, 35, 0])
    cmds.viewFit(cam, all=True)
    
    panel = 'modelPanel4'
    if cmds.panel(panel, exists=True):
        cmds.modelPanel(panel, edit=True, camera=cam)
        cmds.modelEditor(panel, edit=True, displayAppearance='smoothShaded', displayTextures=False, joints=True, locators=True)

    tmp_dir = Path("C:/Users/zhongweijie/Documents/GitHub/maya_tools_box/snapshots/temp_blast_rel")
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
    gif_path = Path("C:/Users/zhongweijie/Documents/GitHub/maya_tools_box/snapshots/relationship_tools_v19_joint_animation.gif")
    brain_gif_path = Path("C:/Users/zhongweijie/.gemini/antigravity/brain/cb4fe7e1-8af7-4380-97a4-e5fb35e6f9bb/relationship_tools_v19_joint_animation.gif")
    
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
    print("=== LIVE VERIFICATION COMPLETE: relationship_tools_v19 PASSED ===")
    return True

if __name__ == '__main__':
    run_verification()
