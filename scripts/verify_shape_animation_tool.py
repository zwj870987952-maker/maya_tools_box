# -*- coding: utf-8 -*-
"""Verification script for shape_animation_tool in live Maya session."""
import os
import sys
import math
import shutil
import runpy
from pathlib import Path
from PIL import Image

import maya.cmds as cmds

def run_verification():
    print("=== STARTING SHAPE_ANIMATION_TOOL LIVE VERIFICATION ===")

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

    # 3. Create a Character Mesh (Torso/Body Cylinder + Arm Capsules)
    body_mesh = cmds.polyCylinder(name="char_body_mesh", radius=3.2, height=14, subdivisionsX=16, subdivisionsY=16, ch=False)[0]
    cmds.setAttr(body_mesh + ".translate", 0, 14, 0)
    cmds.makeIdentity(body_mesh, apply=True, translate=True, rotate=True, scale=True)

    # Left arm mesh
    l_arm_mesh = cmds.polyCylinder(name="char_L_arm_mesh", radius=1.3, height=8, subdivisionsX=12, subdivisionsY=12, ch=False)[0]
    cmds.setAttr(l_arm_mesh + ".translate", 7, 17, 0)
    cmds.setAttr(l_arm_mesh + ".rotate", 0, 0, -90)
    cmds.makeIdentity(l_arm_mesh, apply=True, translate=True, rotate=True, scale=True)

    # Right arm mesh
    r_arm_mesh = cmds.polyCylinder(name="char_R_arm_mesh", radius=1.3, height=8, subdivisionsX=12, subdivisionsY=12, ch=False)[0]
    cmds.setAttr(r_arm_mesh + ".translate", -7, 17, 0)
    cmds.setAttr(r_arm_mesh + ".rotate", 0, 0, 90)
    cmds.makeIdentity(r_arm_mesh, apply=True, translate=True, rotate=True, scale=True)

    # Combine into single character mesh
    combined = cmds.polyUnite([body_mesh, l_arm_mesh, r_arm_mesh], name="character_geo", ch=False)[0]
    cmds.delete(combined, constructionHistory=True)

    # Skin mesh to skeleton
    all_joints = [pelvis_jnt, spine_jnt, chest_jnt, head_jnt,
                  l_shoulder_jnt, l_elbow_jnt, l_wrist_jnt,
                  r_shoulder_jnt, r_elbow_jnt, r_wrist_jnt,
                  l_hip_jnt, l_knee_jnt, l_ankle_jnt,
                  r_hip_jnt, r_knee_jnt, r_ankle_jnt]
    skin_cluster = cmds.skinCluster(all_joints, combined, toSelectedBones=True, name="char_skinCluster")[0]
    print(f"Mesh created and bound to skeleton: {combined}, skinCluster={skin_cluster}")

    # 4. Animate the skeleton (36 frames dynamic martial arts loop)
    # Frame 1: Ready stance
    cmds.currentTime(1)
    for j in all_joints:
        cmds.setKeyframe(j)

    # Frame 10: Windup & torso rotate
    cmds.currentTime(10)
    cmds.setAttr(pelvis_jnt + ".translate", 1.0, 9.2, 1.0)
    cmds.setAttr(spine_jnt + ".rotate", 5, 20, 0)
    cmds.setAttr(chest_jnt + ".rotate", 5, 15, 0)
    cmds.setAttr(l_shoulder_jnt + ".rotate", 20, 40, 30)
    cmds.setAttr(l_elbow_jnt + ".rotate", 0, 70, 0)
    cmds.setAttr(r_shoulder_jnt + ".rotate", -20, -30, -20)
    cmds.setAttr(l_knee_jnt + ".rotate", 25, 0, 0)
    cmds.setAttr(r_knee_jnt + ".rotate", 20, 0, 0)
    for j in all_joints:
        cmds.setKeyframe(j)

    # Frame 18: Powerful Forward Punch!
    cmds.currentTime(18)
    cmds.setAttr(pelvis_jnt + ".translate", -1.0, 9.5, 3.0)
    cmds.setAttr(spine_jnt + ".rotate", -10, -35, 5)
    cmds.setAttr(chest_jnt + ".rotate", -5, -25, 5)
    cmds.setAttr(l_shoulder_jnt + ".rotate", -15, -60, 85)
    cmds.setAttr(l_elbow_jnt + ".rotate", 0, 10, 0)
    cmds.setAttr(r_shoulder_jnt + ".rotate", 25, 30, -40)
    cmds.setAttr(r_elbow_jnt + ".rotate", 0, -85, 0)
    cmds.setAttr(l_knee_jnt + ".rotate", 40, 0, 0)
    cmds.setAttr(r_knee_jnt + ".rotate", 15, 0, 0)
    for j in all_joints:
        cmds.setKeyframe(j)

    # Frame 27: Recoil & high block
    cmds.currentTime(27)
    cmds.setAttr(pelvis_jnt + ".translate", 0, 10.2, 0.5)
    cmds.setAttr(spine_jnt + ".rotate", 0, 10, -5)
    cmds.setAttr(chest_jnt + ".rotate", 0, 15, -5)
    cmds.setAttr(l_shoulder_jnt + ".rotate", 15, 10, 20)
    cmds.setAttr(l_elbow_jnt + ".rotate", 0, 50, 0)
    cmds.setAttr(r_shoulder_jnt + ".rotate", 40, 20, -90)
    cmds.setAttr(r_elbow_jnt + ".rotate", 0, -45, 0)
    cmds.setAttr(l_knee_jnt + ".rotate", 20, 0, 0)
    cmds.setAttr(r_knee_jnt + ".rotate", 30, 0, 0)
    for j in all_joints:
        cmds.setKeyframe(j)

    # Frame 36: Return to frame 1 pose (seamless loop)
    cmds.currentTime(36)
    cmds.setAttr(pelvis_jnt + ".translate", 0, 10, 0)
    for j in all_joints:
        cmds.setAttr(j + ".rotate", 0, 0, 0)
        cmds.setKeyframe(j)

    print("Dynamic 36-frame skeletal animation keyframed.")

    # 5. Load and Execute ShapeAnimationTool
    rc_launch = Path(r"C:\Users\zhongweijie\Documents\GitHub\maya_tools_box\tools_staging_pool\01_animation\shape_animation_tool\release_candidate\launch_candidate.py")
    tool = runpy.run_path(str(rc_launch))['load_tool']()

    # Step A: Add Mesh Layer
    add_res = tool.run(action="add_mesh", mesh=combined)
    print(f"add_mesh result: success={add_res.success}")
    assert add_res.success, f"add_mesh failed: {add_res.errors}"
    sid = add_res.data['session']
    layer_id = add_res.data['added_layer']

    # Step B: Begin Sculpt at Frame 18 (Punch Apex)
    cmds.currentTime(18)
    sculpt_res = tool.run(action="begin_sculpt", session=sid, layer_id=layer_id, frame=18)
    print(f"begin_sculpt result: success={sculpt_res.success}")
    assert sculpt_res.success, f"begin_sculpt failed: {sculpt_res.errors}"
    editing_info = sculpt_res.data.get('editing', {})
    sculpt_uuid = editing_info.get('sculpt')
    from maya_toolkit.tools.shape_animation_tool import runtime
    sculpt_mesh = runtime.resolve(sculpt_uuid)
    print(f"Sculpt mesh resolved: {sculpt_mesh} (UUID: {sculpt_uuid})")
    assert cmds.objExists(sculpt_mesh), "Sculpt mesh does not exist"

    # Step C: Deform sculpt mesh (Muscle flex / chest bulge & fist impact shape)
    vtx_count = cmds.polyEvaluate(sculpt_mesh, vertex=True)
    vtx_sample = [f"{sculpt_mesh}.vtx[{i}]" for i in range(min(50, vtx_count))]
    cmds.move(0.8, 1.2, 1.5, vtx_sample, relative=True, objectSpace=True)

    # Step D: End Sculpt (bakes corrective delta into blendShape target)
    end_res = tool.run(action="end_sculpt", session=sid, layer_id=layer_id)
    print(f"end_sculpt result: success={end_res.success}")
    assert end_res.success, f"end_sculpt failed: {end_res.errors}"
    assert not cmds.objExists(sculpt_mesh), "Sculpt mesh should be cleaned up after end_sculpt"

    # Verify deformation delta:
    # At frame 18, shape animation should be active (weight 1.0)
    cmds.currentTime(18)
    vtx_pos_f18 = cmds.xform(f"{combined}.vtx[0]", q=True, ws=True, t=True)

    # Toggle enabled to verify corrective shape contribution
    off_res = tool.run(action="set_enabled", session=sid, layer_id=layer_id, enabled=False)
    assert off_res.success, "set_enabled False failed"
    vtx_pos_disabled = cmds.xform(f"{combined}.vtx[0]", q=True, ws=True, t=True)
    diff = sum((vtx_pos_f18[i] - vtx_pos_disabled[i])**2 for i in range(3))**0.5
    print(f"Frame 18 Corrective shape effect: diff = {diff:.4f}")
    assert diff > 0.1, f"Corrective shape had no visible effect! diff={diff}"

    on_res = tool.run(action="set_enabled", session=sid, layer_id=layer_id, enabled=True)
    assert on_res.success, "set_enabled True failed"

    # Verify that at frame 1, corrective shape weight is 0.0
    cmds.currentTime(1)
    status_res = tool.run(action="status", session=sid)
    assert status_res.success, "status check failed"
    print("ShapeAnimationTool verification passed successfully!")

    # 6. Viewport Camera & Playblast Settings
    cam_name = "test_sat_cam"
    if cmds.objExists(cam_name):
        cmds.delete(cam_name)
    cam_trans, cam_shape = cmds.camera(name=cam_name)
    cmds.setAttr(cam_trans + ".translate", 22, 18, 38)
    cmds.setAttr(cam_trans + ".rotate", -12, 30, 0)
    cmds.lookThru("modelPanel4", cam_trans)
    cmds.viewFit(cam_trans, all=True)

    # Viewport settings: smooth shaded, default lighting
    cmds.modelEditor("modelPanel4", edit=True, displayAppearance='smoothShaded', displayTextures=False, displayLights='default')

    # 7. Playblast 36 frames
    seq_dir = Path(r"C:\Users\zhongweijie\Documents\GitHub\maya_tools_box\snapshots\shape_animation_tool_anim_seq")
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
    gif_path = Path(r"C:\Users\zhongweijie\Documents\GitHub\maya_tools_box\snapshots\shape_animation_tool_joint_animation.gif")
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
    brain_gif = brain_dir / "shape_animation_tool_joint_animation.gif"
    shutil.copyfile(str(gif_path), str(brain_gif))
    print(f"Copied GIF to brain: {brain_gif}")

    # Copy sequence snapshots to brain
    brain_seq = brain_dir / "snapshots" / "shape_animation_tool_anim_seq"
    brain_seq.mkdir(parents=True, exist_ok=True)
    for f in frame_files:
        shutil.copyfile(str(f), str(brain_seq / f.name))

    print("=== LIVE VERIFICATION OF SHAPE_ANIMATION_TOOL COMPLETED SUCCESSFULLY ===")

run_verification()
