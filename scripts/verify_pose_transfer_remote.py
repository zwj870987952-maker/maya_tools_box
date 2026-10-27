# -*- coding: utf-8 -*-
"""Verification script for pose_transfer_remote in live Maya session."""
import os
import sys
import math
import shutil
import runpy
from pathlib import Path
from PIL import Image

import maya.cmds as cmds

def run_verification():
    print("=== STARTING POSE_TRANSFER_REMOTE LIVE VERIFICATION ===")

    # 1. Reset scene
    cmds.file(new=True, force=True)
    cmds.undoInfo(state=True)
    cmds.playbackOptions(min=1, max=36, ast=1, aet=36)
    cmds.currentTime(1)

    # 2. Build Symmetrical Humanoid Skeletal Chain with Rig Controls
    # Clean selection so joints and controls don't accidentally nest
    cmds.select(clear=True)

    # Hierarchy group
    rig_grp = cmds.group(empty=True, name="char_rig")
    ctrls_grp = cmds.group(empty=True, name="char_controls", parent=rig_grp)
    skel_grp = cmds.group(empty=True, name="char_skeleton", parent=rig_grp)

    # Controls
    root_ctrl = cmds.circle(name="char_root_ctrl", normal=(0, 1, 0), radius=3.0, ch=False)[0]
    cmds.setAttr(root_ctrl + ".translate", 0, 10, 0)
    cmds.parent(root_ctrl, ctrls_grp)

    # Spine chain controls
    spine1_ctrl = cmds.circle(name="char_spine1_ctrl", normal=(0, 1, 0), radius=2.5, ch=False)[0]
    cmds.setAttr(spine1_ctrl + ".translate", 0, 13, 0)
    cmds.parent(spine1_ctrl, root_ctrl)

    chest_ctrl = cmds.circle(name="char_chest_ctrl", normal=(0, 1, 0), radius=2.8, ch=False)[0]
    cmds.setAttr(chest_ctrl + ".translate", 0, 16, 0)
    cmds.parent(chest_ctrl, spine1_ctrl)

    head_ctrl = cmds.circle(name="char_head_ctrl", normal=(0, 1, 0), radius=1.8, ch=False)[0]
    cmds.setAttr(head_ctrl + ".translate", 0, 20, 0)
    cmds.parent(head_ctrl, chest_ctrl)

    # Left Arm controls
    l_shoulder_ctrl = cmds.circle(name="char_L_shoulder_ctrl", normal=(1, 0, 0), radius=1.5, ch=False)[0]
    cmds.setAttr(l_shoulder_ctrl + ".translate", 3, 16, 0)
    cmds.parent(l_shoulder_ctrl, chest_ctrl)

    l_elbow_ctrl = cmds.circle(name="char_L_elbow_ctrl", normal=(1, 0, 0), radius=1.3, ch=False)[0]
    cmds.setAttr(l_elbow_ctrl + ".translate", 7, 16, -1)
    cmds.parent(l_elbow_ctrl, l_shoulder_ctrl)

    l_wrist_ctrl = cmds.circle(name="char_L_wrist_ctrl", normal=(1, 0, 0), radius=1.0, ch=False)[0]
    cmds.setAttr(l_wrist_ctrl + ".translate", 11, 16, 0)
    cmds.parent(l_wrist_ctrl, l_elbow_ctrl)

    # Right Arm controls (Symmetrical)
    r_shoulder_ctrl = cmds.circle(name="char_R_shoulder_ctrl", normal=(1, 0, 0), radius=1.5, ch=False)[0]
    cmds.setAttr(r_shoulder_ctrl + ".translate", -3, 16, 0)
    cmds.parent(r_shoulder_ctrl, chest_ctrl)

    r_elbow_ctrl = cmds.circle(name="char_R_elbow_ctrl", normal=(1, 0, 0), radius=1.3, ch=False)[0]
    cmds.setAttr(r_elbow_ctrl + ".translate", -7, 16, -1)
    cmds.parent(r_elbow_ctrl, r_shoulder_ctrl)

    r_wrist_ctrl = cmds.circle(name="char_R_wrist_ctrl", normal=(1, 0, 0), radius=1.0, ch=False)[0]
    cmds.setAttr(r_wrist_ctrl + ".translate", -11, 16, 0)
    cmds.parent(r_wrist_ctrl, r_elbow_ctrl)

    # Left Leg controls
    l_hip_ctrl = cmds.circle(name="char_L_hip_ctrl", normal=(1, 0, 0), radius=1.4, ch=False)[0]
    cmds.setAttr(l_hip_ctrl + ".translate", 2, 9, 0)
    cmds.parent(l_hip_ctrl, root_ctrl)

    l_knee_ctrl = cmds.circle(name="char_L_knee_ctrl", normal=(1, 0, 0), radius=1.2, ch=False)[0]
    cmds.setAttr(l_knee_ctrl + ".translate", 2, 5, 1)
    cmds.parent(l_knee_ctrl, l_hip_ctrl)

    l_ankle_ctrl = cmds.circle(name="char_L_ankle_ctrl", normal=(0, 1, 0), radius=1.2, ch=False)[0]
    cmds.setAttr(l_ankle_ctrl + ".translate", 2, 1, 0)
    cmds.parent(l_ankle_ctrl, l_knee_ctrl)

    # Right Leg controls (Symmetrical)
    r_hip_ctrl = cmds.circle(name="char_R_hip_ctrl", normal=(1, 0, 0), radius=1.4, ch=False)[0]
    cmds.setAttr(r_hip_ctrl + ".translate", -2, 9, 0)
    cmds.parent(r_hip_ctrl, root_ctrl)

    r_knee_ctrl = cmds.circle(name="char_R_knee_ctrl", normal=(1, 0, 0), radius=1.2, ch=False)[0]
    cmds.setAttr(r_knee_ctrl + ".translate", -2, 5, 1)
    cmds.parent(r_knee_ctrl, r_hip_ctrl)

    r_ankle_ctrl = cmds.circle(name="char_R_ankle_ctrl", normal=(0, 1, 0), radius=1.2, ch=False)[0]
    cmds.setAttr(r_ankle_ctrl + ".translate", -2, 1, 0)
    cmds.parent(r_ankle_ctrl, r_knee_ctrl)

    # Now create Symmetrical Skeletal Chain in skel_grp
    cmds.select(clear=True)
    root_jnt = cmds.joint(name="char_pelvis_jnt", position=(0, 10, 0))
    cmds.parent(root_jnt, skel_grp)
    cmds.parentConstraint(root_ctrl, root_jnt, mo=True)

    cmds.select(root_jnt)
    spine1_jnt = cmds.joint(name="char_spine1_jnt", position=(0, 13, 0))
    cmds.parentConstraint(spine1_ctrl, spine1_jnt, mo=True)

    chest_jnt = cmds.joint(name="char_chest_jnt", position=(0, 16, 0))
    cmds.parentConstraint(chest_ctrl, chest_jnt, mo=True)

    head_jnt = cmds.joint(name="char_head_jnt", position=(0, 20, 0))
    cmds.parentConstraint(head_ctrl, head_jnt, mo=True)

    # Left Arm Joints
    cmds.select(chest_jnt)
    l_shoulder_jnt = cmds.joint(name="char_L_shoulder_jnt", position=(3, 16, 0))
    cmds.parentConstraint(l_shoulder_ctrl, l_shoulder_jnt, mo=True)

    l_elbow_jnt = cmds.joint(name="char_L_elbow_jnt", position=(7, 16, -1))
    cmds.parentConstraint(l_elbow_ctrl, l_elbow_jnt, mo=True)

    l_wrist_jnt = cmds.joint(name="char_L_wrist_jnt", position=(11, 16, 0))
    cmds.parentConstraint(l_wrist_ctrl, l_wrist_jnt, mo=True)

    # Right Arm Joints
    cmds.select(chest_jnt)
    r_shoulder_jnt = cmds.joint(name="char_R_shoulder_jnt", position=(-3, 16, 0))
    cmds.parentConstraint(r_shoulder_ctrl, r_shoulder_jnt, mo=True)

    r_elbow_jnt = cmds.joint(name="char_R_elbow_jnt", position=(-7, 16, -1))
    cmds.parentConstraint(r_elbow_ctrl, r_elbow_jnt, mo=True)

    r_wrist_jnt = cmds.joint(name="char_R_wrist_jnt", position=(-11, 16, 0))
    cmds.parentConstraint(r_wrist_ctrl, r_wrist_jnt, mo=True)

    # Left Leg Joints
    cmds.select(root_jnt)
    l_hip_jnt = cmds.joint(name="char_L_hip_jnt", position=(2, 9, 0))
    cmds.parentConstraint(l_hip_ctrl, l_hip_jnt, mo=True)

    l_knee_jnt = cmds.joint(name="char_L_knee_jnt", position=(2, 5, 1))
    cmds.parentConstraint(l_knee_ctrl, l_knee_jnt, mo=True)

    l_ankle_jnt = cmds.joint(name="char_L_ankle_jnt", position=(2, 1, 0))
    cmds.parentConstraint(l_ankle_ctrl, l_ankle_jnt, mo=True)

    # Right Leg Joints
    cmds.select(root_jnt)
    r_hip_jnt = cmds.joint(name="char_R_hip_jnt", position=(-2, 9, 0))
    cmds.parentConstraint(r_hip_ctrl, r_hip_jnt, mo=True)

    r_knee_jnt = cmds.joint(name="char_R_knee_jnt", position=(-2, 5, 1))
    cmds.parentConstraint(r_knee_ctrl, r_knee_jnt, mo=True)

    r_ankle_jnt = cmds.joint(name="char_R_ankle_jnt", position=(-2, 1, 0))
    cmds.parentConstraint(r_ankle_ctrl, r_ankle_jnt, mo=True)

    cmds.select(clear=True)

    # Set joint display size for clear viewport observation
    for j in cmds.ls(type="joint"):
        cmds.setAttr(j + ".radius", 0.8)

    print("Symmetrical skeletal rig initialized.")

    # 3. Load PoseTransferRemoteTool
    rc_launch = Path(r"C:\Users\zhongweijie\Documents\GitHub\maya_tools_box\tools_staging_pool\01_animation\pose_transfer_remote\release_candidate\launch_candidate.py")
    tool = runpy.run_path(str(rc_launch))['load_tool']()

    # Pose 1: Martial arts stance
    cmds.setAttr(l_shoulder_ctrl + ".rotate", 25, 40, -15)
    cmds.setAttr(l_elbow_ctrl + ".rotate", 0, 60, 20)
    cmds.setAttr(r_shoulder_ctrl + ".rotate", -15, -30, 25)
    cmds.setAttr(r_elbow_ctrl + ".rotate", 0, -45, -15)
    cmds.setAttr(chest_ctrl + ".rotate", 5, 15, 0)
    cmds.setAttr(l_knee_ctrl + ".rotate", 20, 0, 0)
    cmds.setAttr(r_knee_ctrl + ".rotate", 15, 0, 0)

    # 4. Step 1: Detect controllers under root
    detect_res = tool.run(action="detect", root=root_ctrl)
    print(f"Detect result: success={detect_res.success}, count={len(detect_res.data.get('controllers', []))}")
    assert detect_res.success, f"Detect failed: {detect_res.errors}"
    detected_ctrls = detect_res.data['controllers']
    assert len(detected_ctrls) >= 10, f"Expected at least 10 controllers, got {len(detected_ctrls)}"

    # 5. Step 2: Capture pose into locators
    cap_res = tool.run(action="capture", root=root_ctrl, controllers=detected_ctrls)
    print(f"Capture result: success={cap_res.success}, locators={len(cap_res.data.get('locators', []))}")
    assert cap_res.success, f"Capture failed: {cap_res.errors}"
    locators = cap_res.data['locators']
    assert len(locators) == len(detected_ctrls), "Locators count mismatch"

    # Store captured wrist world position
    wrist_world_before = cmds.xform(l_wrist_ctrl, q=True, ws=True, t=True)

    # 6. Step 3: Shift root to new location
    cmds.setAttr(root_ctrl + ".translate", 12, 10, 8)
    shift_res = tool.run(action="shift")
    print(f"Shift result: success={shift_res.success}")
    assert shift_res.success, f"Shift failed: {shift_res.errors}"

    # 7. Step 4: Mess up the pose to verify apply
    cmds.setAttr(l_shoulder_ctrl + ".rotate", 0, 0, 0)
    cmds.setAttr(l_elbow_ctrl + ".rotate", 0, 0, 0)
    cmds.setAttr(r_shoulder_ctrl + ".rotate", 0, 0, 0)
    cmds.setAttr(r_elbow_ctrl + ".rotate", 0, 0, 0)

    # 8. Step 5: Apply pose from locators
    apply_res = tool.run(action="apply")
    print(f"Apply result: success={apply_res.success}")
    assert apply_res.success, f"Apply failed: {apply_res.errors}"

    # Check wrist world position: should be wrist_world_before + offset (12, 0, 8)
    wrist_world_after = cmds.xform(l_wrist_ctrl, q=True, ws=True, t=True)
    expected_wrist = [wrist_world_before[0] + 12.0, wrist_world_before[1], wrist_world_before[2] + 8.0]
    diff = sum((wrist_world_after[i] - expected_wrist[i])**2 for i in range(3))**0.5
    print(f"Pose transfer accuracy: diff = {diff:.6e}")
    assert diff < 1e-3, f"Pose transfer error too large: {diff}"

    # 9. Step 6: Test Undo and Redo
    wrist_world_after = cmds.xform(l_wrist_ctrl, q=True, ws=True, t=True)
    print("Undo queue before undo:", cmds.undoInfo(q=True, undoName=True))
    cmds.undo()
    print("Redo queue after undo:", cmds.undoInfo(q=True, redoName=True))
    wrist_world_undo = cmds.xform(l_wrist_ctrl, q=True, ws=True, t=True)
    undo_diff = sum((wrist_world_undo[i] - wrist_world_after[i])**2 for i in range(3))**0.5
    print(f"After Undo, wrist world pos diff = {undo_diff:.4f}")
    assert undo_diff > 0.5, "Undo did not revert wrist position"

    cmds.redo()
    print("Undo queue after redo:", cmds.undoInfo(q=True, undoName=True))
    wrist_world_redo = cmds.xform(l_wrist_ctrl, q=True, ws=True, t=True)
    redo_diff = sum((wrist_world_redo[i] - wrist_world_after[i])**2 for i in range(3))**0.5
    print(f"After Redo, wrist world pos diff = {redo_diff:.6e}, after={wrist_world_after}, redo={wrist_world_redo}")

    # 10. Step 7: Cleanup locators
    clean_res = tool.run(action="cleanup")
    print(f"Cleanup result: success={clean_res.success}")
    assert clean_res.success, f"Cleanup failed: {clean_res.errors}"
    assert all(not cmds.objExists(loc) for loc in locators), "Locators still exist after cleanup"

    # Reset root back to origin
    cmds.setAttr(root_ctrl + ".translate", 0, 10, 0)

    # 11. Animate the humanoid skeleton for 36 frames dynamic loop
    print("Keyframing dynamic 36-frame looping animation...")
    # Frame 1: Stance
    cmds.currentTime(1)
    for c in detected_ctrls:
        cmds.setKeyframe(c)

    # Frame 10: Swing left arm punch forward, twist torso, bend knees
    cmds.currentTime(10)
    cmds.setAttr(root_ctrl + ".translate", 1.5, 9.2, 2.0)
    cmds.setAttr(chest_ctrl + ".rotate", 10, -25, 5)
    cmds.setAttr(l_shoulder_ctrl + ".rotate", 15, -45, 80)
    cmds.setAttr(l_elbow_ctrl + ".rotate", 0, 15, 0)
    cmds.setAttr(r_shoulder_ctrl + ".rotate", -20, 30, -30)
    cmds.setAttr(r_elbow_ctrl + ".rotate", 0, -90, -10)
    cmds.setAttr(l_knee_ctrl + ".rotate", 35, 0, 0)
    cmds.setAttr(r_knee_ctrl + ".rotate", 25, 0, 0)
    for c in detected_ctrls:
        cmds.setKeyframe(c)

    # Frame 19: High block right arm, recoil left arm, shift weight right
    cmds.currentTime(19)
    cmds.setAttr(root_ctrl + ".translate", -1.5, 9.5, -1.0)
    cmds.setAttr(chest_ctrl + ".rotate", -5, 30, -5)
    cmds.setAttr(r_shoulder_ctrl + ".rotate", 45, 30, -110)
    cmds.setAttr(r_elbow_ctrl + ".rotate", 0, -30, 20)
    cmds.setAttr(l_shoulder_ctrl + ".rotate", -10, -20, 20)
    cmds.setAttr(l_elbow_ctrl + ".rotate", 0, 80, 10)
    cmds.setAttr(l_knee_ctrl + ".rotate", 15, 0, 0)
    cmds.setAttr(r_knee_ctrl + ".rotate", 40, 0, 0)
    for c in detected_ctrls:
        cmds.setKeyframe(c)

    # Frame 28: Spin & kick stance
    cmds.currentTime(28)
    cmds.setAttr(root_ctrl + ".translate", 0, 10.2, 0)
    cmds.setAttr(chest_ctrl + ".rotate", 0, -10, 0)
    cmds.setAttr(l_shoulder_ctrl + ".rotate", 20, 20, 45)
    cmds.setAttr(r_shoulder_ctrl + ".rotate", 20, -20, -45)
    cmds.setAttr(l_knee_ctrl + ".rotate", 25, 0, 0)
    cmds.setAttr(r_knee_ctrl + ".rotate", 20, 0, 0)
    for c in detected_ctrls:
        cmds.setKeyframe(c)

    # Frame 36: Return to start pose for seamless loop
    cmds.currentTime(36)
    cmds.setAttr(root_ctrl + ".translate", 0, 10, 0)
    cmds.setAttr(l_shoulder_ctrl + ".rotate", 25, 40, -15)
    cmds.setAttr(l_elbow_ctrl + ".rotate", 0, 60, 20)
    cmds.setAttr(r_shoulder_ctrl + ".rotate", -15, -30, 25)
    cmds.setAttr(r_elbow_ctrl + ".rotate", 0, -45, -15)
    cmds.setAttr(chest_ctrl + ".rotate", 5, 15, 0)
    cmds.setAttr(l_knee_ctrl + ".rotate", 20, 0, 0)
    cmds.setAttr(r_knee_ctrl + ".rotate", 15, 0, 0)
    for c in detected_ctrls:
        cmds.setKeyframe(c)

    # 12. Setup Viewport Camera
    cam_name = "test_pose_transfer_cam"
    if cmds.objExists(cam_name):
        cmds.delete(cam_name)
    cam_trans, cam_shape = cmds.camera(name=cam_name)
    cmds.setAttr(cam_trans + ".translate", 18, 14, 34)
    cmds.setAttr(cam_trans + ".rotate", -12, 28, 0)
    cmds.lookThru("modelPanel4", cam_trans)
    cmds.viewFit(cam_trans, all=True)

    # Viewport settings: smooth shading, no lights/materials needed, wireframe on shaded or shaded
    cmds.modelEditor("modelPanel4", edit=True, displayAppearance='smoothShaded', displayTextures=False, displayLights='default')

    # 13. Playblast 36 frames
    seq_dir = Path(r"C:\Users\zhongweijie\Documents\GitHub\maya_tools_box\snapshots\pose_transfer_remote_anim_seq")
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

    # 14. Assemble GIF
    frame_files = sorted(list(seq_dir.glob("frame.*.png")))
    if not frame_files:
        frame_files = sorted(list(seq_dir.glob("*.png")))
    print(f"Captured {len(frame_files)} frames for GIF.")
    assert len(frame_files) >= 30, f"Too few frames captured: {len(frame_files)}"

    frames = [Image.open(str(f)) for f in frame_files]
    gif_path = Path(r"C:\Users\zhongweijie\Documents\GitHub\maya_tools_box\snapshots\pose_transfer_remote_joint_animation.gif")
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
    brain_gif = brain_dir / "pose_transfer_remote_joint_animation.gif"
    shutil.copyfile(str(gif_path), str(brain_gif))
    print(f"Copied GIF to brain: {brain_gif}")

    # Also copy sequence snapshots to brain
    brain_seq = brain_dir / "snapshots" / "pose_transfer_remote_anim_seq"
    brain_seq.mkdir(parents=True, exist_ok=True)
    for f in frame_files:
        shutil.copyfile(str(f), str(brain_seq / f.name))

    print("=== LIVE VERIFICATION OF POSE_TRANSFER_REMOTE COMPLETED SUCCESSFULLY ===")

run_verification()
