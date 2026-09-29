# Maya Tools Box（个人 Maya 工具与知识库）

[![Maya](https://img.shields.io/badge/Maya-2017~2026%2B-blue.svg)](https://www.autodesk.com/products/maya)
[![Python](https://img.shields.io/badge/Python-2.7%20%7C%203.7~3.11-green.svg)](https://www.python.org/)
[![Qt](https://img.shields.io/badge/UI-PySide2%20%7C%20PySide6-orange.svg)](https://wiki.qt.io/Qt_for_Python)
[![LLM Native](https://img.shields.io/badge/AI-Function%20Calling%20%26%20MCP%20Schema-brightgreen.svg)](DEVELOPMENT_SPEC.md)

> 本项目持续整理个人编写的 Maya 旧脚本与新工具，将可复用能力沉淀到共享底层。目标是让每项正式工具都有统一 API 和说明文档，既能从 Maya 面板使用，也能由脚本或大模型按参数 Schema 调用，并逐步组合成工作流程。

---

## 🌟 核心特性与架构亮点

- 🤖 **统一调用描述**：正式工具声明 JSON Schema 参数并返回 `ToolResult`；框架可导出 Function Calling 与 MCP 工具描述，供外部 Agent 或 MCP 服务集成。
- 🛡️ **预检与撤销分组**：正式工具通过 `dry_run=True` 执行无场景修改的预检；场景操作使用 Maya Undo Chunk 分组。文件导出等外部影响需由工具单独说明。
- ⚡ **高性能底层支持**：深入结合 Maya API 2.0 (OpenMaya 2.0) 与空间哈希算法（如毫秒级重叠蒙皮检索），大幅超越传统 MEL 或纯 cmds 遍历。
- 🌐 **跨版本适配目标**：逐步兼顾 Maya 2017 ~ 2026+、Python 2.7 / 3.7~3.11 与 PySide2 / PySide6；具体支持范围以工具的 Maya 实测记录为准。
- 🔄 **渐进整理**：自有旧脚本与新原型先进入 `tools_staging_pool/`，经 Maya 直验后再转正到 `maya_toolkit/tools/`。

## 🗂️ Obsidian 项目知识库

整个项目目录可直接作为 Obsidian Vault 打开，入口是 [knowledge/00-首页.md](knowledge/00-首页.md)。知识库从正式工具元数据、待整理库目录、API Schema 和代码 import 关系生成工具页、模块页、规模评估与结构图；源代码仍保留在原位置。

运行 [实时同步脚本](knowledge/启动实时同步.ps1) 后，源码或文档变化会更新知识库页面。结构关联只表示代码复用，实际功能组合仍需 Maya 直验并写入专项知识说明。

在新电脑上恢复同样的 Vault、实时同步与 Codex MCP 连接，按 [Obsidian 换机安装指引](OBSIDIAN_SETUP.md) 操作。日常使用与知识编辑约定见 [MCP 连接说明](knowledge/MCP连接.md)。

---

## 🛠️ 内置官方转正生产工具矩阵

当前已完成工业化架构转正并挂载至启动器的 6 大核心工具：

| 工具标识 (`tool_id`) | 工具名称 | 所属业务领域 (Domain Key) | 核心亮点与能力 | 专项文档 / 兼容入口 |
| :--- | :--- | :--- | :--- | :--- |
| `fix_rotation_winding` | **欧拉旋转 360° 跳变修正** | **动画与动作** (`animation`) | 智能差分识别 ±360°/±720° 旋转空转与阶跃，平滑解包对齐，严格保护曲线切线与权重 | [旧兼容入口](compat/fix_rotation_winding.py) |
| `copy_overlapping_weights` | **空间重叠顶点权重复制** | **角色绑定与变形** (`rigging`) | OpenMaya 2.0 空间网格哈希检索，毫秒级跨模型复制重叠点蒙皮，自动增补缺失骨骼 | [旧兼容入口](compat/copy_overlapping_weights.py) |
| `assign_materials_by_rows` | **双列表行对齐材质传递** | **模型与材质** (`modeling_surfacing`) | 支持双表拖拽排序、名称自然排序，整物及分面材质精准指定，拓扑冲突自动安全回退 | [旧兼容入口](compat/assign_materials_between_groups.py) |
| `compare_and_sync_fbx` | **外部 FBX 深度比对同步** | **资产管线与I/O** (`pipeline_io`) | 纯内存读取外部 FBX，拓扑/材质/位姿全维度 Side-by-Side 检查与选择性一键精准同步 | [专用使用说明](docs/tools/fbx_diff_sync_guide.md) |
| `export_sets_to_fbx` | **选择集批量导出 FBX** | **资产管线与I/O** (`pipeline_io`) | 自动扫描过滤场景用户选择集，支持批量命名、前/后缀修改与详尽 FBX 参数面板配置 | [旧兼容入口](compat/export_sets_to_fbx.py) |
| `clean_namespaces` | **场景命名空间平滑清理** | **场景健康安全** (`scene_hygiene`) | 智能平滑合并本地命名空间至根节点 `:`，支持顶层引用的安全无痕迁移，杜绝引用破坏 | [旧兼容入口](compat/remove_namespace_from_scene.py) |

---

## 🚀 快速上手 (美术师与交互使用)

### 方式一：呼出综合启动器主面板 (推荐)
在 Maya 脚本编辑器 (Script Editor) 中切换到 **Python** 标签，运行：

```python
import sys
tool_root = r"D:/Users/zhongweijie/Documents/GitHub/maya_tools_box"  # 替换为实际存放路径
if tool_root not in sys.path:
    sys.path.insert(0, tool_root)

import maya_toolkit
maya_toolkit.show_ui()  # 打开统一深色启动面板，一键检索并启动所有工具
```

### 方式二：视口一键拖拽安装工具架 (Shelf)
在文件管理器中将根目录下的 **`drag_and_drop_install.mel`** 直接拖入 Maya 3D 视口，系统将自动在当前工具架生成启动按钮，随点随用。

---

## 🤖 大模型 (LLM / Agent) 脚本定制与 API 接入

本工具箱为大模型提供了极简、统一且无状态的调度入口 `maya_toolkit.execute_tool`。

### 1. 大模型单行定制调度范例

```python
import sys
tool_root = r"D:/Users/zhongweijie/Documents/GitHub/maya_tools_box"
if tool_root not in sys.path:
    sys.path.insert(0, tool_root)

import maya_toolkit

# 步骤一：预检诊断（具体检查内容由工具的 validate() 定义）
dry_res = maya_toolkit.execute_tool(
    tool_id="fix_rotation_winding",
    arguments={"nodes": ["char_ctrl"], "tolerance": 90.0},
    dry_run=True
)
print("预检数据:", dry_res.data)

# 步骤二：正式执行（Maya 场景操作由 UndoChunk 分组）
if dry_res.success:
    result = maya_toolkit.execute_tool(
        tool_id="fix_rotation_winding",
        arguments={"nodes": ["char_ctrl"], "tolerance": 90.0},
        dry_run=False
    )
    print("执行结果:", result.to_dict())
```

### 2. 统一返回协议 (`ToolResult`) 结构
通过统一入口调用时，结果可转为如下结构化字典：
```json
{
  "success": true,
  "tool_id": "fix_rotation_winding",
  "message": "成功修正 1 个节点的旋转跳变",
  "data": {
    "jump_count": 2,
    "processed_nodes": ["char_ctrl"]
  },
  "errors": [],
  "warnings": [],
  "dry_run": false,
  "execution_time": 0.0128
}
```

### 3. 一键导出 Tool Schemas (供 Agent 自动发现能力)
```python
import maya_toolkit

# 1. 查询 6 大业务领域概览及旗下工具统计
domains_summary = maya_toolkit.list_domains_summary()

# 2. 导出全部工具的 OpenAI Function Calling / MCP Tools 描述（不包含 MCP 服务端）
openai_schemas = maya_toolkit.export_tool_schemas(format_type="openai")
mcp_schemas = maya_toolkit.export_tool_schemas(format_type="mcp")

# 3. 🌟 支持按业务领域分片导出（精准注入上下文，极大节省 Token 开销）
rigging_tools = maya_toolkit.export_tool_schemas(format_type="openai", domain="rigging")
```

> 📖 **更多大模型调用范例与参数速查**，请参阅：[docs/llm_tools_cheatsheet.md](docs/llm_tools_cheatsheet.md)。

---

## 📁 目录结构总览

```
maya_tools_box/
├── DEVELOPMENT_SPEC.md               # 🌟 统一开发与大模型定制规范 (必读)
├── README.md                         # 🌟 本文档 (项目综合总览与主页)
├── docs/                             # 详细技术文档与速查表
│   ├── llm_tools_cheatsheet.md       # 大模型 API 参数速查手册
│   └── tools/                        # 各专项工具详细说明
│       └── fbx_diff_sync_guide.md    # FBX 深度比对与同步工具操作说明
│
├── maya_toolkit/                     # 核心规范包
│   ├── core/                         # 底层纯函数库 (Mesh/Undo/上下文/排序/样式)
│   ├── framework/                    # 调度框架 (BaseMayaTool, ToolResult, Registry)
│   ├── tools/                        # 按工具建目录的正式实现，category 映射到 6 大业务领域
│   └── ui/                           # 统一启动面板与界面逻辑
│
├── compat/                           # 旧脚本入口的兼容转发层
├── tools_staging_pool/               # 待整理与实验工具储备池 (8大分类、54项工具)
│   ├── 01_animation/                 # 动画类待整理脚本
│   ├── 02_rigging/                   # 绑定类待整理脚本
│   ├── 03_transforms_modeling/       # 变换与建模类待整理脚本
│   └── ...
│
├── tests/                            # 自动化单元测试集
└── drag_and_drop_install.mel         # 视口拖拽一键安装脚本
```

---

## 📖 开发者与新工具准入规范

项目实行严格的**“待整理池 (`tools_staging_pool/`) ➔ Maya 实测直验 ➔ 规范封装 (`maya_toolkit/tools/`)”**生命周期管理。

在整理旧工具或开发新工具前，请阅读：
👉 **[DEVELOPMENT_SPEC.md (Maya 工具箱统一开发与大模型定制规范)](DEVELOPMENT_SPEC.md)**

该规范详尽定义了：
- 底层库复用准则 (DRY 原则)；
- 继承 `BaseMayaTool` 与实现 `parameters_schema` 的标准规范；
- 严禁模块顶层直接执行的安全防线；
- 新工具的 API、知识说明与代码模板。

---
