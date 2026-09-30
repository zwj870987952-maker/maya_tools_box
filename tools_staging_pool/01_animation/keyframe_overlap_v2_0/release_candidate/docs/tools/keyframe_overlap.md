# KF Overlap粒子延迟候选

工具ID `keyframe_overlap`，animation，来源 Burased Uttha (DEX3D) KeyframeOverlap v2.00 alpha。原6资源（完整脚本、空Init、图标、两个安装器、作者链接）按字节保留；未附独立license，原“Only use on $usr_orig$ machine”与用户检查保留，placeholder仍按原逻辑取当前getpass用户，不伪造他人身份。只本地私有整理，不发布/安装/下载。全部4类31方法及完整六模式算法/UI保留，修改见 keyframe_overlap_changes.diff。

## 业务与使用顺序

Create Overlap：按原控制器动画建follow/origin/result/红色animate定位器，烘焙origin为粒子goal；classic particle goal产生动态延迟并烘焙animate。按照offset平移animate键时间，用aim或point constraint驱动result，烘焙follow，再在播放区间两端补目标键并用result约束控制器。留下分组和定位器供手工调整，创建不是最终纯关键帧动画。

用户可编辑红色animate定位器的直接本地不共享动画曲线；Bake Keyframe再烘焙控制器被本图pairBlend驱动的属性，删除本次自有定位器/约束/pairBlend，按原键时间并集与额外采样优化曲线。原创建模拟范围start-10..end+10，烘焙目标start..end，preserveOutsideKeys=False，因此范围外关键帧有删除风险，必须用备份。优化按线性插值差选重要点，不是误差阈值保真压缩；round时间不保证保留子帧和任意Euler圈数。

原模式：aim_xb/aim_yb/aim_zb分别以X/Y/Z方向延迟点驱动另两轴旋转，distance确定偏移距离，aim_invert反向；pos_xzb/pos_yb/pos_xyzb分别驱动XZ/Y/XYZ位置。创建仍按原position端点补全部tx/ty/tz，具体约束skip控制驱动；未驱动轴不宣称完全没有键影响。dynamic转换goal_weight=`1-(dynamic/5)*.5`；smoothness选择goalSmoothness=3.2/2.7及round(2或1*fps/24)采样，候选最小sampleBy=1修复低fps零采样。模拟品质/间帧效果需要真实制作动画检查。

## API

`KeyframeOverlapTool.run(dry_run=False, **arguments) -> ToolResult`。

| 参数 | 默认与含义 |
| --- | --- |
| action | inventory/create/bake/open_ui，默认inventory |
| objects | create明确transform数组；空用选择。bake按record全部控制器，若明确objects必须完整且同序 |
| record_id | bake需要inventory/create返回的真实owner network UUID |
| mode_name | 上述六模式，默认aim_xb；bake使用已经存在图的实际通道 |
| distance / dynamic / offset | 3 / 3 / 0；有限值，.001..500 / 0..6 / -10..10 |
| smoothness / aim_invert | True / False，必须bool |
| start / end | 整数/null，默认round播放min/max；至少两帧，跨度≤10000，总对象模拟采样预算≤100000 |

inventory返回records（record_id/prefix/control_count/mode_name/start/end/state）；create返回record_id/controls/editable_group/mode_name；bake返回baked/range/removed_record_id。候选category/Schema可由框架导出，show_ui保留原模式按钮、distance/dynamic/offset滑块和数值框、Smooth、六模式、invert、预设、创建/烘焙、dock布局。UI Bake需选中完整单组控制器，不能部分删除整组图。

## 保护与操作影响

degree/cm；唯一非实例本地transform、带shape供原尺寸计算、六轴可写且Undo开启、停止播放。创建拒绝已有自有Overlap、引用/对象锁/通道锁/外部约束/层/表达式/共享曲线，不按同名前缀接管或删用户节点。新图每次随机前缀；owner network用controls/members消息和每节点mtbKfoOwner绑定，控制器/helper改名及保存重载按身份继续。外部后代、外部输出、外部输入/锁定或引用曲线拒绝；只接受直接本地不共享曲线对本图helper的手工编辑。半成品state=working失败需先Undo，不能自动按完整图烘焙。

所有场景写入经BaseMayaTool的Undo chunk。原按kfo*、固定组名、控制器同名helper及已有约束的删除，只对已验证本次所有权范围执行；不force覆盖控制器输入。Maya原约束自动产生的pairBlend与曲线记录为本图的一部分；目标外部曲线从不当作前缀垃圾删除。助手与后代删除前检查身份和外部使用者。

validate/dry_run只读参数/图/曲线/时间范围/场景状态，不创建粒子或locator、不改时间/选择/evaluation/refresh/AutoKey、不联网、不读写配置、不弹窗。执行暂关AutoKey、root namespace、evaluation off，finally恢复AutoKey、时间/选择/namespace/evaluation/refresh悬停状态。失败保留自有记录帮助追溯并由Undo撤销部分动作，不自动清理可能有依赖的整图。模拟/bake会推动全场景求值，其他动力学缓存可能受影响，普通Maya Undo不保证恢复所有外部缓存；隔离备份执行。

## 明确适配与修复

原初始化support会下载GitHub代码并exec、安装器同样exec下载代码；原件归档，候选不调用这些流程。原UI用户身份限制保留。自动写脚本旁cfg、APPDATA/kfo_usr、presets/文件改为会话内配置；原Save/Rename/Delete/Load完整预设流程仍可用，明确不覆盖重名预设，关闭重建窗口或重启丢失会话预设。本候选没有外部文件写入业务；此持久化变化需用户验收。

原loc_delay_system构造器刷新/切namespace/删前缀改由标准执行范围管理，UI构造不改场景。完整原方法保留，纯业务UI桥共用API；原两端键、particle goal、约束、bake/optimizer公式保留。原bake两处keyframe查询未定义at，已删无效关键字（查询对象本来就是明确plug）；优化cutKey/keyframe原用range长度索引而非实际帧号，改为实际帧数组，帧10..16实测得到10/13/16；position offset原传x/y/z非有效translate属性，改tx/ty/tz。最低粒子bake采样为1。

```python
preview = tool.run(dry_run=True, action='create', objects=['control'], mode_name='aim_xb', start=1, end=24)
created = tool.run(action='create', objects=['control'], mode_name='aim_xb', start=1, end=24)
if created.success:
    # 在备份中编辑editable_group内红色定位器，比较视窗结果后再烘焙：
    tool.run(action='bake', record_id=created.data['record_id'], start=1, end=24)
```

复用现有BaseMayaTool/ToolResult/Undo，不修改正式core/工具/注册。可接纯关键帧控制器动画，在满意的动力学和定位器编辑结果后烘焙导出；与动画平滑/retarget组合尚未真人验证，不能据静态依赖声称已组合通过。

## 证据与转正

普通Python核对6原资源SHA、4类完整31方法/UI、Schema/非法参数/延迟Maya导入和无open/urlopen/exec运行调用。Maya2025隔离mayapy四组覆盖真实六模式粒子创建/约束/烘焙、红locator直接编辑、非零帧索引稀疏优化、创建Undo/Redo/烘焙Undo、同kfo前缀用户物体保留、rename-saveReload、只读dry、共享曲线/锁/外部约束/外部后代拒绝、注入bake失败的AutoKey/evaluation/refresh/Undo恢复。没有真实GUI、没有跨版本或制作rig的动力学视觉效果验证。prepared_unverified；acceptance.md人工满意后才可按promotion.json执行完整搬迁/注册/面板接入。
