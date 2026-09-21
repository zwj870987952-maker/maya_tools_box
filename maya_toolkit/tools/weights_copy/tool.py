# -*- coding: utf-8 -*-
"""
复制重叠位置顶点蒙皮权重工具：标准 Tool 实现类
"""
from __future__ import absolute_import, division, print_function

import math

try:
    import maya.cmds as cmds
    MAYA_CMDS_AVAILABLE = True
except ImportError:
    cmds = None
    MAYA_CMDS_AVAILABLE = False

try:
    import maya.api.OpenMaya as om
    import maya.api.OpenMayaAnim as oma
    MAYA_API_AVAILABLE = True
except ImportError:
    om = oma = None
    MAYA_API_AVAILABLE = False

from ...framework.base_tool import BaseMayaTool
from ...framework.models import ToolResult
from ...core.maya_utils import get_mesh_shape, get_mesh_dag, get_skin_cluster
from ...core.context import UndoChunkContext


def get_mesh_points(mesh, space="world"):
    """使用 Maya API 2.0 获取网格所有顶点的坐标列表"""
    dag = get_mesh_dag(mesh)
    if not dag or not om:
        return None
    fn_mesh = om.MFnMesh(dag)
    m_space = om.MSpace.kWorld if space.lower() == "world" else om.MSpace.kObject
    return fn_mesh.getPoints(m_space)


def find_overlapping_vertices(src_points, tgt_points, tolerance=0.001):
    """使用空间哈希桶算法（Spatial Grid Hashing）检索重叠顶点对"""
    cell_size = max(float(tolerance), 1e-7)
    grid = {}

    for src_idx, pt in enumerate(src_points):
        cx = int(math.floor(pt.x / cell_size))
        cy = int(math.floor(pt.y / cell_size))
        cz = int(math.floor(pt.z / cell_size))
        key = (cx, cy, cz)
        if key not in grid:
            grid[key] = []
        grid[key].append((src_idx, pt))

    matches = {}
    tol_sq = float(tolerance) * float(tolerance)

    for tgt_idx, pt in enumerate(tgt_points):
        cx = int(math.floor(pt.x / cell_size))
        cy = int(math.floor(pt.y / cell_size))
        cz = int(math.floor(pt.z / cell_size))

        closest_src = None
        min_dist_sq = tol_sq

        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    n_key = (cx + dx, cy + dy, cz + dz)
                    if n_key in grid:
                        for s_idx, s_pt in grid[n_key]:
                            d_sq = (
                                (s_pt.x - pt.x) * (s_pt.x - pt.x)
                                + (s_pt.y - pt.y) * (s_pt.y - pt.y)
                                + (s_pt.z - pt.z) * (s_pt.z - pt.z)
                            )
                            if d_sq <= min_dist_sq:
                                min_dist_sq = d_sq
                                closest_src = s_idx

        if closest_src is not None:
            matches[tgt_idx] = closest_src

    return matches


def ensure_target_skin(src_skin, tgt_mesh, auto_bind=True, add_missing_influences=True):
    """确保目标网格具有 skinCluster 并补充影响骨骼"""
    tgt_skin = get_skin_cluster(tgt_mesh)
    src_influences = cmds.skinCluster(src_skin, query=True, influence=True) or []

    if not tgt_skin:
        if not auto_bind:
            raise RuntimeError("目标对象 [{}] 尚未绑定蒙皮，且 auto_bind 为 False。".format(tgt_mesh))
        if not src_influences:
            raise RuntimeError("源对象蒙皮 [{}] 未检测到有效骨骼。".format(src_skin))

        created_skins = cmds.skinCluster(
            src_influences,
            tgt_mesh,
            toSelectedBones=True,
            bindMethod=0,
            normalizeWeights=1,
            name="{}_skinCluster".format(tgt_mesh.split("|")[-1]),
        )
        return created_skins[0]

    if add_missing_influences:
        tgt_influences = set(cmds.skinCluster(tgt_skin, query=True, influence=True) or [])
        missing_influences = [inf for inf in src_influences if inf not in tgt_influences]
        for inf in missing_influences:
            if cmds.objExists(inf):
                cmds.skinCluster(tgt_skin, edit=True, addInfluence=inf, weight=0.0)

    return tgt_skin


class WeightsCopyTool(BaseMayaTool):
    """
    重叠顶点蒙皮权重精准复制工具：
    基于空间哈希桶在源对象与目标对象之间查找空间重叠顶点并复制蒙皮权重。
    """

    tool_id = "copy_overlapping_weights"
    tool_name = "重叠位置顶点蒙皮权重复制工具"
    category = "Rigging"
    version = "1.2.0"
    description = (
        "在源模型 (A) 与目标模型 (B) 之间，基于三维空间世界坐标匹配重叠的顶点，"
        "并将对应顶点的蒙皮权重精确传递到目标对象上。支持自动绑定与自动补充缺失骨骼。"
    )

    parameters_schema = {
        "type": "object",
        "properties": {
            "source": {
                "type": "string",
                "description": "源网格或 Transform 节点名称（必须带有有效蒙皮簇）。"
            },
            "target": {
                "type": "string",
                "description": "目标网格或 Transform 节点名称（接收蒙皮权重）。"
            },
            "tolerance": {
                "type": "number",
                "default": 0.001,
                "description": "空间顶点重叠判定的最大容差距离（默认 0.001）。"
            },
            "space": {
                "type": "string",
                "enum": ["world", "object"],
                "default": "world",
                "description": "坐标空间，'world' (默认) 或 'object'。"
            },
            "auto_bind": {
                "type": "boolean",
                "default": True,
                "description": "若目标网格未蒙皮，是否自动绑定源网格骨骼（默认 True）。"
            },
            "add_missing_influences": {
                "type": "boolean",
                "default": True,
                "description": "若目标蒙皮缺少源网格的部分骨骼，是否自动添加（默认 True）。"
            }
        },
        "required": ["source", "target"],
        "additionalProperties": False
    }

    def validate(self, source, target, tolerance=0.001, space="world", **kwargs):
        if not MAYA_CMDS_AVAILABLE:
            return ToolResult.fail("Maya 环境不可用")

        if not source or not target:
            return ToolResult.fail("必须同时指定 source 和 target 网格参数！")

        src_shape = get_mesh_shape(source)
        tgt_shape = get_mesh_shape(target)

        if not src_shape:
            return ToolResult.fail("源对象 [{}] 不存在或不是有效的 Mesh 多边形网格！".format(source))
        if not tgt_shape:
            return ToolResult.fail("目标对象 [{}] 不存在或不是有效的 Mesh 多边形网格！".format(target))
        if src_shape == tgt_shape:
            return ToolResult.fail("源对象与目标对象不能是同一个网格！")

        src_skin = get_skin_cluster(src_shape)
        if not src_skin:
            return ToolResult.fail("源对象 [{}] 未检测到绑定的蒙皮簇 (skinCluster)！".format(source))

        src_pts = get_mesh_points(src_shape, space=space)
        tgt_pts = get_mesh_points(tgt_shape, space=space)
        if not src_pts or not tgt_pts:
            return ToolResult.fail("无法获取网格顶点坐标数据。")

        matches = find_overlapping_vertices(src_pts, tgt_pts, tolerance=tolerance)
        match_count = len(matches)

        return ToolResult.ok(
            message="预检通过，源点数: {}，目标点数: {}，匹配到重叠点: {} 个。".format(
                len(src_pts), len(tgt_pts), match_count
            ),
            data={
                "source": src_shape,
                "target": tgt_shape,
                "source_points_count": len(src_pts),
                "target_points_count": len(tgt_pts),
                "matched_vertices_count": match_count,
                "tolerance": tolerance,
                "space": space
            }
        )

    def execute(self, source, target, tolerance=0.001, space="world", auto_bind=True, add_missing_influences=True, **kwargs):
        if not MAYA_CMDS_AVAILABLE or not MAYA_API_AVAILABLE:
            return ToolResult.fail("Maya OpenMaya API 运行环境不可用")

        src_shape = get_mesh_shape(source)
        tgt_shape = get_mesh_shape(target)
        src_skin = get_skin_cluster(src_shape)

        src_dag = get_mesh_dag(src_shape)
        tgt_dag = get_mesh_dag(tgt_shape)
        src_pts = get_mesh_points(src_shape, space=space)
        tgt_pts = get_mesh_points(tgt_shape, space=space)

        matches = find_overlapping_vertices(src_pts, tgt_pts, tolerance=tolerance)
        match_count = len(matches)

        if match_count == 0:
            return ToolResult.fail(
                "未检索到任何重叠点（容差: {}）。请检查模型空间位置或适当增大容差。".format(tolerance),
                data={"source_points": len(src_pts), "target_points": len(tgt_pts)}
            )

        tgt_skin = ensure_target_skin(src_skin, tgt_shape, auto_bind=auto_bind, add_missing_influences=add_missing_influences)

        src_skin_node = om.MSelectionList().add(src_skin).getDependNode(0)
        fn_src_skin = oma.MFnSkinCluster(src_skin_node)
        comp_fn = om.MFnSingleIndexedComponent()
        src_comp = comp_fn.create(om.MFn.kMeshVertComponent)
        comp_fn.setCompleteData(len(src_pts))

        all_src_weights, num_infs = fn_src_skin.getWeights(src_dag, src_comp)
        src_inf_dags = fn_src_skin.influenceObjects()
        src_inf_names = [inf.partialPathName() for inf in src_inf_dags]

        processed = 0
        for tgt_vtx_idx, src_vtx_idx in matches.items():
            start_idx = src_vtx_idx * num_infs
            src_vtx_weights = all_src_weights[start_idx : start_idx + num_infs]
            weight_pairs = [
                (src_inf_names[i], src_vtx_weights[i])
                for i in range(num_infs)
                if src_vtx_weights[i] > 1e-6
            ]
            tgt_vtx_str = "{}.vtx[{}]".format(tgt_shape, tgt_vtx_idx)
            cmds.skinPercent(tgt_skin, tgt_vtx_str, transformValue=weight_pairs, zeroRemainingInfluences=True)
            processed += 1

        return ToolResult.ok(
            message="成功将 {} 个重叠顶点的蒙皮权重复制到目标网格 [{}]。".format(processed, target),
            data={
                "source": source,
                "target": target,
                "matched_vertices_count": processed,
                "target_skin_cluster": tgt_skin
            }
        )

    def show_ui(self, parent=None):
        import copy_overlapping_weights
        try:
            return copy_overlapping_weights.show_ui(parent=parent)
        except TypeError:
            return copy_overlapping_weights.show_ui()
