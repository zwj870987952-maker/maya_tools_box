"""Verification script for cvwrap_weightdriver in live Maya instance."""
import os
import sys
from pathlib import Path
from PIL import Image

repo_root = "C:/Users/zhongweijie/Documents/GitHub/maya_tools_box"
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

def run_verification():
    import maya.cmds as cmds
    import runpy

    # 1. 确认场景锁定
    sn = cmds.file(q=True, sn=True)
    if 'test1026.ma' not in sn:
        raise RuntimeError(f"Scene not pinned to test1026.ma: {sn}")

    # 2. 加载候选工具
    candidate_path = Path(repo_root) / "tools_staging_pool/03_transforms_modeling/cvwrap_weightdriver/release_candidate/launch_candidate.py"
    if candidate_path.is_file():
        tool = runpy.run_path(str(candidate_path))['load_tool']()
    else:
        from maya_toolkit.tools.cvwrap_weightdriver import CvWrapWeightDriverTool
        tool = CvWrapWeightDriverTool()

    print(f"Loaded tool: {tool.tool_id} (version: {tool.version})")

    # 3. 业务操作验证
    # 状态查询与环境依赖预检 (只读)
    status_res = tool.run(action='status', dry_run=True)
    if not status_res.success:
        raise RuntimeError(f"Status validation failed: {status_res.message}")
    print("Status validation OK:", status_res.data)

    # 验证 MEL 模块可用性
    import maya.mel as mel
    mel_paths = list(Path(repo_root).glob("tools_staging_pool/03_transforms_modeling/cvwrap_weightdriver/release_candidate/maya_toolkit/tools/cvwrap_weightdriver/native/*.mel"))
    for mp in mel_paths:
        mel.eval(f'source "{mp.as_posix()}";')
    exists_rbf = mel.eval('exists weightDriverEditRBF')
    exists_ae = mel.eval('exists AEcvWrapTemplate')
    print(f"MEL Procedures verified: weightDriverEditRBF={exists_rbf}, AEcvWrapTemplate={exists_ae}")

    # 4. 动态变形与骨骼关节视口拍屏 (36 帧 24fps)
    start_frame = 1
    end_frame = 36
    cmds.playbackOptions(min=start_frame, max=end_frame, ast=start_frame, aet=end_frame)
    cmds.currentTime(start_frame)

    # 寻找受测骨骼节点 (如 spine_01 或任意现有 joint)
    joints = cmds.ls(type='joint')
    target_joint = None
    orig_rot = (0.0, 0.0, 0.0)
    if joints:
        for j in joints:
            if 'spine' in j.lower() or 'root' in j.lower() or 'hip' in j.lower():
                target_joint = j
                break
        if not target_joint:
            target_joint = joints[0]

    if target_joint:
        orig_rot = cmds.getAttr(f"{target_joint}.rotate")[0]
        # 设置动态周期变形关键帧 (36 帧正弦波)
        import math
        for f in range(start_frame, end_frame + 1):
            phase = (f - 1) / (end_frame - start_frame) * 2 * math.pi
            rx = orig_rot[0] + 15.0 * math.sin(phase)
            rz = orig_rot[2] + 20.0 * math.cos(phase)
            cmds.setKeyframe(target_joint, attribute='rotateX', time=f, value=rx)
            cmds.setKeyframe(target_joint, attribute='rotateZ', time=f, value=rz)

    # 对焦整体网格与骨骼
    meshes = cmds.ls(type='mesh')
    if meshes:
        parents = cmds.listRelatives(meshes[0], parent=True, fullPath=True)
        if parents:
            cmds.select(parents[0])
            cmds.viewFit('persp', animate=False)

    temp_dir = Path("C:/Users/zhongweijie/AppData/Local/Temp/cvwrap_pb").resolve()
    temp_dir.mkdir(parents=True, exist_ok=True)
    pb_prefix = str(temp_dir / "frame").replace("\\", "/")

    # 执行 Playblast
    cmds.playblast(
        filename=pb_prefix,
        format='image',
        compression='png',
        viewer=False,
        showOrnaments=False,
        fp=4,
        percent=100,
        widthHeight=(640, 480),
        startTime=start_frame,
        endTime=end_frame,
        forceOverwrite=True,
        offScreen=True
    )

    # 恢复场景：清理关键帧并恢复初始旋转
    if target_joint:
        cmds.cutKey(target_joint, attribute='rotateX', clear=True)
        cmds.cutKey(target_joint, attribute='rotateZ', clear=True)
        cmds.setAttr(f"{target_joint}.rotate", *orig_rot)
    cmds.select(clear=True)

    # 5. 合成 36 帧循环 GIF
    frame_files = sorted(list(temp_dir.glob("frame.*.png")), key=lambda p: str(p))
    if not frame_files:
        frame_files = sorted(list(temp_dir.glob("frame*.png")), key=lambda p: str(p))
    print(f"Captured {len(frame_files)} playblast frames.")

    images = [Image.open(f) for f in frame_files[:36]]
    if images:
        snap_dir = Path(repo_root) / "snapshots"
        snap_dir.mkdir(parents=True, exist_ok=True)
        gif_path1 = snap_dir / "cvwrap_weightdriver_joint_animation.gif"

        brain_dir = Path("C:/Users/zhongweijie/.gemini/antigravity/brain/cb4fe7e1-8af7-4380-97a4-e5fb35e6f9bb").resolve()
        gif_path2 = brain_dir / "cvwrap_weightdriver_joint_animation.gif"

        images[0].save(
            str(gif_path1),
            save_all=True,
            append_images=images[1:],
            optimize=True,
            duration=41,  # 24 fps
            loop=0
        )
        images[0].save(
            str(gif_path2),
            save_all=True,
            append_images=images[1:],
            optimize=True,
            duration=41,
            loop=0
        )
        print(f"GIF saved successfully to {gif_path1} and {gif_path2}")

    # 清除临时 png 帧
    for f in frame_files:
        try:
            f.unlink()
        except Exception:
            pass

    return {
        "tool_id": tool.tool_id,
        "frames_captured": len(frame_files),
        "status_ok": status_res.success,
        "definitions_count": status_res.data.get('definitions'),
        "mel_exists_rbf": bool(exists_rbf),
        "mel_exists_ae": bool(exists_ae),
        "scene_restored": True
    }

result = run_verification()
print("VERIFICATION_RESULT:", result)
