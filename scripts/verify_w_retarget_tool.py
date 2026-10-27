# -*- coding: utf-8 -*-
"""Verification script for w_retarget_tool in live Maya session."""
import os
import sys
import math
import shutil
import runpy
import tempfile
from pathlib import Path
from PIL import Image

import maya.cmds as cmds

def build_skeleton(prefix, offset_x=0.0):
    cmds.select(clear=True)
    skel_grp = cmds.group(empty=True, name=f"{prefix}_grp")
    cmds.setAttr(f"{skel_grp}.translateX", offset_x)
    cmds.select(clear=True)

    # Pelvis & Spine
    pelvis = cmds.joint(name=f"{prefix}_pelvis_jnt", position=(offset_x, 10, 0))
    cmds.parent(pelvis, skel_grp)
    spine = cmds.joint(name=f"{prefix}_spine_jnt", position=(offset_x, 14, 0))
    chest = cmds.joint(name=f"{prefix}_chest_jnt", position=(offset_x, 17, 0))
    head = cmds.joint(name=f"{prefix}_head_jnt", position=(offset_x, 21, 0))

    # Left Arm
    cmds.select(chest)
    l_shoulder = cmds.joint(name=f"{prefix}_L_shoulder_jnt", position=(offset_x + 3, 17, 0))
    l_elbow = cmds.joint(name=f"{prefix}_L_elbow_jnt", position=(offset_x + 7, 17, -0.5))
    l_wrist = cmds.joint(name=f"{prefix}_L_wrist_jnt", position=(offset_x + 11, 17, 0))

    # Right Arm (Symmetrical)
    cmds.select(chest)
    r_shoulder = cmds.joint(name=f"{prefix}_R_shoulder_jnt", position=(offset_x - 3, 17, 0))
    r_elbow = cmds.joint(name=f"{prefix}_R_elbow_jnt", position=(offset_x - 7, 17, -0.5))
    r_wrist = cmds.joint(name=f"{prefix}_R_wrist_jnt", position=(offset_x - 11, 17, 0))

    # Left Leg
    cmds.select(pelvis)
    l_hip = cmds.joint(name=f"{prefix}_L_hip_jnt", position=(offset_x + 2, 9, 0))
    l_knee = cmds.joint(name=f"{prefix}_L_knee_jnt", position=(offset_x + 2, 5, 0.5))
    l_ankle = cmds.joint(name=f"{prefix}_L_ankle_jnt", position=(offset_x + 2, 1, 0))

    # Right Leg (Symmetrical)
    cmds.select(pelvis)
    r_hip = cmds.joint(name=f"{prefix}_R_hip_jnt", position=(offset_x - 2, 9, 0))
    r_knee = cmds.joint(name=f"{prefix}_R_knee_jnt", position=(offset_x - 2, 5, 0.5))
    r_ankle = cmds.joint(name=f"{prefix}_R_ankle_jnt", position=(offset_x - 2, 1, 0))

    for j in cmds.ls(f"{prefix}_*jnt", type="joint"):
        cmds.setAttr(j + ".radius", 0.9)

    return {
        "grp": skel_grp,
        "pelvis": pelvis,
        "spine": spine,
        "chest": chest,
        "head": head,
        "l_shoulder": l_shoulder,
        "l_elbow": l_elbow,
        "l_wrist": l_wrist,
        "r_shoulder": r_shoulder,
        "r_elbow": r_elbow,
        "r_wrist": r_wrist,
        "l_hip": l_hip,
        "l_knee": l_knee,
        "l_ankle": l_ankle,
        "r_hip": r_hip,
        "r_knee": r_knee,
        "r_ankle": r_ankle,
    }

def run_verification():
    print("=== STARTING W_RETARGET_TOOL LIVE VERIFICATION ===")

    # 1. Reset scene
    cmds.file(new=True, force=True)
    cmds.undoInfo(state=True)
    cmds.playbackOptions(min=1, max=36, ast=1, aet=36)
    cmds.currentTime(1)

    if not cmds.pluginInfo('fbxmaya', query=True, loaded=True):
        cmds.loadPlugin('fbxmaya', quiet=True)

    # 2. Build Source and Target Skeletons (Side-by-side)
    src = build_skeleton("src", offset_x=-10.0)
    tgt = build_skeleton("tgt", offset_x=10.0)
    print("Source (X=-10) and Target (X=+10) skeletons initialized.")

    # 3. Animate Source Skeleton (36 frames dynamic martial arts loop)
    all_src = [src["pelvis"], src["spine"], src["chest"], src["head"],
               src["l_shoulder"], src["l_elbow"], src["l_wrist"],
               src["r_shoulder"], src["r_elbow"], src["r_wrist"],
               src["l_hip"], src["l_knee"], src["l_ankle"],
               src["r_hip"], src["r_knee"], src["r_ankle"]]

    # Frame 1: Ready Stance
    cmds.currentTime(1)
    for j in all_src:
        cmds.setKeyframe(j)

    # Frame 10: Sway left & windup
    cmds.currentTime(10)
    cmds.setAttr(src["pelvis"] + ".translate", -10.0 + 1.2, 9.4, 0.5)
    cmds.setAttr(src["spine"] + ".rotate", 0, 15, -5)
    cmds.setAttr(src["chest"] + ".rotate", 5, 10, -5)
    cmds.setAttr(src["l_shoulder"] + ".rotate", 25, 45, 40)
    cmds.setAttr(src["l_elbow"] + ".rotate", 0, 60, 0)
    cmds.setAttr(src["r_shoulder"] + ".rotate", -20, -30, -20)
    cmds.setAttr(src["r_elbow"] + ".rotate", 0, -50, 0)
    cmds.setAttr(src["l_knee"] + ".rotate", 25, 0, 0)
    cmds.setAttr(src["r_knee"] + ".rotate", 15, 0, 0)
    for j in all_src:
        cmds.setKeyframe(j)

    # Frame 18: Apex Strike
    cmds.currentTime(18)
    cmds.setAttr(src["pelvis"] + ".translate", -10.0 - 1.0, 9.0, 2.5)
    cmds.setAttr(src["spine"] + ".rotate", -5, -30, 5)
    cmds.setAttr(src["chest"] + ".rotate", -5, -20, 5)
    cmds.setAttr(src["l_shoulder"] + ".rotate", -10, -50, 80)
    cmds.setAttr(src["l_elbow"] + ".rotate", 0, 10, 0)
    cmds.setAttr(src["r_shoulder"] + ".rotate", 30, 25, -50)
    cmds.setAttr(src["r_elbow"] + ".rotate", 0, -80, 0)
    cmds.setAttr(src["l_knee"] + ".rotate", 40, 0, 0)
    cmds.setAttr(src["r_knee"] + ".rotate", 20, 0, 0)
    for j in all_src:
        cmds.setKeyframe(j)

    # Frame 27: Recoil & Block
    cmds.currentTime(27)
    cmds.setAttr(src["pelvis"] + ".translate", -10.0, 10.2, -0.5)
    cmds.setAttr(src["spine"] + ".rotate", 5, 10, 0)
    cmds.setAttr(src["chest"] + ".rotate", 5, 10, 0)
    cmds.setAttr(src["l_shoulder"] + ".rotate", 20, 20, 25)
    cmds.setAttr(src["l_elbow"] + ".rotate", 0, 45, 0)
    cmds.setAttr(src["r_shoulder"] + ".rotate", 45, 20, -100)
    cmds.setAttr(src["r_elbow"] + ".rotate", 0, -30, 0)
    cmds.setAttr(src["l_knee"] + ".rotate", 15, 0, 0)
    cmds.setAttr(src["r_knee"] + ".rotate", 35, 0, 0)
    for j in all_src:
        cmds.setKeyframe(j)

    # Frame 36: Return to Ready Stance
    cmds.currentTime(36)
    cmds.setAttr(src["pelvis"] + ".translate", -10.0, 10, 0)
    for j in all_src:
        cmds.setAttr(j + ".rotate", 0, 0, 0)
        cmds.setKeyframe(j)

    print("Dynamic 36-frame skeletal animation keyframed on source.")

    # 4. Load WRetargetTool
    rc_launch = Path(r"C:\Users\zhongweijie\Documents\GitHub\maya_tools_box\tools_staging_pool\01_animation\w_retarget_tool\release_candidate\launch_candidate.py")
    tool = runpy.run_path(str(rc_launch))['load_tool']()

    # Step A: Perform retarget in independent DAG batches (Frames 1 to 37 exclusive -> 1..36)
    batches = [
        # Pass 1: Pelvis
        [{"source": src["pelvis"], "target": tgt["pelvis"]}],
        # Pass 2: Spine
        [{"source": src["spine"], "target": tgt["spine"]}],
        # Pass 3: Chest
        [{"source": src["chest"], "target": tgt["chest"]}],
        # Pass 4: Head
        [{"source": src["head"], "target": tgt["head"]}],
        # Pass 5: Shoulders & Hips (independent sibling transforms)
        [
            {"source": src["l_shoulder"], "target": tgt["l_shoulder"]},
            {"source": src["r_shoulder"], "target": tgt["r_shoulder"]},
            {"source": src["l_hip"], "target": tgt["l_hip"]},
            {"source": src["r_hip"], "target": tgt["r_hip"]},
        ],
        # Pass 6: Elbows & Knees (independent sibling transforms)
        [
            {"source": src["l_elbow"], "target": tgt["l_elbow"]},
            {"source": src["r_elbow"], "target": tgt["r_elbow"]},
            {"source": src["l_knee"], "target": tgt["l_knee"]},
            {"source": src["r_knee"], "target": tgt["r_knee"]},
        ],
        # Pass 7: Wrists & Ankles (independent sibling transforms)
        [
            {"source": src["l_wrist"], "target": tgt["l_wrist"]},
            {"source": src["r_wrist"], "target": tgt["r_wrist"]},
            {"source": src["l_ankle"], "target": tgt["l_ankle"]},
            {"source": src["r_ankle"], "target": tgt["r_ankle"]},
        ],
    ]

    for idx, batch_pairs in enumerate(batches, 1):
        # Validate dry-run first
        dry = tool.run(dry_run=True, pairs=batch_pairs, start_frame=1, end_frame=37)
        assert dry.success, f"Dry run pass {idx} failed: {dry.errors}"

        # Execute retarget
        res = tool.run(pairs=batch_pairs, start_frame=1, end_frame=37)
        assert res.success, f"Execute retarget pass {idx} failed: {res.errors}"
        print(f"Retarget Pass {idx}/7 complete: {[p['target'].split('_')[1] for p in batch_pairs]}")

    # Check helpers cleaned up
    assert cmds.ls('wRetarget_*') == [], f"Helper nodes left in scene: {cmds.ls('wRetarget_*')}"

    # Verify target has animation
    tgt_keys = cmds.keyframe(tgt["r_wrist"], attribute="tx", query=True, timeChange=True)
    print(f"Retargeted keys count on tgt_r_wrist: {len(tgt_keys)}")
    assert len(tgt_keys) == 36, f"Expected 36 frames of keys, got {len(tgt_keys)}"

    # Step B: Test FBX Export
    with tempfile.TemporaryDirectory() as tmp_dir:
        fbx_path = Path(tmp_dir) / "retargeted_char.fbx"
        exp_res = tool.run(
            action="export",
            exports=[{"nodes": [tgt["grp"]], "path": str(fbx_path)}],
            start_frame=1,
            end_frame=37,
            up_axis="y",
            ascii=True
        )
        print(f"FBX Export result: success={exp_res.success}")
        assert exp_res.success, f"FBX export failed: {exp_res.errors}"
        assert fbx_path.exists(), "Exported FBX file does not exist"
        assert fbx_path.stat().st_size > 0, "Exported FBX file is empty"
        print(f"Exported FBX size: {fbx_path.stat().st_size} bytes")

    # 5. Viewport Camera & Playblast
    cam_name = "test_retarget_cam"
    if cmds.objExists(cam_name):
        cmds.delete(cam_name)
    cam_trans, cam_shape = cmds.camera(name=cam_name)
    cmds.setAttr(cam_trans + ".translate", 0, 16, 50)
    cmds.setAttr(cam_trans + ".rotate", -8, 0, 0)
    cmds.lookThru("modelPanel4", cam_trans)
    cmds.viewFit(cam_trans, all=True)

    cmds.modelEditor("modelPanel4", edit=True, displayAppearance='smoothShaded', displayTextures=False, displayLights='default')

    # 6. Playblast 36 frames
    seq_dir = Path(r"C:\Users\zhongweijie\Documents\GitHub\maya_tools_box\snapshots\w_retarget_tool_anim_seq")
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
    gif_path = Path(r"C:\Users\zhongweijie\Documents\GitHub\maya_tools_box\snapshots\w_retarget_tool_joint_animation.gif")
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
    brain_gif = brain_dir / "w_retarget_tool_joint_animation.gif"
    shutil.copyfile(str(gif_path), str(brain_gif))
    print(f"Copied GIF to brain: {brain_gif}")

    # Copy sequence snapshots to brain
    brain_seq = brain_dir / "snapshots" / "w_retarget_tool_anim_seq"
    brain_seq.mkdir(parents=True, exist_ok=True)
    for f in frame_files:
        shutil.copyfile(str(f), str(brain_seq / f.name))

    print("=== LIVE VERIFICATION OF W_RETARGET_TOOL COMPLETED SUCCESSFULLY ===")

run_verification()
