# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

from maya_toolkit.framework import BaseMayaTool, ToolResult
from . import operations

try:
    string_types = (basestring,)
except NameError:
    string_types = (str,)


class ResetPivotTool(BaseMayaTool):
    tool_id = "reset_pivot"
    tool_name = "轴心点与轴向重置"
    category = "modeling_surfacing"
    version = "1.0.0"
    description = "对 transform/joint 执行原脚本七种轴心与轴向动作；冻结与层级变更须在副本场景验收。"
    parameters_schema = {
        "type": "object",
        "properties": {
            "action": {"type": "string", "enum": list(operations.ACTIONS), "default": "center", "description": "center/origin/parent/reset_axes/world/joint/complete"},
            "target_nodes": {"type": "array", "items": {"type": "string"}, "minItems": 1, "description": "省略时读取当前选择；显式空列表非法。"},
            "source_joint": {"type": "string", "description": "joint 动作的源骨骼；仅该动作可用。省略全部节点参数时按选择顺序读取源和目标。"}
        },
        "additionalProperties": False
    }

    def _plan(self, action="center", target_nodes=None, source_joint=None, **kwargs):
        if kwargs:
            raise ValueError("Unknown parameters: {}".format(", ".join(sorted(kwargs))))
        if not isinstance(action, string_types) or action not in operations.ACTIONS:
            raise ValueError("Invalid action")
        if source_joint is not None and (not isinstance(source_joint, string_types) or not source_joint or action != "joint"):
            raise ValueError("source_joint requires joint action and a nonempty node name")
        if target_nodes is not None and (not isinstance(target_nodes, (list, tuple)) or not target_nodes or any(not isinstance(n, string_types) or not n for n in target_nodes)):
            raise ValueError("target_nodes must contain nonempty node names")
        cmds = operations.maya_commands()
        if target_nodes is None:
            target_nodes = cmds.ls(selection=True, long=True) or []
            if action == "joint" and source_joint is None:
                if len(target_nodes) != 2:
                    raise ValueError("Select source joint first, then exactly one target")
                source_joint, target_nodes = target_nodes[0], target_nodes[1:]
        if not target_nodes:
            raise ValueError("No target nodes")
        targets = []
        warnings = []
        seen = set()
        for name in target_nodes:
            if "." in name:
                raise ValueError("Components and plugs are not transform targets: {}".format(name))
            node = operations.resolve(cmds, name)
            if cmds.nodeType(node) not in ("transform", "joint"):
                raise ValueError("Target must be transform or joint: {}".format(node))
            if cmds.referenceQuery(node, isNodeReferenced=True):
                raise ValueError("Referenced targets are not supported: {}".format(node))
            if any(cmds.lockNode(node, query=True, lock=True) or []):
                raise ValueError("Locked node: {}".format(node))
            node_id = cmds.ls(node, uuid=True)[0]
            if len(cmds.ls(node_id, long=True, allPaths=True) or []) != 1:
                raise ValueError("Instanced target is not supported: {}".format(node))
            if action in ("reset_axes", "complete"):
                for shape in cmds.listRelatives(node, shapes=True, fullPath=True) or []:
                    if len(cmds.listRelatives(shape, allParents=True, fullPath=True) or []) > 1:
                        raise ValueError("Cannot freeze an instanced shape: {}".format(shape))
            attrs = ["rotate" + axis for axis in "XYZ"]
            attrs += [kind + axis for kind in ("rotatePivot", "scalePivot", "rotatePivotTranslate", "scalePivotTranslate") for axis in "XYZ"]
            if action in operations.HIERARCHY_ACTIONS:
                attrs += [kind + axis for kind in ("translate", "scale", "shear") for axis in ("XYZ" if kind != "shear" else ("XY", "XZ", "YZ"))]
                warnings.append("{}: operation may reparent or freeze rotation; inspect child transforms and shape effects".format(node))
            for attr in attrs:
                plug = node + "." + attr
                if not cmds.getAttr(plug, settable=True) or cmds.listConnections(plug, source=True, destination=False):
                    raise ValueError("Attribute is locked or driven: {}".format(plug))
            parent = cmds.listRelatives(node, parent=True, fullPath=True) or []
            if action == "parent" and not parent:
                warnings.append("{}: no parent; skipped as in original script".format(node))
                continue
            if parent and action in operations.HIERARCHY_ACTIONS:
                if any(cmds.lockNode(parent[0], query=True, lock=True) or []) or cmds.referenceQuery(parent[0], isNodeReferenced=True):
                    raise ValueError("Cannot safely restore locked/referenced parent: {}".format(parent[0]))
            if node_id not in seen:
                targets.append({"uuid": node_id, "path": node})
                seen.add(node_id)
        orientation = None
        if action == "joint":
            if not source_joint:
                raise ValueError("source_joint is required with explicit joint targets")
            source = operations.resolve(cmds, source_joint)
            if cmds.nodeType(source) != "joint":
                raise ValueError("Source must be joint")
            if cmds.ls(source, uuid=True)[0] in seen:
                raise ValueError("Source joint cannot also be a target")
            orientation = list(cmds.getAttr(source + ".jointOrient")[0])
            warnings.append("Preserves original jointOrient-as-world-Euler behavior; not a general world orientation match")
        return cmds, targets, orientation, warnings

    def validate(self, **kwargs):
        try:
            unused_cmds, targets, unused_orientation, warnings = self._plan(**kwargs)
            return ToolResult.ok("预检通过", data={"action": kwargs.get("action", "center"), "target_nodes": [t["path"] for t in targets], "target_count": len(targets)}, warnings=warnings)
        except Exception as error:
            return ToolResult.fail("预检失败: {}".format(error), errors=[str(error)])

    def execute(self, **kwargs):
        cmds, targets, orientation, warnings = self._plan(**kwargs)
        action = kwargs.get("action", "center")
        processed = []
        for target in targets:
            try:
                node = operations.apply_action(cmds, action, target["uuid"], orientation)
                processed.append(node)
            except Exception as error:
                return ToolResult(success=False, message="执行失败；请检查层级并撤销本次操作", errors=[str(error)], warnings=warnings, data={"action": action, "processed_nodes": processed, "failed_node": target["path"], "failed_uuid": target["uuid"], "partial_changes_possible": True})
        return ToolResult.ok("轴心操作完成", data={"action": action, "processed_nodes": processed, "processed_count": len(processed)}, warnings=warnings)

    def show_ui(self, parent=None):
        from .ui import show
        return show(self)
