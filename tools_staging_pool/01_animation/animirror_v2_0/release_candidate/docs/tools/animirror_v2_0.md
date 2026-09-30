# AniMirror v2.0 动画镜像候选

本候选完整保留原安装 MEL、两页 PDF 及嵌入的九个业务/UI 过程。原安装入口会创建 Shelf，候选从唯一命令字符串提取全部算法，使用定义式加载和独立名称，不运行原安装器。它仍留在待整理池，状态 prepared_unverified，真实 Maya GUI 验收通过后才能晋级。

## 用途和输入输出

依次提供中心、参考、目标三个 transform/joint，创建原 joint/makeIdentity/mirrorJoint/floatMath/约束网络，随参考动画实时镜像。支持多个目标累计、烘焙、清理和 Mirror with Bake。原窗口的 Interactive Mirror、Undo、Bake、Mirror with Bake 及全部平移/旋转开关保留；四个场景按钮改用标准 API。候选窗口名 mtbAV2_AniMirror，原 UI 控件和全局变量使用独立前缀。

类 AnimirrorV2Tool 继承 BaseMayaTool，tool_id=animirror_v2_0，category=animation，version=2.0.1-adapter。实现 validate/execute，通过 run(dry_run=...) 返回 ToolResult；Schema 使用 to_openai_tool/to_mcp_tool 导出，晋级后可通过 maya_toolkit.execute_tool 调用。直接执行内部 MEL 写场景过程会被拒绝。

| 参数 | 契约 |
|---|---|
| action | mirror（默认）、mirror_bake、bake、clear、inventory、open_ui |
| objects | 明确对象名数组，顺序中心→参考→目标；mirror/mirror_bake 空数组使用恰好三项选择。拒绝组件、通配符、重复及不明确名称 |
| translations / rotations | 布尔，默认均 true；镜像时不可同时关闭 |
| translation_axis | X/Y/Z，默认 X；对应原 UI 标签 XZ/YX/ZY，不解释为通用几何镜像平面 |
| invert_rotation | 不重复的 X/Y/Z 数组，默认 [Y,Z]，对应原旋转取反开关 |
| start / end | 同时提供有限数字且 start≤end；省略采用 GUI 高亮范围（跨度>1）或播放范围。保留原高亮上界作为包含边界的行为，可能多采样一帧，应在 GUI 验收 |

inventory 返回资源哈希、完整过程和变更目录，只读；open_ui 返回窗口名与过程来源，需要实际 Maya GUI。mirror 返回 target、metadata、owned_nodes、interactive=true；bake/mirror_bake 返回全部累计 targets、range、warnings、interactive=false；clear 返回实际删除辅助节点和记录的结果。

原位移按钮虽标 XZ/YX/ZY，mirrorJoint 实际选项分别 mirrorXY/mirrorYZ/mirrorXZ，后续 floatMath 实际反转 X/Y/Z 位移。候选保留这种耦合。隔离的零变换中心、普通 transform 测试中，参考 (3,2,1) 对 X/Y/Z 分别得到 (-3,2,1)、(3,-2,1)、(3,2,-1)；默认旋转 (10,20,30) 得到 (10,-20,-30)。这些简单场景结果不能推导复杂骨架、中心非零变换、jointOrient 或负缩放的通用镜像结果。

## 依赖、预检与操作影响

Maya Python 3，现有 framework/core Undo。Maya2025 的 floatMath 由已安装 Autodesk lookdevKit 提供：用户在备份场景显式加载 lookdevKit 后运行，validate 不会自动加载插件。原 PDF 标注 Maya2016–2022 Mac/Windows；候选的 Python3 与本机 Maya2025 standalone 检查没有验证整个原支持范围或其他操作系统。

validate/dry_run 仅查询参数、节点、记录、通道、插件节点类型和时间范围，不 source、开窗、创建节点、改变选择/时间或加载插件。Undo 必须启用。目标引用、锁定或选用 TR 通道已有任何驱动（包括动画曲线）会被拒绝；已有候选镜像目标需先 bake/clear/Undo。若祖先/后代关系可能造成明显循环，也会拒绝；这不是复杂约束网络的完整循环分析。先准备独立目标副本。

每次场景调用使用框架 UndoChunk。mirror 创建 joint、floatMath、unitConversion、constraint 和所有权 network；这些辅助节点共同驱动目标。bake 和 mirror_bake 都处理当前场景的**全部累计候选目标**，不会仅处理当前选择；平移/旋转开关只控制创建镜像，不限制后续 bake 对目标其他可烘焙通道的影响。保留原 simulation=0、sampleBy=1、preserveOutsideKeys、minimizeRotation、删除静态曲线、filterCurve 及清理流程。

原 UI 的 Undo 按钮执行 clear：删除辅助节点/记录、保留目标当前姿态与已有烘焙曲线；它与 Maya 原生 Undo 不同。Maya Undo 能撤回一次候选场景调用，恢复相应节点/曲线。操作没有业务文件写入，不安装 Shelf，不自动改变评估模式。执行 finally 恢复刷新暂停状态、当前时间及仍存在的对象/组件选择。错误不会自动回滚，可能留下部分节点；记录失败所有权后拒绝继续镜像/烘焙，允许 clear 或用户 Maya Undo。

## 所有权、清理和恢复

每次 mirror 创建带 OWNER/record_id/JSON 的 network，源/参考/目标和新辅助节点按 UUID 记录。清理检查类型、标记和 record_id，不按旧名字删除；重命名或原名被外部节点复用不会误删替身。元数据跟随场景保存和 Undo，下一次动作从场景重建 MEL 累计列表，避免 Python/MEL 缓存丢失或 Undo 后遗留全局计数。

辅助 joint 下出现外部后代、辅助节点新增外部输出消费连接时拒绝自动清理。floatMath 的 message→Maya defaultRenderUtilityList.utilities 系统登记允许保留，不当作业务外部连接。删除前先记录 UUID，并将候选目标下的候选约束脱离 DAG，再删除拥有的辅助节点；这避免 Maya 删除 helper joint 时连带删除空目标。不能把手工添加内容到辅助层级当作安全保存方式。

## 示例和可衔接工具

```python
tool.run(objects=['center', 'reference', 'mirrorTarget'], dry_run=True)
tool.run(objects=['center', 'reference', 'mirrorTarget'], translation_axis='X')
tool.run(action='bake', start=1, end=120)
tool.run(action='clear', dry_run=True)
```

可先准备明确长路径/命名空间和无驱动目标，再镜像和烘焙，之后把目标曲线交给动画滤波工具；需要核对范围、动画层和连接。这是接口衔接说明，尚未验证真实跨工具 GUI 组合。已被此工具约束驱动的目标不能直接作为另一个工具的无驱动目标。

## 演进、验证和晋级

原算法和全部窗口布局保留；九个原过程另加两个 typed option/cache 读取过程。原顶层开窗与 reset 去除，但过程内部 reset 保留；参数代替业务 UI 查询，原 UI enable/disable 回调仍保留。修正 withBake 先清空计数再递增的空项问题，Python 在立即烘焙前捕获拥有的节点。原全局名字清理改为 UUID 所有权，四个按钮接入 run，增加来源检查、内部调用保护、finally 恢复和清理保护。完整逐行差异见 animirror_runtime_changes.diff。

普通 Python 五项检查以及 Maya2025 隔离十四项检查通过，包含真实 mirrorJoint/约束/floatMath、三个位移轴、旋转、累计烘焙、Undo、无副作用预检、失败恢复、外部连接/后代、重命名替身和场景保存重载。测试显式加载插件；故障/缺插件 fixture 有明确注入，直接内部调用保护会产生预期且被捕获的错误。未创建真实窗口，没有验证生产 rig、AdvancedSkeleton、其他版本/平台、非默认单位、复杂中心变换或实际高亮时间轴。

promotion.json 预制包、原资源、专项说明和两个测试的目标路径，并准备 AnimirrorV2Tool 的导入、ALL_TOOL_CLASSES 和 __all__ 注册；面板读取注册表，无需再写业务代码。临时正式布局检查不会写正式库。晋级脚本只读预览当前哈希，实际搬迁要求真人验收记录匹配当前候选。具体步骤见根 acceptance.md。

没有发现原资源的独立再分发许可，作者联系信息在原 PDF 内；仅本地保留来源，不据此宣称公开分发授权。原 MEL/PDF 按字节归档，upstream 的 Git 属性关闭文本换行转换以保持跨检出的校验值。
