# -*- coding: utf-8 -*-
"""Built-in node specifications for the blueprint canvas."""


NODE_CLASS_COLORS = {
    "常量": "#4EA1FF",
    "数据获取": "#38C7C7",
    "数据转换": "#9B6DFF",
    "Maya 操作": "#F2994A",
    "流程控制": "#F2C94C",
    "调试 / 报告": "#7FB069",
}


PORT_LABELS = {
    "input": "输入",
    "value": "值",
    "nodes": "节点",
    "nodes_a": "节点 A",
    "nodes_b": "节点 B",
    "matched_nodes": "匹配节点",
    "unmatched_nodes": "未匹配节点",
    "matched_attrs": "匹配属性",
    "unmatched_attrs": "未匹配属性",
    "pattern": "名称文本",
    "index": "索引",
    "count": "数量",
    "selected_nodes": "已选择节点",
    "renamed_nodes": "重命名节点",
    "group_node": "组节点",
    "attrs": "属性引用",
    "attrs_a": "属性 A",
    "attrs_b": "属性 B",
    "materials": "材质节点",
    "report": "报告",
    "drivers": "驱动节点",
    "driven": "被驱动节点",
    "constraints": "约束节点",
    "file_path": "文件路径",
    "imported_nodes": "导入节点",
    "target_path": "目标路径",
    "result": "结果",
    "frame": "帧",
    "frames": "帧",
    "frame_range": "帧范围",
    "start_frame": "起始帧",
    "end_frame": "结束帧",
    "channels": "通道",
    "frame_data": "帧数据",
    "translate_enabled": "位移",
    "rotate_enabled": "旋转",
    "scale_enabled": "缩放",
}


class PortSpec(object):
    """Describes a typed node input or output port."""

    def __init__(self, name, port_type, label=None, required=True):
        self.name = name
        self.port_type = port_type
        self.label = label or PORT_LABELS.get(name, name)
        self.required = required

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.port_type,
            "label": self.label,
            "required": self.required,
        }


class ParameterSpec(object):
    """Describes an editable node parameter."""

    def __init__(
        self,
        name,
        param_type,
        label=None,
        default=None,
        choices=None,
        required=False,
        choice_labels=None,
    ):
        self.name = name
        self.param_type = param_type
        self.label = label or name
        self.default = default
        self.choices = choices or []
        self.required = required
        self.choice_labels = choice_labels or list(self.choices)

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.param_type,
            "label": self.label,
            "default": self.default,
            "choices": list(self.choices),
            "choice_labels": list(self.choice_labels),
            "required": self.required,
        }


class NodeSpec(object):
    """Describes a node type that can be instantiated on the canvas."""

    def __init__(self, node_type, title, category, node_class, inputs=None, outputs=None, parameters=None):
        self.node_type = node_type
        self.title = title
        self.category = category
        self.node_class = node_class
        self.inputs = inputs or []
        self.outputs = outputs or []
        self.parameters = parameters or []

    def default_parameters(self):
        values = {}
        for parameter in self.parameters:
            values[parameter.name] = parameter.default
        return values

    def to_dict(self):
        return {
            "type": self.node_type,
            "title": self.title,
            "category": self.category,
            "node_class": self.node_class,
            "inputs": [port.to_dict() for port in self.inputs],
            "outputs": [port.to_dict() for port in self.outputs],
            "parameters": [parameter.to_dict() for parameter in self.parameters],
        }

    def class_color(self):
        return NODE_CLASS_COLORS.get(self.node_class, "#343b48")


def _built_in_specs():
    return [
        NodeSpec(
            "constant.text",
            "文本",
            "常量",
            "常量",
            outputs=[PortSpec("value", "STRING")],
            parameters=[
                ParameterSpec("value", "text", "值", "", required=False),
            ],
        ),
        NodeSpec(
            "constant.number",
            "数字",
            "常量",
            "常量",
            outputs=[PortSpec("value", "NUMBER")],
            parameters=[
                ParameterSpec("value", "number", "值", 0.0, required=False),
            ],
        ),
        NodeSpec(
            "constant.bool",
            "布尔",
            "常量",
            "常量",
            outputs=[PortSpec("value", "BOOL")],
            parameters=[
                ParameterSpec("value", "bool", "值", False, required=False),
            ],
        ),
        NodeSpec(
            "constant.path",
            "路径",
            "常量",
            "常量",
            outputs=[PortSpec("value", "PATH")],
            parameters=[
                ParameterSpec("value", "path", "路径", "", required=True),
            ],
        ),
        NodeSpec(
            "maya.nodes.node_names",
            "节点名称",
            "数据获取 / 场景入口",
            "数据获取",
            outputs=[PortSpec("nodes", "NODE_LIST")],
            parameters=[
                ParameterSpec("names", "node_list", "节点", [], required=True),
            ],
        ),
        NodeSpec(
            "maya.selection.current",
            "当前选择",
            "数据获取 / 场景入口",
            "数据获取",
            outputs=[PortSpec("nodes", "NODE_LIST")],
            parameters=[
                ParameterSpec("include_shapes", "bool", "包含 Shape", False),
            ],
        ),
        NodeSpec(
            "maya.timeline.current_frame",
            "当前帧",
            "数据获取 / 动画时间",
            "数据获取",
            inputs=[PortSpec("frame", "NUMBER", "时间", required=False)],
            outputs=[PortSpec("frames", "FRAME_LIST", "帧")],
        ),
        NodeSpec(
            "maya.timeline.frame_range",
            "范围帧",
            "数据获取 / 动画时间",
            "数据获取",
            inputs=[
                PortSpec("start_frame", "NUMBER", required=False),
                PortSpec("end_frame", "NUMBER", required=False),
            ],
            outputs=[
                PortSpec("frame_range", "FRAME_RANGE"),
                PortSpec("frames", "FRAME_LIST", "帧"),
            ],
            parameters=[
                ParameterSpec("include_end", "bool", "包含结束帧", True),
            ],
        ),
        NodeSpec(
            "maya.channels.selected_channel_box",
            "获取通道栏选择",
            "数据获取 / 动画通道",
            "数据获取",
            outputs=[PortSpec("channels", "CHANNEL_LIST")],
            parameters=[
                ParameterSpec("default_transform", "bool", "无选择时位移旋转", True),
            ],
        ),
        NodeSpec(
            "maya.nodes.by_type",
            "按 Maya 类型获取节点",
            "数据获取 / 场景入口",
            "数据获取",
            outputs=[PortSpec("nodes", "NODE_LIST")],
            parameters=[
                ParameterSpec(
                    "maya_type",
                    "choice",
                    "Maya 类型",
                    "joint",
                    choices=[
                        "joint",
                        "transform",
                        "mesh",
                        "nurbsCurve",
                        "camera",
                        "locator",
                        "skinCluster",
                        "blendShape",
                        "animCurve",
                        "parentConstraint",
                        "pointConstraint",
                        "orientConstraint",
                        "scaleConstraint",
                        "lambert",
                        "blinn",
                        "phong",
                        "shadingEngine",
                    ],
                    choice_labels=[
                        "joint 骨骼",
                        "transform 变换",
                        "mesh 网格 Shape",
                        "nurbsCurve 曲线 Shape",
                        "camera 摄像机",
                        "locator 定位器",
                        "skinCluster 蒙皮",
                        "blendShape 变形",
                        "animCurve 动画曲线",
                        "parentConstraint 父子约束",
                        "pointConstraint 点约束",
                        "orientConstraint 方向约束",
                        "scaleConstraint 缩放约束",
                        "lambert 材质",
                        "blinn 材质",
                        "phong 材质",
                        "shadingEngine 材质组",
                    ],
                ),
                ParameterSpec(
                    "shape_result",
                    "choice",
                    "Shape 结果",
                    "original",
                    choices=["original", "parent_transform"],
                    choice_labels=["原样返回", "返回父 Transform"],
                ),
                ParameterSpec("long_name", "bool", "返回长名称", True),
            ],
        ),
        NodeSpec(
            "maya.nodes.skin_cluster",
            "获取 SkinCluster",
            "数据获取 / 快捷获取",
            "数据获取",
            inputs=[PortSpec("nodes", "NODE_LIST")],
            outputs=[PortSpec("nodes", "NODE_LIST")],
        ),
        NodeSpec(
            "maya.nodes.blend_shape",
            "获取 BlendShape",
            "数据获取 / 快捷获取",
            "数据获取",
            inputs=[PortSpec("nodes", "NODE_LIST")],
            outputs=[PortSpec("nodes", "NODE_LIST")],
        ),
        NodeSpec(
            "maya.nodes.deformers",
            "获取变形器",
            "数据获取 / 快捷获取",
            "数据获取",
            inputs=[PortSpec("nodes", "NODE_LIST")],
            outputs=[PortSpec("nodes", "NODE_LIST")],
        ),
        NodeSpec(
            "maya.nodes.materials",
            "获取材质",
            "数据获取 / 快捷获取",
            "数据获取",
            inputs=[PortSpec("nodes", "NODE_LIST")],
            outputs=[PortSpec("materials", "NODE_LIST")],
        ),
        NodeSpec(
            "maya.nodes.constraints",
            "获取约束",
            "数据获取 / 快捷获取",
            "数据获取",
            inputs=[PortSpec("nodes", "NODE_LIST")],
            outputs=[PortSpec("constraints", "NODE_LIST")],
        ),
        NodeSpec(
            "maya.attributes.get",
            "获取属性",
            "数据获取 / 属性读取",
            "数据获取",
            inputs=[PortSpec("attrs", "ATTR_LIST")],
            outputs=[PortSpec("value", "VALUE")],
        ),
        NodeSpec(
            "maya.attributes.inspect",
            "检查属性",
            "数据获取 / 属性读取",
            "数据获取",
            inputs=[PortSpec("attrs", "ATTR_LIST")],
            outputs=[
                PortSpec("value", "VALUE"),
                PortSpec("report", "STRING"),
            ],
        ),
        NodeSpec(
            "debug.print_result",
            "打印结果",
            "调试 / 报告",
            "调试 / 报告",
            inputs=[PortSpec("input", "ANY")],
            outputs=[],
            parameters=[
                ParameterSpec("label", "text", "标签", "", required=False),
            ],
        ),
        NodeSpec(
            "maya.attributes.make_ref",
            "创建属性引用",
            "数据转换 / 属性",
            "数据转换",
            inputs=[PortSpec("nodes", "NODE_LIST", required=False)],
            outputs=[PortSpec("attrs", "ATTR_LIST")],
            parameters=[
                ParameterSpec("attribute_items", "attribute_item_list", "属性", [], required=True),
            ],
        ),
        NodeSpec(
            "animation.channels.transform_defaults",
            "变换通道",
            "数据转换 / 动画通道",
            "数据转换",
            inputs=[
                PortSpec("translate_enabled", "BOOL", required=False),
                PortSpec("rotate_enabled", "BOOL", required=False),
                PortSpec("scale_enabled", "BOOL", required=False),
            ],
            outputs=[PortSpec("channels", "CHANNEL_LIST")],
            parameters=[
                ParameterSpec("default_translate", "bool", "默认位移", True),
                ParameterSpec("default_rotate", "bool", "默认旋转", True),
                ParameterSpec("default_scale", "bool", "默认缩放", False),
            ],
        ),
        NodeSpec(
            "transform.node_list.merge",
            "合并节点列表",
            "数据转换 / 节点列表",
            "数据转换",
            inputs=[
                PortSpec("nodes_a", "NODE_LIST"),
                PortSpec("nodes_b", "NODE_LIST"),
            ],
            outputs=[PortSpec("nodes", "NODE_LIST")],
        ),
        NodeSpec(
            "transform.node_list.unique",
            "去重节点列表",
            "数据转换 / 节点列表",
            "数据转换",
            inputs=[PortSpec("nodes", "NODE_LIST")],
            outputs=[PortSpec("nodes", "NODE_LIST")],
        ),
        NodeSpec(
            "transform.node_list.sort_by_name",
            "按名称排序节点",
            "数据转换 / 节点列表",
            "数据转换",
            inputs=[PortSpec("nodes", "NODE_LIST")],
            outputs=[PortSpec("nodes", "NODE_LIST")],
            parameters=[
                ParameterSpec(
                    "name_scope",
                    "choice",
                    "名称范围",
                    "short",
                    choices=["short", "full"],
                    choice_labels=["短名称", "完整路径"],
                ),
                ParameterSpec("case_sensitive", "bool", "区分大小写", False),
                ParameterSpec("descending", "bool", "倒序", False),
            ],
        ),
        NodeSpec(
            "transform.node_list.reverse",
            "反转节点列表",
            "数据转换 / 节点列表",
            "数据转换",
            inputs=[PortSpec("nodes", "NODE_LIST")],
            outputs=[PortSpec("nodes", "NODE_LIST")],
        ),
        NodeSpec(
            "transform.node_list.sort_by_hierarchy",
            "按层级排序节点",
            "数据转换 / 节点列表",
            "数据转换",
            inputs=[PortSpec("nodes", "NODE_LIST")],
            outputs=[PortSpec("nodes", "NODE_LIST")],
            parameters=[
                ParameterSpec("parent_first", "bool", "父级优先", True),
            ],
        ),
        NodeSpec(
            "transform.node_list.filter_by_name",
            "按名称过滤节点",
            "数据转换 / 节点列表",
            "数据转换",
            inputs=[
                PortSpec("nodes", "NODE_LIST"),
                PortSpec("pattern", "STRING", required=False),
            ],
            outputs=[
                PortSpec("matched_nodes", "NODE_LIST"),
                PortSpec("unmatched_nodes", "NODE_LIST"),
            ],
            parameters=[
                ParameterSpec(
                    "match_mode",
                    "choice",
                    "匹配方式",
                    "contains",
                    choices=["contains", "prefix", "suffix", "exact"],
                    choice_labels=["包含", "开头", "结尾", "完全匹配"],
                ),
                ParameterSpec("case_sensitive", "bool", "区分大小写", False),
            ],
        ),
        NodeSpec(
            "transform.node_list.get_item",
            "取节点列表项",
            "数据转换 / 节点列表",
            "数据转换",
            inputs=[
                PortSpec("nodes", "NODE_LIST"),
                PortSpec("index", "NUMBER"),
            ],
            outputs=[PortSpec("nodes", "NODE_LIST")],
        ),
        NodeSpec(
            "transform.node_list.count",
            "节点列表数量",
            "数据转换 / 节点列表",
            "数据转换",
            inputs=[PortSpec("nodes", "NODE_LIST")],
            outputs=[PortSpec("count", "NUMBER")],
        ),
        NodeSpec(
            "transform.attr_list.merge",
            "合并属性引用列表",
            "数据转换 / 属性",
            "数据转换",
            inputs=[
                PortSpec("attrs_a", "ATTR_LIST"),
                PortSpec("attrs_b", "ATTR_LIST"),
            ],
            outputs=[PortSpec("attrs", "ATTR_LIST")],
        ),
        NodeSpec(
            "transform.attr_list.unique",
            "去重属性引用列表",
            "数据转换 / 属性",
            "数据转换",
            inputs=[PortSpec("attrs", "ATTR_LIST")],
            outputs=[PortSpec("attrs", "ATTR_LIST")],
        ),
        NodeSpec(
            "transform.attr_list.filter_by_name",
            "按名称过滤属性引用",
            "数据转换 / 属性",
            "数据转换",
            inputs=[
                PortSpec("attrs", "ATTR_LIST"),
                PortSpec("pattern", "STRING", required=False),
            ],
            outputs=[
                PortSpec("matched_attrs", "ATTR_LIST"),
                PortSpec("unmatched_attrs", "ATTR_LIST"),
            ],
            parameters=[
                ParameterSpec(
                    "match_mode",
                    "choice",
                    "匹配方式",
                    "contains",
                    choices=["contains", "prefix", "suffix", "exact"],
                    choice_labels=["包含", "开头", "结尾", "完全匹配"],
                ),
                ParameterSpec("case_sensitive", "bool", "区分大小写", False),
            ],
        ),
        NodeSpec(
            "transform.attr_list.get_item",
            "取属性引用列表项",
            "数据转换 / 属性",
            "数据转换",
            inputs=[
                PortSpec("attrs", "ATTR_LIST"),
                PortSpec("index", "NUMBER"),
            ],
            outputs=[PortSpec("attrs", "ATTR_LIST")],
        ),
        NodeSpec(
            "transform.attr_list.count",
            "属性引用列表数量",
            "数据转换 / 属性",
            "数据转换",
            inputs=[PortSpec("attrs", "ATTR_LIST")],
            outputs=[PortSpec("count", "NUMBER")],
        ),
        NodeSpec(
            "maya.selection.select_nodes",
            "选择节点",
            "Maya 操作 / 选择",
            "Maya 操作",
            inputs=[PortSpec("nodes", "NODE_LIST")],
            outputs=[PortSpec("selected_nodes", "NODE_LIST")],
        ),
        NodeSpec(
            "maya.animation.copy_frame",
            "复制帧",
            "动画操作 / 世界坐标",
            "数据获取",
            inputs=[
                PortSpec("nodes", "NODE_LIST", "复制对象"),
                PortSpec("frames", "FRAME_LIST", "帧", required=False),
                PortSpec("channels", "CHANNEL_LIST", "通道", required=False),
            ],
            outputs=[PortSpec("frame_data", "TRANSFORM_FRAME_DATA", "帧数据")],
            parameters=[
                ParameterSpec("record_short_name", "bool", "记录短名称", True),
                ParameterSpec("save_json_when_unconnected", "bool", "未连接时保存 JSON", True),
                ParameterSpec("json_path", "path", "JSON 路径", "", required=False),
            ],
        ),
        NodeSpec(
            "maya.attributes.set",
            "设置属性",
            "Maya 操作 / 属性",
            "Maya 操作",
            inputs=[
                PortSpec("attrs", "ATTR_LIST"),
                PortSpec("value", "VALUE"),
            ],
            outputs=[],
            parameters=[
                ParameterSpec(
                    "value_type",
                    "choice",
                    "值类型",
                    "auto",
                    choices=["auto", "text", "number", "bool"],
                    choice_labels=["自动", "文本", "数字", "布尔"],
                ),
            ],
        ),
        NodeSpec(
            "maya.nodes.rename",
            "重命名节点",
            "Maya 操作 / 节点",
            "Maya 操作",
            inputs=[PortSpec("nodes", "NODE_LIST")],
            outputs=[PortSpec("renamed_nodes", "NODE_LIST")],
            parameters=[
                ParameterSpec("base_name", "text", "基础名称", "renamed", required=True),
                ParameterSpec("start_index", "number", "起始编号", 1.0),
                ParameterSpec("padding", "number", "补零位数", 2.0),
            ],
        ),
        NodeSpec(
            "maya.nodes.group",
            "打组节点",
            "Maya 操作 / 节点",
            "Maya 操作",
            inputs=[PortSpec("nodes", "NODE_LIST")],
            outputs=[PortSpec("group_node", "NODE_LIST")],
            parameters=[
                ParameterSpec("group_name", "text", "组名称", "blueprint_grp", required=True),
            ],
        ),
        NodeSpec(
            "maya.nodes.delete",
            "删除节点",
            "Maya 操作 / 节点",
            "Maya 操作",
            inputs=[PortSpec("nodes", "NODE_LIST")],
            outputs=[],
        ),
        NodeSpec(
            "maya.constraints.parent",
            "父子约束",
            "Maya 操作 / 约束",
            "Maya 操作",
            inputs=[
                PortSpec("drivers", "NODE_LIST"),
                PortSpec("driven", "NODE_LIST"),
            ],
            outputs=[
                PortSpec("constraints", "NODE_LIST"),
            ],
            parameters=[
                ParameterSpec("maintain_offset", "bool", "保持偏移", True),
                ParameterSpec("weight", "number", "权重", 1.0),
            ],
        ),
        NodeSpec(
            "maya.constraints.point",
            "点约束",
            "Maya 操作 / 约束",
            "Maya 操作",
            inputs=[
                PortSpec("drivers", "NODE_LIST"),
                PortSpec("driven", "NODE_LIST"),
            ],
            outputs=[
                PortSpec("constraints", "NODE_LIST"),
            ],
            parameters=[
                ParameterSpec("maintain_offset", "bool", "保持偏移", True),
                ParameterSpec("weight", "number", "权重", 1.0),
            ],
        ),
        NodeSpec(
            "maya.constraints.orient",
            "方向约束",
            "Maya 操作 / 约束",
            "Maya 操作",
            inputs=[
                PortSpec("drivers", "NODE_LIST"),
                PortSpec("driven", "NODE_LIST"),
            ],
            outputs=[
                PortSpec("constraints", "NODE_LIST"),
            ],
            parameters=[
                ParameterSpec("maintain_offset", "bool", "保持偏移", True),
                ParameterSpec("weight", "number", "权重", 1.0),
            ],
        ),
        NodeSpec(
            "maya.constraints.scale",
            "缩放约束",
            "Maya 操作 / 约束",
            "Maya 操作",
            inputs=[
                PortSpec("drivers", "NODE_LIST"),
                PortSpec("driven", "NODE_LIST"),
            ],
            outputs=[
                PortSpec("constraints", "NODE_LIST"),
            ],
            parameters=[
                ParameterSpec("maintain_offset", "bool", "保持偏移", True),
                ParameterSpec("weight", "number", "权重", 1.0),
            ],
        ),
        NodeSpec(
            "maya.io.import_file",
            "导入文件",
            "Maya 操作 / 文件",
            "Maya 操作",
            inputs=[PortSpec("file_path", "PATH")],
            outputs=[
                PortSpec("imported_nodes", "NODE_LIST"),
            ],
            parameters=[
                ParameterSpec(
                    "mode",
                    "choice",
                    "模式",
                    "import",
                    choices=["import", "reference"],
                    choice_labels=["导入", "引用"],
                ),
                ParameterSpec("namespace", "text", "命名空间", ""),
                ParameterSpec("preserve_references", "bool", "保留引用", True),
            ],
        ),
        NodeSpec(
            "maya.io.export_fbx",
            "导出 FBX",
            "Maya 操作 / 文件",
            "Maya 操作",
            inputs=[
                PortSpec("nodes", "NODE_LIST"),
                PortSpec("target_path", "PATH"),
            ],
            outputs=[PortSpec("result", "FILE_RESULT")],
            parameters=[
                ParameterSpec("bake_animation", "bool", "烘焙动画", False),
                ParameterSpec("frame_start", "number", "起始帧", 1.0),
                ParameterSpec("frame_end", "number", "结束帧", 120.0),
                ParameterSpec("overwrite_existing", "bool", "覆盖已有文件", False),
            ],
        ),
    ]


def default_node_specs():
    specs = {}
    for spec in _built_in_specs():
        specs[spec.node_type] = spec
    return specs
