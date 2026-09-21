# 03. 空间变换、对齐与建模辅助 (Transforms & Modeling)

> 涵盖世界坐标识别通道对齐、综合旋转与轴向校准、四元数插值、对称镜像、轴心点归零、通道一键解锁与 GPU 缓存转实体等。

## 工具清单与导向

| 序号 | 工具名称 | 对应目录与入口 | 核心功能简述 | 建议重构优先级 |
| :--- | :--- | :--- | :--- | :--- |
| 1 | **世界坐标复制粘贴与对齐 (v4 最新增强版)** | [world_transform_v4](world_transform_v4/复制粘贴世界坐标v4.py) | 提取选中物体的全局世界矩阵（Translate、Rotate），支持识别通道、识别父子关系与迭代误差判定校准。 | P1 - 核心高频 |
| 2 | **多功能旋转与角度对齐工具** | [rotation_aligner](rotation_aligner/旋转对齐工具.py) | 综合对齐面板。整合了角度实时显示、欧拉旋转对齐、骨骼轴向对齐，可计算空间夹角并将选区旋转轴快速校准至目标。 | P1 - 核心高频 |
| 3 | **四元数旋转插值与转换 (Quaternion Tool)** | [quaternion_tool](quaternion_tool/QuaternionTool_Maya.py) | 提供欧拉角与四元数双向转换、球面线性插值 (SLERP)、绕任意轴向量旋转计算，解决旋转插值翻折问题。 | P1 - 核心高频 |
| 4 | **物体对称镜像工具 (Mirror Tool)** | [mirror_tool](mirror_tool/mirror_tool.py) | 根据左右命名规则（如 _L 与 _R），按世界或局部反射平面（XY/YZ/XZ）将位置、旋转与缩放批量镜像到对称侧。 | P1 - 核心高频 |
| 5 | **轴心点与几何中心重置工具** | [reset_pivot](reset_pivot/maya_reset_pivot.py) | 一键将物体 Pivot 轴心重置到 Bounding Box 边界框中心、几何中心或世界原点，并清空轴向旋转。 | P1 - 核心高频 |
| 6 | **一键解锁通道并冻结变换** | [unlock_freeze](unlock_freeze/unlock_and_freeze_transforms.py) | 批量递归遍历选中节点及其子级，一键解锁所有被锁定/隐藏的位移、旋转、缩放通道并安全执行冻结变换。 | P2 - 进阶扩展 |
| 7 | **独立选区孤立显示 (Isolate Selected Only)** | [isolate_selected](isolate_selected/isolate_selected_only.py) | 仅在当前活跃视口中孤立显示选中的物体本体，排查和屏蔽所有子层级与下挂物体，便于精细化编辑。 | P2 - 进阶扩展 |
| 8 | **GPU缓存一键转实体模型** | [gpu_cache_to_mesh](gpu_cache_to_mesh/GPU缓存转实体.py) | 快速读取并解析选中的 gpuCache 节点，还原或重定向关联到真实几何体网格。 | P2 - 进阶扩展 |
| 9 | **UV集批量重命名规范化** | [uv_set_renamer](uv_set_renamer/UV集改名工具.py) | 批量扫描选中模型的 UVsets，一键将杂乱命名统一规范（如统一修正为 map1）。 | P2 - 进阶扩展 |
| 10 | **按 F 键视角错乱修复** | [camera_f_fix](camera_f_fix/按f相机出错解决.mel) | 修复 Maya 视口按 F 键聚焦时摄像机飞出视界、平移矩阵溢出或裁剪面错乱的常见 Bug。 | P2 - 进阶扩展 |

## 整合至 `maya_toolkit` 的规范要求
当您挑选本目录中的工具进行正式重构时，请遵循以下规范：
1. **继承基类**：所有工具类需继承自 `maya_toolkit.core.base_tool.BaseMayaTool`。
2. **标准化输出**：执行入口统一为 `run(**kwargs) -> ToolResult`，支持 `success`, `data`, `message`, `errors` 结构。
3. **大模型 Schema 支持**：通过 `get_schema()` 提供入参类型说明与默认值，支持 Agent 自动读取调用。
4. **安全试运行**：必须支持 `dry_run=True` 预检模式，在执行破坏性/批量操作前不产生实际副作用。
