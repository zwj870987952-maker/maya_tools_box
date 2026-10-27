# JOP世界锁定候选

ID `lock_to_world`，animation，Jesse ONG PHO v09。原业务文件与中文启动文件共2项按字节保留，原13函数/4UI方法与矩阵/四元数算法完整保留。未附独立许可，仅本地私有整理、不发布。差异见lock_to_world_changes.diff。原启动器不执行，候选不import时加载.mll或开窗口。

## 算法与效果边界

按每个控制器在start帧的世界矩阵保存一份目标，再在start..end整数帧用该固定matrix乘当前帧parentInverseMatrix，经decompose/quatToEuler（按目标rotateOrder）求局部位置/旋转，对所选六轴通道写key。冻结分支沿用非零rotatePivot判据：保存世界pivot与旋转（单位scale），回放平移减静态rotatePivot；不键scale、不恢复scale动画。所有六轴锁定在简单静态scale父级下可保持世界矩阵；部分局部通道不保证完整世界空间锁定或脚底接触不滑，尤其其他轴仍动画/父级转动时。

原冻结采样创建pointMatrixMult/decompose/compose后删除，候选改用与已检查JOP矩阵分支等价的只读API2；复用审阅过的私有matrix/identity/quat-plugin/助手范围支持，实际复制在本候选payload中，无其他待整理目录运行依赖。正式core未改，未来共享下沉需真人验收后决定。

## 参数与返回

`LockToWorldTool.run(dry_run=False, **arguments) -> ToolResult`。

| 参数 | 默认/含义 |
| --- | --- |
| action | lock/open_ui，默认lock |
| objects | 明确唯一非实例transform数组；空用选择 |
| start / end | 整数/null；默认int播放min/max，闭区间逐整数帧，最多10001帧、总样本≤200000 |
| attributes | tx/ty/tz/rx/ry/rz唯一数组，空使用全部六轴 |
| use_channel_box | False；True在真实Maya读取主channelBox所选TR属性，空仍为六轴；与明确attributes互斥 |
| allow_reference_edits | False；True允许引用控制器写键，但已有引用/锁曲线拒绝 |

输出locked完整名、range、attributes、frames。原窗口Start/End点击捕获当前帧和按钮标签，Lock to World按原channelBox掩码；长属性translateX/rotateX等正规化短名。候选明确拒绝子帧按钮值，不像原代码截断写键却以子帧采样，属于记录的行为收紧。UI引用目标需要明确允许；所有场景写回经标准run/Undo。

## 前提、影响与恢复

需要degree/cm和Undo开启。拒绝joint/实例/歧义/组件/重复对象、对象锁；动画/驱动rotatePivot/rotatePivotTranslate/rotateAxis拒绝。额外rotateAxis、rotatePivotTranslate须零，offsetParentMatrix identity且无输入。写入的选中轴锁、非直接animCurve输入/约束/层/表达式、锁或引用曲线、外部共享曲线拒绝；未选轴锁不阻止该轴以外的操作。拒绝复合TR外部驱动、奇异起始/父逆矩阵。复杂父级非均匀/负scale、shear和制作rig需真实动画对比，不能宣称普遍可用。

validate/dry_run只读范围、连接、矩阵、枢轴、可写通道，不改时间/选择/AutoKey/插件、场景或开窗口。矩阵采样getAttr(time)/API2只读，无DG采样助手。执行按需加载matrix/quat节点插件（不使用固定Windows后缀），四个临时回放节点随机私有名、真实身份和外部输出检查，只删除本次助手；对每帧覆盖/新增选中轴key，没有原Euler filter，不改未选曲线。范围外键保留，但邻近插值/切线可能变化。

BaseMayaTool整组Undo。AutoKey临时关闭，finally恢复时间/选择/namespace/AutoKey与清理助手；原catch吞真实错误并提示rotateOrder改为保留实际错误，避免误导和重复删除。失败不自动回滚局部键，先一次Undo再检查。可安全卸载且由本调用新加载的插件才卸载；插件/UI不归普通场景Undo。无外部业务文件写入。

```python
tool.run(dry_run=True, objects=['rig:foot'], start=1, end=24, attributes=['tx', 'ty', 'tz'])
tool.run(objects=['rig:foot'], start=1, end=24, attributes=['tx', 'ty', 'tz'])
```

适用于备份中接脚滑排查或世界空间停留段，之后人工对比脚部接触/膝部IK形态再烘焙/导出。不是IK/FK匹配或骨架重定向，不宣称跨工具组合已实测。注册/面板/Schema复用框架；正式库未挂载。

## 检查与晋级

普通Python检查2资源SHA、全部原函数/UI、Schema与延迟Maya导入。Maya2025隔离mayapy三组：六rotateOrder和动画父级逐帧世界矩阵+Undo；冻结世界pivot锁、多控制器、新目标生成六轴键、只读dry、仅tx掩码且未选ry锁/旋转曲线保持；共享曲线/动画pivot/UI batch/channelBox/private写guard，第二键注入错误后助手清理/AutoKey/时间/Undo。没有实际打开GUI、真实引用业务或脚滑生产rig效果验证，prepared_unverified。按acceptance.md真人确认满意后，才执行promotion.json完整代码/资源/知识/测试/注册/面板晋级。
