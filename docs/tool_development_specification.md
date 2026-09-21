# Maya 工具箱统一开发与大模型对接规范 (Tool Development Specification)

> **版本**：v2.0.0  
> **适用环境**：Autodesk Maya 2017 ~ 2026+ (Python 2.7 / 3.7 / 3.9 / 3.10 / 3.11, PySide2 / PySide6)  
> **面向对象**：TA 技术美术、流水线研发工程师 (Pipeline TD)、AI Agent 大模型自主脚本生成

---

## 目录
1. [架构分层与设计哲学](#1-架构分层与设计哲学)
2. [公共基础库复用准则 (DRY 原则)](#2-公共基础库复用准则-dry-原则)
3. [大模型调用与统一接口标准 (BaseMayaTool)](#3-大模型调用与统一接口标准-basemayatool)
4. [统一返回协议 (ToolResult)](#4-统一返回协议-toolresult)
5. [无副作用与 Headless 运行规范](#5-无副作用与-headless-运行规范)
6. [新工具编写开发模板](#6-新工具编写开发模板)

---

## 1. 架构分层与设计哲学

本项目采用四层分层架构，杜绝单文件千行大杂烩，实现**业务逻辑、无界面执行、图形界面与大模型调取**的彻底解耦：

```
maya_tools_box/
├── maya_toolkit/                    # 核心包
│   ├── core/                        # [第一层] 公共基础支撑库 (纯底层工具函数)
│   │   ├── maya_utils.py            # Maya 几何/DAG/Shape/选择集/插件安全工具
│   │   ├── context.py               # UndoChunk / 视口刷新抑制 / 计时上下文
│   │   ├── string_utils.py          # 自然排序 / 命名合法化 / Markdown 表格
│   │   ├── ui_base.py               # 跨版本 Maya 主窗口获取 / 统一深色 QSS
│   │   └── logger.py                # 结构化日志收集器
│   │
│   ├── framework/                   # [第二层] 框架调度与协议层
│   │   ├── models.py                # ToolResult 统一返回协议
│   │   ├── base_tool.py             # BaseMayaTool 抽象基类
│   │   ├── registry.py              # ToolRegistry 工具注册与 Schema 导出中心
│   │   └── executor.py              # execute_tool 统一调度派发器
│   │
│   └── tools/                       # [第三层] 业务工具实现层
│       ├── fbx_diff/                # FBX 深度比对与同步
│       ├── material_transfer/       # 双列表行对齐材质传递
│       ├── weights_copy/            # 空间哈希重叠权重复制
│       ├── fbx_export/              # 选择集批量导出 FBX
│       ├── euler_winding/           # 欧拉角 360 度异常跳变修正
│       └── namespace_clean/         # 场景命名空间平滑清理
│
└── [旧工具脚本兼容入口]              # [第四层] 根目录向后兼容转发层 (Shelf / MEL 按钮)
    ├── compare_and_sync_fbx_assets.py
    ├── assign_materials_between_groups.py
    ├── copy_overlapping_weights.py
    ├── export_sets_to_fbx.py
    ├── fix_rotation_winding.py
    └── remove_namespace_from_scene.py
```

---

## 2. 公共基础库复用准则 (DRY 原则)

凡是涉及以下常见操作，**严禁在工具脚本中重新定义或复制粘贴**，必须统一引用 `maya_toolkit.core`：

| 业务场景 | 统一 API | 来源模块 |
| :--- | :--- | :--- |
| 获取 Mesh 节点长名称（兼容 Transform/组件） | `get_mesh_shape(node)` | `maya_toolkit.core` |
| 获取 OpenMaya 2.0 MDagPath | `get_mesh_dag(node)` | `maya_toolkit.core` |
| 查询绑定的蒙皮簇节点 | `get_skin_cluster(mesh)` | `maya_toolkit.core` |
| 递归解析父组并展开所有网格 | `resolve_selected_meshes(nodes)` | `maya_toolkit.core` |
| 确保指定插件已加载 | `ensure_plugin("fbxmaya")` | `maya_toolkit.core` |
| 获取场景中所有用户选择集 | `get_all_user_selection_sets()` | `maya_toolkit.core` |
| 安全获取 Maya 主窗口作为 Qt 父级 | `get_maya_main_window()` | `maya_toolkit.core` |
| 统一深色样式表美化 | `apply_dark_theme(widget)` | `maya_toolkit.core` |
| 带数字的名称自然排序 (自然排序) | `sorted(list, key=natural_sort_key)` | `maya_toolkit.core` |
| 事务与 Ctrl+Z 撤销包裹 | `with UndoChunkContext("ChunkName"):` | `maya_toolkit.core` |
| 大批量操作提速（挂起刷新） | `with SuspendRefreshContext():` | `maya_toolkit.core` |

---

## 3. 大模型调用与统一接口标准 (BaseMayaTool)

所有新工具或重构工具必须继承 `BaseMayaTool`，并实现以下规范：

```python
from maya_toolkit.framework import BaseMayaTool, ToolResult

class MyCustomTool(BaseMayaTool):
    tool_id = "my_custom_tool"         # 唯一标识符（纯小写字母+下划线）
    tool_name = "我的自定义工具"          # 中文展示名
    category = "Modeling"              # 分类：Animation, Rigging, Modeling, Pipeline
    version = "1.0.0"
    description = "详尽的中文功能描述，大模型依据此语义判定是否触发本工具。"

    # 符合 JSON Schema (Draft-07) 的入参定义
    parameters_schema = {
        "type": "object",
        "properties": {
            "target_nodes": {
                "type": "array",
                "items": {"type": "string"},
                "description": "要处理的节点名称列表。"
            },
            "tolerance": {
                "type": "number",
                "default": 0.01,
                "description": "计算容差阈值。"
            }
        },
        "required": ["target_nodes"],
        "additionalProperties": False
    }

    def validate(self, **kwargs):
        """
        预检校验逻辑：必须无副作用！
        在大模型真正调用修改场景前，校验节点是否存在、参数范围是否合法。
        """
        nodes = kwargs.get("target_nodes", [])
        # 校验逻辑...
        return ToolResult.ok("参数预检通过", dry_run=True)

    def execute(self, **kwargs):
        """
        正式执行逻辑：底层会自动包裹在 UndoChunk 中，
        支持纯 mayapy/无界面环境下执行。
        """
        # 执行逻辑...
        return ToolResult.ok(message="处理完成", data={"processed_count": 10})

    def show_ui(self, parent=None):
        """界面展示逻辑（可选）"""
        pass
```

---

## 4. 统一返回协议 (ToolResult)

所有 API 与大模型调度派发器均返回 `ToolResult` 对象。
`ToolResult` 提供标准字典转换方法 `to_dict()` 与 JSON 序列化 `to_json()`：

```json
{
  "success": true,
  "message": "成功修正 3 条动画曲线，消除 5 处旋转跳变。",
  "data": {
    "modified_curves": 3,
    "fixed_keys_count": 12
  },
  "errors": [],
  "warnings": [],
  "dry_run": false,
  "execution_time": 0.042
}
```

- **success** (`bool`): 执行是否成功；
- **message** (`str`): 面向大模型或用户的高级摘要；
- **data** (`dict`): 结构化业务产出数据；
- **errors** (`list[str]`): 错误详情列表；
- **warnings** (`list[str]`): 告警或降级信息列表；
- **dry_run** (`bool`): 是否为仅预检（无场景修改）模式；
- **execution_time** (`float`): 耗时（秒）。

---

## 5. 无副作用与 Headless 运行规范

1. **严禁在模块顶层直接调用任何产生实际操作的代码**：
   - 错误范例：`remove_namespace_from_scene()` 写在文件最底部；
   - 正确范例：必须包裹在 `if __name__ == '__main__':` 中。
2. **严禁在业务逻辑中硬编码弹出阻塞式对话框**：
   - 错误范例：在核心计算函数中调用 `QtWidgets.QMessageBox.warning(...)`；
   - 正确范例：核心函数通过抛出异常、记录告警或返回 `ToolResult.fail(...)` 反馈，由外层 UI 控件捕获并呈现。
3. **自动兼顾 Headless / mayapy 运行**：
   - 框架层 `run()` 会自动按需调用 `ensure_maya_initialized()`，确保自动化批处理不因 `maya.standalone` 缺少初始化而报错。

---

## 6. 新工具编写开发模板

在 `maya_toolkit/tools/` 下新建工具子文件夹，例如 `maya_toolkit/tools/my_tool/`：

1. `__init__.py`: 导出工具类：
   ```python
   from .tool import MyTool
   __all__ = ["MyTool"]
   ```
2. `tool.py`: 继承 `BaseMayaTool` 实现标准类。
3. 在 `maya_toolkit/tools/__init__.py` 的 `ALL_TOOL_CLASSES` 列表中添加该工具类，即可自动接入全局注册表、大模型 Schema 导出与派发调度器！

---

## 7. 新工具生命周期与准入规范 (待整理库试制 -> Maya直验 -> 正式封装)

为保障生产环境核心库（`maya_toolkit/tools/`）的高质量与稳定性，所有新开发或新引入的工具严格执行**三阶段准入工作流**：

```
[1. 待整理库入驻]  -->  [2. 已开Maya直接实测]  -->  [3. 确认无误后规范化封装]
 tools_staging_pool/       无侵入执行脚本/开界面       BaseMayaTool + LLM Schema
```

1. **阶段一：待整理库试制 (`tools_staging_pool/`)**：
   - 凡是新开发的原型、外部引入的零散脚本，必须首先放入 `tools_staging_pool/` 对应的分类目录下（如 `01_animation/`、`04_pipeline_io/` 等）。
   - 保证脚本与素材、依赖项完整放置，暂无需按照基类深度重构。
2. **阶段二：轻量直验测试（直接在打开的 Maya 中执行）**：
   - 测试方式保持最轻量直观：**直接在已打开的 Maya 实例中执行该文件或呼出界面**。
   - 验证界面能否正常弹出、核心按钮/滑块是否响应、场景操作是否符合预期、Script Editor 无致命报错。
3. **阶段三：确认封装与转正 (`maya_toolkit/tools/`)**：
   - **只有经过 Maya 实测确认可用无误后**，方可由开发者或 Agent 启动正式封装。
   - 正式封装标准：
     - 继承 `BaseMayaTool`，解耦算法与界面；
     - 统一输入输出协议 (`ToolResult` + `get_schema()` + `dry_run`)；
     - 编写 `tests/test_<tool_id>.py` 单元测试；
     - 挂载入综合面板 `maya_toolkit.show_ui()`。

---

## 8. 开源工具吸纳与双向技术迭代规范 (Open-Source Ingestion & Evolution)

本项目支持可持续引入外部优秀开源工具（如 GitHub / Highend3D / Gumroad 分享工具），并实行**“双向技术互哺与择优升级”**：

### 8.1 外部工具统一标准化改造
外部工具在正式转正时，必须完成以下标准化适配：
1. **统一接口契约**：无论原工具是通过 MEL、原生 Qt、还是命令行编写，核心执行逻辑封装为 `run(**kwargs) -> ToolResult`；
2. **大模型 Schema 挂载**：实现 `get_schema()`，使外部工具直接获得被 AI Agent / 大模型调度的能力；
3. **UI 与内核解耦**：将原脚本中混杂在界面按钮事件中的算法剥离为纯函数，UI 部分统一适配 `maya_toolkit.core.ui_base` 深色主题。

### 8.2 双向技术比对与择优互哺 (Cherry-Picking & Evolution)
引入新工具时，必须进行“代际技术比对”：
- **场景 A：项目现有底层更先进**
  - 新工具常包含冗余或私有的辅助函数（如字符串拆分、查找 Shape、查找 SkinCluster、撤销块管理）。
  - **处理方案**：直接删除其私有实现，替换为复用 `maya_toolkit.core`（如 `get_mesh_shape`、`UndoChunk`、`ensure_plugin`），大幅精简代码并提升健壮性。
- **场景 B：外部开源工具算法更先进**
  - 新工具若拥有更高效的算法（如更优的物理次级动力学迭代、四元数插值、更快的空间哈希检索、更完善的异常修复）。
  - **处理方案**：
    1. **能力下沉**：将新工具中的核心先进算法抽象并沉淀至 `maya_toolkit.core`，赋能现有所有工具；
    2. **版本升级**：若新工具在功能和架构上全方位优于项目现有某工具，将其作为该工具的下一代官方升级版（如 `v2.0`），替换原有旧版，并在版本日志中予以记录；
    3. **开源礼仪与合规**：保留原项目开源许可证（MIT/GPL等），并在源码文件头与文档中完整保留原作者致谢。


