# -*- coding: utf-8 -*-
"""
Maya 核心节点与几何工具库：
提供网格 Shape 查询、DAG 获取、蒙皮簇提取、选区层级解析、选择集与插件统一管理。
"""
from __future__ import absolute_import, division, print_function

import os

try:
    import maya.cmds as cmds
    MAYA_CMDS_AVAILABLE = True
except ImportError:
    cmds = None
    MAYA_CMDS_AVAILABLE = False

try:
    import maya.api.OpenMaya as om
    MAYA_API_AVAILABLE = True
except ImportError:
    om = None
    MAYA_API_AVAILABLE = False


def ensure_maya_initialized():
    """
    在外部命令行模式 (mayapy / headless) 下按需自动初始化 Maya Standalone 运行时环境。
    若已在 Maya GUI 进程中或已初始化，则安全跳过。
    """
    global cmds, om, MAYA_CMDS_AVAILABLE, MAYA_API_AVAILABLE
    try:
        import maya.cmds as _cmds
        if not hasattr(_cmds, "about"):
            import maya.standalone
            maya.standalone.initialize(name="python")
            import maya.cmds as _cmds_init
            import maya.api.OpenMaya as _om_init
            cmds = _cmds_init
            om = _om_init
            MAYA_CMDS_AVAILABLE = True
            MAYA_API_AVAILABLE = True
            return True
        return True
    except Exception:
        return False


def get_mesh_shape(node):
    """
    根据输入的 Transform 节点、Shape 节点或组件（如 pCube1.vtx[0] / pCube1.f[2]）
    安全获取其底层的 Mesh Shape 节点（返回长名称 fullPath）。
    若不存在或非多边形网格则返回 None。
    """
    if not MAYA_CMDS_AVAILABLE or not node:
        return None
    if not cmds.objExists(node):
        return None

    # 去除组件标识 (例如 'pSphere1.vtx[0]' -> 'pSphere1')
    base_node = node.split(".")[0] if "." in node else node

    node_type = cmds.nodeType(base_node)
    if node_type == "mesh":
        long_names = cmds.ls(base_node, long=True)
        return long_names[0] if long_names else base_node

    if node_type == "transform":
        shapes = cmds.listRelatives(base_node, shapes=True, fullPath=True, noIntermediate=True) or []
        mesh_shapes = [s for s in shapes if cmds.nodeType(s) == "mesh"]
        if mesh_shapes:
            return mesh_shapes[0]

    return None


def get_mesh_dag(node):
    """
    获取网格 Shape 节点的 OpenMaya.MDagPath 对象。
    """
    if not MAYA_API_AVAILABLE or not om:
        return None
    shape = get_mesh_shape(node)
    if not shape:
        return None

    sel = om.MSelectionList()
    sel.add(shape)
    return sel.getDagPath(0)


def get_skin_cluster(mesh):
    """
    获取网格绑定的 skinCluster 节点名称。
    """
    if not MAYA_CMDS_AVAILABLE:
        return None
    shape = get_mesh_shape(mesh)
    if not shape:
        return None

    history = cmds.listHistory(shape, pruneDagObjects=True) or []
    skin_clusters = cmds.ls(history, type="skinCluster") or []
    return skin_clusters[0] if skin_clusters else None


def resolve_selected_meshes(nodes):
    """
    解析输入的节点列表（严格保持先后顺序且去重）。
    若包含 Group 组节点或父层级 Transform，自动按层级展开并提取其下所有有效的 Mesh Shape。
    """
    if not MAYA_CMDS_AVAILABLE or not nodes:
        return []

    collected = []
    seen = set()

    for node in nodes:
        if not cmds.objExists(node):
            continue

        long_node = cmds.ls(node, long=True)[0]
        node_type = cmds.nodeType(long_node)

        if node_type == "mesh":
            if long_node not in seen:
                seen.add(long_node)
                collected.append(long_node)
        elif node_type == "transform":
            # 检查自己是否有直接的 mesh shape
            direct_shapes = cmds.listRelatives(long_node, shapes=True, fullPath=True, noIntermediate=True) or []
            mesh_direct = [s for s in direct_shapes if cmds.nodeType(s) == "mesh"]
            if mesh_direct:
                for s in mesh_direct:
                    if s not in seen:
                        seen.add(s)
                        collected.append(s)
            else:
                # 是父组，递归展开所有子级 mesh
                all_desc = cmds.listRelatives(long_node, allDescendents=True, fullPath=True, type="mesh", noIntermediate=True) or []
                # 调整为从顶层向下的自然顺序
                all_desc.reverse()
                for s in all_desc:
                    if s not in seen:
                        seen.add(s)
                        collected.append(s)

    return collected


def ensure_plugin(plugin_name):
    """
    确保指定的 Maya 插件（如 fbxmaya）已被加载。
    """
    if not MAYA_CMDS_AVAILABLE:
        return False
    if not cmds.pluginInfo(plugin_name, query=True, loaded=True):
        try:
            cmds.loadPlugin(plugin_name, quiet=True)
        except Exception as e:
            raise RuntimeError("加载 Maya 插件 [{}] 失败: {}".format(plugin_name, e))
    return True


SYSTEM_SET_BLACKLIST = {
    "defaultLightSet",
    "defaultObjectSet",
    "initialShadingGroup",
    "initialParticleSE",
    "defaultColorMgtGlobals",
}


def is_user_selection_set(set_node):
    """判断指定节点是否为普通用户选择集（排除材质着色组、显示层等系统内部集合）"""
    if not MAYA_CMDS_AVAILABLE or not cmds.objExists(set_node):
        return False
    if set_node in SYSTEM_SET_BLACKLIST:
        return False
    if cmds.nodeType(set_node) == "shadingEngine":
        return False
    try:
        if cmds.sets(set_node, q=True, renderable=True):
            return False
    except Exception:
        pass
    if set_node.startswith("renderSetupLayer_") or set_node.startswith("defaultRenderLayer"):
        return False
    return True


def get_all_user_selection_sets():
    """
    获取场景中所有的用户选择集清单及其成员。
    :return: list of dict [{"name": str, "members": list, "count": int}]
    """
    if not MAYA_CMDS_AVAILABLE:
        return []
    raw_sets = cmds.ls(type="objectSet") or []
    sets_data = []
    for s in raw_sets:
        if is_user_selection_set(s):
            members = cmds.sets(s, q=True) or []
            sets_data.append({
                "name": s,
                "members": members,
                "count": len(members)
            })
    sets_data.sort(key=lambda x: x["name"].lower())
    return sets_data


def select_safely(nodes, replace=True, highlight=True):
    """安全选中节点，若节点不存在则自动过滤，避免抛出异常"""
    if not MAYA_CMDS_AVAILABLE:
        return []
    valid = [n for n in (nodes or []) if cmds.objExists(n)]
    if valid:
        cmds.select(valid, replace=replace)
        if highlight and len(valid) == 1:
            try:
                cmds.viewFit(valid[0], animate=True)
            except Exception:
                pass
    else:
        if replace:
            cmds.select(clear=True)
    return valid


def get_node_namespace(node):
    """获取节点的绝对命名空间前缀（例如 ':char:hero:mesh' -> ':char:hero'）"""
    leaf = node.rsplit("|", 1)[-1]
    if ":" not in leaf:
        return None
    return ":" + leaf.rpartition(":")[0].lstrip(":")


def get_clean_basename(node):
    """获取节点的纯叶节点名称（去除所有层级路径与命名空间）"""
    return node.rsplit("|", 1)[-1].rsplit(":", 1)[-1]


def get_current_scene_dir():
    """获取当前场景文件的保存目录，若为 Untitled 则回退到项目目录或用户目录"""
    if not MAYA_CMDS_AVAILABLE:
        return os.path.expanduser("~").replace("\\", "/")
    scene_path = cmds.file(q=True, sceneName=True)
    if scene_path:
        return os.path.dirname(os.path.normpath(scene_path)).replace("\\", "/")
    try:
        ws = cmds.workspace(q=True, rootDirectory=True)
        if ws:
            rule = cmds.workspace(fileRuleEntry="scene") or "scenes"
            sdir = os.path.join(ws, rule)
            if os.path.exists(sdir):
                return os.path.normpath(sdir).replace("\\", "/")
            return os.path.normpath(ws).replace("\\", "/")
    except Exception:
        pass
    return os.path.expanduser("~").replace("\\", "/")
