# -*- coding: utf-8 -*-
"""
================================================================================
Maya 外部 FBX 资产深度比对与差异同步工具 (FBX SDK Asset Diff & Sync Inspector)
================================================================================
- 核心理念：“资产全维度比对 + 差异精准同步”，绝不在比对阶段导入外部模型（保持零场景污染）。
- 底层技术：
  1. 采用 Autodesk FBX SDK 纯内存直接读取外部 FBX 二进制与 ASCII 数据。
  2. 提取网格几何拓扑（顶点数、面数、三角面数、UV集）、材质网络、分面映射与空间变换。
  3. 与当前 Maya 场景同名模型进行 Side-by-Side 全维度属性比对。
  4. 支持选择性一键同步材质与分面、一键同步空间变换位姿、在 Maya 中高亮对焦差异物体。
  5. 兼容 Maya 2017 ~ 2026+ (PySide2 / PySide6, Python 2 / 3)。
================================================================================
"""

from __future__ import print_function, division
import os
import sys
import time
import math
import uuid
import re
import traceback

import maya.cmds as cmds
import maya.mel as mel

# ------------------------------------------------------------------------------
# 兼容导入 PySide2 (Maya 2017~2024) / PySide6 (Maya 2025+)
# ------------------------------------------------------------------------------
try:
    from PySide6 import QtCore, QtGui, QtWidgets
    from PySide6.QtCore import Qt, Signal
except ImportError:
    try:
        from PySide2 import QtCore, QtGui, QtWidgets
        from PySide2.QtCore import Qt
        from PySide2.QtCore import Signal
    except ImportError:
        raise ImportError("当前环境中未找到 PySide2 或 PySide6，无法初始化工具图形界面。")


# ==============================================================================
# 模块 1：FBX SDK 环境检测与动态加载器
# ==============================================================================

class FBXSDKManager(object):
    """管理 Autodesk FBX SDK 的检测、搜索与动态导入。"""

    _fbx_module = None

    @classmethod
    def get_fbx_module(cls):
        """获取已加载的 fbx 模块，若未加载则尝试导入。"""
        if cls._fbx_module is not None:
            return cls._fbx_module

        # 1. 优先自动探测并添加项目随附扩展目录与本地环境路径
        cls.auto_discover_and_add_sdk_paths()

        # 2. 尝试导入
        try:
            import fbx
            cls._fbx_module = fbx
            return cls._fbx_module
        except ImportError:
            pass

        return None

    @classmethod
    def is_sdk_available(cls):
        """判断当前环境是否具备 Autodesk FBX SDK"""
        return cls.get_fbx_module() is not None

    @classmethod
    def load_sdk_from_custom_path(cls, custom_dir):
        """允许用户手动指定包含 fbx.pyd 或 FbxCommon 的目录进行热加载"""
        if not custom_dir or not os.path.isdir(custom_dir):
            return False

        norm_dir = os.path.normpath(custom_dir)
        if norm_dir not in sys.path:
            sys.path.insert(0, norm_dir)

        try:
            import fbx
            cls._fbx_module = fbx
            return True
        except Exception:
            return False

    @classmethod
    def auto_discover_and_add_sdk_paths(cls):
        """自动在系统中搜索常见的 Autodesk FBX SDK Python 安装路径与当前项目的扩展库"""
        current_dir = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else ""
        py_ver_num = "{}{}".format(sys.version_info[0], sys.version_info[1])
        ver_dir_name = "python{}".format(py_ver_num)
        user_site = os.path.expandvars(r"%APPDATA%\Python\Python{}\site-packages".format(py_ver_num))

        # 1. 优先检查项目自带的当前 Python 版本预编译目录 (零依赖独立运行)
        if current_dir:
            bundle_dir = os.path.join(current_dir, "fbx_sdk_dist", ver_dir_name)
            if os.path.isdir(bundle_dir):
                norm_bundle = os.path.normpath(bundle_dir)
                if norm_bundle not in sys.path:
                    sys.path.insert(0, norm_bundle)

        # 2. 检查用户级 site-packages (作为系统级备选)
        if os.path.isdir(user_site):
            norm_user = os.path.normpath(user_site)
            if norm_user not in sys.path:
                sys.path.append(norm_user)

        # 3. 检查常规外部 SDK 安装目录
        search_roots = [
            r"C:\Program Files\Autodesk\FBX\FBX Python SDK",
            r"C:\Program Files (x86)\Autodesk\FBX\FBX Python SDK",
            os.environ.get("FBX_SDK_ROOT", ""),
            os.environ.get("FBX_SDK_PYTHON_PATH", ""),
        ]

        target_pyd_names = [
            "fbx.cp{}-win_amd64.pyd".format(py_ver_num),
            "fbx.pyd"
        ]

        for root in search_roots:
            if not root or not os.path.exists(root):
                continue
            try:
                for r, dirs, files in os.walk(root):
                    # 避免误加载其他 Python 版本的目录 (如在 3.11 下误加载 3.10)
                    folder_lower = os.path.basename(r).lower()
                    if folder_lower.startswith("python") and folder_lower != ver_dir_name:
                        continue
                    if any(f in target_pyd_names for f in files):
                        norm_r = os.path.normpath(r)
                        if norm_r not in sys.path:
                            sys.path.insert(0, norm_r)
            except Exception:
                pass


# ==============================================================================
# 模块 2：Autodesk FBX SDK 核心解析引擎 (纯内存直读，零场景模型导入)
# ==============================================================================

class FBXSDKParser(object):
    """使用 Autodesk FBX SDK 直接解析 FBX 文件中的网格几何指标、材质球、贴图连接与模型映射数据。"""

    @classmethod
    def parse_file(cls, fbx_file_path, log_func=None):
        """
        利用 FBX SDK 解析 FBX 文件。
        :param fbx_file_path: str FBX 文件路径
        :param log_func: callable 日志函数
        :return: dict 包含 materials 和 meshes 数据结构
        """
        fbx = FBXSDKManager.get_fbx_module()
        if not fbx:
            raise RuntimeError("未检测到 Autodesk FBX SDK 模块 (fbx)。请先配置 FBX SDK 路径。")

        def log(msg, level="info"):
            if log_func:
                log_func(msg, level)

        log("正在使用 Autodesk FBX SDK 读取文件数据: {}".format(os.path.basename(fbx_file_path)), "info")

        # 1. 创建 FbxManager 与 FbxIOSettings
        manager = fbx.FbxManager.Create()
        ios = fbx.FbxIOSettings.Create(manager, fbx.IOSROOT)
        manager.SetIOSettings(ios)

        # 2. 创建并初始化 FbxImporter
        importer = fbx.FbxImporter.Create(manager, "")
        init_ok = importer.Initialize(fbx_file_path, -1, manager.GetIOSettings())
        if not init_ok:
            err_msg = importer.GetStatus().GetErrorString()
            importer.Destroy()
            manager.Destroy()
            raise RuntimeError("FBX SDK 初始化文件失败: {}".format(err_msg))

        # 3. 创建 FbxScene 并执行只读导入
        scene = fbx.FbxScene.Create(manager, "FBXScene")
        importer.Import(scene)
        importer.Destroy()

        materials_data = {}
        meshes_data = []

        try:
            # 4. 递归遍历场景所有节点
            root_node = scene.GetRootNode()
            if root_node:
                cls._traverse_node(fbx, root_node, materials_data, meshes_data, fbx_file_path)

            log("FBX SDK 数据解析完成: 找到 {} 个网格节点，{} 个材质配置。".format(
                len(meshes_data), len(materials_data)
            ), "info")

        finally:
            # 5. 销毁 SDK 对象，释放内存
            manager.Destroy()

        return {
            "materials": materials_data,
            "meshes": meshes_data
        }

    @classmethod
    def _traverse_node(cls, fbx, node, materials_data, meshes_data, fbx_file_path):
        """递归遍历 FbxNode 提取网格与材质信息"""
        node_attr = node.GetNodeAttribute()
        if node_attr and node_attr.GetAttributeType() == fbx.FbxNodeAttribute.EType.eMesh:
            mesh = node.GetMesh()
            if mesh:
                mesh_record = cls._parse_mesh_node(fbx, node, mesh, materials_data, fbx_file_path)
                if mesh_record:
                    meshes_data.append(mesh_record)

        # 遍历子节点
        child_count = node.GetChildCount()
        for i in range(child_count):
            child_node = node.GetChild(i)
            cls._traverse_node(fbx, child_node, materials_data, meshes_data, fbx_file_path)

    @classmethod
    def _parse_mesh_node(cls, fbx, node, mesh, materials_data, fbx_file_path):
        """提取单个 FbxMesh 的拓扑指标、材质配置及其面分配"""
        node_name = node.GetName()
        mat_count = node.GetMaterialCount()
        node_materials = []

        for m_idx in range(mat_count):
            fbx_mat = node.GetMaterial(m_idx)
            if not fbx_mat:
                continue
            mat_name = fbx_mat.GetName()
            node_materials.append(mat_name)

            if mat_name not in materials_data:
                materials_data[mat_name] = cls._parse_material(fbx, fbx_mat, fbx_file_path)

        # 解析面与材质的映射关系
        element_mat_count = mesh.GetElementMaterialCount()
        polygon_count = mesh.GetPolygonCount()
        face_assignments = {} # {mat_name: [(start, end), ...] or "all"}

        if element_mat_count > 0 and mat_count > 0:
            element_mat = mesh.GetElementMaterial(0)
            mapping_mode = element_mat.GetMappingMode()

            if mapping_mode == fbx.FbxLayerElement.EMappingMode.eAllSame:
                mat_idx = element_mat.GetIndexArray().GetAt(0)
                if 0 <= mat_idx < len(node_materials):
                    face_assignments[node_materials[mat_idx]] = "all"
            elif mapping_mode == fbx.FbxLayerElement.EMappingMode.eByPolygon:
                index_array = element_mat.GetIndexArray()
                mat_to_faces = {}
                for p_idx in range(polygon_count):
                    m_idx = index_array.GetAt(p_idx)
                    if 0 <= m_idx < len(node_materials):
                        m_name = node_materials[m_idx]
                        if m_name not in mat_to_faces:
                            mat_to_faces[m_name] = []
                        mat_to_faces[m_name].append(p_idx)

                for m_name, face_indices in mat_to_faces.items():
                    face_assignments[m_name] = cls._group_contiguous_ranges(face_indices)
            else:
                if node_materials:
                    face_assignments[node_materials[0]] = "all"
        else:
            if node_materials:
                face_assignments[node_materials[0]] = "all"

        # 计算顶点数与三角面数
        vertex_count = mesh.GetControlPointsCount()
        triangle_count = 0
        for p_i in range(polygon_count):
            p_size = mesh.GetPolygonSize(p_i)
            if p_size >= 3:
                triangle_count += (p_size - 2)

        # 提取所有 UV 通道集合名称
        uv_sets = []
        for u_i in range(mesh.GetElementUVCount()):
            uv_elem = mesh.GetElementUV(u_i)
            if uv_elem:
                u_name = uv_elem.GetName() or "map{}".format(u_i + 1)
                if u_name not in uv_sets:
                    uv_sets.append(u_name)

        # 提取空间变换信息
        try:
            t_vec = node.LclTranslation.Get()
            r_vec = node.LclRotation.Get()
            s_vec = node.LclScaling.Get()
            transform_data = {
                "translation": [round(float(t_vec[0]), 4), round(float(t_vec[1]), 4), round(float(t_vec[2]), 4)],
                "rotation": [round(float(r_vec[0]), 4), round(float(r_vec[1]), 4), round(float(r_vec[2]), 4)],
                "scaling": [round(float(s_vec[0]), 4), round(float(s_vec[1]), 4), round(float(s_vec[2]), 4)]
            }
        except Exception:
            transform_data = {
                "translation": [0.0, 0.0, 0.0],
                "rotation": [0.0, 0.0, 0.0],
                "scaling": [1.0, 1.0, 1.0]
            }

        return {
            "node_name": node_name,
            "vertex_count": vertex_count,
            "polygon_count": polygon_count,
            "triangle_count": triangle_count,
            "uv_sets": uv_sets,
            "transform": transform_data,
            "materials": node_materials,
            "face_assignments": face_assignments
        }

    @classmethod
    def _parse_material(cls, fbx, fbx_mat, fbx_file_path):
        """解析 FbxSurfaceMaterial 的属性与贴图网络"""
        mat_name = fbx_mat.GetName()
        mat_info = {
            "name": mat_name,
            "shader_type": "standardSurface",
            "diffuse_color": [0.8, 0.8, 0.8],
            "diffuse_texture": None,
            "normal_texture": None,
            "roughness_texture": None,
            "metallic_texture": None,
            "specular_texture": None,
            "textures": {}
        }

        if fbx_mat.GetClassId().Is(fbx.FbxSurfacePhong.ClassId):
            mat_info["shader_type"] = "phong"
        elif fbx_mat.GetClassId().Is(fbx.FbxSurfaceLambert.ClassId):
            mat_info["shader_type"] = "lambert"

        diff_prop = fbx_mat.FindProperty(fbx.FbxSurfaceMaterial.sDiffuse)
        if diff_prop.IsValid():
            try:
                diff_val = diff_prop.Get()
                if diff_val:
                    mat_info["diffuse_color"] = [diff_val[0], diff_val[1], diff_val[2]]
            except Exception:
                pass

        fbx_dir = os.path.dirname(fbx_file_path)
        prop_mapping = [
            (fbx.FbxSurfaceMaterial.sDiffuse, "diffuse_texture"),
            (fbx.FbxSurfaceMaterial.sNormalMap, "normal_texture"),
            (fbx.FbxSurfaceMaterial.sBump, "normal_texture"),
            (fbx.FbxSurfaceMaterial.sSpecular, "specular_texture"),
            ("Maya|baseColor", "diffuse_texture"),
            ("Maya|normalCamera", "normal_texture"),
            ("Maya|roughness", "roughness_texture"),
            ("Maya|metalness", "metallic_texture"),
        ]

        for prop_name, target_key in prop_mapping:
            prop = fbx_mat.FindProperty(prop_name)
            if not prop.IsValid():
                continue
            tex_count = prop.GetSrcObjectCount(fbx.FbxCriteria.ObjectType(fbx.FbxFileTexture.ClassId))
            if tex_count > 0:
                tex_obj = prop.GetSrcObject(fbx.FbxCriteria.ObjectType(fbx.FbxFileTexture.ClassId), 0)
                if tex_obj:
                    tex_path = cls._resolve_texture_path(tex_obj, fbx_dir)
                    if tex_path:
                        mat_info[target_key] = tex_path
                        mat_info["textures"][target_key] = tex_path

        return mat_info

    @classmethod
    def _resolve_texture_path(cls, tex_obj, fbx_dir):
        """解析贴图真实物理路径"""
        p = tex_obj.GetFileName()
        if p and os.path.isfile(p):
            return os.path.normpath(p).replace("\\", "/")

        rel_p = tex_obj.GetRelativeFileName()
        if rel_p:
            cand = os.path.normpath(os.path.join(fbx_dir, rel_p)).replace("\\", "/")
            if os.path.isfile(cand):
                return cand

        if p:
            base = os.path.basename(p)
            cand2 = os.path.normpath(os.path.join(fbx_dir, base)).replace("\\", "/")
            if os.path.isfile(cand2):
                return cand2

            tex_sub = os.path.normpath(os.path.join(fbx_dir, "textures", base)).replace("\\", "/")
            if os.path.isfile(tex_sub):
                return tex_sub

            return p.replace("\\", "/")

        return None

    @staticmethod
    def _group_contiguous_ranges(indices):
        """将离散的面索引列表分组压缩为连续区间 [(0, 10), (15, 20)]"""
        if not indices:
            return []
        sorted_indices = sorted(set(indices))
        ranges = []
        start = sorted_indices[0]
        end = sorted_indices[0]

        for idx in sorted_indices[1:]:
            if idx == end + 1:
                end = idx
            else:
                ranges.append((start, end))
                start = idx
                end = idx
        ranges.append((start, end))
        return ranges


# ==============================================================================
# 模块 3：Maya 原生着色器与分面网络构建器 (MayaMaterialBuilder)
# ==============================================================================

class MayaMaterialBuilder(object):
    """负责在 Maya 中根据解析出的材质信息构建 ShadingEngine，并赋予指定物体或分面"""

    @classmethod
    def create_or_get_material_network(cls, mat_info):
        """根据材质描述创建或复用 Maya 材质球与 ShadingEngine"""
        raw_name = mat_info.get("name") or "FBX_Material"
        safe_name = re.sub(r"[^a-zA-Z0-9_]", "_", raw_name)
        if not safe_name or safe_name[0].isdigit():
            safe_name = "mat_" + safe_name

        sg_name = safe_name + "SG"

        if cmds.objExists(sg_name) and cmds.nodeType(sg_name) == "shadingEngine":
            return sg_name

        if cmds.objExists(safe_name):
            sg_conns = cmds.listConnections(safe_name + ".outColor", type="shadingEngine") or []
            if sg_conns:
                return sg_conns[0]

        shader_type = mat_info.get("shader_type", "standardSurface")
        if not cmds.pluginInfo("mtoa", q=True, loaded=True) and shader_type == "standardSurface":
            try:
                cmds.loadPlugin("mtoa", quiet=True)
            except Exception:
                pass

        if not cls._is_node_type_available(shader_type):
            shader_type = "phong"

        shader_node = cmds.shadingNode(shader_type, asShader=True, name=safe_name)
        sg_node = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=sg_name)

        if shader_type == "standardSurface":
            cmds.connectAttr(shader_node + ".outColor", sg_node + ".surfaceShader", force=True)
            diff_col = mat_info.get("diffuse_color", [0.8, 0.8, 0.8])
            cmds.setAttr(shader_node + ".baseColor", diff_col[0], diff_col[1], diff_col[2], type="double3")
            cmds.setAttr(shader_node + ".base", 1.0)
            if mat_info.get("diffuse_texture"):
                cls._connect_file_texture(shader_node + ".baseColor", mat_info["diffuse_texture"])
            if mat_info.get("normal_texture"):
                cls._connect_normal_texture(shader_node, mat_info["normal_texture"])
        else:
            cmds.connectAttr(shader_node + ".outColor", sg_node + ".surfaceShader", force=True)
            diff_col = mat_info.get("diffuse_color", [0.8, 0.8, 0.8])
            cmds.setAttr(shader_node + ".color", diff_col[0], diff_col[1], diff_col[2], type="double3")
            if mat_info.get("diffuse_texture"):
                cls._connect_file_texture(shader_node + ".color", mat_info["diffuse_texture"])
            if mat_info.get("normal_texture"):
                cls._connect_normal_texture(shader_node, mat_info["normal_texture"])

        return sg_node

    @staticmethod
    def _is_node_type_available(node_type):
        try:
            return node_type in cmds.allNodeTypes()
        except Exception:
            return False

    @classmethod
    def _connect_file_texture(cls, target_attr, file_path):
        if not file_path or not os.path.isfile(file_path):
            return None
        file_node = cmds.shadingNode("file", asTexture=True, isColorManaged=True)
        place_node = cmds.shadingNode("place2dTexture", asUtility=True)
        conns = [
            ("coverage", "coverage"),
            ("translateFrame", "translateFrame"),
            ("rotateFrame", "rotateFrame"),
            ("mirrorU", "mirrorU"),
            ("mirrorV", "mirrorV"),
            ("stagger", "stagger"),
            ("wrapU", "wrapU"),
            ("wrapV", "wrapV"),
            ("repeatUV", "repeatUV"),
            ("offset", "offset"),
            ("rotateUV", "rotateUV"),
            ("noiseUV", "noiseUV"),
            ("vertexUvOne", "vertexUvOne"),
            ("vertexUvTwo", "vertexUvTwo"),
            ("vertexUvThree", "vertexUvThree"),
            ("vertexCameraOne", "vertexCameraOne"),
            ("outUV", "uvCoord"),
            ("outUvFilterSize", "uvFilterSize")
        ]
        for src, dst in conns:
            cmds.connectAttr(place_node + "." + src, file_node + "." + dst, force=True)
        cmds.setAttr(file_node + ".fileTextureName", file_path, type="string")
        cmds.connectAttr(file_node + ".outColor", target_attr, force=True)
        return file_node

    @classmethod
    def _connect_normal_texture(cls, shader_node, normal_path):
        if not normal_path or not os.path.isfile(normal_path):
            return None
        bump_node = cmds.shadingNode("bump2d", asUtility=True)
        cmds.setAttr(bump_node + ".bumpInterp", 1)
        file_node = cmds.shadingNode("file", asTexture=True, isColorManaged=True)
        cmds.setAttr(file_node + ".fileTextureName", normal_path, type="string")
        place_node = cmds.shadingNode("place2dTexture", asUtility=True)
        cmds.connectAttr(place_node + ".outUV", file_node + ".uvCoord", force=True)
        cmds.connectAttr(place_node + ".outUvFilterSize", file_node + ".uvFilterSize", force=True)
        cmds.connectAttr(file_node + ".outAlpha", bump_node + ".bumpValue", force=True)
        if cmds.attributeQuery("normalCamera", node=shader_node, exists=True):
            cmds.connectAttr(bump_node + ".outNormal", shader_node + ".normalCamera", force=True)
        return bump_node

    @classmethod
    def assign_to_scene_matching_objects(cls, parsed_data, options=None, log_func=None):
        """将解析出的材质网络对号入座赋予当前场景中的同名物体"""
        if options is None:
            options = {}

        match_by_short_name = options.get("match_by_short_name", True)
        case_insensitive = options.get("case_insensitive", False)
        preserve_face_assignment = options.get("preserve_face_assignment", True)
        fallback_to_object = options.get("fallback_to_object", True)

        def log(msg, level="info"):
            if log_func:
                log_func(msg, level)

        materials_data = parsed_data.get("materials", {})
        meshes_data = parsed_data.get("meshes", [])

        # 1. 预先构建所有材质对应的 ShadingEngine
        sg_map = {}
        for m_name, m_info in materials_data.items():
            try:
                sg_node = cls.create_or_get_material_network(m_info)
                sg_map[m_name] = sg_node
            except Exception as e:
                log("构建材质网络 [{}] 失败: {}".format(m_name, e), "warning")

        # 2. 建立场景物体名称索引
        scene_transforms = cmds.ls(type="transform", long=True) or []
        scene_target_map = {}
        for tr in scene_transforms:
            shapes = cmds.listRelatives(tr, shapes=True, fullPath=True, type="mesh") or []
            if not shapes:
                continue
            short_name = tr.split("|")[-1]
            clean_short = short_name.split(":")[-1]

            keys = [tr, short_name]
            if match_by_short_name:
                keys.append(clean_short)

            for k in keys:
                key = k.lower() if case_insensitive else k
                if key not in scene_target_map:
                    scene_target_map[key] = []
                if tr not in scene_target_map[key]:
                    scene_target_map[key].append(tr)

        # 3. 匹配并赋予
        matched_objects = set()
        assigned_materials = set()

        for mesh_item in meshes_data:
            fbx_mesh_name = mesh_item["node_name"]
            lookup_key = fbx_mesh_name.lower() if case_insensitive else fbx_mesh_name

            targets = scene_target_map.get(lookup_key, [])
            if not targets:
                continue

            face_assignments = mesh_item.get("face_assignments", {})

            for target_obj in targets:
                target_short = target_obj.split("|")[-1]
                matched_objects.add(target_obj)

                for mat_name, ranges in face_assignments.items():
                    sg = sg_map.get(mat_name)
                    if not sg or not cmds.objExists(sg):
                        continue

                    if ranges == "all" or not preserve_face_assignment:
                        try:
                            cmds.sets(target_obj, edit=True, forceElement=sg)
                            assigned_materials.add(sg)
                            log("  -> [整物指定成功] 材质组 [{}] -> 物体 [{}]".format(sg, target_short), "success")
                        except Exception as e:
                            log("  -> [整物指定失败] 物体 [{}]: {}".format(target_short, e), "error")
                    else:
                        face_assign_ok = True
                        for start_idx, end_idx in ranges:
                            comp_str = "{}.f[{}:{}]".format(target_obj, start_idx, end_idx) if start_idx != end_idx else "{}.f[{}]".format(target_obj, start_idx)
                            try:
                                cmds.sets(comp_str, edit=True, forceElement=sg)
                                assigned_materials.add(sg)
                            except Exception as e:
                                face_assign_ok = False
                                log("  -> [分面指定拓扑不符] [{}] 指定失败: {}".format(comp_str, e), "warning")

                        if face_assign_ok:
                            log("  -> [分面指定成功] 材质组 [{}] -> [{}] ({} 个区间)".format(
                                sg, target_short, len(ranges)
                            ), "success")
                        elif fallback_to_object:
                            try:
                                cmds.sets(target_obj, edit=True, forceElement=sg)
                                assigned_materials.add(sg)
                                log("  -> [已安全回退] 拓扑不符，已降级为整物指定 [{}] -> [{}]".format(sg, target_short), "info")
                            except Exception as e:
                                log("  -> [回退指定失败] [{}]: {}".format(target_short, e), "error")

        return {
            "matched_count": len(matched_objects),
            "assigned_materials_count": len(assigned_materials)
        }


# ==============================================================================
# 模块 4：Maya 场景资产深度探针 (MayaSceneInspector)
# ==============================================================================

class MayaSceneInspector(object):
    """提取当前 Maya 场景中网格几何体、材质与空间变换指标，用于与外部 FBX 深度比对"""

    @classmethod
    def inspect_scene_mesh(cls, tr_or_mesh):
        """提取单个 Maya 模型的拓扑、材质分面、UV 通道与变换数据"""
        if cmds.objectType(tr_or_mesh) == "mesh":
            mesh_shape = tr_or_mesh
            parent = cmds.listRelatives(mesh_shape, parent=True, fullPath=True)
            tr = parent[0] if parent else ""
        else:
            tr = cmds.ls(tr_or_mesh, long=True)[0]
            shapes = cmds.listRelatives(tr, shapes=True, fullPath=True, type="mesh") or []
            mesh_shape = shapes[0] if shapes else None

        if not mesh_shape or not cmds.objExists(mesh_shape):
            return None

        # 1. 几何拓扑统计
        v_count = cmds.polyEvaluate(mesh_shape, vertex=True) or 0
        f_count = cmds.polyEvaluate(mesh_shape, face=True) or 0
        t_count = cmds.polyEvaluate(mesh_shape, triangle=True) or 0

        # 2. UV 通道
        uv_sets = cmds.polyUVSet(mesh_shape, query=True, allUVSets=True) or []

        # 3. 空间变换 (位移、旋转、缩放)
        t = cmds.xform(tr, query=True, translation=True, objectSpace=True) or [0.0, 0.0, 0.0]
        r = cmds.xform(tr, query=True, rotation=True, objectSpace=True) or [0.0, 0.0, 0.0]
        s = cmds.xform(tr, query=True, scale=True, objectSpace=True) or [1.0, 1.0, 1.0]

        # 4. 关联材质球与分面情况
        sgs = cmds.listConnections(mesh_shape, type="shadingEngine") or []
        sgs = list(set(sgs))
        materials = []
        face_assignments = {}

        for sg in sgs:
            shaders = cmds.listConnections(sg + ".surfaceShader") or []
            shader_name = shaders[0] if shaders else sg
            materials.append(shader_name)

            members = cmds.sets(sg, query=True) or []
            is_whole = False
            for m in members:
                if m == tr or m == mesh_shape or m.split(".")[0] in (tr, mesh_shape):
                    if ".f[" not in m:
                        is_whole = True
                        break

            if is_whole:
                face_assignments[shader_name] = "all"
            else:
                comp_faces = []
                for m in members:
                    if (tr in m or mesh_shape in m) and ".f[" in m:
                        comp_faces.append(m)
                face_assignments[shader_name] = comp_faces if comp_faces else "all"

        short_name = tr.split("|")[-1]
        clean_name = short_name.split(":")[-1]

        return {
            "node_name": clean_name,
            "short_name": short_name,
            "full_path": tr,
            "shape_name": mesh_shape,
            "vertex_count": v_count,
            "polygon_count": f_count,
            "triangle_count": t_count,
            "uv_sets": uv_sets,
            "materials": materials,
            "face_assignments": face_assignments,
            "transform": {
                "translation": [round(float(x), 4) for x in t],
                "rotation": [round(float(x), 4) for x in r],
                "scaling": [round(float(x), 4) for x in s],
            }
        }

    @classmethod
    def inspect_all_scene_meshes(cls):
        """扫描当前场景所有网格模型并建立多级索引"""
        transforms = cmds.ls(type="transform", long=True) or []
        records = []
        for tr in transforms:
            shapes = cmds.listRelatives(tr, shapes=True, fullPath=True, type="mesh") or []
            if not shapes:
                continue
            rec = cls.inspect_scene_mesh(tr)
            if rec:
                records.append(rec)
        return records


# ==============================================================================
# 模块 5：资产多维度对比引擎 (AssetDiffComparator)
# ==============================================================================

class AssetDiffStatus(object):
    IDENTICAL = "IDENTICAL"              # 🟢 完全吻合
    MATERIAL_DIFF = "MATERIAL_DIFF"      # 🟡 材质差异
    TRANSFORM_DIFF = "TRANSFORM_DIFF"    # 🟠 变换差异
    TOPOLOGY_DIFF = "TOPOLOGY_DIFF"      # 🔴 拓扑冲突
    MISSING_IN_MAYA = "MISSING_IN_MAYA"  # ⚪ 仅在 FBX 存在
    MISSING_IN_FBX = "MISSING_IN_FBX"    # ⚪ 仅在 Maya 存在


class AssetDiffComparator(object):
    """比对 Maya 场景资产与外部 FBX 资产结构，生成全维度差异分析报告"""

    EPSILON = 0.005 # 变换比较浮点容差

    @classmethod
    def compare(cls, fbx_parsed_data, scene_records, options=None):
        if options is None:
            options = {}

        match_short = options.get("match_by_short_name", True)
        case_insensitive = options.get("case_insensitive", False)
        compare_transforms = options.get("compare_transforms", True)

        # 1. 建立场景索引表
        scene_lookup = {}
        for s_rec in scene_records:
            keys = [s_rec["full_path"], s_rec["short_name"]]
            if match_short:
                keys.append(s_rec["node_name"])
            for k in keys:
                k_key = k.lower() if case_insensitive else k
                if k_key not in scene_lookup:
                    scene_lookup[k_key] = []
                if s_rec not in scene_lookup[k_key]:
                    scene_lookup[k_key].append(s_rec)

        fbx_meshes = fbx_parsed_data.get("meshes", [])
        fbx_materials = fbx_parsed_data.get("materials", {})

        diff_results = []
        matched_scene_paths = set()

        # 2. 遍历 FBX 模型与 Maya 场景匹配比对
        for fbx_mesh in fbx_meshes:
            fbx_name = fbx_mesh["node_name"]
            lookup_key = fbx_name.lower() if case_insensitive else fbx_name

            matched_scenes = scene_lookup.get(lookup_key, [])
            if not matched_scenes:
                # 仅在外部 FBX 中存在
                diff_results.append({
                    "name": fbx_name,
                    "status": AssetDiffStatus.MISSING_IN_MAYA,
                    "status_label": "⚪ 仅在FBX存在",
                    "scene_record": None,
                    "fbx_record": fbx_mesh,
                    "fbx_materials": fbx_materials,
                    "diff_details": ["当前 Maya 场景中缺失同名资产，未导入视口"],
                    "topo_diff": True,
                    "mat_diff": True,
                    "transform_diff": False,
                    "can_sync_material": False,
                    "can_sync_transform": False
                })
                continue

            for scene_rec in matched_scenes:
                matched_scene_paths.add(scene_rec["full_path"])
                diff_res = cls._compare_pair(scene_rec, fbx_mesh, fbx_materials, compare_transforms)
                diff_results.append(diff_res)

        # 3. 检查仅在 Maya 中存在的物体
        for s_rec in scene_records:
            if s_rec["full_path"] not in matched_scene_paths:
                diff_results.append({
                    "name": s_rec["short_name"],
                    "status": AssetDiffStatus.MISSING_IN_FBX,
                    "status_label": "⚪ 仅在Maya存在",
                    "scene_record": s_rec,
                    "fbx_record": None,
                    "fbx_materials": fbx_materials,
                    "diff_details": ["外部 FBX 文件中未包含该同名模型"],
                    "topo_diff": False,
                    "mat_diff": False,
                    "transform_diff": False,
                    "can_sync_material": False,
                    "can_sync_transform": False
                })

        return diff_results

    @classmethod
    def _compare_pair(cls, scene_rec, fbx_rec, fbx_materials, compare_transforms=True):
        """对比一对匹配的模型资产"""
        diffs = []
        topo_diff = False
        mat_diff = False
        trans_diff = False

        # 1. 拓扑比对 (顶点数、面数)
        v_maya = scene_rec["vertex_count"]
        v_fbx = fbx_rec["vertex_count"]
        f_maya = scene_rec["polygon_count"]
        f_fbx = fbx_rec["polygon_count"]
        t_maya = scene_rec["triangle_count"]
        t_fbx = fbx_rec["triangle_count"]

        if v_maya != v_fbx:
            diffs.append("顶点数不一致: Maya({}) vs FBX({})".format(v_maya, v_fbx))
            topo_diff = True
        if f_maya != f_fbx:
            diffs.append("多边形面数不一致: Maya({}) vs FBX({})".format(f_maya, f_fbx))
            topo_diff = True
        if not topo_diff and t_maya != t_fbx:
            diffs.append("三角化面数差异: Maya({}) vs FBX({})".format(t_maya, t_fbx))

        # 2. UV 通道比对
        uv_maya = set(scene_rec["uv_sets"])
        uv_fbx = set(fbx_rec.get("uv_sets", []))
        if uv_maya != uv_fbx and uv_fbx:
            diffs.append("UV集不同: Maya{} vs FBX{}".format(list(uv_maya), list(uv_fbx)))

        # 3. 材质与分面分配比对
        mats_maya = set(scene_rec["materials"])
        mats_fbx = set(fbx_rec.get("materials", []))
        if mats_maya != mats_fbx:
            diffs.append("材质球列表不同: Maya{} vs FBX{}".format(list(mats_maya), list(mats_fbx)))
            mat_diff = True
        else:
            fa_maya = scene_rec.get("face_assignments", {})
            fa_fbx = fbx_rec.get("face_assignments", {})
            for m_name in mats_fbx:
                val_m = fa_maya.get(m_name)
                val_f = fa_fbx.get(m_name)
                if val_m != val_f and (val_m != "all" or val_f != "all"):
                    diffs.append("材质 [{}] 分面分配区间不一致".format(m_name))
                    mat_diff = True
                    break

        # 4. 空间变换比对 (位移、旋转、缩放)
        if compare_transforms:
            tr_maya = scene_rec["transform"]
            tr_fbx = fbx_rec["transform"]
            dt = [abs(a - b) for a, b in zip(tr_maya["translation"], tr_fbx["translation"])]
            dr = [abs(a - b) for a, b in zip(tr_maya["rotation"], tr_fbx["rotation"])]
            ds = [abs(a - b) for a, b in zip(tr_maya["scaling"], tr_fbx["scaling"])]

            if any(val > cls.EPSILON for val in dt):
                diffs.append("坐标位移偏差: ΔT=({:.2f}, {:.2f}, {:.2f})".format(*dt))
                trans_diff = True
            if any(val > 0.05 for val in dr):
                diffs.append("旋转角度偏差: ΔR=({:.1f}°, {:.1f}°, {:.1f}°)".format(*dr))
                trans_diff = True
            if any(val > cls.EPSILON for val in ds):
                diffs.append("缩放比例偏差: ΔS=({:.2f}, {:.2f}, {:.2f})".format(*ds))
                trans_diff = True

        # 5. 判定最终综合状态
        if topo_diff:
            status = AssetDiffStatus.TOPOLOGY_DIFF
            status_label = "🔴 拓扑冲突"
        elif mat_diff:
            status = AssetDiffStatus.MATERIAL_DIFF
            status_label = "🟡 材质差异"
        elif trans_diff:
            status = AssetDiffStatus.TRANSFORM_DIFF
            status_label = "🟠 变换差异"
        else:
            status = AssetDiffStatus.IDENTICAL
            status_label = "🟢 完全吻合"
            diffs.append("拓扑、材质与变换数据完全一致")

        return {
            "name": scene_rec["short_name"],
            "clean_name": scene_rec["node_name"],
            "status": status,
            "status_label": status_label,
            "scene_record": scene_rec,
            "fbx_record": fbx_rec,
            "fbx_materials": fbx_materials,
            "diff_details": diffs,
            "topo_diff": topo_diff,
            "mat_diff": mat_diff,
            "transform_diff": trans_diff,
            "can_sync_material": True,
            "can_sync_transform": True
        }


# ==============================================================================
# 模块 6：资产差异修复与同步引擎 (AssetDiffSyncEngine)
# ==============================================================================

class AssetDiffSyncEngine(object):
    """针对比对结果执行精准同步：同步材质、同步变换、视口高亮标亮或导出报告"""

    @classmethod
    def sync_materials(cls, diff_items, options=None, log_func=None):
        """仅针对选中的资产，将外部 FBX 材质同步赋予当前 Maya 物体"""
        if options is None:
            options = {}

        def log(msg, level="info"):
            if log_func:
                log_func(msg, level)

        valid_items = [it for it in diff_items if it.get("can_sync_material") and it.get("scene_record") and it.get("fbx_record")]
        if not valid_items:
            log("未选中任何可同步材质的有效资产。", "warning")
            return 0

        cmds.undoInfo(openChunk=True, chunkName="SyncFBXAssetMaterials")
        synced_count = 0

        try:
            for item in valid_items:
                fbx_mesh = item["fbx_record"]
                materials_dict = item.get("fbx_materials", {})
                scene_node = item["scene_record"]["full_path"]

                parsed_subset = {
                    "materials": materials_dict,
                    "meshes": [fbx_mesh]
                }

                log("正在为物体 [{}] 同步材质与分面...".format(item["name"]), "info")
                try:
                    res = MayaMaterialBuilder.assign_to_scene_matching_objects(
                        parsed_subset, options=options, log_func=log_func
                    )
                    if res["matched_count"] > 0:
                        synced_count += 1
                        item["status"] = AssetDiffStatus.IDENTICAL if not item["transform_diff"] else AssetDiffStatus.TRANSFORM_DIFF
                        item["status_label"] = "🟢 材质已同步"
                        item["mat_diff"] = False
                except Exception as e:
                    log("同步 [{}] 材质失败: {}".format(item["name"], e), "error")

        finally:
            cmds.undoInfo(closeChunk=True)

        log("材质同步操作完成！成功同步 {} 个资产。".format(synced_count), "success")
        return synced_count

    @classmethod
    def sync_transforms(cls, diff_items, log_func=None):
        """将选中的资产在场景中的位移、旋转、缩放对齐到外部 FBX"""
        def log(msg, level="info"):
            if log_func:
                log_func(msg, level)

        valid_items = [it for it in diff_items if it.get("can_sync_transform") and it.get("scene_record") and it.get("fbx_record")]
        if not valid_items:
            log("未选中任何可同步变换的资产。", "warning")
            return 0

        cmds.undoInfo(openChunk=True, chunkName="SyncFBXAssetTransforms")
        synced_count = 0

        try:
            for item in valid_items:
                scene_node = item["scene_record"]["full_path"]
                if not cmds.objExists(scene_node):
                    continue

                fbx_tr = item["fbx_record"]["transform"]
                t = fbx_tr["translation"]
                r = fbx_tr["rotation"]
                s = fbx_tr["scaling"]

                try:
                    cmds.xform(scene_node, translation=t, rotation=r, scale=s, objectSpace=True)
                    synced_count += 1
                    item["transform_diff"] = False
                    if not item["mat_diff"] and not item["topo_diff"]:
                        item["status"] = AssetDiffStatus.IDENTICAL
                        item["status_label"] = "🟢 变换已同步"
                    log("已对齐物体变换 [{}] -> T:{} R:{} S:{}".format(item["name"], t, r, s), "success")
                except Exception as e:
                    log("对齐 [{}] 变换失败: {}".format(item["name"], e), "error")

        finally:
            cmds.undoInfo(closeChunk=True)

        log("变换同步完成！成功对齐 {} 个物体的空间位姿。".format(synced_count), "success")
        return synced_count

    @classmethod
    def select_in_scene(cls, diff_items, log_func=None):
        """在 Maya 视口和大纲中高亮选中指定项并对焦"""
        nodes_to_select = []
        for it in diff_items:
            s_rec = it.get("scene_record")
            if s_rec and cmds.objExists(s_rec["full_path"]):
                nodes_to_select.append(s_rec["full_path"])

        if nodes_to_select:
            cmds.select(nodes_to_select, replace=True)
            try:
                cmds.viewFit()
            except Exception:
                pass
            if log_func:
                log_func("已在场景中高亮选中 {} 个资产并对齐视口焦点。".format(len(nodes_to_select)), "info")
            return len(nodes_to_select)
        return 0

    @classmethod
    def export_diff_report(cls, diff_items, fbx_file_path, out_path=None):
        """生成详细的比对报告 Markdown 文件"""
        if not out_path:
            base_name = os.path.splitext(os.path.basename(fbx_file_path))[0]
            out_path = os.path.join(os.path.expanduser("~"), "FBX_Diff_Report_{}.md".format(base_name))

        lines = [
            "# Maya 场景 vs 外部 FBX 资产差异比对核查报告",
            "",
            "- **比对目标文件**：`{}`".format(fbx_file_path),
            "- **生成时间**：{}".format(time.strftime("%Y-%m-%d %H:%M:%S")),
            "- **资产核查总数**：{} 个".format(len(diff_items)),
            "",
            "## 比对概览清单",
            "",
            "| 状态 | 资产名称 | 拓扑 (Maya/FBX点面) | 材质差异 | 空间变换差异 | 详情说明 |",
            "| :--- | :--- | :--- | :--- | :--- | :--- |"
        ]

        for it in diff_items:
            s_rec = it.get("scene_record")
            f_rec = it.get("fbx_record")

            topo_str = "-"
            if s_rec and f_rec:
                topo_str = "V:{}/{} F:{}/{}".format(
                    s_rec["vertex_count"], f_rec["vertex_count"],
                    s_rec["polygon_count"], f_rec["polygon_count"]
                )

            mat_str = "有差异" if it["mat_diff"] else "一致"
            trans_str = "有偏差" if it["transform_diff"] else "一致"
            detail_str = "; ".join(it["diff_details"][:2])

            lines.append("| {} | **{}** | {} | {} | {} | {} |".format(
                it["status_label"], it["name"], topo_str, mat_str, trans_str, detail_str
            ))

        with open(out_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        return out_path


# ==============================================================================
# 模块 7：UI 界面组件 (PySide2 / PySide6 跨版本兼容)
# ==============================================================================

class FBXAssetDiffDialog(QtWidgets.QDialog):
    """FBX 资产深度比对与差异同步工具主窗口"""
    WINDOW_TITLE = "FBX 资产深度比对与差异同步工具 (FBX SDK Asset Diff & Sync Inspector)"
    WINDOW_OBJECT_NAME = "MayaFBXSDKAssetDiffDialogWin"

    def __init__(self, parent=None):
        super(FBXAssetDiffDialog, self).__init__(parent or self._get_maya_main_window())
        self.setObjectName(self.WINDOW_OBJECT_NAME)
        self.setWindowTitle(self.WINDOW_TITLE)
        self.resize(1120, 780)

        self._all_diff_records = []
        self._filtered_records = []
        self._current_filter = "ALL"
        self._current_fbx_path = ""
        self._parsed_fbx_data = None

        self._init_ui()
        self._apply_dark_style()
        self._update_sdk_status()

    @staticmethod
    def _get_maya_main_window():
        """获取 Maya 主窗口句柄"""
        try:
            import maya.OpenMayaUI as omui
            if hasattr(omui.MQtUtil, "mainWindow"):
                ptr = omui.MQtUtil.mainWindow()
                if ptr is not None:
                    try:
                        import shiboken6
                        return shiboken6.wrapInstance(int(ptr), QtWidgets.QWidget)
                    except ImportError:
                        try:
                            import shiboken2
                            return shiboken2.wrapInstance(int(ptr), QtWidgets.QWidget)
                        except ImportError:
                            pass
        except Exception:
            pass
        return None

    def _init_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(8)

        # ----------------------------------------------------------------------
        # 1. 核心引擎状态与 FBX 文件选择区
        # ----------------------------------------------------------------------
        top_group = QtWidgets.QGroupBox("核心引擎与比对目标 FBX 文件")
        top_layout = QtWidgets.QVBoxLayout(top_group)
        top_layout.setSpacing(6)

        status_row = QtWidgets.QHBoxLayout()
        self.lbl_engine_status = QtWidgets.QLabel("● 引擎模式: 正在探测 Autodesk FBX SDK...")
        self.lbl_engine_status.setStyleSheet("color: #4cd964; font-weight: bold;")
        status_row.addWidget(self.lbl_engine_status)
        status_row.addStretch()

        lbl_custom_sdk = QtWidgets.QLabel("自定义 SDK 路径:")
        self.edit_sdk_path = QtWidgets.QLineEdit()
        self.edit_sdk_path.setPlaceholderText("留空自动探测，或指定包含 fbx.pyd 的目录...")
        self.edit_sdk_path.setFixedWidth(240)
        self.btn_load_sdk = QtWidgets.QPushButton("加载 SDK")
        self.btn_load_sdk.clicked.connect(self._on_custom_sdk_load)

        status_row.addWidget(lbl_custom_sdk)
        status_row.addWidget(self.edit_sdk_path)
        status_row.addWidget(self.btn_load_sdk)
        top_layout.addLayout(status_row)

        file_row = QtWidgets.QHBoxLayout()
        lbl_file = QtWidgets.QLabel("外部 FBX 目标:")
        lbl_file.setStyleSheet("font-weight: bold;")
        self.edit_fbx_path = QtWidgets.QLineEdit()
        self.edit_fbx_path.setPlaceholderText("拖拽 FBX 文件到此输入框，或点击右侧浏览选择...")
        self.btn_browse = QtWidgets.QPushButton("浏览...")
        self.btn_browse.setFixedWidth(75)
        self.btn_browse.clicked.connect(self._on_browse_fbx)

        self.btn_run_compare = QtWidgets.QPushButton("🔍 开始全维度资产深度比对")
        self.btn_run_compare.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1a73e8, stop:1 #00a86b);
                color: #ffffff;
                font-weight: bold;
                font-size: 13px;
                padding: 6px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2b82f6, stop:1 #10b981);
            }
        """)
        self.btn_run_compare.clicked.connect(self._on_run_compare)

        file_row.addWidget(lbl_file)
        file_row.addWidget(self.edit_fbx_path)
        file_row.addWidget(self.btn_browse)
        file_row.addWidget(self.btn_run_compare)
        top_layout.addLayout(file_row)
        main_layout.addWidget(top_group)

        # ----------------------------------------------------------------------
        # 2. 状态过滤器与搜索栏
        # ----------------------------------------------------------------------
        filter_layout = QtWidgets.QHBoxLayout()
        filter_layout.setSpacing(6)

        lbl_filter = QtWidgets.QLabel("资产筛选:")
        lbl_filter.setStyleSheet("font-weight: bold;")
        filter_layout.addWidget(lbl_filter)

        self.btn_filter_all = QtWidgets.QPushButton("全部 (0)")
        self.btn_filter_diff = QtWidgets.QPushButton("仅差异 (0)")
        self.btn_filter_mat = QtWidgets.QPushButton("🟡 材质差异 (0)")
        self.btn_filter_topo = QtWidgets.QPushButton("🔴 拓扑冲突 (0)")
        self.btn_filter_trans = QtWidgets.QPushButton("🟠 变换差异 (0)")
        self.btn_filter_ident = QtWidgets.QPushButton("🟢 完全吻合 (0)")
        self.btn_filter_miss = QtWidgets.QPushButton("⚪ 单侧缺失 (0)")

        self.filter_btn_group = [
            ("ALL", self.btn_filter_all),
            ("DIFF", self.btn_filter_diff),
            (AssetDiffStatus.MATERIAL_DIFF, self.btn_filter_mat),
            (AssetDiffStatus.TOPOLOGY_DIFF, self.btn_filter_topo),
            (AssetDiffStatus.TRANSFORM_DIFF, self.btn_filter_trans),
            (AssetDiffStatus.IDENTICAL, self.btn_filter_ident),
            ("MISSING", self.btn_filter_miss)
        ]

        for code, btn in self.filter_btn_group:
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked=False, c=code: self._on_filter_changed(c))
            filter_layout.addWidget(btn)

        self.btn_filter_all.setChecked(True)
        filter_layout.addSpacing(10)

        self.edit_search = QtWidgets.QLineEdit()
        self.edit_search.setPlaceholderText("实时搜索过滤资产名称...")
        self.edit_search.textChanged.connect(self._apply_filter_and_search)
        filter_layout.addWidget(self.edit_search)

        filter_layout.addSpacing(10)
        self.chk_match_short = QtWidgets.QCheckBox("忽略命名空间匹配同名")
        self.chk_match_short.setChecked(True)
        self.chk_fallback_topo = QtWidgets.QCheckBox("拓扑不符时安全回退")
        self.chk_fallback_topo.setChecked(True)
        filter_layout.addWidget(self.chk_match_short)
        filter_layout.addWidget(self.chk_fallback_topo)

        main_layout.addLayout(filter_layout)

        # ----------------------------------------------------------------------
        # 3. 核心区域：上下分栏 (上：资产对比表；下：双列对照卡片)
        # ----------------------------------------------------------------------
        self.splitter = QtWidgets.QSplitter(Qt.Vertical)

        # 上半部：比对结果总览表
        table_container = QtWidgets.QWidget()
        table_vbox = QtWidgets.QVBoxLayout(table_container)
        table_vbox.setContentsMargins(0, 0, 0, 0)
        table_vbox.setSpacing(4)

        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "启用", "比对状态", "资产名称", "网格拓扑", "材质着色", "空间变换", "UV通道", "差异概要说明"
        ])
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(True)
        self.table.itemSelectionChanged.connect(self._on_table_selection_changed)
        self.table.itemChanged.connect(self._on_table_item_changed)

        # 设置列宽
        self.table.setColumnWidth(0, 45)
        self.table.setColumnWidth(1, 105)
        self.table.setColumnWidth(2, 160)
        self.table.setColumnWidth(3, 140)
        self.table.setColumnWidth(4, 140)
        self.table.setColumnWidth(5, 130)
        self.table.setColumnWidth(6, 110)

        table_vbox.addWidget(self.table)
        self.splitter.addWidget(table_container)

        # 下半部：双列属性逐项对照详情面板 (Side-by-Side Diff)
        detail_container = QtWidgets.QGroupBox("资产属性逐项双列对照详情 (在上方表格中选择任意资产)")
        self.group_detail = detail_container
        detail_vbox = QtWidgets.QVBoxLayout(detail_container)
        detail_vbox.setContentsMargins(8, 8, 8, 8)
        detail_vbox.setSpacing(4)

        self.detail_table = QtWidgets.QTableWidget()
        self.detail_table.setColumnCount(4)
        self.detail_table.setHorizontalHeaderLabels([
            "对比指标", "Maya 场景当前状态", "外部 FBX 目标状态", "比对结论"
        ])
        self.detail_table.horizontalHeader().setStretchLastSection(True)
        self.detail_table.verticalHeader().setVisible(False)
        self.detail_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.detail_table.setColumnWidth(0, 150)
        self.detail_table.setColumnWidth(1, 300)
        self.detail_table.setColumnWidth(2, 300)

        detail_vbox.addWidget(self.detail_table)
        self.splitter.addWidget(detail_container)

        # 设置 Splitter 初始高度比例 (60% 上，40% 下)
        self.splitter.setSizes([360, 240])
        main_layout.addWidget(self.splitter)

        # ----------------------------------------------------------------------
        # 4. 底部差异修复与同步动作栏
        # ----------------------------------------------------------------------
        action_layout = QtWidgets.QHBoxLayout()
        action_layout.setSpacing(8)

        self.btn_select_all = QtWidgets.QPushButton("全选")
        self.btn_select_all.setFixedWidth(60)
        self.btn_select_all.clicked.connect(lambda: self._set_all_checked(True))

        self.btn_deselect_all = QtWidgets.QPushButton("全不选")
        self.btn_deselect_all.setFixedWidth(60)
        self.btn_deselect_all.clicked.connect(lambda: self._set_all_checked(False))

        self.lbl_summary = QtWidgets.QLabel("就绪: 请载入外部 FBX 开始比对")
        self.lbl_summary.setStyleSheet("color: #a0a0a0; font-weight: bold;")

        action_layout.addWidget(self.btn_select_all)
        action_layout.addWidget(self.btn_deselect_all)
        action_layout.addWidget(self.lbl_summary)
        action_layout.addStretch()

        self.btn_select_scene = QtWidgets.QPushButton("🎯 视口高亮对焦选中项")
        self.btn_select_scene.setToolTip("在 Maya 视口和大纲中高亮选中所选物体，并自动对焦视图")
        self.btn_select_scene.clicked.connect(self._on_action_select_scene)

        self.btn_export_report = QtWidgets.QPushButton("📄 导出核查报告")
        self.btn_export_report.setToolTip("将本次比对的完整结果导出为详细的 Markdown 审核报告文件")
        self.btn_export_report.clicked.connect(self._on_action_export_report)

        self.btn_sync_transform = QtWidgets.QPushButton("📐 一键同步选中变换")
        self.btn_sync_transform.setToolTip("将选中资产的位移坐标、旋转角度与缩放比例对齐到外部 FBX")
        self.btn_sync_transform.clicked.connect(self._on_action_sync_transforms)

        self.btn_sync_material = QtWidgets.QPushButton("✨ 一键同步选中材质与分面")
        self.btn_sync_material.setStyleSheet("""
            QPushButton {
                background-color: #2b78e4;
                color: #ffffff;
                font-weight: bold;
                padding: 6px 14px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #3b88f4;
            }
        """)
        self.btn_sync_material.setToolTip("将外部 FBX 中的材质网络与分面指派重构并赋予选中资产 (纯内存直读)")
        self.btn_sync_material.clicked.connect(self._on_action_sync_materials)

        action_layout.addWidget(self.btn_select_scene)
        action_layout.addWidget(self.btn_export_report)
        action_layout.addWidget(self.btn_sync_transform)
        action_layout.addWidget(self.btn_sync_material)
        main_layout.addLayout(action_layout)

        # ----------------------------------------------------------------------
        # 5. 日志与信息反馈控制台
        # ----------------------------------------------------------------------
        self.txt_log = QtWidgets.QTextEdit()
        self.txt_log.setReadOnly(True)
        self.txt_log.setFixedHeight(80)
        main_layout.addWidget(self.txt_log)

    def _apply_dark_style(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
                color: #e0e0e0;
                font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
                font-size: 12px;
            }
            QGroupBox {
                border: 1px solid #333333;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
                color: #9cdcfe;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
            }
            QTableWidget {
                background-color: #252526;
                alternate-background-color: #2a2a2c;
                gridline-color: #383838;
                border: 1px solid #333333;
                border-radius: 4px;
                color: #e0e0e0;
                selection-background-color: #094771;
                selection-color: #ffffff;
            }
            QHeaderView::section {
                background-color: #2d2d30;
                color: #cccccc;
                padding: 4px 6px;
                border: 1px solid #383838;
                font-weight: bold;
            }
            QLineEdit {
                background-color: #2d2d30;
                border: 1px solid #3e3e42;
                border-radius: 3px;
                padding: 4px 8px;
                color: #f1f1f1;
            }
            QLineEdit:focus {
                border: 1px solid #007acc;
            }
            QPushButton {
                background-color: #333337;
                border: 1px solid #434346;
                border-radius: 3px;
                color: #cccccc;
                padding: 4px 10px;
            }
            QPushButton:hover {
                background-color: #3e3e42;
                color: #ffffff;
            }
            QPushButton:checked {
                background-color: #094771;
                border-color: #007acc;
                color: #ffffff;
                font-weight: bold;
            }
            QCheckBox {
                color: #cccccc;
                spacing: 5px;
            }
            QTextEdit {
                background-color: #1a1a1a;
                border: 1px solid #333333;
                border-radius: 4px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 11px;
                color: #d4d4d4;
            }
            QSplitter::handle {
                background-color: #333333;
                height: 4px;
            }
        """)

    def _update_sdk_status(self):
        if FBXSDKManager.is_sdk_available():
            self.lbl_engine_status.setText("● 引擎模式: Autodesk FBX SDK (纯内存极速解析，零场景污染)")
            self.lbl_engine_status.setStyleSheet("color: #4cd964; font-weight: bold;")
        else:
            self.lbl_engine_status.setText("● 引擎模式: 未检测到 fbx 模块 (可在右上角指定路径加载)")
            self.lbl_engine_status.setStyleSheet("color: #ffd60a; font-weight: bold;")

    def _on_custom_sdk_load(self):
        custom_path = self.edit_sdk_path.text().strip()
        if not custom_path:
            custom_path = QtWidgets.QFileDialog.getExistingDirectory(
                self, "选择 FBX SDK Python 库目录 (包含 fbx.pyd)", os.path.expanduser("~")
            )
            if custom_path:
                self.edit_sdk_path.setText(custom_path)

        if custom_path:
            ok = FBXSDKManager.load_sdk_from_custom_path(custom_path)
            if ok:
                self._log("成功从 [{}] 加载 Autodesk FBX SDK！".format(custom_path), "success")
            else:
                self._log("无法从 [{}] 加载 FBX SDK，请确认该目录包含与当前 Python 版本匹配的 fbx.pyd。".format(custom_path), "warning")
            self._update_sdk_status()

    def _on_browse_fbx(self):
        start_dir = os.path.expanduser("~")
        curr = self.edit_fbx_path.text().strip()
        if curr and os.path.isfile(curr):
            start_dir = os.path.dirname(curr)

        f, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "选择要比对的外部 FBX 文件", start_dir, "FBX 文件 (*.fbx)"
        )
        if f:
            norm_f = os.path.normpath(f).replace("\\", "/")
            self.edit_fbx_path.setText(norm_f)

    # --------------------------------------------------------------------------
    # 资产比对执行
    # --------------------------------------------------------------------------

    def _on_run_compare(self):
        fbx_path = self.edit_fbx_path.text().strip().replace("\"", "").replace("\'", "")
        if not fbx_path or not os.path.isfile(fbx_path):
            QtWidgets.QMessageBox.warning(self, "提示", "请先选择有效的外部 FBX 文件！")
            return

        self._current_fbx_path = os.path.normpath(fbx_path).replace("\\", "/")
        self._log("=== 开始执行 Maya 场景资产与外部 FBX 深度比对 ===", "info")

        try:
            # 1. 解析外部 FBX
            self._parsed_fbx_data = FBXSDKParser.parse_file(self._current_fbx_path, log_func=self._log)
            fbx_mesh_count = len(self._parsed_fbx_data.get("meshes", []))
            fbx_mat_count = len(self._parsed_fbx_data.get("materials", {}))

            # 2. 扫描 Maya 场景资产
            scene_meshes = MayaSceneInspector.inspect_all_scene_meshes()
            self._log("已扫描当前 Maya 场景中的 {} 个网格物体。".format(len(scene_meshes)), "info")

            # 3. 执行对比分析
            options = {
                "match_by_short_name": self.chk_match_short.isChecked(),
                "case_insensitive": False,
                "compare_transforms": True
            }
            diff_results = AssetDiffComparator.compare(self._parsed_fbx_data, scene_meshes, options=options)

            self._all_diff_records = []
            for r in diff_results:
                r["checked"] = (r["status"] != AssetDiffStatus.IDENTICAL and r.get("scene_record") is not None)
                self._all_diff_records.append(r)

            # 4. 更新过滤计数与表格
            self._update_filter_counts()
            self._apply_filter_and_search()

            self._log("比对分析完成！共核查 {} 个资产项目。".format(len(self._all_diff_records)), "success")

        except Exception as e:
            err = traceback.format_exc()
            self._log("比对过程中出现异常: {}".format(err), "error")
            QtWidgets.QMessageBox.critical(self, "比对异常", "比对失败:\n{}".format(e))

    def _update_filter_counts(self):
        c_all = len(self._all_diff_records)
        c_diff = sum(1 for r in self._all_diff_records if r["status"] != AssetDiffStatus.IDENTICAL)
        c_mat = sum(1 for r in self._all_diff_records if r["status"] == AssetDiffStatus.MATERIAL_DIFF)
        c_topo = sum(1 for r in self._all_diff_records if r["status"] == AssetDiffStatus.TOPOLOGY_DIFF)
        c_trans = sum(1 for r in self._all_diff_records if r["status"] == AssetDiffStatus.TRANSFORM_DIFF)
        c_ident = sum(1 for r in self._all_diff_records if r["status"] == AssetDiffStatus.IDENTICAL)
        c_miss = sum(1 for r in self._all_diff_records if "MISSING" in r["status"])

        self.btn_filter_all.setText("全部 ({})".format(c_all))
        self.btn_filter_diff.setText("仅差异 ({})".format(c_diff))
        self.btn_filter_mat.setText("🟡 材质差异 ({})".format(c_mat))
        self.btn_filter_topo.setText("🔴 拓扑冲突 ({})".format(c_topo))
        self.btn_filter_trans.setText("🟠 变换差异 ({})".format(c_trans))
        self.btn_filter_ident.setText("🟢 完全吻合 ({})".format(c_ident))
        self.btn_filter_miss.setText("⚪ 单侧缺失 ({})".format(c_miss))

    def _on_filter_changed(self, filter_code):
        self._current_filter = filter_code
        for code, btn in self.filter_btn_group:
            btn.setChecked(code == filter_code)
        self._apply_filter_and_search()

    def _apply_filter_and_search(self):
        search_txt = self.edit_search.text().strip().lower()
        self._filtered_records = []

        for r in self._all_diff_records:
            # 状态过滤
            if self._current_filter == "DIFF":
                if r["status"] == AssetDiffStatus.IDENTICAL:
                    continue
            elif self._current_filter == "MISSING":
                if "MISSING" not in r["status"]:
                    continue
            elif self._current_filter != "ALL":
                if r["status"] != self._current_filter:
                    continue

            # 关键字搜索
            if search_txt:
                if search_txt not in r["name"].lower():
                    continue

            self._filtered_records.append(r)

        self._refresh_main_table()

    def _refresh_main_table(self):
        self.table.blockSignals(True)
        self.table.setRowCount(len(self._filtered_records))

        for row, rec in enumerate(self._filtered_records):
            # 0. 复选框
            chk = QtWidgets.QTableWidgetItem()
            chk.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            chk.setCheckState(Qt.Checked if rec["checked"] else Qt.Unchecked)
            self.table.setItem(row, 0, chk)

            # 1. 比对状态
            status_item = QtWidgets.QTableWidgetItem(rec["status_label"])
            status_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            status_item.setTextAlignment(Qt.AlignCenter)
            if rec["status"] == AssetDiffStatus.IDENTICAL:
                status_item.setForeground(QtGui.QColor("#4cd964"))
            elif rec["status"] == AssetDiffStatus.MATERIAL_DIFF:
                status_item.setForeground(QtGui.QColor("#ffd60a"))
            elif rec["status"] == AssetDiffStatus.TRANSFORM_DIFF:
                status_item.setForeground(QtGui.QColor("#ff9f0a"))
            elif rec["status"] == AssetDiffStatus.TOPOLOGY_DIFF:
                status_item.setForeground(QtGui.QColor("#ff453a"))
            else:
                status_item.setForeground(QtGui.QColor("#8e8e93"))
            self.table.setItem(row, 1, status_item)

            # 2. 资产名称
            name_item = QtWidgets.QTableWidgetItem(rec["name"])
            name_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            name_item.setFont(QtGui.QFont("Segoe UI", 9, QtGui.QFont.Bold))
            self.table.setItem(row, 2, name_item)

            # 3. 网格拓扑状态
            s_rec = rec.get("scene_record")
            f_rec = rec.get("fbx_record")
            if s_rec and f_rec:
                if rec["topo_diff"]:
                    topo_str = "冲突: V:{}/{} F:{}/{}".format(s_rec["vertex_count"], f_rec["vertex_count"], s_rec["polygon_count"], f_rec["polygon_count"])
                    topo_color = QtGui.QColor("#ff453a")
                else:
                    topo_str = "吻合 (点{} / 面{})".format(s_rec["vertex_count"], s_rec["polygon_count"])
                    topo_color = QtGui.QColor("#4cd964")
            elif s_rec:
                topo_str = "仅场景 (点{} / 面{})".format(s_rec["vertex_count"], s_rec["polygon_count"])
                topo_color = QtGui.QColor("#8e8e93")
            else:
                topo_str = "仅FBX (点{} / 面{})".format(f_rec["vertex_count"], f_rec["polygon_count"])
                topo_color = QtGui.QColor("#8e8e93")

            topo_item = QtWidgets.QTableWidgetItem(topo_str)
            topo_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            topo_item.setForeground(topo_color)
            self.table.setItem(row, 3, topo_item)

            # 4. 材质状态
            if s_rec and f_rec:
                if rec["mat_diff"]:
                    mat_str = "材质差异 (Maya{} vs FBX{})".format(len(s_rec["materials"]), len(f_rec.get("materials", [])))
                    mat_color = QtGui.QColor("#ffd60a")
                else:
                    mat_str = "吻合 ({}个材质)".format(len(s_rec["materials"]))
                    mat_color = QtGui.QColor("#4cd964")
            else:
                mat_str = "-"
                mat_color = QtGui.QColor("#8e8e93")

            mat_item = QtWidgets.QTableWidgetItem(mat_str)
            mat_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            mat_item.setForeground(mat_color)
            self.table.setItem(row, 4, mat_item)

            # 5. 变换状态
            if s_rec and f_rec:
                if rec["transform_diff"]:
                    trans_str = "位姿有偏差"
                    trans_color = QtGui.QColor("#ff9f0a")
                else:
                    trans_str = "位姿一致"
                    trans_color = QtGui.QColor("#4cd964")
            else:
                trans_str = "-"
                trans_color = QtGui.QColor("#8e8e93")

            trans_item = QtWidgets.QTableWidgetItem(trans_str)
            trans_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            trans_item.setForeground(trans_color)
            self.table.setItem(row, 5, trans_item)

            # 6. UV 通道
            uv_str = ", ".join(f_rec.get("uv_sets", [])) if f_rec else (", ".join(s_rec["uv_sets"]) if s_rec else "-")
            uv_item = QtWidgets.QTableWidgetItem(uv_str)
            uv_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.table.setItem(row, 6, uv_item)

            # 7. 差异概要说明
            diff_summary = "; ".join(rec["diff_details"])
            detail_item = QtWidgets.QTableWidgetItem(diff_summary)
            detail_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            detail_item.setToolTip(diff_summary)
            self.table.setItem(row, 7, detail_item)

        self.table.blockSignals(False)

        total = len(self._all_diff_records)
        selected = sum(1 for r in self._all_diff_records if r["checked"])
        self.lbl_summary.setText("共检索 {} 个资产 (当前视图 {} 个，已勾选 {} 个)".format(
            total, len(self._filtered_records), selected
        ))

        # 默认选中第一行并刷新详情
        if self._filtered_records:
            self.table.selectRow(0)

    def _on_table_item_changed(self, item):
        if item and item.column() == 0:
            row = item.row()
            if 0 <= row < len(self._filtered_records):
                self._filtered_records[row]["checked"] = (item.checkState() == Qt.Checked)
                selected = sum(1 for r in self._all_diff_records if r["checked"])
                self.lbl_summary.setText("共检索 {} 个资产 (当前视图 {} 个，已勾选 {} 个)".format(
                    len(self._all_diff_records), len(self._filtered_records), selected
                ))

    def _on_table_selection_changed(self):
        sel_rows = self.table.selectionModel().selectedRows()
        if not sel_rows:
            return
        row = sel_rows[0].row()
        if 0 <= row < len(self._filtered_records):
            rec = self._filtered_records[row]
            self._populate_detail_inspector(rec)

    def _populate_detail_inspector(self, rec):
        """填充双列对照卡片属性详情"""
        self.group_detail.setTitle("【资产属性逐项双列对照详情: {}】".format(rec["name"]))

        s_rec = rec.get("scene_record")
        f_rec = rec.get("fbx_record")

        items_to_compare = [
            ("顶点总数 (Vertices)",
             str(s_rec["vertex_count"]) if s_rec else "缺失",
             str(f_rec["vertex_count"]) if f_rec else "缺失",
             (s_rec and f_rec and s_rec["vertex_count"] == f_rec["vertex_count"])),

            ("多边形面数 (Polygons)",
             str(s_rec["polygon_count"]) if s_rec else "缺失",
             str(f_rec["polygon_count"]) if f_rec else "缺失",
             (s_rec and f_rec and s_rec["polygon_count"] == f_rec["polygon_count"])),

            ("三角面总数 (Triangles)",
             str(s_rec["triangle_count"]) if s_rec else "缺失",
             str(f_rec["triangle_count"]) if f_rec else "缺失",
             (s_rec and f_rec and s_rec["triangle_count"] == f_rec["triangle_count"])),

            ("UV 通道集合 (UV Sets)",
             str(s_rec["uv_sets"]) if s_rec else "缺失",
             str(f_rec["uv_sets"]) if f_rec else "缺失",
             (s_rec and f_rec and set(s_rec["uv_sets"]) == set(f_rec.get("uv_sets", [])))),

            ("关联材质列表 (Materials)",
             str(s_rec["materials"]) if s_rec else "缺失",
             str(f_rec["materials"]) if f_rec else "缺失",
             (s_rec and f_rec and set(s_rec["materials"]) == set(f_rec.get("materials", [])))),

            ("分面映射区间 (Face Map)",
             str(s_rec["face_assignments"]) if s_rec else "缺失",
             str(f_rec["face_assignments"]) if f_rec else "缺失",
             (not rec["mat_diff"] if (s_rec and f_rec) else False)),

            ("坐标位移 (Translation)",
             str(s_rec["transform"]["translation"]) if s_rec else "缺失",
             str(f_rec["transform"]["translation"]) if f_rec else "缺失",
             (s_rec and f_rec and s_rec["transform"]["translation"] == f_rec["transform"]["translation"])),

            ("旋转角度 (Rotation)",
             str(s_rec["transform"]["rotation"]) if s_rec else "缺失",
             str(f_rec["transform"]["rotation"]) if f_rec else "缺失",
             (s_rec and f_rec and s_rec["transform"]["rotation"] == f_rec["transform"]["rotation"])),

            ("缩放比例 (Scaling)",
             str(s_rec["transform"]["scaling"]) if s_rec else "缺失",
             str(f_rec["transform"]["scaling"]) if f_rec else "缺失",
             (s_rec and f_rec and s_rec["transform"]["scaling"] == f_rec["transform"]["scaling"])),
        ]

        self.detail_table.setRowCount(len(items_to_compare))
        for row_idx, (prop_name, maya_val, fbx_val, is_match) in enumerate(items_to_compare):
            # 0. 属性名
            p_item = QtWidgets.QTableWidgetItem(prop_name)
            p_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.detail_table.setItem(row_idx, 0, p_item)

            # 1. Maya 状态
            m_item = QtWidgets.QTableWidgetItem(maya_val)
            m_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.detail_table.setItem(row_idx, 1, m_item)

            # 2. FBX 状态
            f_item = QtWidgets.QTableWidgetItem(fbx_val)
            f_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.detail_table.setItem(row_idx, 2, f_item)

            # 3. 结论
            verdict_item = QtWidgets.QTableWidgetItem("✓ 完全吻合" if is_match else "⚠ 存在差异")
            verdict_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            verdict_item.setTextAlignment(Qt.AlignCenter)

            if is_match:
                verdict_item.setForeground(QtGui.QColor("#4cd964"))
            else:
                verdict_item.setForeground(QtGui.QColor("#ff453a" if "Vertices" in prop_name or "Polygons" in prop_name else "#ffd60a"))
                m_item.setBackground(QtGui.QColor("#3d2800"))
                f_item.setBackground(QtGui.QColor("#3d2800"))

            self.detail_table.setItem(row_idx, 3, verdict_item)

    def _set_all_checked(self, checked):
        state = Qt.Checked if checked else Qt.Unchecked
        self.table.blockSignals(True)
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item:
                item.setCheckState(state)
            if row < len(self._filtered_records):
                self._filtered_records[row]["checked"] = checked
        self.table.blockSignals(False)

        selected = sum(1 for r in self._all_diff_records if r["checked"])
        self.lbl_summary.setText("共检索 {} 个资产 (当前视图 {} 个，已勾选 {} 个)".format(
            len(self._all_diff_records), len(self._filtered_records), selected
        ))

    # --------------------------------------------------------------------------
    # 差异同步与修复操作
    # --------------------------------------------------------------------------

    def _on_action_sync_materials(self):
        checked_items = [r for r in self._all_diff_records if r["checked"]]
        if not checked_items:
            QtWidgets.QMessageBox.information(self, "提示", "请先在列表中勾选需要同步材质的资产。")
            return

        options = {
            "match_by_short_name": self.chk_match_short.isChecked(),
            "case_insensitive": False,
            "preserve_face_assignment": True,
            "fallback_to_object": self.chk_fallback_topo.isChecked()
        }

        self._log("=== 开始执行选中资产材质与分面同步 ===", "info")
        count = AssetDiffSyncEngine.sync_materials(checked_items, options=options, log_func=self._log)
        self._update_filter_counts()
        self._refresh_main_table()
        QtWidgets.QMessageBox.information(self, "同步完成", "材质同步操作完成！\n成功同步 {} 个资产。".format(count))

    def _on_action_sync_transforms(self):
        checked_items = [r for r in self._all_diff_records if r["checked"]]
        if not checked_items:
            QtWidgets.QMessageBox.information(self, "提示", "请先在列表中勾选需要同步变换的资产。")
            return

        self._log("=== 开始执行选中资产空间变换 (Translation/Rotation/Scale) 对齐 ===", "info")
        count = AssetDiffSyncEngine.sync_transforms(checked_items, log_func=self._log)
        self._update_filter_counts()
        self._refresh_main_table()
        QtWidgets.QMessageBox.information(self, "变换对齐完成", "空间变换对齐完成！\n成功同步 {} 个物体的坐标、旋转与缩放。".format(count))

    def _on_action_select_scene(self):
        checked_items = [r for r in self._all_diff_records if r["checked"]]
        if not checked_items:
            sel_rows = self.table.selectionModel().selectedRows()
            if sel_rows:
                checked_items = [self._filtered_records[idx.row()] for idx in sel_rows if idx.row() < len(self._filtered_records)]

        if not checked_items:
            QtWidgets.QMessageBox.information(self, "提示", "请在列表中勾选或高亮选择需要对焦的资产。")
            return

        count = AssetDiffSyncEngine.select_in_scene(checked_items, log_func=self._log)
        self._log("已在场景中高亮选中 {} 个资产并对焦。".format(count), "success")

    def _on_action_export_report(self):
        if not self._all_diff_records:
            QtWidgets.QMessageBox.information(self, "提示", "当前无比对数据可供导出，请先执行资产比对。")
            return

        default_name = "FBX_Diff_Report_{}.md".format(
            os.path.splitext(os.path.basename(self._current_fbx_path))[0] if self._current_fbx_path else "Scene"
        )
        save_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "导出资产差异核查报告", os.path.join(os.path.expanduser("~"), default_name), "Markdown 文档 (*.md);;所有文件 (*.*)"
        )
        if save_path:
            out_file = AssetDiffSyncEngine.export_diff_report(self._all_diff_records, self._current_fbx_path, save_path)
            self._log("核查报告已成功导出至: {}".format(out_file), "success")
            QtWidgets.QMessageBox.information(self, "导出成功", "差异核查报告已成功生成:\n{}".format(out_file))

    def _log(self, text, level="info"):
        color_map = {
            "info": "#c8c8c8",
            "success": "#4cd964",
            "warning": "#ffd60a",
            "error": "#ff453a"
        }
        color = color_map.get(level, "#c8c8c8")
        timestamp = time.strftime("%H:%M:%S")
        html = '<span style="color:#6e6e6e;">[{}]</span> <span style="color:{};">{}</span>'.format(
            timestamp, color, text
        )
        self.txt_log.append(html)
        self.txt_log.verticalScrollBar().setValue(self.txt_log.verticalScrollBar().maximum())
        QtWidgets.QApplication.processEvents()


# 向后兼容别名
FBXMaterialIngestDialog = FBXAssetDiffDialog


# ==============================================================================
# 全局单例与外部接口
# ==============================================================================

_GLOBAL_INGEST_DIALOG = None


def show_ui():
    """打开 FBX 资产深度比对与差异同步工具主窗口"""
    global _GLOBAL_INGEST_DIALOG

    if cmds.about(batch=True):
        print("[FBX Diff] 当前处于批处理模式，跳过界面展示。")
        return None

    app = QtWidgets.QApplication.instance()

    try:
        if hasattr(QtWidgets.QApplication, "topLevelWidgets"):
            for widget in QtWidgets.QApplication.topLevelWidgets():
                if widget and hasattr(widget, "objectName"):
                    if widget.objectName() in (FBXAssetDiffDialog.WINDOW_OBJECT_NAME, "MayaFBXSDKMaterialIngestDialogWin"):
                        try:
                            widget.close()
                            widget.deleteLater()
                        except Exception:
                            pass
    except Exception:
        pass

    if _GLOBAL_INGEST_DIALOG is not None:
        try:
            _GLOBAL_INGEST_DIALOG.close()
            _GLOBAL_INGEST_DIALOG.deleteLater()
        except Exception:
            pass
        _GLOBAL_INGEST_DIALOG = None

    _GLOBAL_INGEST_DIALOG = FBXAssetDiffDialog()
    _GLOBAL_INGEST_DIALOG.show()
    return _GLOBAL_INGEST_DIALOG


show_diff_ui = show_ui


def install_shelf_button(root_dir=None):
    """在 Maya 当前活动工具架（Shelf）上创建或更新快速启动图标按钮"""
    import maya.cmds as cmds
    import maya.mel as mel

    if not root_dir:
        root_dir = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else ""

    norm_root = os.path.normpath(root_dir).replace("\\", "/")
    icon_path = os.path.join(norm_root, "icons", "fbx_mat_ingest.png").replace("\\", "/")

    current_shelf = "Custom"
    try:
        shelf_top = mel.eval("global string $gShelfTopLevel; string $res = $gShelfTopLevel;")
        if shelf_top and cmds.tabLayout(shelf_top, exists=True):
            current_shelf = cmds.tabLayout(shelf_top, query=True, selectTab=True) or "Custom"
    except Exception:
        pass

    if not cmds.shelfLayout(current_shelf, exists=True):
        print("[FBX Diff] 当前处于无 GUI 工具架环境，跳过工具架按钮创建。")
        return None

    button_tag = "FBXMaterialIngestShelfBtn"

    try:
        children = cmds.shelfLayout(current_shelf, query=True, childArray=True) or []
        for child in children:
            if cmds.shelfButton(child, exists=True):
                tag = cmds.shelfButton(child, query=True, docTag=True)
                if tag == button_tag:
                    cmds.deleteUI(child)
    except Exception:
        pass

    cmd_code = (
        "import sys, os\n"
        "tool_dir = r'{root}'\n"
        "if tool_dir not in sys.path:\n"
        "    sys.path.insert(0, tool_dir)\n"
        "import compare_and_sync_fbx_assets as fbx_diff_tool\n"
        "fbx_diff_tool.show_ui()\n"
    ).format(root=norm_root)

    btn = cmds.shelfButton(
        parent=current_shelf,
        label="FBX资产比对与同步",
        annotation="【FBX资产比对与同步】对比Maya场景与外部FBX资产拓扑/材质/变换，一键修复差异",
        imageOverlayLabel="DIFF",
        image=icon_path if os.path.isfile(icon_path) else "render_phong.png",
        command=cmd_code,
        sourceType="python",
        docTag=button_tag
    )

    try:
        cmds.inViewMessage(
            amg="<span style=\"color:#4cd964;font-weight:bold;\">FBX 资产比对与同步工具</span> 已成功安装到工具架: <span style=\"color:#ffd60a;\">[{}]</span>".format(current_shelf),
            pos="midCenter",
            fade=True,
            fadeInTime=100,
            fadeOutTime=200,
            fadeStayTime=2500
        )
    except Exception:
        pass

    print("[FBX Diff] 已成功在工具架 [{}] 创建启动按钮。".format(current_shelf))
    return btn


def import_materials_from_fbx(fbx_paths,
                               match_by_short_name=True,
                               case_insensitive=False,
                               preserve_face_assignment=True,
                               fallback_to_object=True,
                               custom_sdk_path=None,
                               log_callback=None):
    """非 UI 纯 Python API 批量从外部 FBX 文件录入材质并指定到场景同名物体"""
    if isinstance(fbx_paths, (str, bytes)):
        fbx_paths = [fbx_paths]

    if custom_sdk_path:
        FBXSDKManager.load_sdk_from_custom_path(custom_sdk_path)

    options = {
        "match_by_short_name": match_by_short_name,
        "case_insensitive": case_insensitive,
        "preserve_face_assignment": preserve_face_assignment,
        "fallback_to_object": fallback_to_object,
    }

    cmds.undoInfo(openChunk=True, chunkName="BatchIngestFBXMaterials")
    results = []

    try:
        for p in fbx_paths:
            parsed = FBXSDKParser.parse_file(p, log_func=log_callback)
            res = MayaMaterialBuilder.assign_to_scene_matching_objects(
                parsed, options=options, log_func=log_callback
            )
            results.append(res)
    finally:
        cmds.undoInfo(closeChunk=True)

    return results


if __name__ == "__main__":
    show_ui()
