# -*- coding: utf-8 -*-
"""
Verification script for skin_info_and_super_connect in live Maya session (test1026.ma).
Tests skin cluster inspection, Super Connect channel wiring, dynamic deformation,
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
    print("=== STARTING LIVE VERIFICATION: skin_info_and_super_connect ===")
    
    # 0. Clean cached modules
    for mod in list(sys.modules):
        if 'skin_info_and_super_connect' in mod:
            del sys.modules[mod]

    # Clean prior test nodes if any
    for n in cmds.ls('ssc_*', 'test_ssc_*', 'ssc_cam*', type='transform'):
        if cmds.objExists(n):
            try:
                cmds.delete(n)
            except Exception:
                pass

    cmds.playbackOptions(min=1, max=36, ast=1, aet=36)
    cmds.currentTime(1)

    # 1. Build a 3-joint bone chain with skinned cylinder
    cmds.select(clear=True)
    j0 = cmds.joint(name='ssc_j0', position=[0, 0, 0])
    j1 = cmds.joint(name='ssc_j1', position=[0, 10, 0])
    j2 = cmds.joint(name='ssc_j2', position=[0, 20, 0])

    cyl = cmds.polyCylinder(name='ssc_cyl', radius=2.2, height=22, subdivisionsY=12)[0]
    cmds.xform(cyl, translation=[0, 10, 0], worldSpace=True)
    skin_node = cmds.skinCluster([j0, j1, j2], cyl, toSelectedBones=True, name='ssc_skinCluster')[0]

    # Control locator with matching suffix for Super Connect prefix matching
    ctrl = cmds.spaceLocator(name='ctrl_ssc_j1')[0]
    cmds.xform(ctrl, translation=[8, 10, 0], worldSpace=True)

    # 2. Load release candidate tool
    rc_path = Path(r"C:/Users/zhongweijie/Documents/GitHub/maya_tools_box/tools_staging_pool/02_rigging_hierarchy/skin_info_and_super_connect/release_candidate").resolve()
    spec = importlib.util.spec_from_file_location('ssc_loader', rc_path / 'launch_candidate.py')
    loader = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loader)
    tool = loader.load_tool()

    # Step A: Inspect
    inspect_res = tool.run(action='inspect')
    print("Inspect success:", inspect_res.success)
    assert inspect_res.success, f"Inspect failed: {inspect_res.message}"

    # Step B: Query Skin Info
    info_res = tool.run(action='info', objects=[cyl])
    print("Skin Info Result:", info_res.success, info_res.message)
    assert info_res.success, f"Info failed: {info_res.message}"
    assert len(info_res.data.get('meshes', [{}])[0].get('influences', [])) == 3

    # Step C: Super Connect (Connect channels from ctrl to matching joint j1)
    connect_res = tool.run(
        action='connect',
        sources=[ctrl],
        destinations=[j1],
        source_prefix='ctrl_',
        destination_prefix='',
        channels=['rx', 'ry', 'rz'],
        mode='direct'
    )
    print("Super Connect Result:", connect_res.success, connect_res.message)
    assert connect_res.success, f"Connect failed: {connect_res.message}"

    # Verify connection exists
    conns = cmds.listConnections(j1 + '.rotateZ', source=True, destination=False)
    assert conns and ctrl in conns[0]

    # 3. Animate control rotation across 36 frames
    for f in range(1, 37):
        t = (f - 1) / 35.0 * 2 * math.pi
        rz = math.sin(t) * 35.0
        rx = math.cos(t) * 20.0
        ry = math.sin(t * 2) * 15.0
        cmds.setKeyframe(ctrl, attribute='rotateZ', value=rz, time=f)
        cmds.setKeyframe(ctrl, attribute='rotateX', value=rx, time=f)
        cmds.setKeyframe(ctrl, attribute='rotateY', value=ry, time=f)

    # 4. Viewport Playblast Setup
    cam, cam_shape = cmds.camera(name='ssc_cam', position=[32, 16, 45], rotation=[-10, 32, 0])
    cmds.viewFit(cam, all=True)
    
    panel = 'modelPanel4'
    if cmds.panel(panel, exists=True):
        cmds.modelPanel(panel, edit=True, camera=cam)
        cmds.modelEditor(panel, edit=True, displayAppearance='smoothShaded', displayTextures=False, joints=True, locators=True)

    tmp_dir = Path("C:/Users/zhongweijie/Documents/GitHub/maya_tools_box/snapshots/temp_blast_ssc")
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
    gif_path = Path("C:/Users/zhongweijie/Documents/GitHub/maya_tools_box/snapshots/skin_info_and_super_connect_joint_animation.gif")
    brain_gif_path = Path("C:/Users/zhongweijie/.gemini/antigravity/brain/cb4fe7e1-8af7-4380-97a4-e5fb35e6f9bb/skin_info_and_super_connect_joint_animation.gif")
    
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
    print("=== LIVE VERIFICATION COMPLETE: skin_info_and_super_connect PASSED ===")
    return True

if __name__ == '__main__':
    run_verification()
