# EB Labs Whiskey Pro 候选知识说明

工具 ID `eblabs_whiskey`，分类 `animation`，原包版本 1.5.4。Eric Bates / EB Labs 版权所有；本候选只用于用户已有副本的私有本地整理，没有独立再分发授权，不公开发布。所有 133 个原始代码、图像、字体、偏好、版本/数据资源逐文件保留并记录 SHA256；完整 `WhiskeyPro.py` 的 22 类、272 方法、全部窗口/widget/slider/曲线工具保留为 `native.py`。Hub、UX、安装器与版本封装仅归档，不执行，不修改原许可管理器。源文件原本注释掉的许可调用保持源行为；此处不对授权状态作推断。

## 用途、输入与输出

补间/自动补间、世界空间补间、快照与命名空间匹配、沿相机方向 In/Out、Pose Pusher、Multiply、彩色关键帧、匹配关键帧、子帧清理、常量/平直区域清理、Smash Bake 和切线设置。面板保留原生 `maya.cmds` 窗口、全部 widget/slider、固定选择、倍率、配置及 profile 工作流。实例由候选私有窗口名 `mtbWK_whisKEY_Pro` 打开，不使用缺失的混合编译 `PackageData`，而是读取随包 JSON 元数据。

标准调用 `WhiskeyTool.run(dry_run=False, **arguments)` 返回 `ToolResult`。`inventory` 只读返回完整类/方法/资源目录；`open_ui` 需要真实 Maya GUI。场景动作包括 `inbetween`、`slider`、`capture_snapshot`、`set_keys`、`rekey`、`clean_subframes`、`remove_boring`、`smash_bake`、`set_tangent`。`objects` 为空使用当前选择，明确列表须唯一的本地可写 transform/joint；`attributes` 空数组使用原算法的可用通道，明确通道支持长短名。部分原算法会按整个对象或 shape 扩展范围，见下文。结果含 `objects`、`native_result`、`collected_data`、`errors`、`warnings`；采集不到有效通道会警告，不能当作成功修改的证据。

`slider_kind` 为 `tween/snapshot/worldSpace/inOut/PosePusher/multiply`；`value` 为 -1..1 有限数值，`use_set_value` 使用原时间比例对应值，`from_current_value` 从当前值朝前/后端点移动。快照使用 `capture_snapshot` 的 `native_result` 原结构传入 `snapshot_data`。API In/Out 必须提供明确 `camera`，GUI 仍使用原活动视图相机；相机只读。`use_all_layers=False` 仅 Tween 使用原动画曲线层分支；其余 slider 保留合成值算法，Multiply 原先调用不存在的方法已修正为标准分支。API 倍率为 1，GUI 保留完整倍率编辑。API 不使用时间轴高亮范围，GUI 保留原高亮行为。

`set_keys` 支持 `special` 彩色刻度。`rekey` 支持 `match_last`，最后对象作为时间模板，其他对象按模板重新打键并删除不在模板上的键；原实现 match-last 或未选 ChannelBox 时对整个对象打键/删键。`clean_subframes` 原本遍历全部连接动画及 shape，不以 `attributes` 限定，取整公式是 `int(float(t)+0.5)`，负时间也保留该原语义。`remove_boring` 的 `leave_first` 决定整条常量曲线留下首键还是清空，平直片段按原规则删中间键并修改边界切线。原 `regions` 未起作用，不对外承诺范围清理。

`smash_bake` 在整数 `start..end`（包含两端，默认动画播放范围）逐帧采样全部未锁定 keyable scalar 通道，然后断开原输入并生成逐帧关键帧、移除相关层属性。它不受 `attributes` 限制；复制场景再使用。允许原约束等驱动作为采样输入，但拒绝失败后用 `delete(inputConnectionsAndNodes=True)` 销毁上游图的原兜底行为。并不删除共享约束节点或清理整个制作图。

## 影响、保护与明确差异

`validate` 与 `dry_run` 只读检查参数、唯一节点、引用/锁定、通道驱动、曲线共享输出及文件覆盖，不创建窗口、关 Undo、改选择/时间/偏好或写文件。写入期间再次检查 UUID 范围，跨对象共享动画曲线、引用/锁定节点和超出预检范围的写入被拒绝。此保护比较保守，复杂 character/自定义驱动不保证兼容。快照的命名空间重映射如试图写未选对象会失败，不能默许扩大作用域。

场景动作及原生 UI 的直接写入方法通过标准框架 Undo 分组；原 `suspendUI` 关闭 Undo、隐藏主面板/改变隔离的做法取消。原跨拖拽事件保持打开的 Undo chunk 改为每次标准回调一个 chunk，拖拽撤销次数会改变。临时 `native_callback` ticket 只供已注册 Python 回调使用，不能传代码字符串。时间、选择、namespace、AutoKey 和既有层 selected/preferred 标志在 finally 恢复；未改变时间时不强制重新求值，以保留 AutoKey 关闭情况下的原 setAttr 临时姿势。API AutoKey 原本开启时对采集到的通道补键，关闭时保留原暂态姿势，改变时间后仍由原动画驱动。失败不会自动回滚已完成写入，返回错误后先 Undo，再检查场景。

原公式和 API2 矩阵分解保持完整。明确修复：包围盒 classmethod 补 `cls`；Multiply 缺失层回调改为标准合成值分支；Tween 层采集跳过没有曲线的通道；Maya 2025 禁止直接 setAttr 动画曲线 keyValue，改为 `keyframe(edit=True,index=...,valueChange=...)` 写入相同计算值。收集阶段原本只打印/吞掉的业务异常现在进入失败结果；其他原可选数据/偏好探测的宽松异常保留。完整原文件/生成差异见 `eblabs_whiskey_changes.diff`。

`set_tangent` 保留原按钮同时更改全局默认切线/weightedTangents 的行为，全局偏好不能保证由 Maya Undo 恢复，用户需记录原值。UI 创建、会话配置和外部 JSON 文件不属于场景 Undo。

偏好在会话内保留，启动只读取随包默认 preset；不写原 Maya 全局 `scripts/eblabs_prefs`。`export_preferences` / `import_preferences` 使用绝对 `.json` 路径显式持久化；已存在文件须 `overwrite_file=True` 才可覆盖，非覆盖写入使用独占创建以防竞争。创建目录/写文件无法由 Maya Undo 撤回。导入后重新打开面板使用新 profile；关闭 Maya 后未导出的会话偏好会丢失。

## 示例与组合

```python
tool.run(dry_run=True, action='slider', objects=['rig:hand_CTL'], attributes=['tx'], value=0.5)
tool.run(action='slider', objects=['rig:hand_CTL'], attributes=['tx'], slider_kind='worldSpace', value=0)
snapshot = tool.run(action='capture_snapshot', objects=['rig:hand_CTL']).data['native_result']
tool.run(action='slider', objects=['rig:hand_CTL'], slider_kind='snapshot', snapshot_data=snapshot, value=1)
tool.run(action='export_preferences', file_path=r'E:\temporary\whiskey.json')
```

输入为动画控制对象，输出为姿势/曲线修改或 JSON 快照，可在备份中接动画平滑、镜像或导出工具。这里只记录输入输出衔接，不代表跨工具组合已实测。只复用现有框架、Undo 与协议，未改生产 core 或正式注册。

## 检查与晋级

静态 AST、完整原资源字节校验、标准 Schema、无 Maya 延迟导入、临时正式布局注册检查，以及 Maya 2025 隔离 mayapy 业务/Undo 检查。真实 GUI、拖拽/固定选择/profile、生产 rig、不同旋转顺序/单位、复杂动画层/character、自定义约束尚待逐项验收。`promotion.json` 预制完整正式目录、知识说明、测试和 `ALL_TOOL_CLASSES` 注册动作；真人通过 `acceptance.md` 后才允许晋级。当前不会迁移或修改正式库。
