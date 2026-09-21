# 04. 资产管线与批量导入导出 (Pipeline & I/O)

> 涵盖工业级 FBX/ABC 选择集批量导出面板、文件拖拽批量导入加强版、工程批量自动化静默处理框架、外部引用路径重定向与损坏清理等。

## 工具清单与导向

| 序号 | 工具名称 | 对应目录与入口 | 核心功能简述 | 建议重构优先级 |
| :--- | :--- | :--- | :--- | :--- |
| 1 | **FBX 批量导出综合套件 v7** | [fbx_batch_exporter_v7](fbx_batch_exporter_v7/fbx_export_CHS_v7.py) | 工业级 FBX 批量导出面板。支持按选择集批量输出、自动内嵌烘焙与重采样、一键取消骨骼分段比例补偿、时间轴区间自适应，并支持将导出预设保存为 JSON。 | P1 - 核心高频 |
| 2 | **Alembic (ABC) 批量导出套件** | [abc_batch_exporter](abc_batch_exporter/ABC导出_v3.py) | 支持按选择集（Selection Sets）批量导出 Alembic ABC 几何体缓存，内置自动建立材质分配信息与输出目录整理。 | P1 - 核心高频 |
| 3 | **文件批量导入加强版 v3** | [batch_importer_v3](batch_importer_v3/批量导入加强版v3.py) | 支持文件/文件夹拖拽批量录入、递归子文件夹导入、一键批量清除/合并 Reference 参考文件、智能去除或添加命名空间。 | P1 - 核心高频 |
| 4 | **工程文件批量自动化处理框架 v3** | [batch_processor_v3](batch_processor_v3/文件批量执行v3.py) | 自动化批处理框架。指定文件夹遍历 .ma/.mb 工程，逐个静默打开并批量运行指定的 Python/MEL 脚本，输出执行日志。 | P1 - 核心高频 |
| 5 | **无效与中文引用路径清理器** | [clean_invalid_paths](clean_invalid_paths/clean_invalid_paths.py) | 深度扫描场景所有节点属性，检测并清理带有中文、乱码或损坏失效的外部 Reference 引用与贴图纹理路径，防止崩溃。 | P1 - 核心高频 |
| 6 | **引用文件路径批量重定向与替换** | [replace_references](replace_references/reference替换EN封装版.py) | 批量搜索并替换场景中 Reference 节点的工程文件根路径与引用物体，用于团队多环境切换与工程迁移。 | P2 - 进阶扩展 |
| 7 | **舰船/载具资产特种 FBX 导出** | [vessel_fbx_exporter](vessel_fbx_exporter/fbx导出工具舰船专用_自动版.py) | 面向特定载具资产的层级规范校验与自动 FBX 导出，自动规范化 Root 层级与材质引用规范。 | P2 - 进阶扩展 |
| 8 | **模型逐帧转 BlendShape 导出 FBX** | [per_frame_bs_fbx](per_frame_bs_fbx/模型逐帧转bs导出fbx_v1.1.py) | 将变形动画模型逐帧生成 BlendShape 目标体，自动构建 BS 权重动画并导出 FBX，用于游戏引擎特种网格特效。 | P2 - 进阶扩展 |

## 整合至 `maya_toolkit` 的规范要求
当您挑选本目录中的工具进行正式重构时，请遵循以下规范：
1. **继承基类**：所有工具类需继承自 `maya_toolkit.core.base_tool.BaseMayaTool`。
2. **标准化输出**：执行入口统一为 `run(**kwargs) -> ToolResult`，支持 `success`, `data`, `message`, `errors` 结构。
3. **大模型 Schema 支持**：通过 `get_schema()` 提供入参类型说明与默认值，支持 Agent 自动读取调用。
4. **安全试运行**：必须支持 `dry_run=True` 预检模式，在执行破坏性/批量操作前不产生实际副作用。
