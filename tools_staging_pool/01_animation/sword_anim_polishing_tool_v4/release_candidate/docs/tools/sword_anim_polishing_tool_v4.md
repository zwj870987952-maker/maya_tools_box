# Sword Anim Polishing 完整候选

tool_id: sword_anim_polishing_tool_v4；animation；真实 Maya GUI not_run，prepared_unverified。作者 Pavel Barnev，Copyright 2018–2020。原9文件（完整主MEL、安装器、许可、ReadMe、四份misc帮助、BMP）全部字节/SHA未改。原主程序57声明、56唯一全局过程、21非Maya内建全局变量完整携带，一处重复过程也未改。许可明确禁止修改/逆向/分发、商业内部使用需购买。本次仅本地整理独立适配，不修改原程序，不购买/发布。原MEL开发缺陷不通过改其字节修复。

## 能力与调用

完整保留 Parent In、Make Aim、Make Sword、Make Reverse、Arc Polish、Bake/Layer Bake、Euler过滤、source/top/side/base/all与path三组快捷选择、MotionTrail Update、VP恢复及四份帮助。独立 Python UI 包含原按钮/参数和新增的明确完成布置步骤；原UI仍在未改vendor内，可通过 show_original_ui() 显式对照，不与候选同时开启。

| action | 输入与原生行为 |
|---|---|
| status | 无场景写入，返回session/pending/failed/owned/groups/完整过程数。|
| parent_in | objects按明确顺序，多个控制器动画录至最后控制器对应的外部locator层级；完整原约束→bake→约束回源与Euler处理。size默认1；start/end默认animation range。必须交互模型视口。|
| begin_aim | 一个或多个对象，原begin创建每对象Top/Side，size默认1，记录范围和输入UUID；移动后finish_setup调用完整原结束过程。|
| begin_sword / begin_reverse | 依序sword、可选wrist、hand共2或3对象；完整原Top/Side/或Pivot设置。Sword大小按原固定值，Reverse size默认1。|
| finish_setup | 无需当前选择，依session UUID还原原全局/输入；拒重合/共线Top/Side；调用完整原Aim/Sword/Reverse收尾含代理joint、方向/相对位置、bake、双向约束和回源控制。|
| arc_polish | 一个已有动画的控制器；knots原范围2..20默认3，show_source原选项。实际时间滑块框选或所选本对象键的区间，不能用未实现的后台时间滑块代替。完整snapshot/MotionTrail/路径重建/cluster/移动控制器/motionPath/nearestPointOnCurve逐帧uValue/Curve_trajectory与pairBlend。|
| bake / bake_layer | 原完整bakeResults -simulation 1 -shape false与最小化旋转的layer行为；包含原Euler后处理，start/end默认animation range。Layer新名BakedAnim，已存在同名节点则预检拒绝。|
| euler_filter | 原首键前10帧临时零旋转键→filterCurve→cutKey；可能改变整个旋转曲线的 winding，影响不局限于bake范围。|
| select_group | group=source/aim_top/aim_side/base/all/path_source/path_locator/path_system，通过记录UUID选择；找不到节点不接管同名对象。|
| delete_system | 先对全部输入成功Bake；仅删除本候选记录helper，拒外部child/输出。保留真实烘焙曲线/animation layer，pairBlend先恢复其烘焙input1输出至控制器再移除；无独立动画则拒绝。|
| update_motion_trails | 原程序更新所有trails；存在未记录外部motionTrail时拒绝，避免误处理其他工具。|
| refresh_viewport | 明确恢复refresh及实际时间滑块显示；原VP不保证异常时有效，本适配不用陈旧startTime/eval_mode重置环境。|
| help / constraint_weights | 四帮助文件只读显示；实际原距离逆权重/零距离分支按objects中目标列表+末尾受约束对象返回weights，不写场景。|

objects省略用当前整transform/joint选择；列表顺序有业务意义。禁止组件/shape、歧义短名、实例、引用、锁定T/R、未知输入driver和外部共享curve；已有rig约束/复杂层需备份场景另验收。size0.01..100，区间整数end>start、最多200000帧。session可填网络节点或UUID，多个候选session时必须明确指定。源码 globals/过程仍共享，不能同时混跑另一版Sword或原UI；发现不同SHA的同名原过程拒覆盖，要求重启Maya。

## 适配与操作影响

BaseMayaTool Schema/validate/execute/ToolResult、共用UndoChunkContext与面板注册协议全部准备。预检只读哈希/场景/会话，不source原MEL、不创建网络、不加载插件、不改prefs/选择/时间。执行才source完整未改MEL并建立UUID会话/新节点owner标记，记录所有源输入、新helper和原全局变量指向。以后重命名、存盘重开、Undo后依据网络记录还原全局，不用Python陈旧对象名。

原begin注册SomethingSelected条件一次性scriptJob，在取消选择时自动写场景。独立适配捕获并取消本次新增的原SW回调，保留原begin创建结果，改为明确finish_setup。没有修改vendor回调源码或替换全局原过程。Top/Side/Pivot位置需用户在真实Maya调整，不能以零偏移自动完成；完整原结束算法由finish调用，Undo阶段明确分组。原UI保留旧自动回调，因此手工对照只能在备份上运行，不用于受预检API的混合流程。

finally恢复时间、对象/键选择、namespace、autokey、线性单位、evaluation、selection-order tracking、相关anim optionVars、Move模式/上下文、cache preference、refresh及时间滑块；操作成功的新输出动画layer不强制改回mute而破坏结果。Arc原程序会把所有motionTrail.nodeState设2，适配在finally按UUID恢复原trails值。非Arc先临时清除全局选键，避免原无对象keyframe查询借用无关对象，再恢复。Maya UI/Prefs和键剪贴板副作用不当作场景Undo保证。

原 SW_7 motionPath过程打开Undo chunk而不关闭，Arc嵌套收尾也会遗留。适配通过实际MCommandMessage命令回调记录本次原MEL中open/close数量，调用结束关闭仅已观测未配对的原chunk，外层框架chunk保留。成功与真正原路径失败均已在隔离Maya验证一次Undo正常；不改源码/不估计当前chunkName深度（实际query只返回最外层名字）。原UI独立运行仍有该缺陷。

源bake内部catch/catchQuiet会吞报错；候选补输出键范围检查和failed会话状态，但仅凭键范围不能证明生产rig/layer结果正确。失败或取消可能已有部分key/连接，必须整体Undo，不宣称自动回滚；未Undo的failed会话阻止新写入。Bake会采样全部原可键属性，Euler可改区间外旋转。Delete须先Bake并确认源动画，再移除只记录的helper；复杂layer/pairBlend清理必须专项真实验收，拒绝时保留系统。

## 本次验证范围

原完整56过程在Maya2025成功source，没创建场景节点/UI或Undo记录；原逆距权重（含零距）与完整Bake/原Euler可在隔离mayapy执行。原native motionPath逐帧uValue、临时nearestPoint/decompose删除、未关闭Undo修复与Undo/Redo已检查。实际Parent In调用在无模型视口的mayapy失败，分步诊断定位到原 SW_6de locator屏幕尺寸过程，故Parent In/Aim/Sword/Reverse/完整Arc明确要求交互Maya，没有删该过程或伪造摄像机来让测试通过。真实按钮、视觉结果、复合武器rig与完整Arc全部待验收。

```python
tool.run(action='status',dry_run=True)
# 在真实Maya：按顺序选weapon、hand
tool.run(action='begin_sword',objects=['weapon','hand'],start=1,end=48)
# 移动已创建Top/Side，session可在Status输出取得
tool.run(action='finish_setup',session=session_id)
tool.run(action='select_group',session=session_id,group='source')
tool.run(action='bake',session=session_id,start=1,end=48)
tool.run(action='delete_system',session=session_id)
```

潜在组合为草稿武器动画→Parent/Aim/Sword/Reverse→Arc调整→Bake→删除本系统→曲线整理，和其他候选联用未实测。原安装器不执行；show_original_ui会按原行为加载matrixNodes并设置autoload偏好，只有明确使用该入口才发生，不由场景Undo撤回。正式目录、文档、tests与ALL_TOOL_CLASSES/面板挂载预制于promotion，真人验收前不apply。
