# 闭源与二进制插件工具库 (Tools Closed Source & Binary Pool)

> 本目录专门存放**无法直接查看明文源码**的 Maya 工具、商业插件与编译扩展（共收纳 **18 个独立工具与大型套件**）。
> 与源码完全开放的 [`tools_staging_pool/`](../tools_staging_pool/) 分开存放，避免在向生产框架 `maya_toolkit/` 迁移转正时因缺少源码导致无法解耦或重构。

---

## 🔒 闭源与编译类型说明

1. **纯字节码 / 纯编译 (.pyc)**：无有效 `.py` 源码，核心功能与 UI 均已被编译为 Python 字节码；
2. **PyTransform 商业混淆加密**：脚本经高强度加密并依赖 `_pytransform.dll / .so` 动态解密；
3. **C++ 原生动态插件 (.mll / .dll / .so)**：核心变形器、解算器或重拓扑算法为 C++ 原生编译二进制，仅提供 Python/MEL 调用外壳；
4. **纯工程资产与模板**：仅包含场景绑定文件与贴图，不含独立可执行脚本源码。

---

## 📚 闭源工具分类导航

| 分类编码 | 分类名称 | 工具数量 | 典型代表 |
| :--- | :--- | :--- | :--- |
| `01_animation` | **动画制作与高阶编辑 (Animation)** | 7 个 | 涵盖该领域的闭源/编译工具 |
| `02_rigging_hierarchy` | **绑定、骨骼与层级管理 (Rigging & Hierarchy)** | 6 个 | 涵盖该领域的闭源/编译工具 |
| `03_transforms_modeling` | **空间变换、对齐与建模辅助 (Transforms & Modeling)** | 2 个 | 涵盖该领域的闭源/编译工具 |
| `07_subsystems_suites` | **大型专业独立子系统与完整套件 (Subsystems & Suites)** | 2 个 | 涵盖该领域的闭源/编译工具 |
| `08_utilities_system` | **系统辅助与环境管理 (Utilities & System)** | 1 个 | 涵盖该领域的闭源/编译工具 |

**总计闭源工具数量**：`18` 项。

---

## 🎯 闭源工具全量检索表

| 序号 | 领域分类 | 工具名称 | 物理路径与入口 | 核心功能简介 | 闭源特征说明 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | 动画制作与高阶编辑 | **ATrack 空间运动轨迹跟踪器** | [atrack_trajectory](01_animation/atrack_trajectory/ATrack/aTrack.pyc) | 实时计算骨骼与控制器的三维运动轨迹线与弧度分析 | 纯 .pyc 字节码（aTrack.pyc 闭源） |
| 2 | 动画制作与高阶编辑 | **视口洋葱皮残影大师 v2.03 (Ghosting Master)** | [ghosting_master_v2_03](01_animation/ghosting_master_v2_03/ghosting_master.mel) | 视口实时显示前后帧残影网格与轨迹姿态，排查动画节奏 | 外壳 MEL 可见，核心 10 个功能模块均为 .pyc |
| 3 | 动画制作与高阶编辑 | **电影级标准摄像机装配模板库 (Iconic Camera Rig)** | [iconic_camera_rig](01_animation/iconic_camera_rig/Arnold_Shoulder_Camera_Rig.ma) | 包含肩扛、五点定位等影视级摄像机装配 .ma 与贴图预设 | 纯摄像机装配资产模板 (.ma / textures)，无独立脚本源码 |
| 4 | 动画制作与高阶编辑 | **Noodle 次级重叠惯性动力学解算器 v1.3** | [noodle_v1_3](01_animation/noodle_v1_3/noodle/install.py) | 解压 noodle_v1.3.zip，排除视频，保留 python 核心算法与测试资产 | 商业级混淆加密 (PyTransform / _pytransform.dll) |
| 5 | 动画制作与高阶编辑 | **Schnapps 角色动作捕捉重对齐工具 v1.2** | [schnapps_v1_2](01_animation/schnapps_v1_2/schnapps/install.py) | 解压 schnapps_v1.2.zip，排除视频，保留核心代码与说明 | 商业级混淆加密 (PyTransform / _pytransform.dll) |
| 6 | 动画制作与高阶编辑 | **动漫速度线生成器 v1.5 (SpeedLine Creator)** | [speedline_creator_v1_5](01_animation/speedline_creator_v1_5/SpeedLine_Creator.pyc) | 排除视频，保留 .ma 模板与核心代码 | 纯 .pyc 字节码（跨版本 SpeedLine_Creator.pyc 闭源） |
| 7 | 动画制作与高阶编辑 | **透明曲线编辑器 (Transparent Graph Editor)** | [transparent_graph_editor](01_animation/transparent_graph_editor/transparentGE.py) | 让 Maya 动画曲线图编辑器半透明悬浮于视口上方 | 外壳开源，核心 transparentGE.pyc 编译闭源 |
| 8 | 绑定、骨骼与层级管理 | **AdvancedSkeleton 高级人体与生物自动装配系统 v5.74** | [advanced_skeleton_v5_74](02_rigging_hierarchy/advanced_skeleton_v5_74/AdvancedSkeleton5.mel) | 业内顶级角色自动装配插件，淘汰旧版 5.55，保留 5.74 最新版完整结构 | 骨骼生成 MEL 开源，高级 DeltaMush 变形器 wbDeltaMushDeformer.mll 编译闭源 |
| 9 | 绑定、骨骼与层级管理 | **约束节点批量管理与状态烘焙面板 v1.3** | [constraint_manager_v1_3](02_rigging_hierarchy/constraint_manager_v1_3/ConstraintManager_1_3/constraintManager.pyc) | 清晰罗列场景所有约束，支持一键烘焙位移并安全断开约束连接 | 纯 .pyc 字节码（constraintManager.pyc 闭源） |
| 10 | 绑定、骨骼与层级管理 | **SSDR 点缓存一键转骨骼蒙皮权重插件** | [ssdr_pointcache_to_skin](02_rigging_hierarchy/ssdr_pointcache_to_skin/SSDR_local_sp/main.py) | 解压 SSDR_local_sp.rar，通过平滑表皮变形分解算法将 ABC 点缓存自动转换为骨骼与 SkinCluster | Python 调度层开源，核心点缓存解算器 dembone.mll 编译闭源 |
| 11 | 绑定、骨骼与层级管理 | **TH RigTools 角色绑定与骨骼工具箱 (免费版)** | [th_rig_tools](02_rigging_hierarchy/th_rig_tools/ThRigTools.py) | 提供一键创建标准控制器、对称骨骼镜像与次级联动 | 安装外壳开源，核心绑定库 thLibrary/main.pyc 闭源 |
| 12 | 绑定、骨骼与层级管理 | **ToolChefs 摄像机晶格变形与柔体 IK 解算器** | [toolchefs_camera_lattice_softik](02_rigging_hierarchy/toolchefs_camera_lattice_softik/tcCameraLattice.py) | 解压 tool chefs.zip，包含 tcCameraLattice 与 tcSoftIkSolver 插件与 Python 封装 | Python 包装层开源，核心晶格与柔体 IK 为 C++ 动态库 .mll |
| 13 | 绑定、骨骼与层级管理 | **WeightSculpt 蒙皮权重雕刻笔刷插件** | [weight_sculpt](02_rigging_hierarchy/weight_sculpt/weightSculpt.py) | 支持多版本 Maya 原生 C++ 插件 (mll/bundle/so)，像雕刻一样直观刷权重 | Python/MEL UI 开源，核心顶点权重解算器 weightSculpt.mll 编译闭源 |
| 14 | 空间变换、对齐与建模辅助 | **Exoside QuadRemesher 四边形自动重拓扑 v1.0.1** | [exoside_quad_remesher](03_transforms_modeling/exoside_quad_remesher/QuadRemesher.py) | 顶尖四边形网格自动拓扑计算核心与 Maya 交互面板 | Python 界面层开源，核心重拓扑引擎 ChSolver.dll 闭源 |
| 15 | 空间变换、对齐与建模辅助 | **seUVBlendShape 基于 UV 拓扑的形态混合插件** | [se_uv_blendshape](03_transforms_modeling/se_uv_blendshape/seUVBlendShape.py) | 突破点序限制，基于 UV 贴图坐标传递形态与生成 BlendShape | Python 调度层开源，底层形态传递节点 seUVBlendShape.mll 编译闭源 |
| 16 | 大型专业独立子系统与完整套件 | **GoSavvy 动画与绑定综合生产套件 v1.3.7** | [gosavvy_toolset_v1_3_7](07_subsystems_suites/gosavvy_toolset_v1_3_7/gosavvyToolset.py) | 包含 C++ 节点插件、Python 控制面板、完整用户文档 | 安装脚本开源，核心 120 个功能模块均为 C++ 编译 .mll |
| 17 | 大型专业独立子系统与完整套件 | **MGTools 动画师生产力综合工作台 v3.3** | [mgtools_v3_3](07_subsystems_suites/mgtools_v3_3/MGTools_Loader.mel) | 集成了关键帧微调、HUD标记、选择集、视口控制与拍屏的经典套件 | MEL 脚本大量开源，但底层崩溃恢复等核心库 animRescue.mll 编译闭源 |
| 18 | 系统辅助与环境管理 | **Maya 模块与插件包可视化管理器 (MayaPackageManager)** | [maya_package_manager](08_utilities_system/maya_package_manager/MayaPackageManager.py) | 管理、启用、禁用场景中的外部 mod 与 python 包 | 启动器开源，底层跨版本管理逻辑 mpm_py3x.pyc 编译闭源 |

---

## 💡 使用与维护建议

1. **直接在 Maya 中加载运行**：此目录下的工具依然是完整可用的，可在 Maya 脚本编辑器中按原作者说明直接调用；
2. **生产库转正原则**：若需将此目录下的工具迁移至 `maya_toolkit/tools/`，由于缺少底层源码，应采用**黑盒包装器 (Wrapper) 模式**，即仅对其命令行接口或 UI 入口进行封装，而无法将算法提取至 `maya_toolkit.core`。
