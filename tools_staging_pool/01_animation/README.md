# 动画制作与高阶编辑 (Animation)

> 当前分类共收纳 **49** 个纯明文开源的工具与脚本。所有代码均已解耦并开放，可直接阅读、调试或封装转正。

## 工具清单与导向

| 序号 | 工具名称 | 对应目录与入口 | 核心功能简述 |
| :--- | :--- | :--- | :--- |
| 1 | **动画曲线过滤器套件 (animFilters)** | [anim_filters](anim_filters/animFilters.mel) | 欧拉角跳变与动画曲线噪点平滑过滤 |
| 2 | **动画层书签关键帧修剪器 (Bookmark Trimmer)** | [anim_layer_bookmark_trimmer](anim_layer_bookmark_trimmer/anim_layer_bookmark_trimmer.py) | 根据时间滑块书签起止端点，仅保留选定动画层在书签起始与结束处的关键帧，修剪清理所有中间非端点帧。支持原子撤销与预检。 |
| 3 | **动画层逐关键帧命令执行器 (AnimLayer Key Runner)** | [anim_layer_key_runner](anim_layer_key_runner/anim_layer_key_runner.py) | 智能检索选中物体在指定动画层（或当前激活层）上的专属关键帧，逐帧跳转并批量触发 MEL 或 Python 命令（如 asAutoSwitchFKIK 自动切换匹配、打关键帧等）。 |
| 4 | **动画层关键帧区间书签生成器** | [anim_layer_keyframe_bookmark](anim_layer_keyframe_bookmark/anim_layer_keyframe_bookmark.py) | 提取所选物体在当前动画层级上的关键帧，在相邻关键帧之间自动创建相邻色彩互斥的时间滑块书签 (Bookmarks)。 |
| 5 | **动画层综合控制面板 v4.0** | [anim_layer_v4_0](anim_layer_v4_0/anim_layer.mel) | 动画层批量关键帧与显示管理增强面板 |
| 6 | **角色动画镜像助手 v1.1 (Studio版)** | [anim_mirror_helper_v1_1](anim_mirror_helper_v1_1/Anim_Mirror_Helper.py) | 角色姿态与控制器动画快速镜像 |
| 7 | **AnimPolish PREMIUM 角色动画修帧曲线抛光神器 v1.23** | [anim_polish_premium_v1_23](anim_polish_premium_v1_23/AnimPolish.py) | 提取 v1.23 最新付费版，淘汰根目录的 v1.19 Basic 旧版，附带说明文档 |
| 8 | **Maya动画重定向工具 (Animation Retarget)** | [animation_retarget](animation_retarget/动画重定向.py) | 跨骨骼/控制器的动画批量转移工具。支持通道映射自定义、配置保存/加载、右键批量重定向。 |
| 9 | **AniMirror 动画镜像工具 v2.0** | [animirror_v2_0](animirror_v2_0/AniMirror.py) | 独立 Qt 界面动画姿态与序列帧镜像工具 |
| 10 | **动画位移回归原点 (Back2Origin 最新增强版)** | [back2origin_v05_gaiv3](back2origin_v05_gaiv3/Back2Origin_v05_gaiv3.py) | 自动识别场景中角色控制器，支持将脱离原点的移动平移回世界原点，新增反向操作与命名空间切换。 |
| 11 | **Aim 朝向与视线注视对齐工具 v1.1** | [bh_aim_tools_v1_1](bh_aim_tools_v1_1/bh_aimTools.py) | Brian Horgan 开发的眼部注视与空间朝向辅助工具 |
| 12 | **局部微调位移旋转工具 (bh_localNudge)** | [bh_local_nudge](bh_local_nudge/bh_localNudge.py) | 在局部/屏幕/父级坐标系下微调动画控制器位移与旋转 |
| 13 | **动漫二次元动画速度线生成器** | [bh_speedlines](bh_speedlines/bh_speedLines.mel) | 生成跟随角色动态的视效速度线与冲击波特效网格 |
| 14 | **跟随重叠动画生成器 (bh_waveIt)** | [bh_wave_it](bh_wave_it/bh_waveIt/bh_waveIt.mel) | 排除演示视频，保留 mel 脚本与图标，为链条、尾巴快速添加基于数学正弦波的波浪跟随 |
| 15 | **Locator 定位器空间位移传递 (BRSLocTransfer 离线版)** | [brs_loc_transfer](brs_loc_transfer/BRSLocTransfer.py) | 无需外网连接，通过中间 Locator 烘焙并转移角色空间位移旋转 |
| 16 | **动捕数据平滑降噪过滤器 (BRSSmoothMocap)** | [brs_smooth_mocap](brs_smooth_mocap/BRSSmoothMocap.py) | 针对动作捕捉抖动关键帧的智能平滑插值降噪器 |
| 17 | **CgShake 电影级摄像机真实手持抖动模拟 (Python3版)** | [cg_shake_py3](cg_shake_py3/CgShake_py3/cgshake.py) | 解压最新的 CgShake_py3.rar，淘汰旧版 Python 2 压缩包，内置手持、爆炸、呼吸等丰富抖动预设 |
| 18 | **复制动画与曲线修复工具** | [copy_animation](copy_animation/复制动画_修复优化版.py) | 批量复制与重映射动画曲线，内置断裂曲线修复算法，支持同名控制器/骨骼曲线通道一键批量传递。 |
| 19 | **多方向位移循环动画工具 v1.1** | [directional_cycle_tool_v1_1](directional_cycle_tool_v1_1/DirectionalCycleTool/main.py) | 解压 DirectionalCycleTool_v1_1.rar，智能循环平铺走跑跳动画位移 |
| 20 | **dofControl 摄像机景深聚焦交互控制工具 v1.0** | [dof_control_v1_0](dof_control_v1_0/dofControl.py) | 在视口中以 Locator 快速驱动摄像机焦点与景深模糊范围 |
| 21 | **EB Labs 视口屏幕空间操控套件 (ScreenSpace)** | [eblabs_screenspace](eblabs_screenspace/ScreenSpace.py) | 直接在摄像机平面屏幕坐标系下锁定并拖拽控制器 |
| 22 | **EB Labs Whiskey 动画姿态与时间轴快照** | [eblabs_whiskey](eblabs_whiskey/Whiskey.py) | EB Labs 出品的高效姿态捕获与动画对比套件 |
| 23 | **多空间无缝切换与吸附工具 (FD Multi-Space)** | [fd_multi_space](fd_multi_space/FD_MULTI-SPACE.py) | 支持角色控制器世界/局部/任意道具层级空间实时无缝切换吸附 |
| 24 | **万向节死锁修复器 (Gimbal Fixer)** | [gimbal_lock_fix](gimbal_lock_fix/maya_animation_gimbal_fix.py) | 自动检测旋转动画曲线中的欧拉角跳变与万向节死锁现象，通过 Euler Filter 与四元数插值平滑修复异常翻滚。 |
| 25 | **IK/FK无缝双向切换与烘焙工具 (Pro 3.0 增强升级版)** | [ik_fk_switch](ik_fk_switch/mog_ikFkSwitchPro.py) | 升级池中现有老版本 mog_ikFkSwitch.py 至 Pro 3.0 架构 |
| 26 | **JOP 角色动画批量重定向套件 v0.9** | [jop_retarget_anim_v09](jop_retarget_anim_v09/jop_retargetAnim/jop_retargetAnim.py) | 完整工程套件，含拖拽安装、通道重映射与图形化映射 UI |
| 27 | **关键帧物理重叠与次级动作解算器 v2.0** | [keyframe_overlap_v2_0](keyframe_overlap_v2_0/KFOverlap/KeyframeOverlap.py) | 一键为骨骼链/毛发飘带生成基于物理摆动的重叠动作 |
| 28 | **kfAnimRig IK/FK 极速匹配切换** | [kf_animrig_ikfk](kf_animrig_ikfk/kfAnimRig_IKFK.mel) | 独立的轻量级 MEL 角色 IK/FK 切换与吸附面板，排除视频 |
| 29 | **世界空间坐标锁定 (lockToWorld)** | [lock_to_world](lock_to_world/jop_lockToWorld.py) | 一键将骨骼或控制器在指定时间段内“钉死”在世界坐标中（经典防滑步、手部固定抓握对齐工具）。 |
| 30 | **Maya 关键帧智能精简工具 (Keyframe Reduction)** | [maya_keyframe_reduction](maya_keyframe_reduction/scripts/keyframeReduction.py) | 开源关键帧容差精简算法，批量去除动捕和烘焙冗余帧 |
| 31 | **时间滑块颜色书签与事件标记插件 (Timeline Marker)** | [maya_timeline_marker](maya_timeline_marker/scripts/timelineMarker/ui.py) | 完整开源工程，在时间轴上创建彩色便签、区域标记与热键跳转 |
| 32 | **MOV拍屏输出工具 (Playblast MOV Tool v11)** | [mov_playblast_v11](mov_playblast_v11/mov拍屏v11.py) | 专业 Playblast 拍屏工具。集成 HUD 镜头遮罩、时间码/帧率显示、摄像机焦距信息、自定义分辨率与 MOV/MP4 格式导出压缩。 |
| 33 | **OverSlapper 弹性重叠与惯性延迟工具 v1.03** | [overslapper_v1_03](overslapper_v1_03/overslapper.py) | 在动画曲线上快速应用弹簧、惯性与阶梯延迟效果 |
| 34 | **Maya 动画物理动力学辅助工具箱** | [physics_tools](physics_tools/PhysicsTools.mel) | 布娃娃/重力/次级惯性动力学物理模拟解算，过滤29个教学视频 |
| 35 | **双角色/骨骼姿态匹配器 (PoseMatcher)** | [pose_matcher](pose_matcher/PoseMatcher.py) | 基于四元数与空间向量运算。支持不同命名空间/不同绑定的双角色之间姿态智能镜像与快速吸附。 |
| 36 | **远距离/任意空间相对姿态还原器 (PoseTransfer)** | [pose_transfer_remote](pose_transfer_remote/PoseTransfer.py) | 提取并规范化 Python 源码为 PoseTransfer.py，跨世界位置精准复制还原角色局部相对 Pose |
| 37 | **RetimeTools 时间节奏与关键帧重配工具** | [retime_tools](retime_tools/RetimeTools.py) | 解压汉化版与原版，支持以滑块自由伸缩整体动作节奏 |
| 38 | **Root动画生成与质心约束烘焙** | [root_motion_bake](root_motion_bake/root动画生成.py) | 自动计算角色质心位移轨迹并生成 Root 根骨骼动画，创建独立动画层并烘焙相对位移与旋转。 |
| 39 | **形状动画形态微调工具 (Shape Animation)** | [shape_animation_tool](shape_animation_tool/ShapeAnimationTool.py) | 排除视频，保留原版与汉化版完整代码与手册 |
| 40 | **关键帧平移与波浪式偏移工具 v3.2** | [shift_animation_v3_2](shift_animation_v3_2/Shift_animation.mel) | 批量阶梯式平移关键帧，制作波浪跟随动画 |
| 41 | **经典物理弹簧骨骼计算器 v3.5a (SpringMagic)** | [spring_magic_v3_5a](spring_magic_v3_5a/springmagic.py) | 经典弹簧骨骼动力学插件，为头发、飘带、尾巴自动生成逼真摆动 |
| 42 | **Stagger 关键帧阶梯偏移图形化面板 (GUI版)** | [stagger_gui](stagger_gui/ui.py) | 相比池中单脚本命令行版，增加独立 SVG 图标与 Qt 面板，清理 macOS 垃圾后入池 |
| 43 | **关键帧阶梯递减偏移工具 (Stagger/Offset)** | [stagger_offset](stagger_offset/批量减选关键帧偏移.py) | 制作重叠动作 (Overlapping Action) 与依次延迟动画的必备工具。自动对选中控制器链逐级减选并向后平移关键帧。 |
| 44 | **武器与刀剑轨迹修帧抛光神器 v4** | [sword_anim_polishing_tool_v4](sword_anim_polishing_tool_v4/Sword_Anim_Polishing_Tool_v4.mel) | 排除视频，保留 mel 脚本与位图组件，精准平滑武器剑尖运动轨迹 |
| 45 | **Tom Bailey 动画效率工具箱 (tbAnimTools)** | [tb_anim_tools](tb_anim_tools/tbAnimToolsInstaller.py) | 解压 HelpImages，包含时间轴平滑拖拽、前后关键帧快速跳转等功能 |
| 46 | **增强型时间轴控制面板** | [timeline_enhanced](timeline_enhanced/maya_timeline_tool_enhanced.py) | 增强的时间轴交互面板，支持时间范围快速缩放/重映射、播放倍速实时调整、帧范围填充与关键帧区间标记。 |
| 47 | **Tweener 快速过渡帧/中间帧滑块 v1.0.2** | [tweener_v1_0_2](tweener_v1_0_2/tweener.py) | Justin Barrett 开发的经典 Breakdown 中间帧百分比混合滑块 |
| 48 | **时间轴运动速度计算器** | [velocity_calculator](velocity_calculator/maya_velocity_calculator.py) | 计算选中物体在当前时间轴区间的空间直线位移与平均运动速度（支持自动换算帧率到单位/秒）。 |
| 49 | **W Retarget Tool 动画快速重定向脚本** | [w_retarget_tool](w_retarget_tool/WretargetTool.py) | 单文件规范化为目录打包，轻量级双骨骼/物体动画烘焙重定向 |

## 整合至 `maya_toolkit` 的规范要求
当您挑选本目录中的工具进行正式重构时，请遵循以下规范：
1. **继承基类**：所有工具类需继承自 `maya_toolkit.framework.base_tool.BaseMayaTool`；
2. **标准化输出**：执行入口统一为 `run(dry_run=False, **kwargs) -> ToolResult`；
3. **大模型 Schema 支持**：通过 `get_schema()` 提供入参类型说明与默认值，支持 Agent 自动读取调用；
4. **安全试运行**：必须支持 `dry_run=True` 预检模式，在执行破坏性/批量操作前不产生实际副作用；
5. **双向反哺下沉**：通用几何、矩阵或 DAG 算法下沉沉淀到 `maya_toolkit.core` 公共库中。
