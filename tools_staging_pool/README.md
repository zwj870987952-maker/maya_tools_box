# 待整理开源工具库 (Tools Staging Pool - Open Source)

> 本目录为**完全开放源码（.py / .mel 明文代码可见）**的标准化待整理收拢池。所有闭源、已编译或纯二进制插件工具已统一分流至 [`tools_closed_source_pool/`](../tools_closed_source_pool/)。当前池内共收纳 **109 个纯明文开源工具单元与大型专业套件**。

> [!IMPORTANT]
> **项目准入规则**：所有工具均为源码完全开放状态，可直接阅读、调试核心数学解算与业务逻辑。在真实场景中实测通过且确认满意后，按照 `BaseMayaTool` 规范正式封装迁移至 `maya_toolkit/tools/`，并将通用算法下沉到 `maya_toolkit.core`。

---

## 📚 目录分类快速导航

| 分类编码 | 分类名称 | 包含工具数 | 核心定位 |
| :--- | :--- | :--- | :--- |
| `01_animation` | **动画制作与高阶编辑 (Animation)** | 49 个 | 涵盖该领域的开源精选工具、插件与脚本 |
| `02_rigging_hierarchy` | **绑定、骨骼与层级管理 (Rigging & Hierarchy)** | 14 个 | 涵盖该领域的开源精选工具、插件与脚本 |
| `03_transforms_modeling` | **空间变换、对齐与建模辅助 (Transforms & Modeling)** | 15 个 | 涵盖该领域的开源精选工具、插件与脚本 |
| `04_pipeline_io` | **资产管线与批量导入导出 (Pipeline & I/O)** | 9 个 | 涵盖该领域的开源精选工具、插件与脚本 |
| `05_ue_pipeline` | **虚幻引擎协同管线 (Unreal Engine Pipeline)** | 5 个 | 涵盖该领域的开源精选工具、插件与脚本 |
| `06_diagnostics_security` | **场景体检、安全杀毒与快照 (Diagnostics & Security)** | 3 个 | 涵盖该领域的开源精选工具、插件与脚本 |
| `07_subsystems_suites` | **大型专业独立子系统与完整套件 (Subsystems & Suites)** | 7 个 | 涵盖该领域的开源精选工具、插件与脚本 |
| `08_utilities_system` | **系统辅助与环境管理 (Utilities & System)** | 7 个 | 涵盖该领域的开源精选工具、插件与脚本 |

**总计开源工具数量**：`109` 个独立工具与子系统。

---

## 🎯 全量开源工具总览与检索表

| 序号 | 领域分类 | 工具名称 | 物理路径与入口 | 核心功能简介 |
| :--- | :--- | :--- | :--- | :--- |
| 1 | 动画制作与高阶编辑 | **动画曲线过滤器套件 (animFilters)** | [anim_filters](<01_animation/anim_filters/animFilters-v1.0-maya17/scripts/animFilters/animFilters.py>) | 欧拉角跳变与动画曲线噪点平滑过滤 |
| 2 | 动画制作与高阶编辑 | **动画层书签关键帧修剪器 (Bookmark Trimmer)** | [anim_layer_bookmark_trimmer](01_animation/anim_layer_bookmark_trimmer/anim_layer_bookmark_trimmer.py) | 根据时间滑块书签起止端点，仅保留选定动画层在书签起始与结束处的关键帧，修剪清理所有中间非端点帧。支持原子撤销与预检。 |
| 3 | 动画制作与高阶编辑 | **动画层逐关键帧命令执行器 (AnimLayer Key Runner)** | [anim_layer_key_runner](01_animation/anim_layer_key_runner/anim_layer_key_runner.py) | 智能检索选中物体在指定动画层（或当前激活层）上的专属关键帧，逐帧跳转并批量触发 MEL 或 Python 命令（如 asAutoSwitchFKIK 自动切换匹配、打关键帧等）。 |
| 4 | 动画制作与高阶编辑 | **动画层关键帧区间书签生成器** | [anim_layer_keyframe_bookmark](01_animation/anim_layer_keyframe_bookmark/anim_layer_keyframe_bookmark.py) | 提取所选物体在当前动画层级上的关键帧，在相邻关键帧之间自动创建相邻色彩互斥的时间滑块书签 (Bookmarks)。 |
| 5 | 动画制作与高阶编辑 | **动画层综合控制面板 v4.0** | [anim_layer_v4_0](<01_animation/anim_layer_v4_0/anim_layer_v4_0/layerEditor.mel>) | 动画层批量关键帧与显示管理增强面板 |
| 6 | 动画制作与高阶编辑 | **角色动画镜像助手 v1.1 (Studio版)** | [anim_mirror_helper_v1_1](<01_animation/anim_mirror_helper_v1_1/Anim_Mirror_Helper_v1_1_studio_lic/mirror_walk_tool_code.mel>) | 角色姿态与控制器动画快速镜像 |
| 7 | 动画制作与高阶编辑 | **AnimPolish PREMIUM 角色动画修帧曲线抛光神器 v1.23** | [anim_polish_premium_v1_23](<01_animation/anim_polish_premium_v1_23/animPolish/ui.py>) | 提取 v1.23 最新付费版，淘汰根目录的 v1.19 Basic 旧版，附带说明文档 |
| 8 | 动画制作与高阶编辑 | **Maya动画重定向工具 (Animation Retarget)** | [animation_retarget](01_animation/animation_retarget/动画重定向.py) | 跨骨骼/控制器的动画批量转移工具。支持通道映射自定义、配置保存/加载、右键批量重定向。 |
| 9 | 动画制作与高阶编辑 | **AniMirror 动画镜像工具 v2.0** | [animirror_v2_0](<01_animation/animirror_v2_0/AniMirror(Drag&Drop Install).mel>) | 独立 Qt 界面动画姿态与序列帧镜像工具 |
| 10 | 动画制作与高阶编辑 | **动画位移回归原点 (Back2Origin 最新增强版)** | [back2origin_v05_gaiv3](01_animation/back2origin_v05_gaiv3/Back2Origin_v05_gaiv3.py) | 自动识别场景中角色控制器，支持将脱离原点的移动平移回世界原点，新增反向操作与命名空间切换。 |
| 11 | 动画制作与高阶编辑 | **Aim 朝向与视线注视对齐工具 v1.1** | [bh_aim_tools_v1_1](<01_animation/bh_aim_tools_v1_1/bh_aimTools_v1.1/bh_aimTools.mel>) | Brian Horgan 开发的眼部注视与空间朝向辅助工具 |
| 12 | 动画制作与高阶编辑 | **局部微调位移旋转工具 (bh_localNudge)** | [bh_local_nudge](<01_animation/bh_local_nudge/bh_localNudge/bh_localNudge.mel>) | 在局部/屏幕/父级坐标系下微调动画控制器位移与旋转 |
| 13 | 动画制作与高阶编辑 | **动漫二次元动画速度线生成器** | [bh_speedlines](<01_animation/bh_speedlines/bh_speedLines(速度线)/bh_speedLines.mel>) | 生成跟随角色动态的视效速度线与冲击波特效网格 |
| 14 | 动画制作与高阶编辑 | **跟随重叠动画生成器 (bh_waveIt)** | [bh_wave_it](01_animation/bh_wave_it/bh_waveIt/bh_waveIt.mel) | 排除演示视频，保留 mel 脚本与图标，为链条、尾巴快速添加基于数学正弦波的波浪跟随 |
| 15 | 动画制作与高阶编辑 | **Locator 定位器空间位移传递 (BRSLocTransfer 离线版)** | [brs_loc_transfer](01_animation/brs_loc_transfer/BRSLocTransfer.py) | 无需外网连接，通过中间 Locator 烘焙并转移角色空间位移旋转 |
| 16 | 动画制作与高阶编辑 | **动捕数据平滑降噪过滤器 (BRSSmoothMocap)** | [brs_smooth_mocap](01_animation/brs_smooth_mocap/BRSSmoothMocap.py) | 针对动作捕捉抖动关键帧的智能平滑插值降噪器 |
| 17 | 动画制作与高阶编辑 | **CgShake 电影级摄像机真实手持抖动模拟 (Python3版)** | [cg_shake_py3](01_animation/cg_shake_py3/CgShake_py3/cgshake.py) | 解压最新的 CgShake_py3.rar，淘汰旧版 Python 2 压缩包，内置手持、爆炸、呼吸等丰富抖动预设 |
| 18 | 动画制作与高阶编辑 | **复制动画与曲线修复工具** | [copy_animation](01_animation/copy_animation/复制动画_修复优化版.py) | 批量复制与重映射动画曲线，内置断裂曲线修复算法，支持同名控制器/骨骼曲线通道一键批量传递。 |
| 19 | 动画制作与高阶编辑 | **多方向位移循环动画工具 v1.1** | [directional_cycle_tool_v1_1](01_animation/directional_cycle_tool_v1_1/DirectionalCycleTool/main.py) | 解压 DirectionalCycleTool_v1_1.rar，智能循环平铺走跑跳动画位移 |
| 20 | 动画制作与高阶编辑 | **dofControl 摄像机景深聚焦交互控制工具 v1.0** | [dof_control_v1_0](<01_animation/dof_control_v1_0/dofControl.mel>) | 在视口中以 Locator 快速驱动摄像机焦点与景深模糊范围 |
| 21 | 动画制作与高阶编辑 | **EB Labs 视口屏幕空间操控套件 (ScreenSpace)** | [eblabs_screenspace](<01_animation/eblabs_screenspace/ScreenSpace/ScreenSpace.py>) | 直接在摄像机平面屏幕坐标系下锁定并拖拽控制器 |
| 22 | 动画制作与高阶编辑 | **EB Labs Whiskey 动画姿态与时间轴快照** | [eblabs_whiskey](<01_animation/eblabs_whiskey/Whiskey/Whiskey.py>) | EB Labs 出品的高效姿态捕获与动画对比套件 |
| 23 | 动画制作与高阶编辑 | **多空间无缝切换与吸附工具 (FD Multi-Space)** | [fd_multi_space](<01_animation/fd_multi_space/FD_Multi_Space_tool_GUI.py>) | 支持角色控制器世界/局部/任意道具层级空间实时无缝切换吸附 |
| 24 | 动画制作与高阶编辑 | **万向节死锁修复器 (Gimbal Fixer)** | [gimbal_lock_fix](01_animation/gimbal_lock_fix/maya_animation_gimbal_fix.py) | 自动检测旋转动画曲线中的欧拉角跳变与万向节死锁现象，通过 Euler Filter 与四元数插值平滑修复异常翻滚。 |
| 25 | 动画制作与高阶编辑 | **IK/FK无缝双向切换与烘焙工具 (Pro 3.0 增强升级版)** | [ik_fk_switch](01_animation/ik_fk_switch/mog_ikFkSwitchPro.py) | 升级池中现有老版本 mog_ikFkSwitch.py 至 Pro 3.0 架构 |
| 26 | 动画制作与高阶编辑 | **JOP 角色动画批量重定向套件 v0.9** | [jop_retarget_anim_v09](01_animation/jop_retarget_anim_v09/jop_retargetAnim/jop_retargetAnim.py) | 完整工程套件，含拖拽安装、通道重映射与图形化映射 UI |
| 27 | 动画制作与高阶编辑 | **关键帧物理重叠与次级动作解算器 v2.0** | [keyframe_overlap_v2_0](01_animation/keyframe_overlap_v2_0/KFOverlap/KeyframeOverlap.py) | 一键为骨骼链/毛发飘带生成基于物理摆动的重叠动作 |
| 28 | 动画制作与高阶编辑 | **kfAnimRig IK/FK 极速匹配切换** | [kf_animrig_ikfk](01_animation/kf_animrig_ikfk/kfAnimRig_IKFK.mel) | 独立的轻量级 MEL 角色 IK/FK 切换与吸附面板，排除视频 |
| 29 | 动画制作与高阶编辑 | **世界空间坐标锁定 (lockToWorld)** | [lock_to_world](01_animation/lock_to_world/jop_lockToWorld.py) | 一键将骨骼或控制器在指定时间段内“钉死”在世界坐标中（经典防滑步、手部固定抓握对齐工具）。 |
| 30 | 动画制作与高阶编辑 | **Maya 关键帧智能精简工具 (Keyframe Reduction)** | [maya_keyframe_reduction](<01_animation/maya_keyframe_reduction/maya-keyframe-reduction-master/scripts/keyframeReduction/classes/keyframeReduction.py>) | 开源关键帧容差精简算法，批量去除动捕和烘焙冗余帧 |
| 31 | 动画制作与高阶编辑 | **时间滑块颜色书签与事件标记插件 (Timeline Marker)** | [maya_timeline_marker](<01_animation/maya_timeline_marker/maya-timeline-marker-master/scripts/timelineMarker/ui.py>) | 完整开源工程，在时间轴上创建彩色便签、区域标记与热键跳转 |
| 32 | 动画制作与高阶编辑 | **MOV拍屏输出工具 (Playblast MOV Tool v11)** | [mov_playblast_v11](01_animation/mov_playblast_v11/mov拍屏v11.py) | 专业 Playblast 拍屏工具。集成 HUD 镜头遮罩、时间码/帧率显示、摄像机焦距信息、自定义分辨率与 MOV/MP4 格式导出压缩。 |
| 33 | 动画制作与高阶编辑 | **OverSlapper 弹性重叠与惯性延迟工具 v1.03** | [overslapper_v1_03](<01_animation/overslapper_v1_03/overslapper_v1_03/overslapper/overslapper_tool.py>) | 在动画曲线上快速应用弹簧、惯性与阶梯延迟效果 |
| 34 | 动画制作与高阶编辑 | **Maya 动画物理动力学辅助工具箱** | [physics_tools](<01_animation/physics_tools/PhysicsTools_v1.8.mel>) | 布娃娃/重力/次级惯性动力学物理模拟解算，过滤29个教学视频 |
| 35 | 动画制作与高阶编辑 | **双角色/骨骼姿态匹配器 (PoseMatcher)** | [pose_matcher](01_animation/pose_matcher/PoseMatcher.py) | 基于四元数与空间向量运算。支持不同命名空间/不同绑定的双角色之间姿态智能镜像与快速吸附。 |
| 36 | 动画制作与高阶编辑 | **远距离/任意空间相对姿态还原器 (PoseTransfer)** | [pose_transfer_remote](01_animation/pose_transfer_remote/PoseTransfer.py) | 提取并规范化 Python 源码为 PoseTransfer.py，跨世界位置精准复制还原角色局部相对 Pose |
| 37 | 动画制作与高阶编辑 | **RetimeTools 时间节奏与关键帧重配工具** | [retime_tools](<01_animation/retime_tools/RetimeTools/RetimeTools.py>) | 解压汉化版与原版，支持以滑块自由伸缩整体动作节奏 |
| 38 | 动画制作与高阶编辑 | **Root动画生成与质心约束烘焙** | [root_motion_bake](01_animation/root_motion_bake/root动画生成.py) | 自动计算角色质心位移轨迹并生成 Root 根骨骼动画，创建独立动画层并烘焙相对位移与旋转。 |
| 39 | 动画制作与高阶编辑 | **形状动画形态微调工具 (Shape Animation)** | [shape_animation_tool](<01_animation/shape_animation_tool/sat【修型插件】/sat_2022_py3【汉化版】/__init__.py>) | 排除视频，保留原版与汉化版完整代码与手册 |
| 40 | 动画制作与高阶编辑 | **关键帧平移与波浪式偏移工具 v3.2** | [shift_animation_v3_2](<01_animation/shift_animation_v3_2/Shift_animation_v3_2/barnev_Shift_animation_code.mel>) | 批量阶梯式平移关键帧，制作波浪跟随动画 |
| 41 | 动画制作与高阶编辑 | **经典物理弹簧骨骼计算器 v3.5a (SpringMagic)** | [spring_magic_v3_5a](<01_animation/spring_magic_v3_5a/springmagic/springMagic.py>) | 经典弹簧骨骼动力学插件，为头发、飘带、尾巴自动生成逼真摆动 |
| 42 | 动画制作与高阶编辑 | **Stagger 关键帧阶梯偏移图形化面板 (GUI版)** | [stagger_gui](<01_animation/stagger_gui/stagger/ui.py>) | 相比池中单脚本命令行版，增加独立 SVG 图标与 Qt 面板，清理 macOS 垃圾后入池 |
| 43 | 动画制作与高阶编辑 | **关键帧阶梯递减偏移工具 (Stagger/Offset)** | [stagger_offset](01_animation/stagger_offset/批量减选关键帧偏移.py) | 制作重叠动作 (Overlapping Action) 与依次延迟动画的必备工具。自动对选中控制器链逐级减选并向后平移关键帧。 |
| 44 | 动画制作与高阶编辑 | **武器与刀剑轨迹修帧抛光神器 v4** | [sword_anim_polishing_tool_v4](<01_animation/sword_anim_polishing_tool_v4/sword_anim_polish_tool.mel>) | 排除视频，保留 mel 脚本与位图组件，精准平滑武器剑尖运动轨迹 |
| 45 | 动画制作与高阶编辑 | **Tom Bailey 动画效率工具箱 (tbAnimTools)** | [tb_anim_tools](01_animation/tb_anim_tools/tbAnimToolsInstaller.py) | 解压 HelpImages，包含时间轴平滑拖拽、前后关键帧快速跳转等功能 |
| 46 | 动画制作与高阶编辑 | **增强型时间轴控制面板** | [timeline_enhanced](01_animation/timeline_enhanced/maya_timeline_tool_enhanced.py) | 增强的时间轴交互面板，支持时间范围快速缩放/重映射、播放倍速实时调整、帧范围填充与关键帧区间标记。 |
| 47 | 动画制作与高阶编辑 | **Tweener 快速过渡帧/中间帧滑块 v1.0.2** | [tweener_v1_0_2](01_animation/tweener_v1_0_2/tweener.py) | Justin Barrett 开发的经典 Breakdown 中间帧百分比混合滑块 |
| 48 | 动画制作与高阶编辑 | **时间轴运动速度计算器** | [velocity_calculator](01_animation/velocity_calculator/maya_velocity_calculator.py) | 计算选中物体在当前时间轴区间的空间直线位移与平均运动速度（支持自动换算帧率到单位/秒）。 |
| 49 | 动画制作与高阶编辑 | **W Retarget Tool 动画快速重定向脚本** | [w_retarget_tool](01_animation/w_retarget_tool/WretargetTool.py) | 单文件规范化为目录打包，轻量级双骨骼/物体动画烘焙重定向 |
| 50 | 绑定、骨骼与层级管理 | **OverRig 角色二级动力学绑定装配系统 v9.0** | [base_overrig_v9_0](02_rigging_hierarchy/base_overrig_v9_0/base_OverRig_scripts_V9_0/base_OverRig_scripts.mel) | 完整用户手册、图标与骨骼模板，高级副级动力学约束系统 |
| 51 | 绑定、骨骼与层级管理 | **按顺序批量蒙皮/绑定与代理生成** | [batch_skin_bind](02_rigging_hierarchy/batch_skin_bind/批量绑骨头.py) | 按选择顺序将成组模型与骨骼链自动执行标准蒙皮绑定，支持快速骨骼碰撞代理生成。 |
| 52 | 绑定、骨骼与层级管理 | **bb_Tools 绑定与控制器综合工具集** | [bb_tools](<02_rigging_hierarchy/bb_tools/bb_Tools/bb_Tools.mel>) | 包含属性批量控制、毛囊生成、控制器造型库与蒙皮权重清单 |
| 53 | 绑定、骨骼与层级管理 | **场景约束综合管理与重建工具** | [constraint_manager_v6](02_rigging_hierarchy/constraint_manager_v6/约束管理v6.py) | 约束全生命周期管理。支持将场景约束拓扑导出为 JSON、一键批量静音/恢复、安全删除与无损重建（含偏移保持）。 |
| 54 | 绑定、骨骼与层级管理 | **DAG节点层级关系分析器** | [hierarchy_analyzer](02_rigging_hierarchy/hierarchy_analyzer/maya_hierarchy_analysis.py) | 深度分析场景选中节点的完整父子继承链、DAG 绝对路径及依赖节点关系，结构化输出层级树。 |
| 55 | 绑定、骨骼与层级管理 | **骨骼朝向与轴向优化神器 (Joint Optimal Pro v4.1)** | [joint_optimal_pro_v4_1](<02_rigging_hierarchy/joint_optimal_pro_v4_1/Joint_Optimal_Pro_Application_v4.1/barnev_Joint_Optimal_Pro_Application_code.mel>) | 专业纠正骨骼旋转轴 (Rotate Axis) 与关节定向 (Joint Orient)，带完整 PDF 说明 |
| 56 | 绑定、骨骼与层级管理 | **RdM Tools 自动化角色绑定与装配套件 v2 (中文版)** | [rdm_tools_v2](02_rigging_hierarchy/rdm_tools_v2/RdMToolsV2/__init__.py) | 解压中文版源码与 UI，过滤教程视频，全自动手臂、腿部、头部装配与蒙皮工具 |
| 57 | 绑定、骨骼与层级管理 | **高级层级与空间切换工具 (Relationship Tools v19)** | [relationship_tools_v19](02_rigging_hierarchy/relationship_tools_v19/Relationship Tools_v19.py) | 历经 19 次迭代的核心层级/约束工具。支持父子/世界空间切换、约束烘焙、层级安全断开与重连、主从关系维护。 |
| 58 | 绑定、骨骼与层级管理 | **reParent Pro 高级层级重构与父子切换器 v1.5.1** | [reparent_pro_v1_5_1](<02_rigging_hierarchy/reparent_pro_v1_5_1/reParent_Pro_v1.5.1/reParentPro _v1.5.1.mel>) | 无损维持当前位移旋转情况下动态重构 DAG 父子从属关系 |
| 59 | 绑定、骨骼与层级管理 | **批量取消骨骼分段比例补偿 (Segment Scale Fix)** | [segment_scale_fix](02_rigging_hierarchy/segment_scale_fix/批量取消骨骼分段比例补偿.py) | 一键递归遍历骨骼链关闭 segmentScaleCompensate 属性（游戏引擎骨骼缩放动画的关键避坑点，防止导入 UE/Unity 缩放异常）。 |
| 60 | 绑定、骨骼与层级管理 | **选区顺序生成骨骼链** | [skeleton_generator](02_rigging_hierarchy/skeleton_generator/选区生成骨骼链.py) | 根据当前选中的多个物体/Locator 的世界坐标顺序，自动创建定向对齐的 Joint 骨骼链。 |
| 61 | 绑定、骨骼与层级管理 | **SkinInfo v1.92 权重导入导出与 SuperConnect 约束管理器** | [skin_info_and_super_connect](<02_rigging_hierarchy/skin_info_and_super_connect/Export - Import SkinCluster/skinInfo_V1.92.mel>) | 淘汰旧版 1.7/1.8/1.91，打包最新的 skinInfo_V1.92 与 Super_Connect 约束链接器 |
| 62 | 绑定、骨骼与层级管理 | **SkinMagic 蒙皮权重平滑与魔法笔刷** | [skin_magic](<02_rigging_hierarchy/skin_magic/SkinMagic/skinMagic.py>) | 图形化蒙皮权重调节器，快速分配、镜像与就近吸附顶点权重 |
| 63 | 绑定、骨骼与层级管理 | **骨骼蒙皮权重转移工具** | [skin_weight_transfer](02_rigging_hierarchy/skin_weight_transfer/骨骼权重转移.py) | 提取源骨骼链的 SkinCluster 蒙皮权重，按骨骼命名或就近空间拓扑快速转移至新骨骼链。 |
| 64 | 空间变换、对齐与建模辅助 | **按 F 键视角错乱修复** | [camera_f_fix](03_transforms_modeling/camera_f_fix/按f相机出错解决.mel) | 修复 Maya 视口按 F 键聚焦时摄像机飞出视界、平移矩阵溢出或裁剪面错乱的常见 Bug。 |
| 65 | 空间变换、对齐与建模辅助 | **cvWrap 拓扑包裹与 weightDriver RBF 权重驱动修形套件** | [cvwrap_weightdriver](<03_transforms_modeling/cvwrap_weightdriver/cvwrap/bindui.py>) | 整合 cvwrap 与 weightDriver 高性能修形变形算法与 mgear animbits 模块 |
| 66 | 空间变换、对齐与建模辅助 | **EB Labs 世界空间坐标对齐与矩阵传递 (WorldSpaceTools)** | [eblabs_world_space_tools](<03_transforms_modeling/eblabs_world_space_tools/WorldSpaceTools/WorldSpaceTools.py>) | 在任意复合层级和空间下无缝传递世界坐标矩阵 |
| 67 | 空间变换、对齐与建模辅助 | **FCM 视口层级元素快速隐藏/隔离器** | [fcm_hider](<03_transforms_modeling/fcm_hider/FCM_Hider Install/Drag_and_drop_Install_FCM_Hider.mel>) | 一键快速切换骨骼、曲线、多边形等视口组件的可见性 |
| 68 | 空间变换、对齐与建模辅助 | **GPU缓存一键转实体模型** | [gpu_cache_to_mesh](03_transforms_modeling/gpu_cache_to_mesh/GPU缓存转实体.py) | 快速读取并解析选中的 gpuCache 节点，还原或重定向关联到真实几何体网格。 |
| 69 | 空间变换、对齐与建模辅助 | **独立选区孤立显示 (Isolate Selected Only)** | [isolate_selected](03_transforms_modeling/isolate_selected/isolate_selected_only.py) | 仅在当前活跃视口中孤立显示选中的物体本体，排查和屏蔽所有子层级与下挂物体，便于精细化编辑。 |
| 70 | 空间变换、对齐与建模辅助 | **物体对称镜像工具 (Mirror Tool)** | [mirror_tool](03_transforms_modeling/mirror_tool/mirror_tool.py) | 根据左右命名规则（如 _L 与 _R），按世界或局部反射平面（XY/YZ/XZ）将位置、旋转与缩放批量镜像到对称侧。 |
| 71 | 空间变换、对齐与建模辅助 | **视口选中白边高亮切换器 v2** | [no_highlight_v2](03_transforms_modeling/no_highlight_v2/NoHigh_Light_v2.py) | 单文件规范化入池，快速关闭视口物体选中高亮白边以观察真实光影 |
| 72 | 空间变换、对齐与建模辅助 | **四元数旋转插值与转换 (Quaternion Tool)** | [quaternion_tool](03_transforms_modeling/quaternion_tool/QuaternionTool_Maya.py) | 提供欧拉角与四元数双向转换、球面线性插值 (SLERP)、绕任意轴向量旋转计算，解决旋转插值翻折问题。 |
| 73 | 空间变换、对齐与建模辅助 | **轴心点与几何中心重置工具** | [reset_pivot](03_transforms_modeling/reset_pivot/maya_reset_pivot.py) | 一键将物体 Pivot 轴心重置到 Bounding Box 边界框中心、几何中心或世界原点，并清空轴向旋转。 |
| 74 | 空间变换、对齐与建模辅助 | **多功能旋转与角度对齐工具** | [rotation_aligner](03_transforms_modeling/rotation_aligner/旋转对齐工具.py) | 综合对齐面板。整合了角度实时显示、欧拉旋转对齐、骨骼轴向对齐，可计算空间夹角并将选区旋转轴快速校准至目标。 |
| 75 | 空间变换、对齐与建模辅助 | **SmartMesh 智能多边形网格操作工具** | [smart_mesh](<03_transforms_modeling/smart_mesh/dpSmartMeshTools.mel>) | 快速合并、清理、法线统一与重合面检测脚本 |
| 76 | 空间变换、对齐与建模辅助 | **一键解锁通道并冻结变换** | [unlock_freeze](03_transforms_modeling/unlock_freeze/unlock_and_freeze_transforms.py) | 批量递归遍历选中节点及其子级，一键解锁所有被锁定/隐藏的位移、旋转、缩放通道并安全执行冻结变换。 |
| 77 | 空间变换、对齐与建模辅助 | **UV集批量重命名规范化** | [uv_set_renamer](03_transforms_modeling/uv_set_renamer/UV集改名工具.py) | 批量扫描选中模型的 UVsets，一键将杂乱命名统一规范（如统一修正为 map1）。 |
| 78 | 空间变换、对齐与建模辅助 | **世界坐标复制粘贴与对齐 (v4 最新增强版)** | [world_transform_v4](03_transforms_modeling/world_transform_v4/复制粘贴世界坐标v4.py) | 提取选中物体的全局世界矩阵（Translate、Rotate），支持识别通道、识别父子关系与迭代误差判定校准。 |
| 79 | 资产管线与批量导入导出 | **Alembic (ABC) 批量导出套件** | [abc_batch_exporter](04_pipeline_io/abc_batch_exporter/ABC导出_v3.py) | 支持按选择集（Selection Sets）批量导出 Alembic ABC 几何体缓存，内置自动建立材质分配信息与输出目录整理。 |
| 80 | 资产管线与批量导入导出 | **AssetIt 个人与团队资产库管理器 v1.2.0 最新版** | [asset_it_v1_2](04_pipeline_io/asset_it_v1_2/AssetIt/AssetIt_Launcher.py) | 淘汰旧版 1.0.1，解压 1.2.0 完整工程，排除教程视频，保留预设模型库、图标与核心代码 |
| 81 | 资产管线与批量导入导出 | **文件批量导入加强版 v3** | [batch_importer_v3](04_pipeline_io/batch_importer_v3/批量导入加强版v3.py) | 支持文件/文件夹拖拽批量录入、递归子文件夹导入、一键批量清除/合并 Reference 参考文件、智能去除或添加命名空间。 |
| 82 | 资产管线与批量导入导出 | **工程文件批量自动化处理框架 v3** | [batch_processor_v3](04_pipeline_io/batch_processor_v3/文件批量执行v3.py) | 自动化批处理框架。指定文件夹遍历 .ma/.mb 工程，逐个静默打开并批量运行指定的 Python/MEL 脚本，输出执行日志。 |
| 83 | 资产管线与批量导入导出 | **无效与中文引用路径清理器** | [clean_invalid_paths](04_pipeline_io/clean_invalid_paths/clean_invalid_paths.py) | 深度扫描场景所有节点属性，检测并清理带有中文、乱码或损坏失效的外部 Reference 引用与贴图纹理路径，防止崩溃。 |
| 84 | 资产管线与批量导入导出 | **FBX 批量导出综合套件 v7** | [fbx_batch_exporter_v7](04_pipeline_io/fbx_batch_exporter_v7/fbx_export_CHS_v7.py) | 工业级 FBX 批量导出面板。支持按选择集批量输出、自动内嵌烘焙与重采样、一键取消骨骼分段比例补偿、时间轴区间自适应，并支持将导出预设保存为 JSON。 |
| 85 | 资产管线与批量导入导出 | **模型逐帧转 BlendShape 导出 FBX** | [per_frame_bs_fbx](04_pipeline_io/per_frame_bs_fbx/模型逐帧转bs导出fbx_v1.1.py) | 将变形动画模型逐帧生成 BlendShape 目标体，自动构建 BS 权重动画并导出 FBX，用于游戏引擎特种网格特效。 |
| 86 | 资产管线与批量导入导出 | **引用文件路径批量重定向与替换** | [replace_references](04_pipeline_io/replace_references/reference替换EN封装版.py) | 批量搜索并替换场景中 Reference 节点的工程文件根路径与引用物体，用于团队多环境切换与工程迁移。 |
| 87 | 资产管线与批量导入导出 | **舰船/载具资产特种 FBX 导出** | [vessel_fbx_exporter](04_pipeline_io/vessel_fbx_exporter/fbx导出工具舰船专用_自动版.py) | 面向特定载具资产的层级规范校验与自动 FBX 导出，自动规范化 Root 层级与材质引用规范。 |
| 88 | 虚幻引擎协同管线 | **UE 骨骼树清单导出 (Python + C++插件)** | [ue_bone_exporter](05_ue_pipeline/ue_bone_exporter/ExportBoneList.py) | 包含运行于 UE5 编辑器 Python 环境的导出脚本，以及原生 UE5 C++ 插件 (BoneListGenerator_UPlugin)，批量将 Skeletal Mesh 骨骼拓扑结构导出为文本。 |
| 89 | 虚幻引擎协同管线 | **UE5 编辑器右键源路径打印菜单** | [ue_context_menu](05_ue_pipeline/ue_context_menu/print_source_paths_menu.py) | UE5 编辑器右键资产菜单扩展，点击即可在日志中输出源 DCC 文件的物理路径。 |
| 90 | 虚幻引擎协同管线 | **UE 资产自动化导入配置与执行脚本** | [ue_fbx_auto_import](05_ue_pipeline/ue_fbx_auto_import/ue导入fbx配置.py) | Maya 端配置好 FBX 导入参数后，直接跨进程触发 Unreal Engine 自动化执行资产导入与属性安全设置。 |
| 91 | 虚幻引擎协同管线 | **UE 资产引用依赖与断链检查器** | [ue_reference_checker](05_ue_pipeline/ue_reference_checker/UE资产引用检查器.py) | 基于 Tkinter 的桌面工具，批量检测虚幻引擎项目资产间的引用依赖与断链丢失。 |
| 92 | 虚幻引擎协同管线 | **UE 资产源文件迁移与反向查找** | [ue_source_finder](05_ue_pipeline/ue_source_finder/UE源文件迁移.py) | 结合 UE 资产管理，根据 Unreal 资产引用逆向反查 DCC（Maya/FBX）源文件路径，支持跨工程资产映射与迁移。 |
| 93 | 场景体检、安全杀毒与快照 | **场景未知与垃圾节点清理 (HM Cleaner)** | [clean_junk_nodes](06_diagnostics_security/clean_junk_nodes/HM_清理垃圾节点.py) | 深度清除场景中残留的 unknown 节点、失效插件声明与无引用垃圾数据，减小文件体积、解决无法保存问题。 |
| 94 | 场景体检、安全杀毒与快照 | **Maya 场景病毒专杀与免疫疫苗** | [scene_virus_cleaner](06_diagnostics_security/scene_virus_cleaner/文件病毒清理魔改版.py) | 专门查杀与清除 Maya 常见恶意脚本蠕虫病毒（如 vaccine.py, fuckVirus, breed_gene），清除恶意 scriptJob 与节点，防止工程交叉感染。 |
| 95 | 场景体检、安全杀毒与快照 | **场景快照记录点与撤销恢复系统 (Undo Checkpoint)** | [undo_checkpoint](06_diagnostics_security/undo_checkpoint/maya_undo_checkpoint.py) | 突破 Maya 原生撤销限制。可随时为场景创建快照存档点（Checkpoint），一键快速恢复或清空，带专用工具架按钮。 |
| 96 | 大型专业独立子系统与完整套件 | **animBot 完整 UI 与工具克隆套件** | [animbot_copy](07_subsystems_suites/animbot_copy/launch.py) | 完整复刻知名动画插件 animBot 的 UI 与工具库：包含 Graph Editor 曲线编辑器嵌入式工具栏、弹性回弹多段滑块、工作区管理。 |
| 97 | 大型专业独立子系统与完整套件 | **GETOOLS 动力学与次级动作套件 (含 Overlappy / CenterOfMass)** | [getools_overlappy](07_subsystems_suites/getools_overlappy/GeneralWindow.py) | 包含两大神器：1. Overlappy 一键自动生成物理次级重叠惯性动作；2. CenterOfMass 角色实时重心质心解算。 |
| 98 | 大型专业独立子系统与完整套件 | **Malcolm341 Maya 高级实用脚本合集 (MegaPack 2023)** | [malcolm341_mega_pack](<07_subsystems_suites/malcolm341_mega_pack/malcolm341_mega_pack_20230114/shelf_malcolm341_mega_pack.mel>) | 汇集了大量影视游戏一线制作加速脚本与架上工具 |
| 99 | 大型专业独立子系统与完整套件 | **Maya 节点式蓝图自动化工具箱 (Blueprint Toolbox 完整工程)** | [maya_blueprint_toolbox](07_subsystems_suites/maya_blueprint_toolbox/main.py) | 基于 Qt 的可视化节点连线画布与执行引擎。支持像虚幻蓝图一样连线驱动 Maya 操作，内置动画、属性、约束等通用 API 包装。 |
| 100 | 大型专业独立子系统与完整套件 | **Maya 视口智能拖拽与对话框拦截助手** | [smart_assistant](07_subsystems_suites/smart_assistant/main.py) | 视口拖拽与文件对话框拦截：将图片序列拖入视口自动生成摄像机与 ImagePlane；拖入 FBX/MA 自动弹窗提示导入/引用规则。 |
| 101 | 大型专业独立子系统与完整套件 | **Studio Library 世界空间扩展增强包 (PlusPatch)** | [studiolibrary_patch](07_subsystems_suites/studiolibrary_patch/studiolibrary_wanimation/__init__.py) | 在原生 Studio Library 基础上增加了世界坐标动画抓取与跨角色粘贴 (WAnimation)、世界坐标姿态对齐 (WPose) 与中文汉化。 |
| 102 | 大型专业独立子系统与完整套件 | **TheKeyMachine 动画师综合套件 (完整汉化增强版)** | [the_key_machine](07_subsystems_suites/the_key_machine/core/toolbar.py) | 关键帧微调工具：包含曲线平滑、切线权重批量调整、反向动画、自定义曲线图编辑器与一键汉化补丁。 |
| 103 | 系统辅助与环境管理 | **吸附式悬浮快捷工具栏** | [floating_toolbar](08_utilities_system/floating_toolbar/floating_toolbar.py) | 基于 PySide2 的悬浮工具条，可自动吸附在 Maya 视口边缘，支持拖拽 Shelf 命令或自定义按钮生成轻量操作浮窗。 |
| 104 | 系统辅助与环境管理 | **KS NodeOutliner 节点分类大纲增强管理器 v2.2.0** | [ks_node_outliner_v2_2](<08_utilities_system/ks_node_outliner_v2_2/KS_NodeOutliner-2.2.0/ks_nodeOutliner/ksNodeOutliner.py>) | 解压 KS_NodeOutliner-2.2.0.zip，按节点类型过滤与大纲容器聚合展示 |
| 105 | 系统辅助与环境管理 | **KS SaveTimer 智能工程自动保存与版本递增 (原版+汉化版)** | [ks_save_timer_v1_3_0](<08_utilities_system/ks_save_timer_v1_3_0/KS_SaveTimer-1.3.0/【原版】/ks_saveTimer/runApp/runMaya.py>) | 包含原版与汉化版完整代码与手册，定期提醒与多重备份 |
| 106 | 系统辅助与环境管理 | **Maya 进程与端口查找器 (MayaFinder)** | [maya_process_finder](08_utilities_system/maya_process_finder/maya_process_finder.py) | Windows 独立桌面 GUI。自动探测枚举本机所有运行中的 Maya 进程 PID、占用端口（Command Port），排查卡死与多开。 |
| 107 | 系统辅助与环境管理 | **Maya-Tabs 视口多工程标签页切换扩展 v1.3a** | [maya_tabs_v1_3a](08_utilities_system/maya_tabs_v1_3a/plug-ins/Maya-Tabs.py) | 解压 Maya-Tabs_v1.3a.zip，在视口顶部呈现类似浏览器标签的多场景快速切换条 |
| 108 | 系统辅助与环境管理 | **Maya 视口智能文件拖拽重载扩展** | [perform_file_drop_action](08_utilities_system/perform_file_drop_action/performFileDropAction.mel) | 重载 performFileDropAction.mel，支持拖拽自动识别格式与智能弹窗处理 |
| 109 | 系统辅助与环境管理 | **Maya 跨版本工具架管理器 (2018-2026)** | [shelf_manager](08_utilities_system/shelf_manager/shelf_manager.py) | 集中管理 Maya 2018~2026 各版本的 Shelf 工具架配置，区分中英文路径，支持跨版本复制、同步与备份。 |