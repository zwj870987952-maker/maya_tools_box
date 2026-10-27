# -*- coding: utf-8 -*-
"""Verification script for timeline_enhanced in live Maya session."""
import os
import sys
import math
import shutil
import runpy
import tempfile
from pathlib import Path
from PIL import Image

import maya.cmds as cmds

def run_verification():
    print("=== STARTING TIMELINE_ENHANCED LIVE VERIFICATION ===")

    # 1. Reset scene
    cmds.file(new=True, force=True)
    cmds.undoInfo(state=True)
    cmds.playbackOptions(min=1, max=36, ast=1, aet=36)
    cmds.currentTime(1)

    # 2. Build Symmetrical Humanoid Skeletal Chain
    cmds.select(clear=True)
    skel_grp = cmds.group(empty=True, name="char_skeleton")
    cmds.select(clear=True)

    # Pelvis & Spine
    pelvis_jnt = cmds.joint(name="char_pelvis_jnt", position=(0, 10, 0))
    cmds.parent(pelvis_jnt, skel_grp)
    spine_jnt = cmds.joint(name="char_spine_jnt", position=(0, 14, 0))
    chest_jnt = cmds.joint(name="char_chest_jnt", position=(0, 17, 0))
    head_jnt = cmds.joint(name="char_head_jnt", position=(0, 21, 0))

    # Left Arm
    cmds.select(chest_jnt)
    l_shoulder_jnt = cmds.joint(name="char_L_shoulder_jnt", position=(3, 17, 0))
    l_elbow_jnt = cmds.joint(name="char_L_elbow_jnt", position=(7, 17, -0.5))
    l_wrist_jnt = cmds.joint(name="char_L_wrist_jnt", position=(11, 17, 0))

    # Right Arm (Symmetrical)
    cmds.select(chest_jnt)
    r_shoulder_jnt = cmds.joint(name="char_R_shoulder_jnt", position=(-3, 17, 0))
    r_elbow_jnt = cmds.joint(name="char_R_elbow_jnt", position=(-7, 17, -0.5))
    r_wrist_jnt = cmds.joint(name="char_R_wrist_jnt", position=(-11, 17, 0))

    # Left Leg
    cmds.select(pelvis_jnt)
    l_hip_jnt = cmds.joint(name="char_L_hip_jnt", position=(2, 9, 0))
    l_knee_jnt = cmds.joint(name="char_L_knee_jnt", position=(2, 5, 0.5))
    l_ankle_jnt = cmds.joint(name="char_L_ankle_jnt", position=(2, 1, 0))

    # Right Leg (Symmetrical)
    cmds.select(pelvis_jnt)
    r_hip_jnt = cmds.joint(name="char_R_hip_jnt", position=(-2, 9, 0))
    r_knee_jnt = cmds.joint(name="char_R_knee_jnt", position=(-2, 5, 0.5))
    r_ankle_jnt = cmds.joint(name="char_R_ankle_jnt", position=(-2, 1, 0))

    for j in cmds.ls(type="joint"):
        cmds.setAttr(j + ".radius", 0.9)

    print("Symmetrical skeleton initialized.")

    # 3. Animate the skeleton (36 frames dynamic martial arts loop)
    # Frame 1: Ready Stance
    cmds.currentTime(1)
    all_joints = [pelvis_jnt, spine_jnt, chest_jnt, head_jnt,
                  l_shoulder_jnt, l_elbow_jnt, l_wrist_jnt,
                  r_shoulder_jnt, r_elbow_jnt, r_wrist_jnt,
                  l_hip_jnt, l_knee_jnt, l_ankle_jnt,
                  r_hip_jnt, r_knee_jnt, r_ankle_jnt]
    for j in all_joints:
        cmds.setKeyframe(j)

    # Frame 10: Sway left & raise arms
    cmds.currentTime(10)
    cmds.setAttr(pelvis_jnt + ".translate", 1.2, 9.4, 0.5)
    cmds.setAttr(spine_jnt + ".rotate", 0, 15, -5)
    cmds.setAttr(chest_jnt + ".rotate", 5, 10, -5)
    cmds.setAttr(l_shoulder_jnt + ".rotate", 25, 45, 40)
    cmds.setAttr(l_elbow_jnt + ".rotate", 0, 60, 0)
    cmds.setAttr(r_shoulder_jnt + ".rotate", -20, -30, -20)
    cmds.setAttr(r_elbow_jnt + ".rotate", 0, -50, 0)
    cmds.setAttr(l_knee_jnt + ".rotate", 25, 0, 0)
    cmds.setAttr(r_knee_jnt + ".rotate", 15, 0, 0)
    for j in all_joints:
        cmds.setKeyframe(j)

    # Frame 18: Strike Pose & Twist
    cmds.currentTime(18)
    cmds.setAttr(pelvis_jnt + ".translate", -1.0, 9.0, 2.5)
    cmds.setAttr(spine_jnt + ".rotate", -5, -30, 5)
    cmds.setAttr(chest_jnt + ".rotate", -5, -20, 5)
    cmds.setAttr(l_shoulder_jnt + ".rotate", -10, -50, 80)
    cmds.setAttr(l_elbow_jnt + ".rotate", 0, 10, 0)
    cmds.setAttr(r_shoulder_jnt + ".rotate", 30, 25, -50)
    cmds.setAttr(r_elbow_jnt + ".rotate", 0, -80, 0)
    cmds.setAttr(l_knee_jnt + ".rotate", 40, 0, 0)
    cmds.setAttr(r_knee_jnt + ".rotate", 20, 0, 0)
    for j in all_joints:
        cmds.setKeyframe(j)

    # Frame 27: Recoil & Block
    cmds.currentTime(27)
    cmds.setAttr(pelvis_jnt + ".translate", 0, 10.2, -0.5)
    cmds.setAttr(spine_jnt + ".rotate", 5, 10, 0)
    cmds.setAttr(chest_jnt + ".rotate", 5, 10, 0)
    cmds.setAttr(l_shoulder_jnt + ".rotate", 20, 20, 25)
    cmds.setAttr(l_elbow_jnt + ".rotate", 0, 45, 0)
    cmds.setAttr(r_shoulder_jnt + ".rotate", 45, 20, -100)
    cmds.setAttr(r_elbow_jnt + ".rotate", 0, -30, 0)
    cmds.setAttr(l_knee_jnt + ".rotate", 15, 0, 0)
    cmds.setAttr(r_knee_jnt + ".rotate", 35, 0, 0)
    for j in all_joints:
        cmds.setKeyframe(j)

    # Frame 36: Return to Ready Stance
    cmds.currentTime(36)
    cmds.setAttr(pelvis_jnt + ".translate", 0, 10, 0)
    for j in all_joints:
        cmds.setAttr(j + ".rotate", 0, 0, 0)
        cmds.setKeyframe(j)

    print("Dynamic 36-frame skeletal animation keyframed.")

    # 4. Load and Execute TimelineEnhancedTool
    rc_launch = Path(r"C:\Users\zhongweijie\Documents\GitHub\maya_tools_box\tools_staging_pool\01_animation\timeline_enhanced\release_candidate\launch_candidate.py")
    tool = runpy.run_path(str(rc_launch))['load_tool']()

    # Step A: Pre-inspect keyframes on skeleton
    pre_keys = cmds.keyframe(pelvis_jnt, query=True, timeChange=True)
    print(f"Pre-keys on pelvis: {pre_keys}")

    # Step B: Sync with Maya timeline
    sync_res = tool.run(action="sync")
    print(f"sync result: success={sync_res.success}, start={sync_res.data['state']['start_frame']}, count={sync_res.data['state']['frame_count']}")
    assert sync_res.success, f"sync failed: {sync_res.errors}"
    assert sync_res.data['state']['start_frame'] == 1, "Expected start_frame 1"
    assert sync_res.data['state']['frame_count'] == 36, "Expected frame_count 36"
    state = sync_res.data['state']

    # Step C: Add planning blocks at dynamic key frames
    # Frame 1: Ready (keyframe style)
    res1 = tool.run(action="add", state=state, frame=1, block_type="keyframe", block={"label": "Ready", "color": [1.0, 0.3, 0.3], "name": "Contact"})
    assert res1.success, f"add frame 1 failed: {res1.errors}"
    state = res1.data['state']

    # Frame 10: Anticipate (breakdown style)
    res10 = tool.run(action="add", state=state, frame=10, block_type="breakdown", block={"label": "Anticipate", "color": [0.3, 1.0, 0.3], "name": "Windup"})
    assert res10.success, f"add frame 10 failed: {res10.errors}"
    state = res10.data['state']

    # Frame 18: Strike (effect style)
    res18 = tool.run(action="add", state=state, frame=18, block_type="effect", block={"label": "Strike", "color": [0.8, 0.0, 0.8], "name": "Apex"})
    assert res18.success, f"add frame 18 failed: {res18.errors}"
    state = res18.data['state']

    # Frame 27: Block (hold style)
    res27 = tool.run(action="add", state=state, frame=27, block_type="hold", block={"label": "Block", "color": [1.0, 1.0, 0.3], "name": "Recovery"})
    assert res27.success, f"add frame 27 failed: {res27.errors}"
    state = res27.data['state']

    # Frame 36: Loop (camera style)
    res36 = tool.run(action="add", state=state, frame=36, block_type="camera", block={"label": "Loop", "color": [1.0, 0.6, 0.0], "name": "Return"})
    assert res36.success, f"add frame 36 failed: {res36.errors}"
    state = res36.data['state']

    print(f"Added 5 planning blocks: {list(state['blocks'].keys())}")
    assert len(state['blocks']) == 5, f"Expected 5 blocks, got {len(state['blocks'])}"

    # Step D: Test Selection, Copy & Paste
    sel_res = tool.run(action="select", state=state, frames=[10, 18])
    assert sel_res.success, f"select failed: {sel_res.errors}"
    state = sel_res.data['state']
    assert set(state['selected']) == {10, 18}

    copy_res = tool.run(action="copy", state=state)
    assert copy_res.success, f"copy failed: {copy_res.errors}"
    state = copy_res.data['state']
    assert len(state['clipboard']) == 2

    # Paste at frame 20 (anticipate copied from 10 to 20, strike copied from 18 to 28)
    paste_res = tool.run(action="paste", state=state, frame=20, overwrite=True)
    assert paste_res.success, f"paste failed: {paste_res.errors}"
    print(f"Pasted blocks at frames: {list(paste_res.data['state']['blocks'].keys())}")

    # Step E: Test set_current_frame
    time_res = tool.run(action="set_current_frame", frame=18)
    assert time_res.success, f"set_current_frame failed: {time_res.errors}"
    assert cmds.currentTime(query=True) == 18, f"Expected Maya time 18, got {cmds.currentTime(query=True)}"
    print("set_current_frame(18) verified on live timeline.")

    # Step F: Test JSON Save & Load
    with tempfile.TemporaryDirectory() as tmp_dir:
        json_path = Path(tmp_dir) / "timeline_plan.json"
        save_res = tool.run(action="save", state=state, path=str(json_path))
        assert save_res.success, f"save failed: {save_res.errors}"
        assert json_path.exists(), "Saved JSON file missing"

        load_res = tool.run(action="load", path=str(json_path))
        assert load_res.success, f"load failed: {load_res.errors}"
        loaded_state = load_res.data['state']
        assert loaded_state['blocks'].keys() == state['blocks'].keys(), "Loaded blocks mismatch"
        print("JSON document persistence verified.")

    # Step G: Verify Scene Keys Untouched
    post_keys = cmds.keyframe(pelvis_jnt, query=True, timeChange=True)
    assert pre_keys == post_keys, f"Scene keys were modified by timeline tool! {pre_keys} vs {post_keys}"
    print("Scene keyframe isolation confirmed (planning blocks are memory/JSON only).")

    # 5. Viewport Camera & Playblast
    cam_name = "test_timeline_cam"
    if cmds.objExists(cam_name):
        cmds.delete(cam_name)
    cam_trans, cam_shape = cmds.camera(name=cam_name)
    cmds.setAttr(cam_trans + ".translate", 22, 16, 36)
    cmds.setAttr(cam_trans + ".rotate", -12, 30, 0)
    cmds.lookThru("modelPanel4", cam_trans)
    cmds.viewFit(cam_trans, all=True)

    cmds.modelEditor("modelPanel4", edit=True, displayAppearance='smoothShaded', displayTextures=False, displayLights='default')

    # 6. Playblast 36 frames
    seq_dir = Path(r"C:\Users\zhongweijie\Documents\GitHub\maya_tools_box\snapshots\timeline_enhanced_anim_seq")
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

    # 7. Assemble GIF
    frame_files = sorted(list(seq_dir.glob("frame.*.png")))
    if not frame_files:
        frame_files = sorted(list(seq_dir.glob("*.png")))
    print(f"Captured {len(frame_files)} frames for GIF.")
    assert len(frame_files) >= 30, f"Too few frames: {len(frame_files)}"

    frames = [Image.open(str(f)) for f in frame_files]
    gif_path = Path(r"C:\Users\zhongweijie\Documents\GitHub\maya_tools_box\snapshots\timeline_enhanced_joint_animation.gif")
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
    brain_dir = Path(r"C:\Users\zhongweijie\.gemini\antigravity\brain\f8152522-dcb3-4911-9254-38b4c32bd26d")
    brain_gif = brain_dir / "timeline_enhanced_joint_animation.gif"
    shutil.copyfile(str(gif_path), str(brain_gif))
    print(f"Copied GIF to brain: {brain_gif}")

    # Copy sequence snapshots to brain
    brain_seq = brain_dir / "snapshots" / "timeline_enhanced_anim_seq"
    brain_seq.mkdir(parents=True, exist_ok=True)
    for f in frame_files:
        shutil.copyfile(str(f), str(brain_seq / f.name))

    print("=== LIVE VERIFICATION OF TIMELINE_ENHANCED COMPLETED SUCCESSFULLY ===")

run_verification()
