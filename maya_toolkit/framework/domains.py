# -*- coding: utf-8 -*-
"""
数字资产管线全局业务领域分类定义 (Tool Domain Taxonomy)
为整个 Maya 工具箱确立 6 大工业级业务领域标准。
"""
from __future__ import absolute_import, division, print_function


class ToolDomain(object):
    """领域键名枚举常量"""
    ANIMATION = "animation"
    RIGGING = "rigging"
    MODELING_SURFACING = "modeling_surfacing"
    PIPELINE_IO = "pipeline_io"
    SCENE_HYGIENE = "scene_hygiene"
    ENGINE_BRIDGE = "engine_bridge"


# 6 大核心领域元数据字典
TOOL_DOMAINS = {
    ToolDomain.ANIMATION: {
        "id": ToolDomain.ANIMATION,
        "name": "动画与动作制作",
        "en_name": "Animation & Motion",
        "badge_color": "#0e639c",  # 沉稳科技蓝
        "badge_text_color": "#ffffff",
        "desc": "关键帧编辑、欧拉/万向节曲线修整、IK/FK吸附烘焙、时间轴控制、姿态匹配、拍屏等。",
        "order": 1,
    },
    ToolDomain.RIGGING: {
        "id": ToolDomain.RIGGING,
        "name": "角色绑定与变形",
        "en_name": "Rigging & Skinning",
        "badge_color": "#68217a",  # 优雅紫
        "badge_text_color": "#ffffff",
        "desc": "骨骼拓扑生成、层级约束管理与烘焙、空间切换、蒙皮权重计算/转移、比例补偿修复等。",
        "order": 2,
    },
    ToolDomain.MODELING_SURFACING: {
        "id": ToolDomain.MODELING_SURFACING,
        "name": "模型、外观与材质",
        "en_name": "Modeling & Surfacing",
        "badge_color": "#d97706",  # 暖金橙
        "badge_text_color": "#ffffff",
        "desc": "几何体拓扑检测、材质球指定与传递、UV重命名与规范化、空间变换校准、轴心重置、对称镜像等。",
        "order": 3,
    },
    ToolDomain.PIPELINE_IO: {
        "id": ToolDomain.PIPELINE_IO,
        "name": "资产管线与导入导出",
        "en_name": "Pipeline & I/O",
        "badge_color": "#107c41",  # 资产绿
        "badge_text_color": "#ffffff",
        "desc": "FBX/Alembic 批量导出、外部资产深度比对与同步、文件/文件夹拖拽批量录入、选择集管理等。",
        "order": 4,
    },
    ToolDomain.SCENE_HYGIENE: {
        "id": ToolDomain.SCENE_HYGIENE,
        "name": "场景健康、体检与安全",
        "en_name": "Scene Hygiene & Security",
        "badge_color": "#b91c1c",  # 警戒红/防护盾
        "badge_text_color": "#ffffff",
        "desc": "场景命名空间平滑清理、未知与垃圾节点清除、外部断链/中文路径排查、蠕虫病毒查杀与场景快照备份等。",
        "order": 5,
    },
    ToolDomain.ENGINE_BRIDGE: {
        "id": ToolDomain.ENGINE_BRIDGE,
        "name": "跨引擎互通与协同",
        "en_name": "Engine Bridge",
        "badge_color": "#0284c7",  # 虚幻/引擎青蓝
        "badge_text_color": "#ffffff",
        "desc": "面向 Unreal Engine (UE) 或 Unity 的引擎协同管线，包括骨骼清单逆向提取、源资产逆向追溯、自动化导入等。",
        "order": 6,
    },
}


def get_domain_info(domain_key):
    """安全获取指定领域的元数据，未匹配时返回兜底通用领域"""
    normalized = str(domain_key).lower().strip() if domain_key else ""
    if normalized in TOOL_DOMAINS:
        return TOOL_DOMAINS[normalized]

    # 兼容历史分类映射
    legacy_map = {
        "pipeline": ToolDomain.PIPELINE_IO,
        "modeling": ToolDomain.MODELING_SURFACING,
        "assets": ToolDomain.PIPELINE_IO,
        "diagnostics": ToolDomain.SCENE_HYGIENE,
        "utilities": ToolDomain.SCENE_HYGIENE,
    }
    if normalized in legacy_map:
        return TOOL_DOMAINS[legacy_map[normalized]]

    return {
        "id": normalized or "other",
        "name": normalized.upper() or "其他通用",
        "en_name": normalized or "Other",
        "badge_color": "#4b5563",
        "badge_text_color": "#ffffff",
        "desc": "未划分到指定核心领域的扩展工具。",
        "order": 99,
    }


def list_domains():
    """按标准排序返回所有领域的元数据列表"""
    return sorted(TOOL_DOMAINS.values(), key=lambda d: d["order"])
