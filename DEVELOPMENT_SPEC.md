# Maya 个人工具知识库开发规范

> 版本：v2.2（与当前 framework 接口对齐）
>
> 范围：整理用户自己编写的旧 Maya 脚本和新工具。具体 Maya、Python、Qt 兼容范围以逐工具实测记录为准。

## 1. 项目目标

本项目把分散的脚本逐步整理为可复用、可检索、可调用、可组合的 Maya 工具知识库：

1. Maya 用户可通过统一启动面板使用工具。
2. 脚本和大模型通过同一执行入口调用工具，获得结构化结果。
3. 工具共享 maya_toolkit.core 的通用能力，不重复维护相同底层逻辑。
4. 每个转正工具都附有面向人和大模型的说明，写清适用条件、参数、结果、影响及关联工具。
5. 新旧工具持续进入待整理库，经过真实 Maya 验证后再转正。

当前框架提供单工具调度与 Schema 导出；跨工具流程编排和文档检索仍是后续建设方向。MCP 格式导出的是工具描述，需要另行接入 MCP 服务端才能提供远程调用。

## 2. 目录与业务领域

| 路径 | 职责 |
| --- | --- |
| maya_toolkit/core/ | Maya 节点、几何、Undo、字符串、UI 等可复用能力 |
| maya_toolkit/framework/ | BaseMayaTool、ToolResult、ToolRegistry 与统一执行入口 |
| maya_toolkit/tools/TOOL_NAME/ | 已通过 Maya 直验的正式工具，当前按工具建目录 |
| maya_toolkit/ui/ | 统一启动面板 |
| tools_staging_pool/ | 个人旧脚本和新原型的待整理库 |
| docs/tools/ | 转正工具的操作与知识说明 |
| tests/ | 框架及转正工具的回归测试 |

正式工具的 category 是业务领域元数据，不要求目录与领域一一对应。只能使用以下六个领域键：animation、rigging、modeling_surfacing、pipeline_io、scene_hygiene、engine_bridge。待整理库的八个物理分类与正式工具的六个业务领域是两套不同用途的分类。

## 3. 当前框架的真实调用契约

正式工具继承 BaseMayaTool，声明 tool_id、tool_name、category、version、description 和 parameters_schema，并实现：

- validate(**kwargs) -> ToolResult：无副作用预检。检查参数、选择和场景条件；失败时返回 ToolResult.fail(...)。
- execute(**kwargs) -> ToolResult：正式业务操作。只在预检成功后由基类调用。
- run(dry_run=False, **kwargs) -> ToolResult：基类提供的统一入口，普通工具不需要重新实现。
- show_ui(parent=None)：可选的独立 UI 入口。

对外优先通过 maya_toolkit.execute_tool(tool_id, arguments=None, dry_run=False) 调用。ToolRegistry 会找到工具，再调用该工具的 run。parameters_schema 用于导出调用描述；**当前框架不会自动按 Schema 校验参数**，必要校验必须由 validate 实现。当前基类没有 get_schema() 方法，也不采用 execute(arguments, dry_run=False) 签名。

示例：

~~~python
from maya_toolkit.framework import BaseMayaTool, ToolResult, ToolDomain


class MyTool(BaseMayaTool):
    tool_id = "my_tool"
    tool_name = "我的工具"
    category = ToolDomain.MODELING_SURFACING
    version = "1.0.0"
    description = "对指定对象执行一项明确的操作。"
    parameters_schema = {
        "type": "object",
        "properties": {
            "target_nodes": {
                "type": "array",
                "items": {"type": "string"},
                "description": "目标节点列表"
            }
        },
        "required": ["target_nodes"],
        "additionalProperties": False
    }

    def validate(self, target_nodes=None, **kwargs):
        if not target_nodes:
            return ToolResult.fail(message="未提供目标节点", errors=["EMPTY_TARGETS"])
        # 此处继续检查节点与场景状态，但不得修改场景。
        return ToolResult.ok(message="预检通过", data={"target_count": len(target_nodes)})

    def execute(self, target_nodes=None, **kwargs):
        # 基类在 Maya Undo Chunk 中调用此方法。
        # 文件写入、导出等外部影响需要额外处理。
        return ToolResult.ok(message="处理完成", data={"processed_nodes": target_nodes})
~~~

调用示例：

~~~python
import maya_toolkit

args = {"target_nodes": ["pCube1"]}
preview = maya_toolkit.execute_tool("my_tool", args, dry_run=True)
if preview.success:
    result = maya_toolkit.execute_tool("my_tool", args)
    print(result.to_dict())
~~~

## 4. 统一结果与大模型描述

通过 run 或 execute_tool 返回的 ToolResult 包含以下字段：

| 字段 | 含义 |
| --- | --- |
| success | 执行是否成功 |
| tool_id | 工具 ID；经统一入口返回时由框架填写 |
| message | 供用户和大模型阅读的简短结论 |
| data | 结构化业务结果 |
| errors、warnings | 错误与警告列表 |
| dry_run | 是否为预检结果 |
| execution_time | 执行耗时，单位为秒 |

ToolResult 支持 to_dict() 和 to_json()。data 应使用可序列化的基础类型，避免将 Maya 对象或 Qt 对象直接放入结果。

ToolRegistry 可按 category 列出工具并导出 OpenAI Function Calling 或 MCP Tools 格式的参数描述。Schema 负责“怎么调用”；完整知识说明还应补足“什么时候调用、会产生什么影响、能接到哪个工具后面”。

## 5. 每项工具的知识说明

转正时在 docs/tools/ 建立说明，可使用 [_tool_knowledge_template.md](docs/tools/_tool_knowledge_template.md)。至少写明：

1. 工具 ID、用途、适用与不适用场景。
2. 输入参数、默认值、选择依赖和必要前提。
3. dry_run 实际检查的内容。
4. 输出 data 的字段、错误与警告含义。
5. 场景修改、文件写入、导出等影响，以及可撤销范围。
6. 一段可运行的单工具调用示例。
7. 可组合的其他 tool_id、传递的数据和组合顺序。
8. Maya 实测版本、结果和已知限制。

不要在文档中声称一个未经过验证的工具或版本已经可用。工具 Schema 与说明文档变动时应同步更新。

## 6. 安全与兼容原则

- 模块导入不得自动修改 Maya 场景，也不得自动打开阻塞式对话框。
- validate 和 dry_run 路径不得修改场景或写文件。
- 基类的 run 会把 execute 放入一个 Maya Undo Chunk，便于对场景修改执行一次撤销；Undo Chunk 会在异常时关闭，但**不会自动回滚**已经发生的操作。
- 文件导出、外部文件覆盖及跨进程操作不受 Maya Undo 保护。此类工具应在文档中说明影响，并在执行前检查路径与覆盖条件。
- UI 与业务 API 分离，使核心逻辑尽可能在 mayapy 或批处理环境下使用。
- 跨版本兼容是目标，不能仅凭语法或条件导入就宣称某个 Maya 版本已通过验证。

## 7. 三步准入与回归

1. **入库**：个人旧脚本或新原型进入 tools_staging_pool/ 对应分类，保留所需素材与配置。
2. **真实 Maya 直验**：在已打开的 Maya 中启动 UI、操作核心控件、验证选区与场景行为，并检查 Script Editor 的错误信息。不合格则留在待整理库继续修改。
3. **转正**：复用或扩展 core，按第 3 节封装 API，增加知识说明与 tests/test_TOOL_ID.py，注册到 ALL_TOOL_CLASSES 并接入统一面板。转正后再次在 Maya 中验证。

不因整理文档或通过纯 Python 单测就跳过真实 Maya 验证。对现有已转正工具，本规范作为后续修订目标；不把尚未完成的要求写成已实现事实。
