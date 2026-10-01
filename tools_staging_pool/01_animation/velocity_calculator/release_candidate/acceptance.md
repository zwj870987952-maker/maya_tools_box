# 速度计算器真实 Maya 验收（not_run）

1. 备份动画场景，加载 launch_candidate.py 的 load_tool，使用已知线性位移与不同currentTime；dry_run后检查时间/节点/键/Undo/选择不变。
2. 两按钮UI顺利打开、中文解释和inViewMessage正确。选择多对象默认首个，API显式列表逐项完整返回，component/属性/歧义/零时长/无选择拒绝。
3. average真实start/end，instant向后一帧（可小数sample_step）结果正确且时间不跳；往返到原点average可为0，明确与沿路径速率不同。
4. 24/60/120fps、自定义fps、秒/分钟，cm/m/in线性单位及负/小数帧比较；world父层动画/旋转pivot/实例路径检查，以transform原点为标准。
5. 用测试场景对照生产constraint/IK/expression/缓存与动态模拟真实逐帧播放结果，若历史依赖导致context不同记录限制/报错，不能在生产场景试改后宣称正确。
6. Script Editor无Fatal，测量不改reference/锁/场景或文件；GUI/版本与依赖证据记录后再使用预制promotion动作，不提前转正。
