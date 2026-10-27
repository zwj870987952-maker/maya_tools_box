# KF Auto Rig IK/FK匹配候选

ID `kf_animrig_ikfk`，animation，原作者 Kiel Figgins，版本3.02（2019-08-14）。原MEL与三张说明图片按字节保留；未附独立许可，仅当前用户本地私有整理、不发布。完整七个原过程、UI/说明窗口与手臂/普通腿/狗腿/高级样条算法保留在native.mel，过程与窗口名私有化，差异见kf_animrig_ikfk_changes.diff。

这是专用KF Auto Rig匹配器，要求作者rig的准确命名/属性/引用结构。不能把任意同名骨架当成兼容rig；不改pinner/IKFK切换属性。`matchIKtoFK` 表示把IK控制器匹配到FK姿态，`matchFKtoIK`相反；API保持原命名语义，避免“转换至FK/IK”的误解。

## 完整业务

手臂IK匹配：世界pivot/旋转从FK Wrist转给Hand，临时分组与point/parent constraints按原双倍局部X公式计算ElbowPole，原rotateAxisX=-180右手补偿保留。普通腿同样匹配Foot/KneePole，从FK Toe复制toeXYZ并重置脚掌/踝/鞋跟等控制属性。狗腿额外两个极向量、独立IK控制器、可选Foot_IKFK_Match、shinRoll/limb长度分支保留。

FK匹配：复制FK控制器的parent-only临时对象，将复制体对齐IK链并读局部旋转写回；按原rig MD的input1X和当前IK骨段长度计算stretch，乘数2/3.333保留。普通脚复制toe关节旋转。狗腿按原五段临时parent constraints匹配。高级样条IK按FK控制器世界pivot重建/重采样临时曲线来移动cluster；样条FK重置allRot/allLength/scale后逐控制器约束到原rig_IK节点。算法不保证长转圈、所有scale/层级/极点姿态下无跳变，原资产必须真人验证。

## 接口与保护

`KFAnimRigTool.run(dry_run=False, **arguments) -> ToolResult`。

| 参数 | 默认与含义 |
| --- | --- |
| action | inspect / match_ik_to_fk / match_fk_to_ik / bake_ik_to_fk / bake_fk_to_ik / spline_ik_to_fk / spline_fk_to_ik / open_ui，默认inspect |
| control | 明确唯一命名空间短名CTRL_*_Hand/Foot或CTRL_*_Pinner；空读唯一选择；不接受DAG路径、组件、引号或MEL语法 |
| start / end | 整数/null，bake默认整数播放范围，闭区间逐整数帧，最多10001帧 |
| allow_reference_edits | 默认False；必须明确True才允许匹配/烘焙引用rig；UI点击操作也明确确认 |

inspect输出control/namespace/limb/referenced/requires_original_kf_rig/switches_pinner；匹配输出matched/procedure/targets/frame_count/switches_pinner=False。inspect只读，可对本地同名对象检查类型信息，不等于兼容性通过；写动作要求引用KF rig、degree/cm、Undo开启、播放停止，以及所需读节点和写控制器均属于同一实际reference node。目标通道/属性缺失、对象/通道锁、非直接animCurve输入/层/约束、引用/锁曲线或共享外部曲线拒绝。FK原MD长度来源为零/缺失拒绝。安全准入比原逐轴忽略锁更严格，不擅自解锁原控制器。

原七过程及UI与说明文字完整保留。私有写过程直接被UI调用时先转标准API；运行内才允许原业务。setAttr/move/rotate/xform/关键目标constraints加实际身份/目标属性范围检查；delete改为只允许此次新建助手及其新建后代，保护已有场景与外部使用者。parent-only duplicate/原临时组不按名字删除；场景里同名group或其他rig内容不接管。辅助图finally清理，新的目标动画曲线/自动Maya blend不冒险当垃圾删；制作狗腿或样条需检查残留驱动，不满意先Undo。

validate/dry_run只读命名、引用、范围、依赖、连接/属性，不加载MEL过程、创建/删除节点、改时间/选择/AutoKey、写键或弹窗。执行加载候选包自带native.mel，仅定义私有过程，无外部source/install/下载。过程定义/UI不归场景Undo。

标准BaseMayaTool整次Undo；单帧匹配暂关AutoKey，不自动键目标，已有动画通道的值可能仅在当前帧暂态，用户自行选择键控。烘焙使用Python明确start..end循环调用原匹配，并对预检目标属性显式setKeyframe；替代原依赖已有键的AutoKey loop，补全未键目标通道，属于明确行为变化。保留范围外键但插值/Euler方向/引用编辑的生产影响待实测。原UI popup timeline转同一标准bake，原带错误参数Ten(0)回调改为无参数。不会设置pinner；用户按原说明在备份中选择正确源姿态/显示模式。

finally恢复当前时间、选择、namespace和AutoKey，清理新助手。失败不自动撤销局部目标写入，先一次Undo再检查，不能把返回success理解为生产rig满意。无外部业务文件读写；加载自带MEL仅程序读取。

```python
tool.run(action='inspect', control='char:CTRL_L_Hand')
tool.run(dry_run=True, action='match_ik_to_fk', control='char:CTRL_L_Hand', allow_reference_edits=True)
tool.run(action='bake_ik_to_fk', control='char:CTRL_L_Hand', start=1, end=24, allow_reference_edits=True)
```

可接KF作者rig的手动pinner切换、姿态核对、烘焙导出步骤；不能替代Universal IK FK或通用骨架retarget。与其他工具组合尚未真人验收。复用既有BaseMayaTool/ToolResult/Undo，正式core/注册/库不改。

## 验证限制与晋级

普通Python核对4资源SHA、完整七过程/关键分支/私有guard、Schema和延迟Maya导入。Maya2025隔离mayapy编译全部MEL定义；临时构建引用手臂fixture验证原Hand世界位置/旋转匹配、原Pole公式、引用编辑/dry、逐帧1/2/3显式键、Undo及AutoKey/时间/选择/助手清理，注入助手属性故障后finally/Undo。fixture不是作者真实rig，不将普通腿、狗腿、反向FK stretch或高级样条记为运行通过；完整分支源码已备但仍需原资产和真实GUI直验。prepared_unverified；acceptance.md通过后才可执行预制promotion.json完整代码/MEL/资源/文档/测试/注册/面板晋级。
