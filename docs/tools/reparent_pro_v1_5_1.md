# ReParent Pro 1.5.1 候选知识说明

用途：将控制器运动烘焙到辅助 locator，再约束原控制器；支持静态 Pin、手动 pivot、相对末选控制器、Freeze main、三控制器 FK 转 IK 及 Local。完整原 MEL 13 个过程与图标保存在 vendor，候选移除自动打开 UI、全局首选项写入，并隔离过程、全局变量、辅助节点与 UI 名称。原版权 Dmitrii Kolpakov 2020；包内未提供许可文件，不推断发布授权。

## 参数与输入输出

工具 ID `reparent_pro_v1_5_1`，类别 `rigging`。`action=inspect` 只返回全部资源、过程和验收状态；其它参数见 Schema。`objects` 为有序、叶名全局唯一的非引用、非锁定、非 DAG 实例 transform/joint，省略时使用当前选择。relative 至少两项且末项为参照；freeze 至少两项且首项为主控制器；IK 恰好三项，首项必须有父节点，肢体非共线、非零长。

动作：`reparent`（可 `pin=True`）、`manual_start`（生成可移动 pivot）、`manual_go`（可 Pin）、`manual_cancel`、`relative`、`freeze`、`ik`（可 `local=True`）、`bake_delete`、`locator_size`（原内部尺寸计算，必须有自有临时 locator）。Go/Cancel 使用本候选最后会话，最终 bake 使用全部会话。不会自动认领原工具的旧会话。重用同一控制器前先 bake_delete。

`frame_range=[start,end]` 含首尾，整数、最多 10001 帧、最多 200000 对象帧，省略使用 playback；所有原颠倒的 bake 时间字符串已修正。`delete_redundant=True` 保留原连续相同键删除，仅针对新辅助 locator。API 返回解析的对象、范围、原始结果选择和创建节点 UUID；调用者选择、当前时间、namespace、autokey、选择顺序首选项、playback、原动画混合首选项及可恢复的键选择恢复。

## 操作影响与边界

原 reparent/manual_go/relative/freeze 会清除控制器全部六个 TR 通道动画键，包括范围外键。因此必须 `allow_clear_animation=True`，GUI 必须明确勾选。Pin 会固定当前姿态。Freeze 主控制器原语义为冻结主控，其他控制器重新烘焙；IK 会建立临时关节、handle、Pole、约束并改变控制器关联/变换限制。这些原算法完整保留，仍需真实生产 rig 验收。全六 TR 通道需要可编辑；锁定、非 keyable、共享曲线、动画层/非独立时间曲线及外部约束拒绝。此保守准入不会自动解锁或破坏已有 rig 驱动。

每次执行一个 Undo chunk；错误可能留下部分修改，可执行一次 Undo。辅助节点以 owner 标记归属，集合额外保存原控制器 UUID；删除前复核成员、引用锁、外部后代和连接。原全场景后缀通配符清理由 `bake_delete` 的自有节点计划替换，原 TempLocator、原后缀组和非自有会话保留。最终 bake 保存范围外键；写回六 TR 并清理自有辅助，烘焙到真实控制器的曲线保留。

`bake_on_layer=True` 仅适用于最终 bake_delete，生成 override 动画层并保留结果。原源码的 layer 菜单只有 UI，业务代码从未读取它；候选不声称原模式具有层功能，界面注明该选项只在最终 bake 有效。原完整窗口、Help、模式开关、Go/Cancel 保留，业务按钮路由至同一个 API。Help 打开原 YouTube 链接，不作为离线验收。窗口和 MEL 声明不属于场景 Undo；工具不导出文件、不安装 shelf、不修改正式库。

## 示例与组合

```python
tool.run(dry_run=True, action='reparent', objects=['rig:hand_ctrl'],
         frame_range=[1, 120], allow_clear_animation=True)
tool.run(action='reparent', objects=['rig:hand_ctrl'],
         frame_range=[1, 120], allow_clear_animation=True)
tool.run(action='bake_delete', frame_range=[1, 120])
```

手动模式先 manual_start，再在真实 Maya 移动自有 locator，最后 manual_go 或 manual_cancel。可先用 hierarchy_analyzer 审阅输入树，再用本工具在备份场景制作新运动；bake_delete 后才能与动画过滤、姿态传递继续组合。静态依赖不代表组合已经实测。

验收状态：隔离测试见运行清单；Maya 2025 standalone 只证明相应 fixture，完整真实 GUI、生产 FK/IK、Freeze、不同 Maya 版本均 not_run。候选仍在待整理库，通过人工验收后执行 promotion.json 对应晋级脚本；无需再次重构或修改注册代码。
