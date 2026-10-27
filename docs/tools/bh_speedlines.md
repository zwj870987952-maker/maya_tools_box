# bh_speedLines 速度线候选

`bh_speedlines`，`animation`，`SpeedLinesTool`，1.02.1-adapter。状态 prepared_unverified；真实 GUI 验收 not_run。完整保留原 21 个 MEL 过程和原生窗口、相机选择器、EP/Pencil 绘画、深度滑条、两曲线生成网格、简化、平滑、翻法线和可见性打键，另加 typed option reader。八份原资源按字节归档，中文版本与四张 sampleTextures 保留；运行使用英文过程。原 ReadMe 的安装/重启/Shelf 路径不执行，未找到独立再分发授权，仅本地私有整理，不公开发布。

## 调用与参数

候选启动见 acceptance.md。验收并晋级后可通过 `maya_toolkit.execute_tool('bh_speedlines', arguments, dry_run=True)` 预检，再执行；当前正式库未注册。直接实例调用 `tool.run(...)` 返回 ToolResult，`validate`/dry_run 只查询，不 source MEL、不改转换偏好、选择、工具上下文或场景。沿用现有 BaseMayaTool、UndoChunk 和面板注册，无新增 core。

| 参数 | 默认 | 用途 |
|---|---|---|
| action | inventory | inventory/open_ui/geometry/flip/simplify/smooth/key_visibility/start_draw/stop_draw/draw_depth/reset_depth |
| objects | [] | 明确 transform 名数组；非绘画业务为空时读当前选择，不接受组件/通配符/歧义或重复名 |
| camera | persp | geometry/绘画使用的明确 camera transform |
| high_detail | false | geometry 原高细节选项 |
| on_layer | false | geometry 放入本候选拥有的 displayLayer |
| consume_curves | true | geometry 删除两条输入曲线；false 保留输入，这是明确增加的非消耗选项 |
| hold_two | false | 可见性保持两帧，false 只保持一帧 |
| ep_tool | false | start_draw：false 原 Pencil，true 原 EP 曲线上下文 |
| depth | 0 | start_draw/draw_depth 原深度字段/增量 |

geometry 恰需两条 nurbsCurve；smooth 需曲线；flip 需 mesh；simplify 需 mesh 或 spans>=2 曲线。对象引用、节点锁定、非唯一形状等拒绝。可见性通道锁定或非 animCurve 驱动拒绝。消耗曲线时拒绝额外非 shape 子对象和外部输出消费者；保留曲线模式不删除输入。复杂历史、约束或绑定请使用副本人工验收。

## 原算法与影响

- geometry 保留原 loft/多边形转换、相机朝向/法线判断、冻结变换和 CenterPivot 流程。默认删除两输入曲线，成功选择生成网格。高细节与层选项保持原分支。不自动赋材质，sampleTextures 只作为随包素材。
- simplify 保留原 polyReduce 和曲线折半 spans/degree=2 rebuildCurve，改变拓扑、曲线形状和 pivot。原 `ch=0` 在已有生成历史网格上会被 Maya 忽略并产生历史节点；不能保证完全没有 construction history。
- smooth 调用原 SmoothHairCurves；flip 调用原 polyNormal。参数和算法未为统一 API 重写，其他 Maya 版本需复验。
- key_visibility 将 currentTime 转整数 t。默认 t-1/t/t+1 写 0/1/0；hold_two 在 t-1/t/t+1/t+2 写 0/1/1/0。只给 transform.visibility 打键，不给 shape 打键；可能覆盖原邻帧键。小数时间截断保留原语义，不是取最近帧。
- geometry 临时设置原 16 项 nurbsToPolygonsPref，finally 恢复查询到的值；这是 Maya 应用偏好，不能依赖场景 Undo 恢复。恢复失败返回失败并提示检查偏好/时间/选择，仍关闭内部写入许可。无外部文件写入、安装、播放范围或 evaluation 模式改变。
- 单次标准 API 的场景写入由 UndoChunk 分组。异常不自动回滚已发生的部分写入；观察 ToolResult/Script Editor，必要时 Undo。普通业务恢复时间和原存活选择，geometry 成功选择结果；绘画成功保留 live plane/交互上下文供鼠标继续操作。

## 绘画生命周期

必须真实 GUI 且先打开候选窗口。原相机列表、绘画平面、EP/Pencil、near clip 限制、深度拖动/释放和 cutDecimals 截断到两位小数保留。UI 按钮走标准 API；过程/控件名加 mtbSL_，所有内部写场景过程带入口 guard。

平面记录 Owner、UUID、原 live 对象 UUID、原工具上下文与自身 shapes UUID。stop_draw 仅删除本候选平面，恢复仍存在的原 live 对象/有效工具上下文，按本会话保存的 job ID 清理自己任务；外部同名平面、添加的子对象/消费者拒绝删除。本候选层同样必须 Owner 匹配，不能借用外部同名层。平面重命名仍可按 UUID 退出；深度调整拒绝重命名后的固定名操作，需先退出再重建。原 live plane 和鼠标画出的曲线是不同对象，退出不删除所画曲线。

EP ToolChanged runOnce 和 Undo 任务 parent 到候选窗口，关闭窗口走 stop_draw，Undo 删除平面后 deferred 清理旧绘画状态。此类 GUI 事件尚未运行验收，不能把任务代码或 headless 清理测试当作已验证的交互生命周期。Undo/Redo 只保证场景命令归组，不保证交互上下文、异步任务可自动复原；必须人工检查 Redo 残留。保存、切场景、重开窗口前先 stop_draw，避免会话 job/context 与场景记录分离。

## 输出与组合

inventory 返回完整来源哈希/过程/资源审计；open_ui 返回 source/procedures/window。场景操作返回 action、created_nodes、执行时 selection、draw_plane、owned_script_job 和 warnings。selection 记录执行时选中对象，不表示 finally 恢复后的选择；owned_script_job 是 EP job ID，非全部任务列表。

推荐组合：候选绘画生成两曲线 → stop_draw → geometry → 按需 flip/simplify → key_visibility → 人工材质/动画预览。高细节影响后续 simplify，输入曲线默认消耗，先备份或 consume_curves=False。此流程是可调用关系，完整真人交互组合未验收；不宣称与其他未验收工具的生产组合可用。

## 验证与晋级

4 项普通 Python 检查通过：八资源 SHA、完整过程/顶层副作用审计、严格参数、Schema/无 Maya inventory。Maya2025 隔离 9 项通过：22 过程编译/来源/guard、真实 loft/rebuild/SmoothHairCurves/polyReduce/polyNormal/visibility 键、偏好恢复、Undo、层所有权、失败恢复，以及人工创建的 owned 平面在 headless 下按 UUID 清理/外部对象保护。

没有创建真实 GUI，没有执行鼠标绘画、深度拖放、EP/Pencil、ToolChanged/关闭/deferred Undo 回调；headless 平面 fixture 不证明 start_draw 工作。普通与隔离检查、临时正式布局/注册检查的报告存于 plans/staging_run，均不等于真人验收。promotion.json 已准备完整目标文件、资源、测试和注册合并，真实当前哈希验收通过后才允许晋级。
