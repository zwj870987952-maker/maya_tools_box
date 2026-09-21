# 待整理工具库 (Tools Staging Pool)

> 本目录为原始零散脚本与历史工具的**标准化过渡收拢池**。汇总了来自 `D:\jiaoben` 与 `C:\BaiduSyncdisk\自定义脚本` 的全部精选、去重、最新版本的实用工具，共包含 **54 个独立工具单元与大型专业套件**。

> [!IMPORTANT]
> **项目准入规则**：所有新制作或新引入的工具**必须首先置于本待整理库中**。测试方式以最轻量直观的**“直接在已打开的 Maya 中执行打开界面或运行功能”**为主。只有在真实场景中实测通过且确认满意后，才由开发者或 Agent 按照 `BaseMayaTool` 规范正式封装迁移至 `maya_toolkit/tools/` 生产库中。


---

## 📚 目录分类快速导航

| 分类编码 | 分类名称 | 包含工具数 | 核心定位 | 目录链接 |
| :--- | :--- | :--- | :--- | :--- |
| `01_animation` | **动画制作与高阶编辑 (Animation)** | 12 个 | 涵盖影视/游戏动画全生命周期的高频工具，包括拍屏、IK/FK... | [进入分类](01_animation/README.md) |
| `02_rigging_hierarchy` | **绑定、骨骼与层级管理 (Rigging & Hierarchy)** | 7 个 | 涵盖历经多次迭代的高级层级与空间切换工具 (Relation... | [进入分类](02_rigging_hierarchy/README.md) |
| `03_transforms_modeling` | **空间变换、对齐与建模辅助 (Transforms & Modeling)** | 10 个 | 涵盖世界坐标识别通道对齐、综合旋转与轴向校准、四元数插值、对... | [进入分类](03_transforms_modeling/README.md) |
| `04_pipeline_io` | **资产管线与批量导入导出 (Pipeline & I/O)** | 8 个 | 涵盖工业级 FBX/ABC 选择集批量导出面板、文件拖拽批量... | [进入分类](04_pipeline_io/README.md) |
| `05_ue_pipeline` | **虚幻引擎协同管线 (Unreal Engine Pipeline)** | 5 个 | 涵盖 UE 资产源文件逆向追溯、UE 骨骼拓扑清单导出（Py... | [进入分类](05_ue_pipeline/README.md) |
| `06_diagnostics_security` | **场景体检、安全杀毒与快照 (Diagnostics & Security)** | 3 个 | 涵盖针对 Maya 知名蠕虫脚本病毒的专杀与免疫疫苗、场景未... | [进入分类](06_diagnostics_security/README.md) |
| `07_subsystems_suites` | **大型专业独立子系统与完整套件 (Subsystems & Suites)** | 6 个 | 整包完整移植的成熟独立套件：包含 Maya 节点式蓝图自动化... | [进入分类](07_subsystems_suites/README.md) |
| `08_utilities_system` | **系统辅助与环境管理 (Utilities & System)** | 3 个 | 涵盖 Windows 独立桌面 Maya 进程/端口侦查器 ... | [进入分类](08_utilities_system/README.md) |

**总计工具数量**：`54` 个独立工具与子系统。

---

## 🎯 全量工具总览与检索表

| 序号 | 领域分类 | 工具名称 | 物理路径 | 核心功能简介 |
| :--- | :--- | :--- | :--- | :--- |
| 1 | 动画制作与高阶编辑 | **MOV拍屏输出工具 (Playblast MOV Tool v11)** | [mov_playblast_v11](01_animation/mov_playblast_v11/mov拍屏v11.py) | 专业 Playblast 拍屏工具。集成 HUD 镜头遮罩、时间码/帧率显示、摄像机焦距信息、自定义分辨率与 MOV/MP4 格式导出压缩。 |
| 2 | 动画制作与高阶编辑 | **IK/FK无缝双向切换与烘焙工具** | [ik_fk_switch](01_animation/ik_fk_switch/mog_ikFkSwitch.py) | 角色 IK 与 FK 控制器双向无缝匹配吸附。支持当前帧单帧吸附，以及时间轴选定区间的全自动动画烘焙切换。 |
| 3 | 动画制作与高阶编辑 | **双角色/骨骼姿态匹配器 (PoseMatcher)** | [pose_matcher](01_animation/pose_matcher/PoseMatcher.py) | 基于四元数与空间向量运算。支持不同命名空间/不同绑定的双角色之间姿态智能镜像与快速吸附。 |
| 4 | 动画制作与高阶编辑 | **复制动画与曲线修复工具** | [copy_animation](01_animation/copy_animation/复制动画_修复优化版.py) | 批量复制与重映射动画曲线，内置断裂曲线修复算法，支持同名控制器/骨骼曲线通道一键批量传递。 |
| 5 | 动画制作与高阶编辑 | **Root动画生成与质心约束烘焙** | [root_motion_bake](01_animation/root_motion_bake/root动画生成.py) | 自动计算角色质心位移轨迹并生成 Root 根骨骼动画，创建独立动画层并烘焙相对位移与旋转。 |
| 6 | 动画制作与高阶编辑 | **动画位移回归原点 (Back2Origin 最新增强版)** | [back2origin_v05_gaiv3](01_animation/back2origin_v05_gaiv3/Back2Origin_v05_gaiv3.py) | 自动识别场景中角色控制器，支持将脱离原点的移动平移回世界原点，新增反向操作与命名空间切换。 |
| 7 | 动画制作与高阶编辑 | **增强型时间轴控制面板** | [timeline_enhanced](01_animation/timeline_enhanced/maya_timeline_tool_enhanced.py) | 增强的时间轴交互面板，支持时间范围快速缩放/重映射、播放倍速实时调整、帧范围填充与关键帧区间标记。 |
| 8 | 动画制作与高阶编辑 | **万向节死锁修复器 (Gimbal Fixer)** | [gimbal_lock_fix](01_animation/gimbal_lock_fix/maya_animation_gimbal_fix.py) | 自动检测旋转动画曲线中的欧拉角跳变与万向节死锁现象，通过 Euler Filter 与四元数插值平滑修复异常翻滚。 |
| 9 | 动画制作与高阶编辑 | **时间轴运动速度计算器** | [velocity_calculator](01_animation/velocity_calculator/maya_velocity_calculator.py) | 计算选中物体在当前时间轴区间的空间直线位移与平均运动速度（支持自动换算帧率到单位/秒）。 |
| 10 | 动画制作与高阶编辑 | **关键帧阶梯递减偏移工具 (Stagger/Offset)** | [stagger_offset](01_animation/stagger_offset/批量减选关键帧偏移.py) | 制作重叠动作 (Overlapping Action) 与依次延迟动画的必备工具。自动对选中控制器链逐级减选并向后平移关键帧。 |
| 11 | 动画制作与高阶编辑 | **世界空间坐标锁定 (lockToWorld)** | [lock_to_world](01_animation/lock_to_world/jop_lockToWorld.py) | 一键将骨骼或控制器在指定时间段内“钉死”在世界坐标中（经典防滑步、手部固定抓握对齐工具）。 |
| 12 | 动画制作与高阶编辑 | **Maya动画重定向工具 (Animation Retarget)** | [animation_retarget](01_animation/animation_retarget/动画重定向.py) | 跨骨骼/控制器的动画批量转移工具。支持通道映射自定义、配置保存/加载、右键批量重定向。 |
| 13 | 绑定、骨骼与层级管理 | **高级层级与空间切换工具 (Relationship Tools v19)** | [relationship_tools_v19](02_rigging_hierarchy/relationship_tools_v19/Relationship Tools_v19.py) | 历经 19 次迭代的核心层级/约束工具。支持父子/世界空间切换、约束烘焙、层级安全断开与重连、主从关系维护。 |
| 14 | 绑定、骨骼与层级管理 | **场景约束综合管理与重建工具** | [constraint_manager_v6](02_rigging_hierarchy/constraint_manager_v6/约束管理v6.py) | 约束全生命周期管理。支持将场景约束拓扑导出为 JSON、一键批量静音/恢复、安全删除与无损重建（含偏移保持）。 |
| 15 | 绑定、骨骼与层级管理 | **骨骼蒙皮权重转移工具** | [skin_weight_transfer](02_rigging_hierarchy/skin_weight_transfer/骨骼权重转移.py) | 提取源骨骼链的 SkinCluster 蒙皮权重，按骨骼命名或就近空间拓扑快速转移至新骨骼链。 |
| 16 | 绑定、骨骼与层级管理 | **批量取消骨骼分段比例补偿 (Segment Scale Fix)** | [segment_scale_fix](02_rigging_hierarchy/segment_scale_fix/批量取消骨骼分段比例补偿.py) | 一键递归遍历骨骼链关闭 segmentScaleCompensate 属性（游戏引擎骨骼缩放动画的关键避坑点，防止导入 UE/Unity 缩放异常）。 |
| 17 | 绑定、骨骼与层级管理 | **选区顺序生成骨骼链** | [skeleton_generator](02_rigging_hierarchy/skeleton_generator/选区生成骨骼链.py) | 根据当前选中的多个物体/Locator 的世界坐标顺序，自动创建定向对齐的 Joint 骨骼链。 |
| 18 | 绑定、骨骼与层级管理 | **DAG节点层级关系分析器** | [hierarchy_analyzer](02_rigging_hierarchy/hierarchy_analyzer/maya_hierarchy_analysis.py) | 深度分析场景选中节点的完整父子继承链、DAG 绝对路径及依赖节点关系，结构化输出层级树。 |
| 19 | 绑定、骨骼与层级管理 | **按顺序批量蒙皮/绑定与代理生成** | [batch_skin_bind](02_rigging_hierarchy/batch_skin_bind/批量绑骨头.py) | 按选择顺序将成组模型与骨骼链自动执行标准蒙皮绑定，支持快速骨骼碰撞代理生成。 |
| 20 | 空间变换、对齐与建模辅助 | **世界坐标复制粘贴与对齐 (v4 最新增强版)** | [world_transform_v4](03_transforms_modeling/world_transform_v4/复制粘贴世界坐标v4.py) | 提取选中物体的全局世界矩阵（Translate、Rotate），支持识别通道、识别父子关系与迭代误差判定校准。 |
| 21 | 空间变换、对齐与建模辅助 | **多功能旋转与角度对齐工具** | [rotation_aligner](03_transforms_modeling/rotation_aligner/旋转对齐工具.py) | 综合对齐面板。整合了角度实时显示、欧拉旋转对齐、骨骼轴向对齐，可计算空间夹角并将选区旋转轴快速校准至目标。 |
| 22 | 空间变换、对齐与建模辅助 | **四元数旋转插值与转换 (Quaternion Tool)** | [quaternion_tool](03_transforms_modeling/quaternion_tool/QuaternionTool_Maya.py) | 提供欧拉角与四元数双向转换、球面线性插值 (SLERP)、绕任意轴向量旋转计算，解决旋转插值翻折问题。 |
| 23 | 空间变换、对齐与建模辅助 | **物体对称镜像工具 (Mirror Tool)** | [mirror_tool](03_transforms_modeling/mirror_tool/mirror_tool.py) | 根据左右命名规则（如 _L 与 _R），按世界或局部反射平面（XY/YZ/XZ）将位置、旋转与缩放批量镜像到对称侧。 |
| 24 | 空间变换、对齐与建模辅助 | **轴心点与几何中心重置工具** | [reset_pivot](03_transforms_modeling/reset_pivot/maya_reset_pivot.py) | 一键将物体 Pivot 轴心重置到 Bounding Box 边界框中心、几何中心或世界原点，并清空轴向旋转。 |
| 25 | 空间变换、对齐与建模辅助 | **一键解锁通道并冻结变换** | [unlock_freeze](03_transforms_modeling/unlock_freeze/unlock_and_freeze_transforms.py) | 批量递归遍历选中节点及其子级，一键解锁所有被锁定/隐藏的位移、旋转、缩放通道并安全执行冻结变换。 |
| 26 | 空间变换、对齐与建模辅助 | **独立选区孤立显示 (Isolate Selected Only)** | [isolate_selected](03_transforms_modeling/isolate_selected/isolate_selected_only.py) | 仅在当前活跃视口中孤立显示选中的物体本体，排查和屏蔽所有子层级与下挂物体，便于精细化编辑。 |
| 27 | 空间变换、对齐与建模辅助 | **GPU缓存一键转实体模型** | [gpu_cache_to_mesh](03_transforms_modeling/gpu_cache_to_mesh/GPU缓存转实体.py) | 快速读取并解析选中的 gpuCache 节点，还原或重定向关联到真实几何体网格。 |
| 28 | 空间变换、对齐与建模辅助 | **UV集批量重命名规范化** | [uv_set_renamer](03_transforms_modeling/uv_set_renamer/UV集改名工具.py) | 批量扫描选中模型的 UVsets，一键将杂乱命名统一规范（如统一修正为 map1）。 |
| 29 | 空间变换、对齐与建模辅助 | **按 F 键视角错乱修复** | [camera_f_fix](03_transforms_modeling/camera_f_fix/按f相机出错解决.mel) | 修复 Maya 视口按 F 键聚焦时摄像机飞出视界、平移矩阵溢出或裁剪面错乱的常见 Bug。 |
| 30 | 资产管线与批量导入导出 | **FBX 批量导出综合套件 v7** | [fbx_batch_exporter_v7](04_pipeline_io/fbx_batch_exporter_v7/fbx_export_CHS_v7.py) | 工业级 FBX 批量导出面板。支持按选择集批量输出、自动内嵌烘焙与重采样、一键取消骨骼分段比例补偿、时间轴区间自适应，并支持将导出预设保存为 JSON。 |
| 31 | 资产管线与批量导入导出 | **Alembic (ABC) 批量导出套件** | [abc_batch_exporter](04_pipeline_io/abc_batch_exporter/ABC导出_v3.py) | 支持按选择集（Selection Sets）批量导出 Alembic ABC 几何体缓存，内置自动建立材质分配信息与输出目录整理。 |
| 32 | 资产管线与批量导入导出 | **文件批量导入加强版 v3** | [batch_importer_v3](04_pipeline_io/batch_importer_v3/批量导入加强版v3.py) | 支持文件/文件夹拖拽批量录入、递归子文件夹导入、一键批量清除/合并 Reference 参考文件、智能去除或添加命名空间。 |
| 33 | 资产管线与批量导入导出 | **工程文件批量自动化处理框架 v3** | [batch_processor_v3](04_pipeline_io/batch_processor_v3/文件批量执行v3.py) | 自动化批处理框架。指定文件夹遍历 .ma/.mb 工程，逐个静默打开并批量运行指定的 Python/MEL 脚本，输出执行日志。 |
| 34 | 资产管线与批量导入导出 | **无效与中文引用路径清理器** | [clean_invalid_paths](04_pipeline_io/clean_invalid_paths/clean_invalid_paths.py) | 深度扫描场景所有节点属性，检测并清理带有中文、乱码或损坏失效的外部 Reference 引用与贴图纹理路径，防止崩溃。 |
| 35 | 资产管线与批量导入导出 | **引用文件路径批量重定向与替换** | [replace_references](04_pipeline_io/replace_references/reference替换EN封装版.py) | 批量搜索并替换场景中 Reference 节点的工程文件根路径与引用物体，用于团队多环境切换与工程迁移。 |
| 36 | 资产管线与批量导入导出 | **舰船/载具资产特种 FBX 导出** | [vessel_fbx_exporter](04_pipeline_io/vessel_fbx_exporter/fbx导出工具舰船专用_自动版.py) | 面向特定载具资产的层级规范校验与自动 FBX 导出，自动规范化 Root 层级与材质引用规范。 |
| 37 | 资产管线与批量导入导出 | **模型逐帧转 BlendShape 导出 FBX** | [per_frame_bs_fbx](04_pipeline_io/per_frame_bs_fbx/模型逐帧转bs导出fbx_v1.1.py) | 将变形动画模型逐帧生成 BlendShape 目标体，自动构建 BS 权重动画并导出 FBX，用于游戏引擎特种网格特效。 |
| 38 | 虚幻引擎协同管线 | **UE 资产源文件迁移与反向查找** | [ue_source_finder](05_ue_pipeline/ue_source_finder/UE源文件迁移.py) | 结合 UE 资产管理，根据 Unreal 资产引用逆向反查 DCC（Maya/FBX）源文件路径，支持跨工程资产映射与迁移。 |
| 39 | 虚幻引擎协同管线 | **UE 骨骼树清单导出 (Python + C++插件)** | [ue_bone_exporter](05_ue_pipeline/ue_bone_exporter/ExportBoneList.py) | 包含运行于 UE5 编辑器 Python 环境的导出脚本，以及原生 UE5 C++ 插件 (BoneListGenerator_UPlugin)，批量将 Skeletal Mesh 骨骼拓扑结构导出为文本。 |
| 40 | 虚幻引擎协同管线 | **UE 资产自动化导入配置与执行脚本** | [ue_fbx_auto_import](05_ue_pipeline/ue_fbx_auto_import/ue导入fbx配置.py) | Maya 端配置好 FBX 导入参数后，直接跨进程触发 Unreal Engine 自动化执行资产导入与属性安全设置。 |
| 41 | 虚幻引擎协同管线 | **UE 资产引用依赖与断链检查器** | [ue_reference_checker](05_ue_pipeline/ue_reference_checker/UE资产引用检查器.py) | 基于 Tkinter 的桌面工具，批量检测虚幻引擎项目资产间的引用依赖与断链丢失。 |
| 42 | 虚幻引擎协同管线 | **UE5 编辑器右键源路径打印菜单** | [ue_context_menu](05_ue_pipeline/ue_context_menu/print_source_paths_menu.py) | UE5 编辑器右键资产菜单扩展，点击即可在日志中输出源 DCC 文件的物理路径。 |
| 43 | 场景体检、安全杀毒与快照 | **Maya 场景病毒专杀与免疫疫苗** | [scene_virus_cleaner](06_diagnostics_security/scene_virus_cleaner/文件病毒清理魔改版.py) | 专门查杀与清除 Maya 常见恶意脚本蠕虫病毒（如 vaccine.py, fuckVirus, breed_gene），清除恶意 scriptJob 与节点，防止工程交叉感染。 |
| 44 | 场景体检、安全杀毒与快照 | **场景未知与垃圾节点清理 (HM Cleaner)** | [clean_junk_nodes](06_diagnostics_security/clean_junk_nodes/HM_清理垃圾节点.py) | 深度清除场景中残留的 unknown 节点、失效插件声明与无引用垃圾数据，减小文件体积、解决无法保存问题。 |
| 45 | 场景体检、安全杀毒与快照 | **场景快照记录点与撤销恢复系统 (Undo Checkpoint)** | [undo_checkpoint](06_diagnostics_security/undo_checkpoint/maya_undo_checkpoint.py) | 突破 Maya 原生撤销限制。可随时为场景创建快照存档点（Checkpoint），一键快速恢复或清空，带专用工具架按钮。 |
| 46 | 大型专业独立子系统与完整套件 | **Maya 节点式蓝图自动化工具箱 (Blueprint Toolbox 完整工程)** | [maya_blueprint_toolbox](07_subsystems_suites/maya_blueprint_toolbox/main.py) | 基于 Qt 的可视化节点连线画布与执行引擎。支持像虚幻蓝图一样连线驱动 Maya 操作，内置动画、属性、约束等通用 API 包装。 |
| 47 | 大型专业独立子系统与完整套件 | **GETOOLS 动力学与次级动作套件 (含 Overlappy / CenterOfMass)** | [getools_overlappy](07_subsystems_suites/getools_overlappy/GeneralWindow.py) | 包含两大神器：1. Overlappy 一键自动生成物理次级重叠惯性动作；2. CenterOfMass 角色实时重心质心解算。 |
| 48 | 大型专业独立子系统与完整套件 | **TheKeyMachine 动画师综合套件 (完整汉化增强版)** | [the_key_machine](07_subsystems_suites/the_key_machine/core/toolbar.py) | 关键帧微调工具：包含曲线平滑、切线权重批量调整、反向动画、自定义曲线图编辑器与一键汉化补丁。 |
| 49 | 大型专业独立子系统与完整套件 | **animBot 完整 UI 与工具克隆套件** | [animbot_copy](07_subsystems_suites/animbot_copy/launch.py) | 完整复刻知名动画插件 animBot 的 UI 与工具库：包含 Graph Editor 曲线编辑器嵌入式工具栏、弹性回弹多段滑块、工作区管理。 |
| 50 | 大型专业独立子系统与完整套件 | **Studio Library 世界空间扩展增强包 (PlusPatch)** | [studiolibrary_patch](07_subsystems_suites/studiolibrary_patch/studiolibrary_wanimation/__init__.py) | 在原生 Studio Library 基础上增加了世界坐标动画抓取与跨角色粘贴 (WAnimation)、世界坐标姿态对齐 (WPose) 与中文汉化。 |
| 51 | 大型专业独立子系统与完整套件 | **Maya 视口智能拖拽与对话框拦截助手** | [smart_assistant](07_subsystems_suites/smart_assistant/main.py) | 视口拖拽与文件对话框拦截：将图片序列拖入视口自动生成摄像机与 ImagePlane；拖入 FBX/MA 自动弹窗提示导入/引用规则。 |
| 52 | 系统辅助与环境管理 | **Maya 进程与端口查找器 (MayaFinder)** | [maya_process_finder](08_utilities_system/maya_process_finder/maya_process_finder.py) | Windows 独立桌面 GUI。自动探测枚举本机所有运行中的 Maya 进程 PID、占用端口（Command Port），排查卡死与多开。 |
| 53 | 系统辅助与环境管理 | **Maya 跨版本工具架管理器 (2018-2026)** | [shelf_manager](08_utilities_system/shelf_manager/shelf_manager.py) | 集中管理 Maya 2018~2026 各版本的 Shelf 工具架配置，区分中英文路径，支持跨版本复制、同步与备份。 |
| 54 | 系统辅助与环境管理 | **吸附式悬浮快捷工具栏** | [floating_toolbar](08_utilities_system/floating_toolbar/floating_toolbar.py) | 基于 PySide2 的悬浮工具条，可自动吸附在 Maya 视口边缘，支持拖拽 Shelf 命令或自定义按钮生成轻量操作浮窗。 |

---

## 🛠️ 后续挑选与整合工作流指南

当您准备开始整合某项工具时，可直接指示 Agent：
```text
请帮我把 tools_staging_pool/01_animation/mov_playblast_v11 整合进 maya_toolkit
```

### 标准化迁移流程：
1. **代码与逻辑解耦**：将原有 UI 逻辑与 Maya 执行内核拆分，纯算法/API 放入 `maya_toolkit/tools/<domain>/`；
2. **统一基类封装**：继承 `BaseMayaTool`，补充 `tool_id`、`name`、`description` 和 `get_schema()`；
3. **安全操作封装**：使用 `maya_toolkit.core.undo.UndoChunk` 与 `dry_run` 支持；
4. **自动化单元测试**：在 `tests/` 下添加针对该工具的 `unittest` 用例，并在 Live Maya 实例中进行实时校验；
5. **界面统一收拢**：工具自动挂载到 `maya_toolkit.show_ui()` 的统一综合启动器面板中。
