# Directional Cycle Tool v1.1 候选

用途：从已有前进循环生成 Left/Right/Back，保留 Baptiste COLIN (FallingNT0) 原八函数、完整 Dockable 窗口及校正/反旋转流程。原五文件逐字节保存在 upstream；原 README 的 CC BY-SA 4.0 许可与署名随包保留，修改分发需遵循该许可。原“任意 rig”宣传未经本项目验证。

## 调用与输入

工具 ID `directional_cycle_tool_v1_1`，category `animation`，统一 `run(dry_run=False, **kwargs)` / execute_tool，输出 ToolResult。`inventory` 离线读取 catalog；`open_ui` 只在真实 Maya GUI；`run` 写场景；`cleanup` 按明确 record UUID 清理。Schema 是类 parameters_schema。

`controllers` 必须有序且唯一：Master，feet_number 个 Feet，MainBody，Upperbody，Head，共 feet_number+4；允许唯一完整 DAG 路径/namespace，拒绝组件/通配符/引用/锁定/外部驱动。建议使用 Master 为其余角色父级的备份循环场景。`feet_number` 1..999，`angle` 0..90，`direction` left/right/back；`start/end` 默认播放区间，允许有限小数，start<end、跨度≤100000。Maya Undo 必须开启。有层时先手动选 BaseAnimation；预检不改变层选择。未清理的 live/failed 记录与控制器重叠时拒绝新周期。

`bake=True` 默认，原循环逐帧烘焙并保留方向层，删除自建约束/定位器；False 保留 live 辅助供编辑，须 cleanup 后重新运行。`correction_locators=True` 与原 UI 相同；`counter_rotation=False` 默认，仅左右方向有效；back 忽略 angle/counter_rotation，原 master/upperbody 角色未直接参与后退。

```python
result = tool.run(action='run', direction='left', controllers=ordered_controls,
                  feet_number=2, angle=45, start=1, end=24,
                  bake=False, correction_locators=True, counter_rotation=True)
record_id = result.data['record_uuid']
tool.run(action='cleanup', record_id=record_id, remove_layers=False)
```

## 原算法与场景影响

左右：脚 world 采样到 locator，删除全部临时采样约束；master locator 世界 Y 旋转 ±angle，脚组世界 Y 旋转 ±90；用 pointConstraint 驱动脚，head aimConstraint 保持初始偏移。back：脚 world 采样，所有关键帧以首尾中点 timeScale=-1；parentConstraint 驱动脚，Back_Pelvis 为主身体 TY 写 currentTY-10，RX 写 currentRX*-1。这是原层公式，不代表最终世界 TY 必定降低 10。头 aim locator 原点起步再世界相对移动 (0,100,500)，没有自动跟随角色朝向。

原校正：先 bake feet、建立每足 correction/temp motion/temp position、校正 Y=2、shape localScaleXYZ=30、回 bake，删除临时节点。CounterRotation 计算 FeetAngle-MainRotation，转临时旋转定位器后 match 校正位置。保留原算法；非均匀缩放、长旋转、jointOrient、复杂 rig、循环 seam、脚接地/滑移均需人工检查。

左右烘焙整个有序选择，back 烘焙 Feet+MainBody+Head（含 start-1 起帧）；Maya bakeResults 默认整对象可打键属性及相关 shape 属性可能被写入，包含自定义通道/visibility，非仅六 TR；原作用域保留，预检检查这些通道的锁/驱动。已有层、其他 active/preferred layer、自动键/缓存/求解器可能影响结果；BaseAnimation 被选中不等于隔离其他 active 层，用户应在备份中检查混合/静音。复杂已有驱动结构可能被保护性清理拒绝，返回 failed 并保留可追踪记录，需 Undo。

自建 layer/helper/shape/constraint/animCurve/aux 使用 token+Owner/Role 和真实 UUID；network 记录 controller message，保存重载与重命名后可清理。方向层/Back_Pelvis 全部生成唯一名字，不覆盖旧 Left/Right/Back/Back_Pelvis，模板固定名称不能误删除外部对象。原只删第一组临时约束改为删完整嵌套列表；校正 shape 使用真实路径，不拼 Shape 名。

cleanup 只删本周期 helper/constraint，先移约束到世界再删，保护空控制器；默认保留方向/骨盆层、network 来源记录与可能携带旧动画的 blend/aux。`remove_layers=True` 明确删除本周期 owned 层及该层动画，外部子节点/输出/新增层属性或子层会拒绝。cleanup 不承诺恢复原动画姿态；完整恢复用 Undo 或原备份。失败可能部分写入，无自动回滚；检查 ToolResult.errors，立即 Undo 可撤销一次标准工具 chunk。

finally 恢复时间、原选择、原有层 selected/preferred 标记与内部 guard；不切播放区间/不 suspend refresh/不改 OGS，不写外部文件（Maya 测试仅临时保存）。没有源 import-time GUI、GUI 警告弹窗或自动基础层切换。Dockable 原窗口参数/角色保存/三个方向按钮通过标准 API，足数变化后重新检查当前计数；本工具复用 core.ui_base Qt/Maya 主窗绑定及标准 Undo/结果，不新增未直验的 core 算法。

## 输出、组合及验证

结果含 record_uuid、direction、state、各类存活资源与 warnings；cleanup 返回保留层/辅助。只支持基于明确角色的循环转换，可在干净备份先完成 Copy Animation/滤波后的实际前进循环再调用；无真实 Maya 组合验收，静态同 category/import 不构成可组合证明。未烘焙 helpers 必须先由本工具清理，避免交给其他工具当原始控制器处理。

普通 Python 3 项检查、Maya2025 隔离 7 项及临时正式布局注册/面板/Schema 检查通过。实际验证左右 ±90 脚轨迹、后退 timeScale=-1、三足 correction/counter-rotation 路径、两个 back 层、完整清理、外部命名/后代保护、重命名及保存重载、只读预检、失败 finally/Undo。未构造 Qt 或连接制作角色；prepared_unverified，真实 GUI、运动效果与其他 Maya/Python 版本待用户验收，不能转正。
