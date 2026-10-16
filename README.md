# Maya Tools Box（个人 Maya 工具与知识库）

[![Maya](https://img.shields.io/badge/Maya-per_tool_verification-blue.svg)](DEVELOPMENT_SPEC.md)
[![LLM Native](https://img.shields.io/badge/AI-Function%20Calling%20%26%20MCP%20Schema-brightgreen.svg)](DEVELOPMENT_SPEC.md)

> 本项目持续整理个人编写的 Maya 旧脚本与新工具，将可复用能力沉淀到共享底层。目标是让每项正式工具都有统一 API 和说明文档，既能从 Maya 面板使用，也能由脚本或大模型按参数 Schema 调用，并逐步组合成工作流程。

---

## 🌟 核心特性与架构亮点

- 🤖 **统一调用描述**：正式工具声明 JSON Schema 参数并返回 `ToolResult`；框架可导出 Function Calling 与 MCP 工具描述，供外部 Agent 或 MCP 服务集成。
- 🛡️ **预检与撤销分组**：正式工具通过 `dry_run=True` 执行无场景修改的预检；场景操作使用 Maya Undo Chunk 分组。文件导出等外部影响需由工具单独说明。
- ⚙️ **底层能力复用**：使用 Maya API、空间哈希等实现可复用能力；性能取决于数据规模、环境与算法，比较结果以实际测量为准。
- 🌐 **跨版本适配目标**：逐步兼顾 Maya 2017 ~ 2026+、Python 2.7 / 3.7~3.11 与 PySide2 / PySide6；具体支持范围以工具的 Maya 实测记录为准。
- 🔄 **渐进整理**：自有旧脚本与新原型先进入 `tools_staging_pool/`，经 Maya 直验后再转正到 `maya_toolkit/tools/`。

## 🗂️ Obsidian 项目知识库

整个项目目录可直接作为 Obsidian Vault 打开，入口是 [knowledge/00-首页.md](knowledge/00-首页.md)。知识库从正式工具元数据、待整理库目录、API Schema 和代码 import 关系生成工具页、模块页、规模评估与结构图；源代码仍保留在原位置。

运行 [实时同步脚本](knowledge/启动实时同步.ps1) 后，源码或文档变化会更新知识库页面。结构关联只表示代码复用，实际功能组合仍需 Maya 直验并写入专项知识说明。

在新电脑上恢复同样的 Vault、实时同步与 Codex MCP 连接，按 [Obsidian 换机安装指引](OBSIDIAN_SETUP.md) 操作。日常使用与知识编辑约定见 [MCP 连接说明](knowledge/MCP连接.md)。

---

## 🛠️ 正式工具矩阵

当前正式库列出并挂载至启动器的 8 个工具如下。正式库状态不代表所有模式、版本和组合均已验证，适用范围需结合专项说明与实测记录判断。

| 工具标识 (`tool_id`) | 工具名称 | 所属业务领域 (Domain Key) | 核心亮点与能力 | 专项文档 / 兼容入口 |
| :--- | :--- | :--- | :--- | :--- |
| `fix_rotation_winding` | **欧拉旋转 360° 跳变修正** | **动画与动作** (`animation`) | 处理旋转曲线的 360 度整数倍数值跳变；不是所有旋转问题的通用修复 | [旧兼容入口](compat/fix_rotation_winding.py) |
| `copy_overlapping_weights` | **空间重叠顶点权重复制** | **角色绑定与变形** (`rigging`) | 按空间容差匹配重叠顶点并复制权重，可按参数补充缺失影响骨骼 | [旧兼容入口](compat/copy_overlapping_weights.py) |
| `assign_materials_by_rows` | **双列表行对齐材质传递** | **模型与材质** (`modeling_surfacing`) | 按列表顺序传递材质；拓扑不匹配时的整物赋材质回退会改变分面效果 | [旧兼容入口](compat/assign_materials_between_groups.py) |
| `compare_and_sync_fbx` | **外部 FBX 比对同步** | **资产管线与I/O** (`pipeline_io`) | 比对工具支持的网格、材质及变换信息，并选择同步目标；读取方式取决于引擎 | [专用使用说明](docs/tools/fbx_diff_sync_guide.md) |
| `export_sets_to_fbx` | **选择集批量导出 FBX** | **资产管线与I/O** (`pipeline_io`) | 自动扫描过滤场景用户选择集，支持批量命名、前/后缀修改与详尽 FBX 参数面板配置 | [旧兼容入口](compat/export_sets_to_fbx.py) |
| `clean_namespaces` | **场景命名空间清理** | **场景健康安全** (`scene_hygiene`) | 合并本地命名空间及处理顶层引用命名空间；操作后需核对重名与引用状态 | [旧兼容入口](compat/remove_namespace_from_scene.py) |
| `advanced_skeleton_mirror` | **ADV 原生 Mirror** | **动画与动作** (`animation`) | 调用本机 ADV 原生姿态镜像，并提供无目标动画层的逐帧动画扩展；已验证 Maya 2024 / ADV 6.640 | [专项说明](docs/tools/advanced_skeleton_mirror.md) |
| `advanced_skeleton_animation` | **ADV 动画工具** | **动画与动作** (`animation`) | 封装 46 个原生入口，保留窗口、设备和插件环境的验证边界；默认发现本机最新 ADV 安装 | [专项说明与验收范围](docs/tools/advanced_skeleton_animation.md) |

---

## 🚀 快速上手 (美术师与交互使用)

### 方式一：呼出综合启动器主面板 (推荐)
在 Maya 脚本编辑器 (Script Editor) 中切换到 **Python** 标签，运行：

```python
import sys
tool_root = r"D:/path/to/maya_tools_box"  # 替换为实际存放路径
if tool_root not in sys.path:
    sys.path.insert(0, tool_root)

import maya_toolkit
maya_toolkit.show_ui()  # 打开统一深色启动面板，一键检索并启动所有工具
```

### 方式二：视口一键拖拽安装工具架 (Shelf)
在文件管理器中将根目录下的 **`drag_and_drop_install.mel`** 直接拖入 Maya 3D 视口，系统将自动在当前工具架生成启动按钮，随点随用。

---

## 🤖 大模型 (LLM / Agent) 脚本定制与 API 接入

本工具箱提供统一调度入口 `maya_toolkit.execute_tool`。调用仍依赖当前 Maya 场景、插件及工具运行状态；省略部分参数时还可能依赖当前选择，不能视为无状态调用。

### 1. 大模型单行定制调度范例

```python
import sys
tool_root = r"D:/path/to/maya_tools_box"  # 替换为实际存放路径
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
通过统一入口调用时，结果可转为如下结构化字典。下例仅展示公共字段；`data` 的业务字段因工具及预检/执行阶段而异，应读取实际结果，不从此示意推断字段名。
```json
{
  "success": true,
  "tool_id": "fix_rotation_winding",
  "message": "示意：处理完成",
  "data": {},
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

工具知识的 Agent Skills 组织与后续建设方案见 [Agent Skills 装配规范](docs/AGENT_SKILLS_ASSEMBLY_SPEC.md)：一次任务可组合多个 Skill 与工具，按功能条件和实际使用结果选择实现；结果默认后台记录，必要时才询问用户。规范同时覆盖不同 Agent 的统一装配和目标客户端的安装验收。当前已建立设计规范，自动装配、安装及使用记录评分功能尚未实现。

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
│   ├── core/                         # 公共能力库 (Mesh/Undo/上下文/排序/样式，部分依赖 Maya)
│   ├── framework/                    # 调度框架 (BaseMayaTool, ToolResult, Registry)
│   ├── tools/                        # 按工具建目录的正式实现，category 映射到 6 大业务领域
│   └── ui/                           # 统一启动面板与界面逻辑
│
├── compat/                           # 旧脚本入口的兼容转发层
├── tools_staging_pool/               # 待整理工具储备池，分类和数量以实际目录为准
│   ├── 01_animation/                 # 动画类脚本
│   ├── 02_rigging_hierarchy/         # 绑定与层级类脚本
│   ├── 03_transforms_modeling/       # 变换与建模类脚本
│   └── ...                          # 其余分类见实际目录和生成规模评估
├── tools_closed_source_pool/         # 闭源与二进制插件工具池
│   ├── 01_animation/                 # 动画类编译/混淆工具
│   ├── 02_rigging_hierarchy/         # 绑定类 C++ 动态插件 (.mll)
│   └── ...
│
├── tests/                            # 自动化单元测试集
└── drag_and_drop_install.mel         # 视口拖拽一键安装脚本
```

待整理库的当前数量见 [生成规模评估](knowledge/_generated/规模评估.md)。`plans/` 下的整理与验收记录描述各自批次，不作为当前库存或新增验证的证明。

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
