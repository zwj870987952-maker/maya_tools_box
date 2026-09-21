# 01. 动画制作与高阶编辑 (Animation)

> 涵盖影视/游戏动画全生命周期的高频工具，包括拍屏、IK/FK切换、姿态匹配、曲线修复、质心烘焙、原点归零、时间轴微调与阶梯关键帧偏移等。

## 工具清单与导向

| 序号 | 工具名称 | 对应目录与入口 | 核心功能简述 | 建议重构优先级 |
| :--- | :--- | :--- | :--- | :--- |
| 1 | **MOV拍屏输出工具 (Playblast MOV Tool v11)** | [mov_playblast_v11](mov_playblast_v11/mov拍屏v11.py) | 专业 Playblast 拍屏工具。集成 HUD 镜头遮罩、时间码/帧率显示、摄像机焦距信息、自定义分辨率与 MOV/MP4 格式导出压缩。 | P1 - 核心高频 |
| 2 | **IK/FK无缝双向切换与烘焙工具** | [ik_fk_switch](ik_fk_switch/mog_ikFkSwitch.py) | 角色 IK 与 FK 控制器双向无缝匹配吸附。支持当前帧单帧吸附，以及时间轴选定区间的全自动动画烘焙切换。 | P1 - 核心高频 |
| 3 | **双角色/骨骼姿态匹配器 (PoseMatcher)** | [pose_matcher](pose_matcher/PoseMatcher.py) | 基于四元数与空间向量运算。支持不同命名空间/不同绑定的双角色之间姿态智能镜像与快速吸附。 | P1 - 核心高频 |
| 4 | **复制动画与曲线修复工具** | [copy_animation](copy_animation/复制动画_修复优化版.py) | 批量复制与重映射动画曲线，内置断裂曲线修复算法，支持同名控制器/骨骼曲线通道一键批量传递。 | P1 - 核心高频 |
| 5 | **Root动画生成与质心约束烘焙** | [root_motion_bake](root_motion_bake/root动画生成.py) | 自动计算角色质心位移轨迹并生成 Root 根骨骼动画，创建独立动画层并烘焙相对位移与旋转。 | P1 - 核心高频 |
| 6 | **动画位移回归原点 (Back2Origin 最新增强版)** | [back2origin_v05_gaiv3](back2origin_v05_gaiv3/Back2Origin_v05_gaiv3.py) | 自动识别场景中角色控制器，支持将脱离原点的移动平移回世界原点，新增反向操作与命名空间切换。 | P2 - 进阶扩展 |
| 7 | **增强型时间轴控制面板** | [timeline_enhanced](timeline_enhanced/maya_timeline_tool_enhanced.py) | 增强的时间轴交互面板，支持时间范围快速缩放/重映射、播放倍速实时调整、帧范围填充与关键帧区间标记。 | P2 - 进阶扩展 |
| 8 | **万向节死锁修复器 (Gimbal Fixer)** | [gimbal_lock_fix](gimbal_lock_fix/maya_animation_gimbal_fix.py) | 自动检测旋转动画曲线中的欧拉角跳变与万向节死锁现象，通过 Euler Filter 与四元数插值平滑修复异常翻滚。 | P2 - 进阶扩展 |
| 9 | **时间轴运动速度计算器** | [velocity_calculator](velocity_calculator/maya_velocity_calculator.py) | 计算选中物体在当前时间轴区间的空间直线位移与平均运动速度（支持自动换算帧率到单位/秒）。 | P2 - 进阶扩展 |
| 10 | **关键帧阶梯递减偏移工具 (Stagger/Offset)** | [stagger_offset](stagger_offset/批量减选关键帧偏移.py) | 制作重叠动作 (Overlapping Action) 与依次延迟动画的必备工具。自动对选中控制器链逐级减选并向后平移关键帧。 | P2 - 进阶扩展 |
| 11 | **世界空间坐标锁定 (lockToWorld)** | [lock_to_world](lock_to_world/jop_lockToWorld.py) | 一键将骨骼或控制器在指定时间段内“钉死”在世界坐标中（经典防滑步、手部固定抓握对齐工具）。 | P2 - 进阶扩展 |
| 12 | **Maya动画重定向工具 (Animation Retarget)** | [animation_retarget](animation_retarget/动画重定向.py) | 跨骨骼/控制器的动画批量转移工具。支持通道映射自定义、配置保存/加载、右键批量重定向。 | P2 - 进阶扩展 |

## 整合至 `maya_toolkit` 的规范要求
当您挑选本目录中的工具进行正式重构时，请遵循以下规范：
1. **继承基类**：所有工具类需继承自 `maya_toolkit.core.base_tool.BaseMayaTool`。
2. **标准化输出**：执行入口统一为 `run(**kwargs) -> ToolResult`，支持 `success`, `data`, `message`, `errors` 结构。
3. **大模型 Schema 支持**：通过 `get_schema()` 提供入参类型说明与默认值，支持 Agent 自动读取调用。
4. **安全试运行**：必须支持 `dry_run=True` 预检模式，在执行破坏性/批量操作前不产生实际副作用。
