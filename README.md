# Maya 生产力工具箱 (Maya Tools Box v2.0)

> **工业级 Maya 生产力工具集 & 大模型 (LLM / Agent) 脚本调用统一框架**
> - **统一规范架构**：公共基础库 (`maya_toolkit.core`) + 框架协议 (`maya_toolkit.framework`) + 业务工具层 (`maya_toolkit.tools`)。
> - **大模型直接调取**：支持标准 JSON Schema / OpenAI Function Calling / MCP Tools 导出，大模型可通过单行 `execute_tool(tool_id, args)` 调度任何工具。
> - **安全预检与事务保障**：所有工具支持 `dry_run` 预检模式（零场景污染），正式执行严格受控于 Maya 原生单层 Undo Chunk（`Ctrl+Z` 一键撤销）。
> - **100% 保持向后兼容**：保留原有根目录脚本入口与 Shelf 视口一键拖拽安装，平滑升级无缝使用。

---

## 🧰 内置六大生产力工具一览

| 工具 ID (`tool_id`) | 工具名称 | 分类 | 核心功能简介 |
| :--- | :--- | :--- | :--- |
| **`compare_and_sync_fbx`** | FBX外部资产深度比对与同步 | Pipeline | 纯内存读取外部FBX，全维度比对拓扑/材质/位姿并选择性精准同步 |
| **`assign_materials_by_rows`** | 双列表按行一对一材质指定 | Modeling | 严格按行号传递材质，支持分面多材质与拓扑不一致安全降级 |
| **`copy_overlapping_weights`** | 复制重叠位置顶点蒙皮权重 | Rigging | OpenMaya 2.0 空间哈希检索，毫秒级快速传递重叠点蒙皮权重 |
| **`export_sets_to_fbx`** | 选择集批量导出 FBX 工具 | Pipeline | 自动读取用户选择集 (objectSet)，批量导出为独立FBX文件 |
| **`fix_rotation_winding`** | 欧拉旋转360度跳变修正工具 | Animation | 识别并消除 ±360°/±720° 异常阶跃导致的自转暴走，切线无损保护 |
| **`clean_namespaces`** | 场景命名空间清理工具 | Pipeline | 本地命名空间安全合并至根目录，引用节点平滑迁移消除命名空间 |

---

## 🤖 大模型 (LLM / Agent) 与自动化流水线调用

通过统一派发器，大模型可以精准执行任务或进行预检：

```python
import sys
tool_root = r"D:/Users/zhongweijie/Documents/GitHub/maya_tools_box"
if tool_root not in sys.path:
    sys.path.insert(0, tool_root)

import maya_toolkit

# 1. 预检模式 (Dry-Run: 仅做校验，绝不修改场景)
dry_res = maya_toolkit.execute_tool(
    "clean_namespaces",
    {"nodes": ["char:body"]},
    dry_run=True
)
print("预检结果:", dry_res.to_dict())

# 2. 导出所有工具的 OpenAI Function Calling / MCP Tools 定义规范
openai_tools = maya_toolkit.export_tool_schemas(format_type="openai")
```

更多大模型调用与各工具详细入参定义，请参考：[llm_tools_cheatsheet.md](file:///d:/Users/zhongweijie/Documents/GitHub/maya_tools_box/docs/llm_tools_cheatsheet.md)  
开发者扩展新工具规范，请参考：[tool_development_specification.md](file:///d:/Users/zhongweijie/Documents/GitHub/maya_tools_box/docs/tool_development_specification.md)

---

## 🌟 跨机器安装与启动方法 (任选一种)

### 🚀 方法一：视口一键拖拽安装 (最推荐，3秒搞定)
1. 打开 Autodesk Maya（支持 Maya 2017 ~ 2026+）。
2. 在 Windows 文件管理器中，将本文件夹中的 **`drag_and_drop_install.mel`** 直接鼠标拖拽到 Maya 的 **3D 视口中心**。
3. Maya 会弹出安装成功提示，并在您当前的工具架（Shelf）上自动生成专有图标按钮，并自动弹出统一工具箱主面板！

---

### 💻 方法二：脚本编辑器一键启动 (临时使用或集成流水线)
打开 Maya **脚本编辑器 (Script Editor)** -> 切换到 **Python** 标签页，运行以下两行代码即可打开统一控制台：

```python
import sys
tool_dir = r"D:/path/to/maya_tools_box"
if tool_dir not in sys.path:
    sys.path.insert(0, tool_dir)

import maya_toolkit
maya_toolkit.show_ui()
```

---

### ⚙️ 方法三：双击 `install.bat` (系统环境配置)
- 如果其他电脑的艺术家希望直接将 FBX SDK 模块安装到系统默认的 Maya Python 库中，可直接双击运行本目录下的 **`install.bat`**。
- 脚本会自动检测本地已安装的 Maya 2024、Maya 2025、Maya 2026 并自动执行安装。

---

## 🛠️ 跨机器兼容性与引擎说明

| Maya 版本 | Python 版本 | 激活引擎模式 | 说明 |
| :--- | :--- | :--- | :--- |
| **Maya 2025 / 2026** | Python 3.11 | **● Autodesk FBX SDK** | 自动加载本包自带的 `python311` 官方预编译库，纯内存解析 |
| **Maya 2024** | Python 3.10 | **● Autodesk FBX SDK** | 自动加载本包自带的 `python310` 官方预编译库，纯内存解析 |
| **Maya 2022 / 2023** | Python 3.7 / 3.9 | **● Maya 沙箱隔离提取引擎** | 自动平滑降级为静默沙箱隔离加载 + 提取赋材质 + 彻底销毁临时几何体，确保 100% 零残留运行 |

> **提示**：如果您的工作站有特定外置 FBX SDK 路径，可在界面顶部 `自定义 SDK 路径` 输入框中填入并点击 `加载 SDK` 随时热切换。

---

## 📋 功能特点与操作指南

### 1. 🔍 全维度资产比对
- 载入外部 FBX 后，点击 **“开始全维度资产深度比对”**，系统将自动扫描场景与 FBX 并进行比对分类：
  - **🟢 完全吻合**：拓扑、材质球分配、UV 通道与变换位姿 100% 一致。
  - **🟡 材质差异**：几何拓扑一致，但材质球名称、贴图属性或分面分配区间不同。
  - **🟠 变换差异**：拓扑与材质一致，但位移坐标、旋转角度或缩放比例存在偏差。
  - **🔴 拓扑冲突**：顶点数、多边形面数或三角化面数不同，标记风险。
  - **⚪ 单侧缺失**：仅存在于 Maya 场景或仅存在于外部 FBX 文件中。

### 2. 🗂️ 动态过滤器与实时搜索
- 顶部过滤器标签提供实时数量徽章（如 `全部 (12)`、`仅差异 (5)`、`材质差异 (2)`、`拓扑冲突 (1)` 等）。
- 支持在搜索框中实时根据资产名称过滤显示。

### 3. 📊 逐项双列对照详情卡片 (Side-by-Side Inspector)
- 在上方列表中单击选中任意资产，下方即刻展现该资产在 **Maya 场景** 与 **外部 FBX** 的逐项对比：
  - 顶点总数 (Vertices)、面数 (Polygons)、三角面数 (Triangles)
  - UV 通道集 (UV Sets)
  - 关联材质球列表与分面区间 (Face Assignments)
  - 空间坐标位移 (Translation)、旋转 (Rotation)、缩放 (Scaling)

### 4. ⚡ 差异修改与精准同步
- **✨ 一键同步选中材质与分面**：
  - 将外部 FBX 中的材质网络与分面指派重构并赋予选中资产。
  - **智能安全回退**：若模型面数被优化导致拓扑不一致，自动安全回退为整物赋予主材质，绝不报错或损坏模型。
- **📐 一键同步选中变换**：
  - 将选中的 Maya 资产空间位移、旋转角度、缩放比例瞬间对齐到外部 FBX。
- **🎯 视口高亮对焦选中项**：
  - 在列表中选中资产后，点击此按钮可直接在 Maya 3D 视口和大纲视图中选择并自动对焦（Frame）该物体。
- **📄 导出核查报告**：
  - 一键将本次比对的完整资产清单、状态及差异指标导出为高可读性的 Markdown 文档，便于团队交接与美术质检。

### 5. 🛡️ 完整撤销保护 (Undo)
- 所有同步操作均包裹在 Maya 原生 Undo Chunk 中，只需在 Maya 中按下 `Ctrl + Z` 即可一键撤销所有修改。

---

## 📦 待整理工具库与新工具准入工作流 (Tools Staging Pool)

项目建立了独立的待整理工具库：[`tools_staging_pool/`](tools_staging_pool/README.md)，收纳了来自历史脚本与网盘积累的 **54 个精选工具**（涵盖动画、绑定、空间变换、资产管线、UE管线、安全杀毒、大型子套件等 8 大领域）。

### 规则：新工具准入与转正流程
1. **待整理库优先入驻**：所有新制作、新收集的工具原型必须首先放置在 `tools_staging_pool/` 对应分类下；
2. **轻量 Maya 直验模式**：测试方式保持最轻量直接——在已打开的 Maya 实例中直接运行脚本或呼出界面进行实操验证；
3. **确认无误后规范化转正**：只有在 Maya 实测可用且确认无报错后，才由开发者或 Agent 继承 `BaseMayaTool`、编写单元测试并正式封装迁移至 `maya_toolkit/tools/` 生产库中。

