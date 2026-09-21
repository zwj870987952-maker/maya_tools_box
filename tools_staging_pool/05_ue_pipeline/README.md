# 05. 虚幻引擎协同管线 (Unreal Engine Pipeline)

> 涵盖 UE 资产源文件逆向追溯、UE 骨骼拓扑清单导出（Python 脚本 + C++ 插件包）、Maya 与 UE 自动化导入联动等跨软件工作流。

## 工具清单与导向

| 序号 | 工具名称 | 对应目录与入口 | 核心功能简述 | 建议重构优先级 |
| :--- | :--- | :--- | :--- | :--- |
| 1 | **UE 资产源文件迁移与反向查找** | [ue_source_finder](ue_source_finder/UE源文件迁移.py) | 结合 UE 资产管理，根据 Unreal 资产引用逆向反查 DCC（Maya/FBX）源文件路径，支持跨工程资产映射与迁移。 | P1 - 核心高频 |
| 2 | **UE 骨骼树清单导出 (Python + C++插件)** | [ue_bone_exporter](ue_bone_exporter/ExportBoneList.py) | 包含运行于 UE5 编辑器 Python 环境的导出脚本，以及原生 UE5 C++ 插件 (BoneListGenerator_UPlugin)，批量将 Skeletal Mesh 骨骼拓扑结构导出为文本。 | P1 - 核心高频 |
| 3 | **UE 资产自动化导入配置与执行脚本** | [ue_fbx_auto_import](ue_fbx_auto_import/ue导入fbx配置.py) | Maya 端配置好 FBX 导入参数后，直接跨进程触发 Unreal Engine 自动化执行资产导入与属性安全设置。 | P1 - 核心高频 |
| 4 | **UE 资产引用依赖与断链检查器** | [ue_reference_checker](ue_reference_checker/UE资产引用检查器.py) | 基于 Tkinter 的桌面工具，批量检测虚幻引擎项目资产间的引用依赖与断链丢失。 | P1 - 核心高频 |
| 5 | **UE5 编辑器右键源路径打印菜单** | [ue_context_menu](ue_context_menu/print_source_paths_menu.py) | UE5 编辑器右键资产菜单扩展，点击即可在日志中输出源 DCC 文件的物理路径。 | P1 - 核心高频 |

## 整合至 `maya_toolkit` 的规范要求
当您挑选本目录中的工具进行正式重构时，请遵循以下规范：
1. **继承基类**：所有工具类需继承自 `maya_toolkit.core.base_tool.BaseMayaTool`。
2. **标准化输出**：执行入口统一为 `run(**kwargs) -> ToolResult`，支持 `success`, `data`, `message`, `errors` 结构。
3. **大模型 Schema 支持**：通过 `get_schema()` 提供入参类型说明与默认值，支持 Agent 自动读取调用。
4. **安全试运行**：必须支持 `dry_run=True` 预检模式，在执行破坏性/批量操作前不产生实际副作用。
