# -*- coding: utf-8 -*-
"""Verification script for sword_anim_polishing_tool_v4 in live Maya session."""
import os
import sys
import math
import shutil
import runpy
from pathlib import Path
from PIL import Image

import maya.cmds as cmds
import maya.mel as mel

def run_verification():
    print("=== STARTING SWORD_ANIM_POLISHING_TOOL_V4 LIVE VERIFICATION ===")

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

    # 3. Create Sword Weapon Geometry (Blade + Hilt) attached to Right Wrist
    cmds.select(clear=True)
    sword_grp = cmds.group(empty=True, name="sword_weapon")
    blade = cmds.polyCube(name="sword_blade", width=0.4, height=12, depth=0.8, ch=False)[0]
    cmds.setAttr(blade + ".translate", 0, 6, 0)
    guard = cmds.polyCube(name="sword_guard", width=2.4, height=0.4, depth=1.2, ch=False)[0]
    handle = cmds.polyCylinder(name="sword_handle", radius=0.3, height=3.0, ch=False)[0]
    cmds.setAttr(handle + ".translate", 0, -1.5, 0)
    cmds.parent([blade, guard, handle], sword_grp)
    cmds.setAttr(sword_grp + ".translate", 0, 0, 0)
    cmds.setAttr(sword_grp + ".rotate", 0, 0, 90)
    cmds.makeIdentity(sword_grp, apply=True, translate=True, rotate=True, scale=True)
    cmds.parent(sword_grp, r_wrist_jnt)

    print("Skeleton and Sword weapon initialized.")

    # 4. Animate the skeleton and sword (36 frames dynamic sword slash loop)
    # Frame 1: Combat Ready Stance
    cmds.currentTime(1)
    all_joints = [pelvis_jnt, spine_jnt, chest_jnt, head_jnt,
                  l_shoulder_jnt, l_elbow_jnt, l_wrist_jnt,
                  r_shoulder_jnt, r_elbow_jnt, r_wrist_jnt,
                  l_hip_jnt, l_knee_jnt, l_ankle_jnt,
                  r_hip_jnt, r_knee_jnt, r_ankle_jnt]
    for j in all_joints:
        cmds.setKeyframe(j)
    cmds.setKeyframe(sword_grp)

    # Frame 10: Overhead Windup / Charge
    cmds.currentTime(10)
    cmds.setAttr(pelvis_jnt + ".translate", 0.8, 9.2, -1.0)
    cmds.setAttr(spine_jnt + ".rotate", -10, 25, -5)
    cmds.setAttr(chest_jnt + ".rotate", -5, 20, -5)
    cmds.setAttr(r_shoulder_jnt + ".rotate", 60, 45, -120)
    cmds.setAttr(r_elbow_jnt + ".rotate", 0, -60, 30)
    cmds.setAttr(l_shoulder_jnt + ".rotate", 10, -20, 30)
    cmds.setAttr(l_elbow_jnt + ".rotate", 0, 70, 0)
    cmds.setAttr(l_knee_jnt + ".rotate", 25, 0, 0)
    cmds.setAttr(r_knee_jnt + ".rotate", 35, 0, 0)
    for j in all_joints:
        cmds.setKeyframe(j)
    cmds.setKeyframe(sword_grp)

    # Frame 18: Powerful Diagonal Downward Slash!
    cmds.currentTime(18)
    cmds.setAttr(pelvis_jnt + ".translate", -1.2, 8.8, 3.5)
    cmds.setAttr(spine_jnt + ".rotate", 15, -40, 10)
    cmds.setAttr(chest_jnt + ".rotate", 10, -30, 10)
    cmds.setAttr(r_shoulder_jnt + ".rotate", -40, -45, 60)
    cmds.setAttr(r_elbow_jnt + ".rotate", 0, 15, 0)
    cmds.setAttr(l_shoulder_jnt + ".rotate", -20, 30, -30)
    cmds.setAttr(l_elbow_jnt + ".rotate", 0, -80, 0)
    cmds.setAttr(l_knee_jnt + ".rotate", 45, 0, 0)
    cmds.setAttr(r_knee_jnt + ".rotate", 20, 0, 0)
    for j in all_joints:
        cmds.setKeyframe(j)
    cmds.setKeyframe(sword_grp)

    # Frame 27: Follow-through and Recoil to Parrying Guard
    cmds.currentTime(27)
    cmds.setAttr(pelvis_jnt + ".translate", 0, 9.8, 1.0)
    cmds.setAttr(spine_jnt + ".rotate", 5, 10, 0)
    cmds.setAttr(chest_jnt + ".rotate", 5, 10, 0)
    cmds.setAttr(r_shoulder_jnt + ".rotate", 20, -15, -20)
    cmds.setAttr(r_elbow_jnt + ".rotate", 0, -45, -15)
    cmds.setAttr(l_shoulder_jnt + ".rotate", 15, -10, 20)
    cmds.setAttr(l_elbow_jnt + ".rotate", 0, 40, 0)
    cmds.setAttr(l_knee_jnt + ".rotate", 20, 0, 0)
    cmds.setAttr(r_knee_jnt + ".rotate", 25, 0, 0)
    for j in all_joints:
        cmds.setKeyframe(j)
    cmds.setKeyframe(sword_grp)

    # Frame 36: Return to Ready Stance (Seamless loop)
    cmds.currentTime(36)
    cmds.setAttr(pelvis_jnt + ".translate", 0, 10, 0)
    for j in all_joints:
        cmds.setAttr(j + ".rotate", 0, 0, 0)
        cmds.setKeyframe(j)
    cmds.setKeyframe(sword_grp)

    print("Dynamic 36-frame sword slash animation keyframed.")

    # 5. Load and Execute SwordAnimPolishTool
    rc_launch = Path(r"C:\Users\zhongweijie\Documents\GitHub\maya_tools_box\tools_staging_pool\01_animation\sword_anim_polishing_tool_v4\release_candidate\launch_candidate.py")
    tool = runpy.run_path(str(rc_launch))['load_tool']()

    # Step A: Status Check
    status_res = tool.run(action="status")
    print(f"Status result: success={status_res.success}, procs={status_res.data.get('source_procedures')}")
    assert status_res.success, f"Status failed: {status_res.errors}"

    # Step B: Constraint Weights Check
    cw_res = tool.run(action="constraint_weights", objects=[r_shoulder_jnt, r_elbow_jnt, r_wrist_jnt])
    print(f"Constraint weights result: success={cw_res.success}, weights={cw_res.data.get('weights')}")
    assert cw_res.success, f"Constraint weights failed: {cw_res.errors}"

    # Step C: Begin Sword Setup
    begin_res = tool.run(action="begin_sword", objects=["sword_weapon", r_wrist_jnt], start=1, end=36)
    print(f"begin_sword result: success={begin_res.success}")
    assert begin_res.success, f"begin_sword failed: {begin_res.errors}"
    sid = begin_res.data['session']

    # Step D: Adjust Top and Side locators
    from maya_toolkit.tools.sword_anim_polishing_tool_v4 import runtime
    ledger = runtime.v.Ledger(sid)
    top_locs = runtime.live_group(ledger, 'aim_top')
    side_locs = runtime.live_group(ledger, 'aim_side')
    print(f"Top locators: {top_locs}, Side locators: {side_locs}")
    assert top_locs and side_locs, "Top/Side locators not found"

    # Move top up, side forward to ensure non-collinear axes
    cmds.move(0, 8, 0, top_locs[0], relative=True)
    cmds.move(0, 0, 8, side_locs[0], relative=True)

    # Step E: Finish Setup
    finish_res = tool.run(action="finish_setup", session=sid)
    print(f"finish_setup result: success={finish_res.success}")
    assert finish_res.success, f"finish_setup failed: {finish_res.errors}"

    # Step F: Bake & Euler Filter
    bake_res = tool.run(action="bake", session=sid, objects=["sword_weapon", r_wrist_jnt], start=1, end=36)
    print(f"bake result: success={bake_res.success}")
    assert bake_res.success, f"bake failed: {bake_res.errors}"

    euler_res = tool.run(action="euler_filter", session=sid, objects=["sword_weapon", r_wrist_jnt])
    print(f"euler_filter result: success={euler_res.success}")
    assert euler_res.success, f"euler_filter failed: {euler_res.errors}"

    # Step G: Delete System (clean up helper locators after bake)
    del_res = tool.run(action="delete_system", session=sid)
    print(f"delete_system result: success={del_res.success}")
    assert del_res.success, f"delete_system failed: {del_res.errors}"

    print("SwordAnimPolishTool full workflow verified successfully!")

    # 6. Viewport Camera & Playblast
    cam_name = "test_sword_cam"
    if cmds.objExists(cam_name):
        cmds.delete(cam_name)
    cam_trans, cam_shape = cmds.camera(name=cam_name)
    cmds.setAttr(cam_trans + ".translate", 24, 18, 36)
    cmds.setAttr(cam_trans + ".rotate", -12, 32, 0)
    cmds.lookThru("modelPanel4", cam_trans)
    cmds.viewFit(cam_trans, all=True)

    cmds.modelEditor("modelPanel4", edit=True, displayAppearance='smoothShaded', displayTextures=False, displayLights='default')

    # 7. Playblast 36 frames
    seq_dir = Path(r"C:\Users\zhongweijie\Documents\GitHub\maya_tools_box\snapshots\sword_anim_polishing_tool_v4_anim_seq")
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

    # 8. Assemble GIF
    frame_files = sorted(list(seq_dir.glob("frame.*.png")))
    if not frame_files:
        frame_files = sorted(list(seq_dir.glob("*.png")))
    print(f"Captured {len(frame_files)} frames for GIF.")
    assert len(frame_files) >= 30, f"Too few frames: {len(frame_files)}"

    frames = [Image.open(str(f)) for f in frame_files]
    gif_path = Path(r"C:\Users\zhongweijie\Documents\GitHub\maya_tools_box\snapshots\sword_anim_polishing_tool_v4_joint_animation.gif")
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
    brain_gif = brain_dir / "sword_anim_polishing_tool_v4_joint_animation.gif"
    shutil.copyfile(str(gif_path), str(brain_gif))
    print(f"Copied GIF to brain: {brain_gif}")

    # Copy sequence snapshots to brain
    brain_seq = brain_dir / "snapshots" / "sword_anim_polishing_tool_v4_anim_seq"
    brain_seq.mkdir(parents=True, exist_ok=True)
    for f in frame_files:
        shutil.copyfile(str(f), str(brain_seq / f.name))

    print("=== LIVE VERIFICATION OF SWORD_ANIM_POLISHING_TOOL_V4 COMPLETED SUCCESSFULLY ===")

run_verification()
