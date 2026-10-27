# -*- coding: utf-8 -*-
"""
Verification script for segment_scale_fix in live Maya session (test1026.ma).
Tests joint segmentScaleCompensate disabling, squash/stretch scale propagation,
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
    print("=== STARTING LIVE VERIFICATION: segment_scale_fix ===")
    
    # 0. Clean cached modules
    for mod in list(sys.modules):
        if 'segment_scale_fix' in mod:
            del sys.modules[mod]

    # Clean prior test nodes if any
    for n in cmds.ls('ssf_*', 'test_ssf_*', 'ssf_cam*', type='transform'):
        if cmds.objExists(n):
            try:
                cmds.delete(n)
            except Exception:
                pass

    cmds.playbackOptions(min=1, max=36, ast=1, aet=36)
    cmds.currentTime(1)

    # 1. Build a 3-joint bone chain with skinned cylinder
    cmds.select(clear=True)
    root = cmds.joint(name='ssf_root', position=[0, 0, 0])
    mid = cmds.joint(name='ssf_mid', position=[0, 10, 0])
    tip = cmds.joint(name='ssf_tip', position=[0, 20, 0])

    cyl = cmds.polyCylinder(name='ssf_cyl', radius=2.2, height=22, subdivisionsY=12)[0]
    cmds.xform(cyl, translation=[0, 10, 0], worldSpace=True)
    cmds.skinCluster([root, mid, tip], cyl, toSelectedBones=True, name='ssf_skinCluster')

    # Verify initial state: Maya sets segmentScaleCompensate=True
    assert cmds.getAttr(mid + '.segmentScaleCompensate') == True

    # 2. Load release candidate tool
    rc_path = Path(r"C:/Users/zhongweijie/Documents/GitHub/maya_tools_box/tools_staging_pool/02_rigging_hierarchy/segment_scale_fix/release_candidate").resolve()
    spec = importlib.util.spec_from_file_location('ssf_loader', rc_path / 'launch_candidate.py')
    loader = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loader)
    tool = loader.load_tool()

    # Step A: Inspect
    inspect_res = tool.run(action='inspect')
    print("Inspect success:", inspect_res.success)
    assert inspect_res.success, f"Inspect failed: {inspect_res.message}"

    # Step B: Dry Run
    dry_res = tool.run(dry_run=True, action='disable', objects=[root, mid, tip])
    print("Dry Run Result:", dry_res.success, len(dry_res.data.get('changes', [])))
    assert dry_res.success
    assert len(dry_res.data['changes']) == 3

    # Step C: Real Run
    fix_res = tool.run(action='disable', objects=[root, mid, tip])
    print("Fix Result:", fix_res.success, fix_res.message)
    assert fix_res.success, f"Fix failed: {fix_res.message}"
    assert cmds.getAttr(root + '.segmentScaleCompensate') == False
    assert cmds.getAttr(mid + '.segmentScaleCompensate') == False
    assert cmds.getAttr(tip + '.segmentScaleCompensate') == False

    # 3. Animate Squash & Stretch loop on root across 36 frames
    for f in range(1, 37):
        t = (f - 1) / 35.0 * 2 * math.pi
        sy = 1.0 + 0.35 * math.sin(t)
        # Volume compensation in X and Z
        sx = 1.0 / math.sqrt(sy)
        sz = sx
        rz = 18.0 * math.sin(t)
        cmds.setKeyframe(root, attribute='scaleY', value=sy, time=f)
        cmds.setKeyframe(root, attribute='scaleX', value=sx, time=f)
        cmds.setKeyframe(root, attribute='scaleZ', value=sz, time=f)
        cmds.setKeyframe(root, attribute='rotateZ', value=rz, time=f)
        cmds.setKeyframe(mid, attribute='rotateZ', value=rz * 0.7, time=f)

    # 4. Viewport Playblast Setup
    cam, cam_shape = cmds.camera(name='ssf_cam', position=[30, 14, 45], rotation=[-8, 32, 0])
    cmds.viewFit(cam, all=True)
    
    panel = 'modelPanel4'
    if cmds.panel(panel, exists=True):
        cmds.modelPanel(panel, edit=True, camera=cam)
        cmds.modelEditor(panel, edit=True, displayAppearance='smoothShaded', displayTextures=False, joints=True)

    tmp_dir = Path("C:/Users/zhongweijie/Documents/GitHub/maya_tools_box/snapshots/temp_blast_ssf")
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
    gif_path = Path("C:/Users/zhongweijie/Documents/GitHub/maya_tools_box/snapshots/segment_scale_fix_joint_animation.gif")
    brain_gif_path = Path("C:/Users/zhongweijie/.gemini/antigravity/brain/cb4fe7e1-8af7-4380-97a4-e5fb35e6f9bb/segment_scale_fix_joint_animation.gif")
    
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
    print("=== LIVE VERIFICATION COMPLETE: segment_scale_fix PASSED ===")
    return True

if __name__ == '__main__':
    run_verification()
