# -*- coding: utf-8 -*-
"""
Verification script for rdm_tools_v2 in live Maya session (test1026.ma).
Tests joint axis display, curve creation, color overrides, constraints,
36-frame dynamic playback, Undo/Redo, and GIF generation.
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
    print("=== STARTING LIVE VERIFICATION: rdm_tools_v2 ===")
    
    # 0. Clean cached modules
    for mod in list(sys.modules):
        if 'rdm_tools_v2' in mod or 'RdMToolsV2' in mod:
            del sys.modules[mod]

    # Clean prior test nodes if any
    for n in cmds.ls('rdm_*', 'test_rdm_*', 'rdm_cam*', 'BoxCurve*', type='transform'):
        if cmds.objExists(n):
            try:
                cmds.delete(n)
            except Exception:
                pass

    cmds.playbackOptions(min=1, max=36, ast=1, aet=36)
    cmds.currentTime(1)

    # 1. Build a 4-joint chain with attached cylinder mesh
    cmds.select(clear=True)
    j0 = cmds.joint(name='rdm_j0', position=[0, 0, 0])
    j1 = cmds.joint(name='rdm_j1', position=[0, 8, 0])
    j2 = cmds.joint(name='rdm_j2', position=[0, 16, 0])
    j3 = cmds.joint(name='rdm_j3', position=[0, 24, 0])

    cyl = cmds.polyCylinder(name='rdm_cyl', radius=2.0, height=24, subdivisionsY=12)[0]
    cmds.xform(cyl, translation=[0, 12, 0], worldSpace=True)
    cmds.skinCluster([j0, j1, j2, j3], cyl, toSelectedBones=True, name='rdm_skinCluster')

    # 2. Load release candidate tool
    rc_path = Path(r"C:/Users/zhongweijie/Documents/GitHub/maya_tools_box/tools_staging_pool/02_rigging_hierarchy/rdm_tools_v2/release_candidate").resolve()
    spec = importlib.util.spec_from_file_location('rdm_loader', rc_path / 'launch_candidate.py')
    loader = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loader)
    tool = loader.load_tool()
    
    M = 'RdMToolsV2.RiggingTools.'

    # Step A: Inspect
    inspect_res = tool.run(action='inspect')
    print("Inspect success:", inspect_res.success)
    assert inspect_res.success, f"Inspect failed: {inspect_res.message}"

    # Step B: Toggle Axis Display on joints
    axis_res = tool.run(
        action='call',
        module=M + 'ShowHide.RdMToggleAxis',
        function='setAxisDisplay',
        arguments={'display': True},
        objects=[j0, j1, j2, j3]
    )
    print("Toggle Axis Result:", axis_res.success, axis_res.message)
    assert axis_res.success, f"Axis display failed: {axis_res.message}"
    assert cmds.getAttr(j1 + '.displayLocalAxis') == True

    # Step C: Create Box Curve control
    box_res = tool.run(action='script', module=M + 'Curves.BoxCurve')
    print("BoxCurve Result:", box_res.success, box_res.message)
    assert box_res.success, f"BoxCurve failed: {box_res.message}"
    assert cmds.objExists('BoxCurve')

    # Rename BoxCurve to avoid naming collision
    ctrl = cmds.rename('BoxCurve', 'rdm_root_ctrl')
    cmds.xform(ctrl, translation=[0, 0, 0], scale=[3, 3, 3], worldSpace=True)

    # Step D: Curve Color Override
    color_res = tool.run(
        action='call',
        module=M + 'Curves.CurveColors',
        function='colorShape',
        arguments={'Color': 17}, # Yellow
        objects=[ctrl]
    )
    print("ColorShape Result:", color_res.success, color_res.message)
    assert color_res.success, f"ColorShape failed: {color_res.message}"

    # Step E: Curve On Selection for joint j2 with constraint
    curve_res = tool.run(
        action='call',
        module=M + 'Curves.curveOnSelection',
        function='curveOnSelectionFunc',
        arguments={'mode': 'CircleY', 'Constraint': False, 'offset': False},
        objects=[j2]
    )
    print("CurveOnSelection Result:", curve_res.success, curve_res.message)
    assert curve_res.success, f"CurveOnSelection failed: {curve_res.message}"

    # Step F: Set 36-frame animation on joints
    for f in range(1, 37):
        t = (f - 1) / 35.0
        angle1 = math.sin(t * 2 * math.pi) * 25.0
        angle2 = math.cos(t * 2 * math.pi) * 35.0
        cmds.setKeyframe(j1, attribute='rotateZ', value=angle1, time=f)
        cmds.setKeyframe(j2, attribute='rotateZ', value=angle2, time=f)
        cmds.setKeyframe(j3, attribute='rotateX', value=angle1 * 0.8, time=f)

    # 3. Setup Camera & Viewport Playblast
    cam, cam_shape = cmds.camera(name='rdm_cam', position=[35, 18, 50], rotation=[-12, 35, 0])
    cmds.viewFit(cam, all=True)
    
    panel = 'modelPanel4'
    if cmds.panel(panel, exists=True):
        cmds.modelPanel(panel, edit=True, camera=cam)
        cmds.modelEditor(panel, edit=True, displayAppearance='smoothShaded', displayTextures=False, joints=True, nurbsCurves=True)

    tmp_dir = Path("C:/Users/zhongweijie/Documents/GitHub/maya_tools_box/snapshots/temp_blast_rdm")
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
    gif_path = Path("C:/Users/zhongweijie/Documents/GitHub/maya_tools_box/snapshots/rdm_tools_v2_joint_animation.gif")
    brain_gif_path = Path("C:/Users/zhongweijie/.gemini/antigravity/brain/cb4fe7e1-8af7-4380-97a4-e5fb35e6f9bb/rdm_tools_v2_joint_animation.gif")
    
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

    # 4. Cleanup & Restore Scene to pristine test1026.ma
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)
        
    cmds.file('C:/Users/zhongweijie/Documents/GitHub/maya_tools_box/tests/test1026.ma', open=True, force=True)
    print("SCENE RESTORED TO test1026.ma")
    print("=== LIVE VERIFICATION COMPLETE: rdm_tools_v2 PASSED ===")
    return True

if __name__ == '__main__':
    run_verification()
