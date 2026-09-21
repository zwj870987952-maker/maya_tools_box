# -*- coding: utf-8 -*-
"""
命名空间清理工具实现：
支持规范化 API 传参、Dry-Run 预检与原子化执行。
"""
from __future__ import absolute_import, division, print_function

try:
    import maya.cmds as cmds
    MAYA_AVAILABLE = True
except ImportError:
    cmds = None
    MAYA_AVAILABLE = False

from ...framework.base_tool import BaseMayaTool
from ...framework.models import ToolResult
from ...core.maya_utils import get_node_namespace, get_clean_basename


class NamespaceCleanTool(BaseMayaTool):
    """
    场景与选定物体命名空间消除工具：
    支持本地节点合并到根命名空间 (':')，以及将顶层引用节点平滑迁移至根命名空间。
    """

    tool_id = "clean_namespaces"
    tool_name = "命名空间清理工具"
    category = "Pipeline"
    version = "1.1.0"
    description = (
        "清理指定节点或当前选中节点的命名空间。支持将本地命名空间安全合并至根目录 (':')，"
        "并支持在保持引用关系的前提下平滑迁移 Top-level Reference 引用节点。"
    )

    parameters_schema = {
        "type": "object",
        "properties": {
            "nodes": {
                "type": "array",
                "items": {"type": "string"},
                "description": "要清理命名空间的目标节点列表。若为空则自动使用视口当前选中的节点。"
            },
            "process_all_scene": {
                "type": "boolean",
                "default": False,
                "description": "是否处理全场景中所有的本地命名空间（默认为 False，仅处理指定或选中的节点）。"
            }
        },
        "required": [],
        "additionalProperties": False
    }

    def _reference_edits(self, reference_node):
        """查询引用节点的编辑历史"""
        try:
            return cmds.referenceQuery(
                reference_node,
                editStrings=True,
                successfulEdits=True,
                failedEdits=True,
            ) or []
        except RuntimeError:
            return []

    def _reference_in_root(self, reference_node):
        """在根命名空间重新加载引用"""
        if cmds.referenceQuery(reference_node, isNodeReferenced=True):
            raise RuntimeError("嵌套的子级引用无法直接从父场景迁移。")

        if not cmds.referenceQuery(reference_node, isLoaded=True):
            raise RuntimeError("目标引用必须处于加载状态。")

        edits = self._reference_edits(reference_node)
        if edits:
            raise RuntimeError(
                "该引用包含 {} 个编辑操作，重建引用将丢弃这些编辑。".format(len(edits))
            )

        reference_file = cmds.referenceQuery(reference_node, filename=True)
        references_before = set(cmds.ls(type="reference") or [])
        new_reference_node = None

        try:
            cmds.file(
                reference_file,
                reference=True,
                namespace=":",
                mergeNamespacesOnClash=True,
            )

            references_after = set(cmds.ls(type="reference") or [])
            created_references = list(references_after - references_before)

            if len(created_references) != 1:
                raise RuntimeError("无法唯一标识新建的根引用节点。")

            new_reference_node = created_references[0]
            new_namespace = cmds.referenceQuery(new_reference_node, namespace=True)

            if new_namespace != ":":
                raise RuntimeError("新建的引用未成功置于根命名空间。")

            new_nodes = cmds.referenceQuery(new_reference_node, nodes=True, dagPath=True) or []
            if not new_nodes:
                raise RuntimeError("新建的根引用不包含任何节点。")

            if not all(cmds.referenceQuery(n, isNodeReferenced=True) for n in new_nodes if cmds.objExists(n)):
                raise RuntimeError("部分新创建的节点未保持引用状态。")

            old_reference_file = cmds.referenceQuery(reference_node, filename=True)
            cmds.file(old_reference_file, removeReference=True)
            return new_reference_node

        except Exception:
            if new_reference_node and cmds.objExists(new_reference_node):
                try:
                    new_ref_file = cmds.referenceQuery(new_reference_node, filename=True)
                    cmds.file(new_ref_file, removeReference=True)
                except Exception:
                    pass
            raise

    def validate(self, nodes=None, process_all_scene=False, **kwargs):
        """预检节点是否存在以及需要处理的命名空间"""
        if not MAYA_AVAILABLE:
            return ToolResult.fail("Maya 环境不可用，无法执行命名空间操作。")

        target_nodes = nodes
        if not target_nodes and not process_all_scene:
            target_nodes = cmds.ls(selection=True, objectsOnly=True, long=True) or []
            if not target_nodes:
                return ToolResult.fail("未指定 target nodes，且场景中未选中任何物体。")

        # 检查传入的节点是否存在
        if target_nodes:
            missing = [n for n in target_nodes if not cmds.objExists(n)]
            if missing:
                return ToolResult.fail(
                    "指定的以下节点在当前 Maya 场景中不存在: {}".format(missing[:5]),
                    errors=missing
                )

        return ToolResult.ok(
            message="参数预检通过",
            data={
                "target_node_count": len(target_nodes) if target_nodes else 0,
                "process_all_scene": process_all_scene
            }
        )

    def execute(self, nodes=None, process_all_scene=False, **kwargs):
        """正式执行命名空间清理"""
        if not MAYA_AVAILABLE:
            return ToolResult.fail("Maya 环境不可用")

        target_nodes = nodes
        if not target_nodes and not process_all_scene:
            target_nodes = cmds.ls(selection=True, objectsOnly=True, long=True) or []

        references = {}
        local_namespaces = set()
        untouched_nodes = []

        if process_all_scene:
            # 搜集所有本地非系统命名空间
            all_ns = cmds.namespaceInfo(listOnlyNamespaces=True, recurse=True) or []
            sys_ns = {"UI", "shared"}
            for ns in all_ns:
                if ns not in sys_ns:
                    local_namespaces.add(":" + ns.lstrip(":"))
        else:
            for obj in target_nodes:
                ns = get_node_namespace(obj)
                if not ns:
                    untouched_nodes.append(obj)
                    continue

                try:
                    is_ref = cmds.referenceQuery(obj, isNodeReferenced=True)
                except RuntimeError:
                    is_ref = False

                if is_ref:
                    ref_node = cmds.referenceQuery(obj, referenceNode=True)
                    references.setdefault(ref_node, []).append(obj)
                else:
                    local_namespaces.add(ns)

        removed_local = []
        removed_references = []
        errors = []
        replacement_selection = []

        # 1. 处理引用节点的根迁移
        for ref_node, selected_ref_nodes in references.items():
            try:
                old_ns = cmds.referenceQuery(ref_node, namespace=True)
                old_ref_nodes = cmds.referenceQuery(ref_node, nodes=True, dagPath=True) or []
                old_ref_nodes = [(cmds.ls(n, long=True) or [n])[0] for n in old_ref_nodes]

                selection_records = []
                for s_node in selected_ref_nodes:
                    s_long = (cmds.ls(s_node, long=True) or [s_node])[0]
                    try:
                        n_idx = old_ref_nodes.index(s_long)
                    except ValueError:
                        n_idx = None
                    selection_records.append((n_idx, get_clean_basename(s_node), cmds.nodeType(s_node)))

                new_ref_node = self._reference_in_root(ref_node)
                new_nodes = cmds.referenceQuery(new_ref_node, nodes=True, dagPath=True) or []
                new_nodes = [(cmds.ls(n, long=True) or [n])[0] for n in new_nodes]

                for n_idx, base_name, n_type in selection_records:
                    if (
                        n_idx is not None
                        and n_idx < len(new_nodes)
                        and cmds.objExists(new_nodes[n_idx])
                        and cmds.nodeType(new_nodes[n_idx]) == n_type
                    ):
                        replacement_selection.append(new_nodes[n_idx])
                        continue

                    matches = [
                        n for n in new_nodes
                        if cmds.objExists(n) and get_clean_basename(n) == base_name and cmds.nodeType(n) == n_type
                    ]
                    if matches:
                        replacement_selection.append(matches[0])

                removed_references.append(old_ns)
            except Exception as e:
                errors.append("迁移引用命名空间失败 [{}]: {}".format(ref_node, str(e)))

        # 2. 处理本地命名空间的合并
        sorted_namespaces = sorted(local_namespaces, key=lambda n: n.count(":"), reverse=True)
        for ns in sorted_namespaces:
            if not cmds.namespace(exists=ns):
                continue
            try:
                cmds.namespace(moveNamespace=(ns, ":"), force=True)
                if cmds.namespace(exists=ns):
                    cmds.namespace(removeNamespace=ns)
                removed_local.append(ns)
            except Exception as e:
                errors.append("移除本地命名空间 [{}] 失败: {}".format(ns, str(e)))

        # 3. 恢复选区
        final_selection = [n for n in (untouched_nodes + replacement_selection) if cmds.objExists(n)]
        if final_selection:
            cmds.select(final_selection, replace=True)

        msg = "成功清理本地命名空间 {} 个，迁移引用命名空间 {} 个。".format(
            len(removed_local), len(removed_references)
        )
        if errors:
            msg += " 过程中伴随 {} 个非阻断告警。".format(len(errors))

        return ToolResult.ok(
            message=msg,
            data={
                "removed_local_namespaces": removed_local,
                "removed_reference_namespaces": removed_references,
            },
            warnings=errors
        )

    def show_ui(self, parent=None):
        from .ui import show_ui as launch_clean_ui
        return launch_clean_ui(parent=parent)
