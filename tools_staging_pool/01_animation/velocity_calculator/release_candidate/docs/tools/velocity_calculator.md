# 世界空间位移速度计算

原自有单文件、完整四个入口/距离公式与两个按钮保留可追溯。本候选修复平均计算先读取当前帧、再切到start读作end、最终留在end的顺序错误；原四种fps以外把帧差当秒的问题也修复。现在用worldMatrix的MDGContext在真实start/end求值，不切换currentTime、不给场景添加helper、不写关键帧。API矩阵内单位是cm，经 MDistance 转当前线性单位；时间经 MTime 当前时间单位换秒，不使用有限fps表。

`VelocityCalculatorTool.run(mode='average', objects=[...], start_frame=..., end_frame=...) -> ToolResult`，tool_id=`velocity_calculator`。average默认playback min/max，要求end>start；instant使用frame（默认当前）与frame-sample_step，sample_step默认1，必须正数。允许负帧/小数帧，最大绝对帧10000000。明确whole transform绝对DAG路径或唯一名字；拒components/属性/歧义/重复别名。省略objects保留原行为只计算首个选中对象，显式对象列表可批量。引用/锁对象允许只读查询，不解锁、不改reference。

`ToolResult.data` 包含mode、真实start/end、duration_seconds、Maya时间/线性单位、quantity、每对象start_position/end_position/distance/speed/velocity_vector（当前线性单位/s）和gui_acceptance=not_run。`show_result=False`默认结构化输出，True明确交互Maya inViewMessage且仅显示第一项；batch使用结构化输出。

“平均速度”保留端点位移长度/经过秒数的含义，不是沿完整运动路径累计距离的平均速率；往返到原点可得到0。“瞬时速度”是向后一段的有限差分，不是解析导数。向量含方向，speed为向量模。worldMatrix描述transform原点，不是旋转pivot/mesh质心。原0时长输出0缺乏定义，候选明确拒绝。distance公式完整保留，单位与采样时刻修正已列为行为变化。

validate/dry_run只检对象、区间、单位和交互消息条件；不采样历史曲线、不改场景/时间/Undo/选择或文件。execute只读DGContext求值，依赖Base框架但不承诺因UndoChunk而改变读取结果；GUI独立懒打开，原始自动create_ui入口只在 `.py.original` 归档。两个中文按钮和私有窗口完整提供，并标明量的实际含义；无配置写入或外部依赖。

父层动画/实例世界路径按MDagPath.instanceNumber选择worldMatrix；非均匀scale会改变真实世界位移，属于计算输入。离线检查覆盖基本父动画/常规单位；历史模拟、动力学/缓存、特殊约束/表达式的上下文求值是否等同真实逐帧播放需人工确认，不能切真实生产时间轴去伪造通过。出现NaN/Infinity拒返回有效速度。

可在动画修改前后比较JSON结果，但没有验证自动组合。core当前常规世界位置查询不支持指定MDGContext，候选只保留自身采样逻辑，不改正式core。无单独许可文件，原SHA完整保留；晋级清单含代码、原件、文档、测试和panel注册，真实GUI/生产场景验收前不转正。
