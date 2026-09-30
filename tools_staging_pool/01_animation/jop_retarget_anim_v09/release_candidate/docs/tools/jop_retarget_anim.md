# JOP世界矩阵动画回放候选

工具ID `jop_retarget_anim`，分类 animation。来源 Jesse ONG PHO 的 jop_retargetAnim v09；原Python、图标、安装说明/MEL/拖放安装器和许可共6文件按字节保留。许可允许个人/商业使用和修改，禁止向第三方分享或分发；本候选仅供当前用户本地使用。候选不执行安装器，不写shelf、userSetup或偏好目录。完整14函数、3个UI方法和原矩阵/四元数回放算法保留，适配差异见 jop_retarget_anim_changes.diff。

## 用途、输入与输出

先保存控制器世界矩阵，再改变父级空间、整体位置或rotateOrder，最后按保存时的时间点重建六轴平移/旋转关键帧。原工具不是角色骨架映射器，不生成IK/FK匹配、不改变父级关系、不键scale。稀疏模式采样所选对象任意属性键时间的并集；Bake模式按整数start..end逐帧采样。没有插值误差保证，稀疏模式不会保存两键之间的完整轨迹。

`JopRetargetTool.run(dry_run=False, **arguments) -> ToolResult`：

| 参数 | 说明 |
| --- | --- |
| action | capture / retarget / open_ui；默认capture |
| objects | 明确唯一非实例transform数组；capture为空用选择；retarget为空按快照UUID/reference上下文恢复，有值则按records顺序一一映射 |
| bake | capture逐帧采样，默认False；retarget使用已经保存的样本 |
| start / end | 整数/null；capture默认播放min/max取整数，范围最多100001帧、总样本最多200000 |
| snapshot_data | capture返回的format/records对象；retarget必须完整传入，最多1000条记录，有限time与16数matrix |
| allow_reference_edits | 默认False；retarget允许引用控制器本身的明确编辑，但原引用/锁定曲线仍拒绝 |

capture返回 `format=maya_toolkit.jop_retarget_anim.v1`，records每项含object_name、node_uuid、reference_uuid、samples[{time,matrix}]。结构可JSON序列化；本工具没有文件读写API，调用方自行持久化时需自行说明覆盖影响。retarget返回retargeted完整目标名、sample_counts。引用节点的UUID可能与原加载场景相同，必须结合reference node UUID定位，避免写到本地同UUID节点。

## 原业务与边界

普通分支保存完整worldMatrix。冻结分支以非零rotatePivot为判据，保存pivot经worldMatrix变换后的世界点及该矩阵旋转，使用单位scale。原先为了获取该分支会创建pointMatrixMult/decomposeMatrix/composeMatrix再删除；候选用只读API2矩阵/旋转分解计算，隔离Maya已对照原DG构图验证普通旋转/平移和静态pivot等价。该分支仍继承原工具丢弃scale的行为。

回放完整保留 multMatrix(world * parentInverse)、decomposeMatrix、quatToEuler按目标rotateOrder转换、plusMinusAverage减静态pivot、六轴setKeyframe与filterCurve。最终Euler过滤针对整个目标曲线，不局限保存范围，可能影响范围外旋转；原工具没有原始Euler圈数保留保证。目标scale不键，父级非均匀scale/负scale/shear以及生产rig必须实测比较。不得把保存端world matrix直接理解为任何复杂目标层级都可精确还原。

当前degree/cm；唯一transform，不接受joint或实例。动画/驱动rotatePivot及rotatePivotTranslate拒绝。回放目标rotateAxis和rotatePivotTranslate须零、offsetParentMatrix须identity且无输入；不接管这些额外变换。六轴锁/对象锁、外部驱动/约束/层/表达式、引用或锁定动画曲线、共享曲线输出、奇异快照/父逆矩阵拒绝。capture可只读引用/锁对象，但仍受静态pivot限制；引用动画可显式映射回放到本地控制器。无曲线且通道可写的新本地目标允许生成六轴曲线。

validate/dry_run只读取连接、身份、键时间和矩阵，不改时间、选择、AutoKey、插件、场景或打开UI。capture只读时间上下文采样，不建DG辅助节点；只在进程中维护计时/返回数据。retarget由标准Undo chunk分组，AutoKey临时关闭，finally恢复时间/选择/命名空间/AutoKey；矩阵助手使用每次随机私有名称和真实身份，删除前确认没有外部输出。失败不自动撤销已写关键帧，先Undo再检查报错。

需要的矩阵/四元数节点若不存在才加载Maya插件（不再import时加载Windows .mll）。完成后删除自有助手，可安全卸载且由本调用新加载的插件才卸载；插件状态、UI、进程内快照不归普通场景Undo，无法卸载时保留插件。无外部业务文件写入。

## UI、修复与组合

保留Bake复选框、Save Anim、Retarget Anim完整原窗口。Save回调通过标准capture生成快照；Retarget只接受本候选保存的会话缓存，经标准run写键，按UUID处理对象改名；若目标引用，窗口要求明确允许编辑。关闭/重开窗口会清空窗口字段，重启Maya丢失进程缓存；API快照可由调用方保存后重用。私有DG/key写函数要求当前标准运行，不能直接绕过预检使用。

修复原空选择函数引用未定义mySelec；去掉原顶层插件加载；冻结capture改为只读等价计算；补全参数/真实身份/曲线范围/对象保护/助手清理与UI标准桥。其余原采样和回放公式保留，不为统一框架擅自替换算法。复用现有BaseMayaTool、ToolResult和Undo；正式core、注册和工具库未修改。

```python
saved = tool.run(action='capture', objects=['rig:control'], bake=True, start=1, end=24)
if saved.success:
    tool.run(dry_run=True, action='retarget', snapshot_data=saved.data)
    # 在备份里完成用户需要的父级/旋转顺序改动后：
    tool.run(action='retarget', snapshot_data=saved.data)
```

可接用户已验证的空间切换、整体移动、旋转顺序调整步骤，再对比轨迹后导出；跨工具组合尚未真实Maya GUI验收，不能自动宣称可组合。候选不与animation_retarget骨架映射或IK/FK工具互相替代。

## 验证与晋级

普通Python验证延迟Maya导入、Schema/非法快照、6文件SHA、完整native函数/UI。Maya2025隔离mayapy五组验证：六rotateOrder/父级变换矩阵回放+Undo；只读capture/dry；两对象逐帧和冻结API对照原DG；JSON/rename/saveReload/UUID与原UI业务桥/显式新目标；真实引用相同UUID上下文保护；锁/共享/动画pivot/单位/rotateAxis/奇异矩阵保护；第二键故障的助手清理、AutoKey/时间和Undo。没有实际创建GUI，不等于真人直验；其他版本和生产复杂scale/pivot动画仍待acceptance.md验收。prepared_unverified；promotion.json预制完整代码/资源/文档/测试/注册/面板接入，仅人工确认后可晋级。
