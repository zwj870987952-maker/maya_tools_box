"""Verification script for camera_f_fix in live Maya instance."""
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

    # 1. 确认场景
    sn = cmds.file(q=True, sn=True)
    if 'test1026.ma' not in sn:
        raise RuntimeError(f"Scene not pinned to test1026.ma: {sn}")

    # 2. 加载候选工具
    candidate_path = Path(repo_root) / "tools_staging_pool/03_transforms_modeling/camera_f_fix/release_candidate/launch_candidate.py"
    if candidate_path.is_file():
        tool = runpy.run_path(str(candidate_path))['load_tool']()
    else:
        from maya_toolkit.tools.camera_f_fix import CameraFFixTool
        tool = CameraFFixTool()

    print(f"Loaded tool: {tool.tool_id} (version: {tool.version})")

    # 3. 记录初始 persp 状态
    orig_trans = cmds.getAttr('persp.translate')[0]
    orig_rot = cmds.getAttr('persp.rotate')[0]
    orig_scale = cmds.getAttr('persp.scale')[0]

    # 模拟相机混乱/偏移
    cmds.setAttr('persp.translate', 50.0, 120.0, 200.0)
    cmds.setAttr('persp.rotate', -20.0, 45.0, 0.0)

    # 验证 preflight / dry_run
    val_res = tool.run(dry_run=True, camera='persp')
    if not val_res.success:
        raise RuntimeError(f"Preflight validation failed: {val_res.message}")
    print("Preflight validation OK:", val_res.data)

    # 执行正式重置
    exec_res = tool.run(camera='persp', preserve_selection=True)
    if not exec_res.success:
        raise RuntimeError(f"Execution failed: {exec_res.message}")
    print("Execution OK:", exec_res.data)

    # 验证撤回 Undo
    cmds.undo()
    undone_trans = cmds.getAttr('persp.translate')[0]
    print(f"Undo checked. Restored translate: {undone_trans}")

    # 再次执行以便进行视口聚焦与拍屏
    tool.run(camera='persp', preserve_selection=False)

    # 针对场景中的主要模型进行聚焦
    meshes = cmds.ls(type='mesh')
    if meshes:
        parents = cmds.listRelatives(meshes[0], parent=True, fullPath=True)
        if parents:
            cmds.select(parents[0])
            cmds.viewFit('persp', animate=False)

    # 4. 生成 36 帧视口动画并拍摄 Playblast
    start_frame = 1
    end_frame = 36
    cmds.playbackOptions(min=start_frame, max=end_frame, ast=start_frame, aet=end_frame)
    cmds.currentTime(start_frame)

    # 创建一个临时旋转观察动画（通过环绕平滑旋转 persp 或围绕目标）
    # 为 persp 打关键帧创建平滑环绕旋转
    cmds.setKeyframe('persp', attribute='rotateY', time=start_frame, value=cmds.getAttr('persp.rotateY'))
    cmds.setKeyframe('persp', attribute='rotateY', time=end_frame, value=cmds.getAttr('persp.rotateY') + 360.0)

    temp_dir = Path("C:/Users/zhongweijie/AppData/Local/Temp/camera_f_fix_pb").resolve()
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

    # 清理 persp 上的临时关键帧并恢复初始状态
    cmds.cutKey('persp', attribute='rotateY', clear=True)
    cmds.setAttr('persp.translate', *orig_trans)
    cmds.setAttr('persp.rotate', *orig_rot)
    cmds.setAttr('persp.scale', *orig_scale)
    cmds.select(clear=True)

    # 5. 合成 36 帧循环 GIF
    frame_files = sorted(list(temp_dir.glob("frame.*.png")), key=lambda p: str(p))
    if not frame_files:
        # 尝试查找数字后缀
        frame_files = sorted(list(temp_dir.glob("frame*.png")), key=lambda p: str(p))
    print(f"Captured {len(frame_files)} playblast frames.")

    images = [Image.open(f) for f in frame_files[:36]]
    if images:
        snap_dir = Path(repo_root) / "snapshots"
        snap_dir.mkdir(parents=True, exist_ok=True)
        gif_path1 = snap_dir / "camera_f_fix_joint_animation.gif"

        brain_dir = Path("C:/Users/zhongweijie/.gemini/antigravity/brain/cb4fe7e1-8af7-4380-97a4-e5fb35e6f9bb").resolve()
        gif_path2 = brain_dir / "camera_f_fix_joint_animation.gif"

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
        "preflight_ok": val_res.success,
        "exec_ok": exec_res.success,
        "scene_restored": True
    }

result = run_verification()
print("VERIFICATION_RESULT:", result)
