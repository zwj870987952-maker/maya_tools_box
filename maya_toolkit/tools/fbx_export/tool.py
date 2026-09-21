# -*- coding: utf-8 -*-
"""
选择集批量导出 FBX 工具：标准 Tool 实现类
"""
from __future__ import absolute_import, division, print_function

import os

try:
    import maya.cmds as cmds
    import maya.mel as mel
    MAYA_AVAILABLE = True
except ImportError:
    cmds = mel = None
    MAYA_AVAILABLE = False

from ...framework.base_tool import BaseMayaTool
from ...framework.models import ToolResult
from ...core.maya_utils import ensure_plugin, get_all_user_selection_sets, get_current_scene_dir


def apply_fbx_export_settings(options):
    """根据字典设置配置 Maya FBX 导出参数"""
    ensure_plugin("fbxmaya")
    mel.eval("FBXResetExport;")

    is_ascii = options.get("ascii", False)
    mel.eval("FBXExportInAscii -v {};".format("true" if is_ascii else "false"))

    fbx_version = options.get("fbx_version", "FBX202000")
    if fbx_version and fbx_version != "DEFAULT":
        try:
            mel.eval('FBXExportFileVersion -v "{}";'.format(fbx_version))
        except Exception:
            pass

    mel.eval("FBXExportSmoothingGroups -v {};".format("true" if options.get("smoothing_groups", True) else "false"))
    mel.eval("FBXExportSmoothMesh -v {};".format("true" if options.get("smooth_mesh", False) else "false"))
    mel.eval("FBXExportTriangulate -v {};".format("true" if options.get("triangulate", False) else "false"))
    mel.eval("FBXExportTangents -v {};".format("true" if options.get("tangents", False) else "false"))
    mel.eval("FBXExportSkins -v {};".format("true" if options.get("skins", True) else "false"))
    mel.eval("FBXExportShapes -v {};".format("true" if options.get("blend_shapes", True) else "false"))

    animation = options.get("animation", False)
    mel.eval("FBXExportAnimationOnly -v false;")
    try:
        mel.eval('FBXProperty "Export|IncludeGrp|Animation" -v {};'.format("true" if animation else "false"))
    except Exception:
        pass

    if animation and options.get("bake_animation", False):
        mel.eval("FBXExportBakeComplexAnimation -v true;")
        mel.eval("FBXExportBakeComplexStart -v {};".format(options.get("start_frame", 1)))
        mel.eval("FBXExportBakeComplexEnd -v {};".format(options.get("end_frame", 24)))
        mel.eval("FBXExportBakeComplexStep -v {};".format(options.get("step", 1)))
        mel.eval("FBXExportBakeResampleAnimation -v true;")

    mel.eval("FBXExportEmbeddedTextures -v {};".format("true" if options.get("embed_media", False) else "false"))
    mel.eval("FBXExportCameras -v {};".format("true" if options.get("cameras", False) else "false"))
    mel.eval("FBXExportLights -v {};".format("true" if options.get("lights", False) else "false"))

    up_axis = str(options.get("up_axis", "y")).lower()
    if up_axis in ("y", "z"):
        mel.eval('FBXExportUpAxis "{}";'.format(up_axis))

    mel.eval("FBXExportScaleFactor {};".format(float(options.get("scale_factor", 1.0))))


class FBXExportTool(BaseMayaTool):
    """
    选择集批量导出 FBX 工具：
    根据场景中的 objectSet 选择集或指定项，将成员批量导出为独立的 FBX 资产。
    """

    tool_id = "export_sets_to_fbx"
    tool_name = "选择集批量导出FBX工具"
    category = "Pipeline"
    version = "1.2.0"
    description = (
        "自动读取 Maya 场景中的用户选择集 (objectSet)，或根据传入的导出配置列表，"
        "将各个选择集中的模型成员独立批量导出为 FBX 文件。支持完整的平滑组、骨骼、动画烘焙等参数控制。"
    )

    parameters_schema = {
        "type": "object",
        "properties": {
            "export_items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "set_name": {"type": "string", "description": "Maya 选择集名称"},
                        "fbx_name": {"type": "string", "description": "导出的 FBX 文件名（可含 .fbx 扩展名）"},
                        "export_dir": {"type": "string", "description": "保存目标目录"}
                    },
                    "required": ["set_name"]
                },
                "description": "需要导出的选择集配置项列表。若为空则默认导出当前场景中所有用户选择集。"
            },
            "fbx_options": {
                "type": "object",
                "properties": {
                    "smoothing_groups": {"type": "boolean", "default": True},
                    "smooth_mesh": {"type": "boolean", "default": False},
                    "triangulate": {"type": "boolean", "default": False},
                    "skins": {"type": "boolean", "default": True},
                    "blend_shapes": {"type": "boolean", "default": True},
                    "animation": {"type": "boolean", "default": False},
                    "bake_animation": {"type": "boolean", "default": False},
                    "embed_media": {"type": "boolean", "default": False},
                    "ascii": {"type": "boolean", "default": False},
                    "up_axis": {"type": "string", "enum": ["y", "z"], "default": "y"}
                },
                "description": "FBX 导出参数配置字典。"
            }
        },
        "required": [],
        "additionalProperties": False
    }

    def validate(self, export_items=None, fbx_options=None, **kwargs):
        if not MAYA_AVAILABLE:
            return ToolResult.fail("Maya 环境不可用")

        items = export_items
        if not items:
            all_sets = get_all_user_selection_sets()
            if not all_sets:
                return ToolResult.fail("当前 Maya 场景中未检测到任何有效的用户选择集 (objectSet)。")
            default_dir = get_current_scene_dir()
            items = [
                {
                    "set_name": s["name"],
                    "fbx_name": s["name"] + ".fbx",
                    "export_dir": default_dir
                }
                for s in all_sets
            ]

        # 检查选择集存在性
        missing_sets = [item["set_name"] for item in items if not cmds.objExists(item["set_name"])]
        if missing_sets:
            return ToolResult.fail("以下选择集在场景中不存在: {}".format(missing_sets), errors=missing_sets)

        # 检查空选择集
        empty_sets = [
            item["set_name"] for item in items
            if not cmds.sets(item["set_name"], q=True)
        ]

        return ToolResult.ok(
            message="预检通过，待导出选择集数量: {}".format(len(items)),
            data={
                "items_count": len(items),
                "empty_sets_warning": empty_sets
            },
            warnings=["选择集为空: {}".format(s) for s in empty_sets]
        )

    def execute(self, export_items=None, fbx_options=None, **kwargs):
        if not MAYA_AVAILABLE:
            return ToolResult.fail("Maya 环境不可用")

        options = fbx_options or {}
        apply_fbx_export_settings(options)

        items = export_items
        if not items:
            default_dir = get_current_scene_dir()
            items = [
                {
                    "set_name": s["name"],
                    "fbx_name": s["name"] + ".fbx",
                    "export_dir": default_dir
                }
                for s in get_all_user_selection_sets()
            ]

        # 暂存当前视口选区
        orig_sel = cmds.ls(selection=True, long=True) or []
        exported_files = []
        errors = []

        try:
            for item in items:
                set_name = item["set_name"]
                if not cmds.objExists(set_name):
                    errors.append("集合 [{}] 不存在，跳过。".format(set_name))
                    continue

                members = cmds.sets(set_name, q=True) or []
                if not members:
                    errors.append("集合 [{}] 内容为空，跳过导出。".format(set_name))
                    continue

                export_dir = item.get("export_dir") or get_current_scene_dir()
                if not os.path.exists(export_dir):
                    try:
                        os.makedirs(export_dir)
                    except Exception as e:
                        errors.append("无法创建导出目录 {}: {}".format(export_dir, e))
                        continue

                fbx_name = item.get("fbx_name") or (set_name + ".fbx")
                if not fbx_name.lower().endswith(".fbx"):
                    fbx_name += ".fbx"

                out_path = os.path.normpath(os.path.join(export_dir, fbx_name)).replace("\\", "/")

                # 选中成员并导出
                cmds.select(members, replace=True)
                if options.get("include_children", True):
                    cmds.select(hierarchy=True)

                mel_cmd = 'FBXExport -f "{}" -s;'.format(out_path)
                try:
                    mel.eval(mel_cmd)
                    if os.path.isfile(out_path):
                        exported_files.append(out_path)
                    else:
                        errors.append("导出命令执行但未生成文件: {}".format(out_path))
                except Exception as e:
                    errors.append("导出 [{}] 失败: {}".format(out_path, str(e)))

        finally:
            if orig_sel and all(cmds.objExists(n) for n in orig_sel):
                cmds.select(orig_sel, replace=True)
            else:
                cmds.select(clear=True)

        return ToolResult.ok(
            message="成功导出 {} 个 FBX 文件。".format(len(exported_files)),
            data={"exported_files": exported_files},
            warnings=errors
        )

    def show_ui(self, parent=None):
        import export_sets_to_fbx
        try:
            return export_sets_to_fbx.show_ui(parent=parent)
        except TypeError:
            return export_sets_to_fbx.show_ui()
