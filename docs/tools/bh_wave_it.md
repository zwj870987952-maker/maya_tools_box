# bh_waveIt 波浪造型候选

`bh_wave_it` / `animation` / `WaveItTool` / 1.09-adapter。prepared_unverified，真实 Maya GUI not_run。原十个 MEL 过程、compact/advanced 原生窗口、四 S/C 按钮、六轴开关、Channel Box、Interactive 与四滑条均保留，另加四个 typed 参数 reader/setter。两处顶层开窗移除，原完整 MEL、图标与附带说明按 SHA 归档；未找到独立再分发授权，仅本地私有准备，不执行安装、Shelf 或发布。

## 契约与参数

候选加载见 acceptance.md，未来真人验收晋级后通过 `maya_toolkit.execute_tool('bh_wave_it', arguments, dry_run)` 注册调用。当前正式库没有本工具。沿用 BaseMayaTool/ToolResult/UndoChunk 与现有注册面板，不新增 core，也不借用正式 Euler/filter 工具替代原造型算法。

| 参数 | 默认/范围 | 含义 |
|---|---|---|
| action | inventory | inventory/open_ui/wave/basic_s/inverse_s/basic_c/inverse_c/invert/base_offset |
| objects | [] | 有序、明确 transform/joint 名数组，空时读取当前选择的观察顺序 |
| rotate_axes | [X] | 写入旋转 X/Y/Z |
| translate_axes | [] | 写入位移 X/Y/Z |
| custom_attributes | [] | 所有对象上存在的数值标量属性名，API 显式传入，不查询 Channel Box |
| amplitude | .15，0..1 | 原 Size |
| frequency | 1，-1..1 | 原 Frequency |
| phase | 0，-10..10 | 原 Offset |
| base_offset | 0，-180..180 | 原 Rotate Base Offset |

严格拒绝未知参数、布尔冒充数值、非有限数、重复名、组件/通配符、歧义、引用/锁定节点、缺失/非数值/不可写属性、非 animCurve 外部驱动。base_offset 仅验证/写首对象旋转通道，其他给定对象仍要求明确非引用/非锁；此动作忽略位移和 custom_attributes，rotate_axes 为空则拒绝。API 支持 long/short/byte/bool/enum 等标量，实际 setAttr 可能强制转换或拒绝越界值，输出实际 after；不要按浮点计算值假定所有属性保持同一值。

## 原算法和 UI 行为

对 n 个对象，第 i 个（从 0 开始）的计算值为：

```python
degrees(sin(((i + 1 + phase) * (6.28 / n)) * frequency) * amplitude)
```

第一个对象再减 base_offset；wave 把结果覆盖每个启用的旋转、位移和自定义属性。保留原 6.28，而非改成 2*pi；保留 MEL rad_to_deg 数值。写 local 属性值，不处理 world space，不是增量，也不自动创建波浪动画。角度数值也写入位移/自定义属性；当前 Maya 单位及属性强制转换决定含义，没有额外单位换算。显式 objects 顺序与场景选中列表排序无关；改变顺序会改变形状/第一个对象。

- basic_s/inverse_s 把 frequency 设为 ±1、phase=0；basic_c/inverse_c 设为 ±.5、phase=0。保留 amplitude/base_offset，执行同一 wave。
- invert 将传入 frequency 取负，保留 phase。原隐藏 invertFields 过程仍归档在 suite，API 使用相同有效参数；原窗口没有新增该按钮。
- base_offset 单独把第一个对象启用旋转轴覆盖为 -base_offset，其他对象/位移/custom 不改；并不是 wave 的完整重算。
- 原 Interactive 默认关闭；Size/Frequency/Offset 拖动或释放只有开启后才调用 wave。四预设始终执行；Rotate Base Offset 滑条始终执行首对象 base_offset，与 Interactive 无关。
- 标准按钮/滑条回调读取原 UI 和 Channel Box，调用 run；成功后同步有效 frequency/phase。compact/advanced 切换保持原 190 宽、130/300 高。

## 影响、输出与组合

validate/dry_run 查询通道、顺序、计算写入预览，返回 operations，不加载 MEL、不改 UI/选择/时间/Undo。执行不改实际选中对象来决定顺序，MEL 使用显式有序对象数组。场景调用一个 UndoChunk，finally 恢复时间/组件选择并关闭内部 guard；无外部文件写入、节点创建、播放范围/偏好/evaluation 修改。发生部分写入错误不自动回滚，检查后 Undo。Interactive 每次回调单独归组，不保证整个拖动只占一次 Undo。

inventory 返回来源/资源/过程审计；open_ui 返回 source/procedures/window；其他操作返回 action、ordered_objects、operations（plug/before/computed_value/实际 after）、effective_frequency、effective_phase。computed_value 是读预检的浮点目标，after 记录执行时值，不能当作持久动画键证据。

原算法不显式 setKeyframe；animCurve 通道可写但 autoKey 关闭时旧键不变，切时间后旧曲线值恢复。autoKey 开启、动画层/约束/复杂 blend 不宣称通过；非 animCurve 驱动预检拒绝。推荐用于副本 joint/控制器的有序静态波浪造型，再人工确认姿态并打键/后续工具处理。可与后续动画烘焙组合的输入是明确通道和对象，未实测跨工具生产流程，不声称已有正式动画生成能力。

## 验证与演进

普通 Python 四项通过：三资源哈希/十原过程+十四运行过程/无顶层副作用，严格参数/预设，Schema 与无 Maya inventory，原公式/首对象偏移。Maya2025 隔离八项通过：编译/来源/guard、真实多轴/自定义通道/有序数组/组件选择/Undo，四预设/invert/base_offset，dry_run/锁/驱动、同叶名与实际 reference 拒绝，MEL 故障恢复，以及 autoKey 关闭键不变。早期严格浮点相等 fixture 对角度内部转换误报，改为近似比较后通过；没有据此修改原算法。

原 native GUI、Interactive 鼠标拖动、真实 Channel Box、非默认单位、整数/枚举属性、其他 Maya 版本和制作 rig 未验收。晋级描述准备完整代码/资源/知识/两测试与注册合并；真实哈希匹配的人验记录后再 apply，当前只在 tools_staging_pool。
