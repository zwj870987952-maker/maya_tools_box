# -*- coding: utf-8 -*-
"""Verification script for velocity_calculator in live Maya session."""
import os
import sys
import math
import shutil
import runpy
from pathlib import Path
from PIL import Image

import maya.cmds as cmds

def run_verification():
    print("=== STARTING VELOCITY_CALCULATOR LIVE VERIFICATION ===")

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

    # Frame 10: Sway left & wind up right arm
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

    # Frame 18: Apex Strike (High-speed punch with right wrist)
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

    # 4. Load and Execute VelocityCalculatorTool
    rc_launch = Path(r"C:\Users\zhongweijie\Documents\GitHub\maya_tools_box\tools_staging_pool\01_animation\velocity_calculator\release_candidate\launch_candidate.py")
    tool = runpy.run_path(str(rc_launch))['load_tool']()

    # Step A: Pre-check scene state
    pre_time = cmds.currentTime(query=True)
    pre_keys = cmds.keyframe(r_wrist_jnt, query=True, timeChange=True)

    # Step B: Measure Average Velocity during Strike (Frames 10 -> 18)
    avg_res = tool.run(
        objects=[r_wrist_jnt],
        mode="average",
        start_frame=10,
        end_frame=18
    )
    print(f"average strike measurement: success={avg_res.success}, message={avg_res.message}")
    assert avg_res.success, f"average run failed: {avg_res.errors}"
    meas = avg_res.data['measurements'][0]
    print(f"R_Wrist Strike: Distance = {meas['distance']:.2f} cm, Speed = {meas['speed']:.2f} cm/s, Duration = {avg_res.data['duration_seconds']:.4f} s")
    assert meas['speed'] > 0, "Expected positive speed during strike"
    assert meas['distance'] > 0, "Expected positive displacement during strike"

    # Step C: Measure Instantaneous Velocity at Apex Frame 18 (Backward finite difference: 17.5 -> 18.0)
    inst_res = tool.run(
        objects=[r_wrist_jnt],
        mode="instant",
        frame=18.0,
        sample_step=0.5
    )
    print(f"instant measurement at frame 18: success={inst_res.success}")
    assert inst_res.success, f"instant run failed: {inst_res.errors}"
    inst_meas = inst_res.data['measurements'][0]
    print(f"R_Wrist Instant Speed at F18: {inst_meas['speed']:.2f} cm/s (vector: {[round(x, 2) for x in inst_meas['velocity_vector']]})")
    assert inst_meas['speed'] > 0, "Expected positive instantaneous speed"

    # Step D: Multi-joint simultaneous velocity measurement
    multi_res = tool.run(
        objects=[r_wrist_jnt, l_wrist_jnt, head_jnt, pelvis_jnt],
        mode="average",
        start_frame=1,
        end_frame=18
    )
    assert multi_res.success, f"multi run failed: {multi_res.errors}"
    assert len(multi_res.data['measurements']) == 4, "Expected 4 measurements"
    print("Multi-joint measurement summary:")
    for m in multi_res.data['measurements']:
        j_short = m['object'].split('|')[-1]
        print(f" - {j_short}: speed = {m['speed']:.2f} cm/s, distance = {m['distance']:.2f} cm")

    # Step E: Interactive show_result in live Maya
    ui_msg_res = tool.run(
        objects=[r_wrist_jnt],
        mode="average",
        start_frame=10,
        end_frame=18,
        show_result=True
    )
    assert ui_msg_res.success, f"show_result failed: {ui_msg_res.errors}"
    print("inViewMessage triggered successfully.")

    # Step F: Verify scene state is completely unchanged
    post_time = cmds.currentTime(query=True)
    post_keys = cmds.keyframe(r_wrist_jnt, query=True, timeChange=True)
    assert pre_time == post_time, f"Current time changed! {pre_time} -> {post_time}"
    assert pre_keys == post_keys, f"Keys changed! {pre_keys} -> {post_keys}"
    print("Scene isolation verified: timeline and keyframes were completely untouched.")

    # 5. Viewport Camera & Playblast
    cam_name = "test_vel_cam"
    if cmds.objExists(cam_name):
        cmds.delete(cam_name)
    cam_trans, cam_shape = cmds.camera(name=cam_name)
    cmds.setAttr(cam_trans + ".translate", 22, 16, 36)
    cmds.setAttr(cam_trans + ".rotate", -12, 30, 0)
    cmds.lookThru("modelPanel4", cam_trans)
    cmds.viewFit(cam_trans, all=True)

    cmds.modelEditor("modelPanel4", edit=True, displayAppearance='smoothShaded', displayTextures=False, displayLights='default')

    # 6. Playblast 36 frames
    seq_dir = Path(r"C:\Users\zhongweijie\Documents\GitHub\maya_tools_box\snapshots\velocity_calculator_anim_seq")
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
    gif_path = Path(r"C:\Users\zhongweijie\Documents\GitHub\maya_tools_box\snapshots\velocity_calculator_joint_animation.gif")
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
    brain_gif = brain_dir / "velocity_calculator_joint_animation.gif"
    shutil.copyfile(str(gif_path), str(brain_gif))
    print(f"Copied GIF to brain: {brain_gif}")

    # Copy sequence snapshots to brain
    brain_seq = brain_dir / "snapshots" / "velocity_calculator_anim_seq"
    brain_seq.mkdir(parents=True, exist_ok=True)
    for f in frame_files:
        shutil.copyfile(str(f), str(brain_seq / f.name))

    print("=== LIVE VERIFICATION OF VELOCITY_CALCULATOR COMPLETED SUCCESSFULLY ===")

run_verification()
