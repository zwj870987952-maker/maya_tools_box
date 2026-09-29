# 空间变换、对齐与建模辅助 (Transforms & Modeling)

> 当前分类共收纳 **15** 个纯明文开源的工具与脚本。所有代码均已解耦并开放，可直接阅读、调试或封装转正。

## 工具清单与导向

| 序号 | 工具名称 | 对应目录与入口 | 核心功能简述 |
| :--- | :--- | :--- | :--- |
| 1 | **按 F 键视角错乱修复** | [camera_f_fix](camera_f_fix/按f相机出错解决.mel) | 修复 Maya 视口按 F 键聚焦时摄像机飞出视界、平移矩阵溢出或裁剪面错乱的常见 Bug。 |
| 2 | **cvWrap 拓扑包裹与 weightDriver RBF 权重驱动修形套件** | [cvwrap_weightdriver](cvwrap_weightdriver/scripts/cvwrap/bindui.py) | 整合 cvwrap 与 weightDriver 高性能修形变形算法与 mgear animbits 模块 |
| 3 | **EB Labs 世界空间坐标对齐与矩阵传递 (WorldSpaceTools)** | [eblabs_world_space_tools](eblabs_world_space_tools/WorldSpaceTools.py) | 在任意复合层级和空间下无缝传递世界坐标矩阵 |
| 4 | **FCM 视口层级元素快速隐藏/隔离器** | [fcm_hider](fcm_hider/FCM_Hider.mel) | 一键快速切换骨骼、曲线、多边形等视口组件的可见性 |
| 5 | **GPU缓存一键转实体模型** | [gpu_cache_to_mesh](gpu_cache_to_mesh/GPU缓存转实体.py) | 快速读取并解析选中的 gpuCache 节点，还原或重定向关联到真实几何体网格。 |
| 6 | **独立选区孤立显示 (Isolate Selected Only)** | [isolate_selected](isolate_selected/isolate_selected_only.py) | 仅在当前活跃视口中孤立显示选中的物体本体，排查和屏蔽所有子层级与下挂物体，便于精细化编辑。 |
| 7 | **物体对称镜像工具 (Mirror Tool)** | [mirror_tool](mirror_tool/mirror_tool.py) | 根据左右命名规则（如 _L 与 _R），按世界或局部反射平面（XY/YZ/XZ）将位置、旋转与缩放批量镜像到对称侧。 |
| 8 | **视口选中白边高亮切换器 v2** | [no_highlight_v2](no_highlight_v2/NoHigh_Light_v2.py) | 单文件规范化入池，快速关闭视口物体选中高亮白边以观察真实光影 |
| 9 | **四元数旋转插值与转换 (Quaternion Tool)** | [quaternion_tool](quaternion_tool/QuaternionTool_Maya.py) | 提供欧拉角与四元数双向转换、球面线性插值 (SLERP)、绕任意轴向量旋转计算，解决旋转插值翻折问题。 |
| 10 | **轴心点与几何中心重置工具** | [reset_pivot](reset_pivot/maya_reset_pivot.py) | 一键将物体 Pivot 轴心重置到 Bounding Box 边界框中心、几何中心或世界原点，并清空轴向旋转。 |
| 11 | **多功能旋转与角度对齐工具** | [rotation_aligner](rotation_aligner/旋转对齐工具.py) | 综合对齐面板。整合了角度实时显示、欧拉旋转对齐、骨骼轴向对齐，可计算空间夹角并将选区旋转轴快速校准至目标。 |
| 12 | **SmartMesh 智能多边形网格操作工具** | [smart_mesh](smart_mesh/mel_SmartMesh.mel) | 快速合并、清理、法线统一与重合面检测脚本 |
| 13 | **一键解锁通道并冻结变换** | [unlock_freeze](unlock_freeze/unlock_and_freeze_transforms.py) | 批量递归遍历选中节点及其子级，一键解锁所有被锁定/隐藏的位移、旋转、缩放通道并安全执行冻结变换。 |
| 14 | **UV集批量重命名规范化** | [uv_set_renamer](uv_set_renamer/UV集改名工具.py) | 批量扫描选中模型的 UVsets，一键将杂乱命名统一规范（如统一修正为 map1）。 |
| 15 | **世界坐标复制粘贴与对齐 (v4 最新增强版)** | [world_transform_v4](world_transform_v4/复制粘贴世界坐标v4.py) | 提取选中物体的全局世界矩阵（Translate、Rotate），支持识别通道、识别父子关系与迭代误差判定校准。 |

## 整合至 `maya_toolkit` 的规范要求
当您挑选本目录中的工具进行正式重构时，请遵循以下规范：
1. **继承基类**：所有工具类需继承自 `maya_toolkit.framework.base_tool.BaseMayaTool`；
2. **标准化输出**：执行入口统一为 `run(dry_run=False, **kwargs) -> ToolResult`；
3. **大模型 Schema 支持**：通过 `get_schema()` 提供入参类型说明与默认值，支持 Agent 自动读取调用；
4. **安全试运行**：必须支持 `dry_run=True` 预检模式，在执行破坏性/批量操作前不产生实际副作用；
5. **双向反哺下沉**：通用几何、矩阵或 DAG 算法下沉沉淀到 `maya_toolkit.core` 公共库中。
