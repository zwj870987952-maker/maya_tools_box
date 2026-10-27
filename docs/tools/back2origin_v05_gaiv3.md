# Back2Origin v0.5 增强版候选说明

将 root 的 X/Z 动量转到可选 global，再重采样 IK、Pole Vector 和道具控制器；也支持从 global 返回 root。完整原八个帮助算法、反向循环和原生窗口均保留；导入不再复制脚本、开窗或写默认 Maya scripts 目录。当前仅候选，真实 Maya GUI 验收后才能转正。

## 接口、参数和结果

Back2OriginTool 继承 BaseMayaTool，tool_id=back2origin_v05_gaiv3，category=animation，version=0.5.1-adapter。实现 validate/execute，外部使用 run(dry_run=...)，返回 ToolResult；to_openai_tool/to_mcp_tool 导出 Schema，晋级后 maya_toolkit.execute_tool 可统一调度。

| 参数 | 含义 |
|---|---|
| action | convert（默认）、reverse、discover、inventory、open_ui |
| root_control | 明确 transform/joint 名称，convert/reverse 必需 |
| global_control | convert 可省略：只归零/重采样、不保存动量；reverse 必需 |
| ik_controls / pv_controls / other_controls | 明确对象名数组，默认空；不同角色不允许重复对象 |
| channels | 非空、不重复的 X/Z 数组，默认 [Z]；没有 Y 模式 |
| start / end | 同时提供整数、start≤end；省略使用播放范围 int(min/max)，保留原整数边界 |
| frame_step | 正整数，默认1；先逐整数帧采样和打键，再删除内部 frame % step != 0 的平移键 |
| namespace | discover 使用，None 查全部、空字符串查根、其他字符串查该命名空间，支持嵌套命名空间 |

convert/reverse 输出 objects、range、sampled_frames、frame_step 和 warnings。discover 返回 matches（各角色的长路径数组）、namespaces、ambiguous；不默认把多个 root/global 中第一项当成正确对象。inventory 返回原文件校验、完整函数目录和行为记录。open_ui 返回原生窗口名，需要真实 GUI。

## 原坐标约定和算法

正向先记录 IK/PV/其他控制器相对 root 的**世界位置差**，采样 root 的世界 X/Z；逐帧将 root 所选**局部**通道归零，按新的 root 世界位置加原相对差重写其他控制器的世界平移；最后把所存 root 世界数值写到 global 的**局部**X/Z通道。global 既有值会被覆盖，不是相加。其他控制器写 translateXYZ；原帮助提示它们需按预期归属 root 或相应约束组。

反向先采样 global 局部 X/Z 和其他控制器当前世界位置；用 global 数值**替换** root 对应局部值、将 global 对应值归零，再恢复其他控制器世界位置并打 XYZ 键。它不会把 root 已有值与 global 相加，也不是任何父级条件下正向算法的数学逆运算。候选保留原约定，不据此承诺通用世界空间/引擎根运动正确性。非零 global、旋转/缩放父级、jointOrient、道具归属及生产绑定需要副本实测。

frame_step 不是只每隔 N 帧采样：仍每帧采样，再按绝对帧号取模删内部键，首尾保留；不是相对 start 的步长。cutKey 使用 translate，因此 step>1 时可能删 root/global **未选轴**的既有平移键；IK/PV/其他也是三个轴。范围外键不主动删除。没有额外 bakeResults/filterCurve，不修改旋转或缩放。

## 预检与影响

严格类型/范围检查；对象必须唯一存在且是 transform/joint，拒绝组件和通配符。所有写入对象拒绝引用或节点锁定，相关平移通道拒绝锁定/非 animCurve 驱动（动画层、约束、表达式等应先准备副本）。普通 animCurve 可覆盖、补键；step>1 按可能被删除的全部平移轴检查。Undo 必须开启。这是明确边界的准入检查，不全面验证绑定拓扑或坐标语义。

validate/dry_run 不修改选择、时间、曲线、节点、播放范围、评估/刷新或 UI，不导入原生窗口、不复制文件。场景操作沿用 core/framework UndoChunk，每次转换/反向是一组 Undo。执行临时 evaluation=off、refresh suspend，finally 恢复原评估、刷新、时间、仍存在的选择/组件和四个播放范围值；显式 start/end 不再遗留原脚本的播放范围修改。失败可能留下部分键，框架不会自动回滚，用户可 Maya Undo 撤回。

业务动作没有外部文件写入。原 save_script_to_maya_default 的硬编码用户路径复制已禁用，原件仍完整归档。原 Help/About/Contact/网站按钮保留，网站仅用户点击时打开。窗口及控件使用 mtbB2O_ 前缀；字符串命令变为模块内 callable，原 native callbacks 支持额外回调参数。发现控制器匹配叶名称而非不明确短名，字段在 namespace 切换时清空旧值，root/global 有歧义时不自动选第一项。

## 示例与衔接

```python
tool.run(action='discover', namespace='character')
args = dict(root_control='character:RootX_M', global_control='character:Main',
            ik_controls=['character:IKLeg_R', 'character:IKLeg_L'], channels=['X','Z'], start=1, end=120)
tool.run(dry_run=True, **args)
tool.run(**args)
tool.run(action='reverse', **args)
```

可在清楚控制器归属和父级的副本上使用，再由动画滤波/导出工具处理输出曲线；需要核对步长删键、动画层、引擎轴向和根节点规则。接口衔接不等于已验证的跨工具或 Unity/Unreal 组合。

## 验证、来源和晋级

原单文件36函数按字节保留 upstream。八个帮助函数的 AST 与原件一致；反向保存原循环，仅移除 UI 参数读取并从 args 接受 frame_step。适配的行为变更为导入副作用移除、独立 UI 名称/模块回调、参数预检、标准 Undo、runtime finally、发现歧义和陈旧字段保护。native_ui 与原文件变化附 back2origin_changes.diff，算法保存在 algorithms.py/reverse.py。

普通 Python五项检查通过；Maya2025隔离十项实际节点检查通过，包括正向/反向逐帧值与世界位置、单次 Undo、未选轴删键、范围外键保持、缺省范围/无global、预检驱动/锁定/引用、嵌套命名空间和异常恢复。检查不创建窗口，不验证真实复杂rig/其他版本/游戏引擎结果。首次 Undo fixture 在工具后用 currentTime 采样，给 Undo 队列增加其他动作而失败；修正为只读 worldMatrix/time 查询后通过，未将首次失败记为通过。

完整包、原文件、专项文档、两个测试和注册准备在 promotion.json；临时正式布局验证 ToolRegistry 与面板入口。真人步骤见根 acceptance.md，晋级必须匹配当前候选哈希和实测记录。源码没有独立再分发许可，按本地来源保留，不宣称公开授权。Git -text 属性保持原件及候选哈希跨检出一致。
