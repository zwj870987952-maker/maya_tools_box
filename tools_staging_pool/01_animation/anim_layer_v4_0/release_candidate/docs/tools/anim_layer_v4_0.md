# Anim Layer v4.0 第三方动画层套件

工具 ID `anim_layer_v4_0`，类别 Animation，原版 v4.0，外层适配版本 4.0.1-adapter。作者 Barnev Pavel；原 readme/License/MEL/帮助图与 NoUI 安装器共 6 文件，逐字节镜像于运行包 `upstream/`。没有改写第三方算法、删除版权通知或重编码非 UTF-8 原文件。

## 范围、来源和条件

完整套件保留创建层、Channel Box 通道建层、按键/时间滑块区间建层、零层键、提取到基础/叠加/覆盖层、快速/智能合并、烘焙、Euler filter、选层/选对象、权重滑块/字段扩展，以及原标准动画/渲染/显示层编辑器过程。不是只保留一个菜单入口。

完整版有 216 个声明、197 global；NoUI 33 global。所有 global 签名作为 package catalog 和[过程目录](anim_layer_v4_0_procedures.md)保留，原 local 帮助函数随原文件 source，不作为外部 API 单独导出。getLayerDisplayType 在完整版同时存在 global/local 声明，未改动原定义；其全版加载/调用兼容性须实测。

原 License.txt 为自定义商业许可，列明商业使用、再分发及修改限制；原完整版还带 Autodesk 2021 的许可/版权头。此候选保留现有本地材料与外层调用适配，不声称开源、重新授权或已获公开分发许可，未发布/推送套件。具体使用范围以包内原文及用户已有授权为准。

需要 Maya cmds/mel、原生 animation/render/display layerEditor 支持、Python 3 与现有 framework/core。原 readme 示例为 Maya 2018；内嵌标准编辑器带 Autodesk 2021 头。本轮 only NoUI 在 Maya 2025 mayapy 隔离加载和部分过程检查；不能因此宣布所有版本/编辑器过程兼容。GUI 依赖 Maya 的内置图标、Channel Box、AnimLayerTab、时间滑块和全局 UI 变量；这些属于目标 Maya 安装/桌面环境，6 个包内文件齐全不能替代它们。

## 加载和原运行方式

`no_ui` 文件只定义 33 个过程，没有顶层执行；它仍有很多读取或操作原生 UI 的过程，名称不表示全部支持批处理。适配器仅允许 7 个不需要桌面 UI 的已审阅入口在 batch 查询/执行，其余要求交互 Maya。load no_ui 在 mayapy 可明确 source，不自动调用菜单或场景操作。

`full` 会覆盖大量标准 MEL 同名定义，并在顶层条件加载 createMayaRenderPassTab.mel、设置全局颜色变量、直接 createLayerEditor/updateLayerEditor。必须在真实交互 Maya 加载；不在 standalone 执行该入口来强行测试 UI。MEL 定义、UI、scriptJobs/optionVar 等会话影响不能用场景 Undo 撤回。需要还原原生定义/全局设置时，关闭测试 Maya 并重新启动干净会话；适配器不提供虚假的 unload。

原 NoUI 拖放安装器 source 后会创建 Shelf 按钮；仅保留为原始资源，不自动运行、不复制文件到用户 scripts、不修改 Shelf 或用户配置。正式包通过完整绝对路径 source 原文件，所以无需全局 sys.path/MEL 脚本目录安装。

加载器用 whatIs 检查所需过程是否来自当前包路径；已经来自该版本时跳过重复 source，force_reload=true 明确重新加载。别的脚本覆盖该过程会触发所选原文件重新 source。切换到 NoUI 不卸载全版曾定义的其他过程，不能当作恢复标准编辑器。source 失败时可能已有部分全局定义/界面变化，ToolResult 会如实提示。

## 框架参数与调用

| 参数 | 默认 | 作用 |
| --- | --- | --- |
| action | inventory | inventory 查目录；load 明确加载；invoke 调用签名过程；open_ui 加载并打开原工具菜单 |
| edition | no_ui | no_ui 或 full，full 加载本身会重建层编辑器 |
| procedure | 空 | invoke 必须是所选版本导出的 global 名；inventory 可指定一个过程查签名 |
| arguments | {} | 键须与 catalog parameters.name 完全一致；值按 MEL string/int/float 及对应数组验证 |
| force_reload | false | 明确 source 即使 marker 已来自该版本 |
| restore_runtime_state | true | API 调用后尽力恢复 evaluation mode/refresh suspension，显式 disable/enable_viewport 保留其作用 |

Schema 列出全部 global 名并提供通用 arguments 类型；不同版本/不同过程参数契约由 catalog 精确检查。int 是非 bool 的 32-bit 整数；float 必须有限；数组逐项验证；字符串拒绝控制字符并按 MEL 字面量转义。timerange 必须两个递增数；rotation_mod/mod/fidelity 为 0/1；tolerance/side_frames 非负。多层时间查询必须至少给一个层。

对象/层明确列表会检查存在性；BaseAnimation 在原时间查询中是直接曲线 sentinel，无需真实基础层节点。部分参数其实是 UI 标识或标签，不能一概当作 DAG 节点。预检不会全面证明引用/锁定节点可写、图层合并/烘焙可用或调用链依赖齐全。

`validate(**kwargs)` 和 `run(dry_run=True)` 只读校验资源 SHA、契约、环境和明确目标，不 source/运行原 MEL，不改变选择、键、UI 或文件。inventory 可在普通 Python 查询，不需要 Maya。框架 execute 用 UndoChunk 包裹适配器调度的场景操作；原 GUI 按钮保持原回调，它们**不会自动经过新增的 validate/Undo 包装**，需按原工具行为单独验收，不能将适配器保证扩大到所有原界面。

## 主要业务过程和影响

| 业务 | 代表过程 | 约束/影响 |
| --- | --- | --- |
| 创建/选择 | create_and_select_anim_layer、create_anim_layer_from_channelbox_attrib | 当前选择/高亮通道，rotation 模式；可创建层并改选层状态 |
| 区间建层 | create_add_anim_layer_from_timerange、create_add_anim_layer_from_objects_and_set_framerange_from_multiply_anim_layers | 使用原时间滑块/所选键/层时间；默认键、层父级与选择会改变 |
| 提取 | extract_part_to_over_layer、extract_animation_to_additive_layer、extract_anim_on_base_layer_selected_object | 烘焙、加/删键、层成员、锁/静音及选择可能改变；在备份场景比较动画 |
| 合并 | execute_fast_merge、execute_smart_fast_merge、execute_fast_selected_merge、execute_smart_fast_selected_merge | 可能删除层/移除成员并烘焙基础动画；fidelity/tolerance 控制原 smart 参数 |
| 烘焙/旋转 | bake_simulation_timerange_on_over_layer、bake_simulation_playback_range、bake_smart_simulation_playback_range、euler_filter_on_selected | 键/切线/覆盖层、evaluation 状态与选择；内置 catchQuiet 可能只警告，不返回操作失败标志 |
| 查询/选择 | get_anim_time_range_from_anim_layer、get_anim_time_range_from_multiply_anim_layers、get_min_max_from_selected、select_skip_no_exist、select_few_Layers、select_best_layer | 原数组/数值结果，选择过程会改对象或层选择；无曲线单层查询可返回 {0}，不能假设永远是合法的两个端点 |
| 完整编辑器 | 动画/渲染/显示层 catalog 中其余 global | 原标准 UI/legacy render pass 等依赖；可改层权重、成员、连接、渲染设置、scriptJobs/optionVar；GUI/版本兼容待验收 |

直接 API 的 animLayersSaveExportClbc 只接受现有目录中的新绝对路径；目标存在时拒绝，不覆盖、不提前建文件。原 animLayersExport 打开原导出界面，后续原 MEL 回调仍按原方式选择/写文件；用户需选临时目录并检查覆盖。文件导出、保存和插件/设置影响不可由 Maya Undo 撤回。其他过程内部字符串拼接 eval/依赖调用保持原样，外层字面量转义只防止逃出适配器调用，不保证原函数的所有内部拼接都安全。

## 返回与异常

ToolResult.data 包括 action/edition/procedure/arguments/signature、mel_command、资源数、selection 和 source_executed。inventory 还给 procedures/top_level_lines；load 给 source/already_loaded；invoke 给 return_value/error/restoration_errors。执行成功只表示 MEL 调用返回且外层恢复未报错，不能检测原 catchQuiet 吞掉的操作失败或证明最终动画正确。void 返回 null；数组/字符串/数值保留原协议。

source 和调用异常不自动回滚；已有部分场景修改由用户检查后 Undo，进程级 MEL/UI/设置不由场景 Undo 保证。默认外层尽力恢复 evaluation/refresh 状态，选择/当前时间/层结果保留原业务行为，不强行恢复而破坏选层输出。直接 viewport 开关明确保留开关作用，需按原函数配对使用。

## 示例

```python
import maya_toolkit
# 转正后：先查签名，避免猜参数名称。
signature = maya_toolkit.execute_tool('anim_layer_v4_0',
    dict(action='inventory', edition='no_ui', procedure='get_anim_time_range_from_anim_layer'), dry_run=True)
args = dict(action='invoke', edition='no_ui', procedure='get_anim_time_range_from_anim_layer',
            arguments={'anim_layer_name': 'BaseAnimation'})
preview = maya_toolkit.execute_tool('anim_layer_v4_0', args, dry_run=True)
if preview.success:
    result = maya_toolkit.execute_tool('anim_layer_v4_0', args)
```

候选阶段用 launch_candidate.py 的 load_tool()。show_ui 打开外层网关，先选 NoUI/full，再查签名、输入 JSON、预检或明确执行；开网关不 source 原套件。open_ui 打开原工具菜单，full 同时保留原层编辑器重建。帮助按钮展示原 JPG（六个布局功能说明），不把图中的性能宣传当作本轮测量结论。

## 复用、组合与演进

复用框架 BaseMayaTool/ToolResult/UndoChunkContext，未把第三方内部函数下沉公共 core。原 suite 源文件/许可完整保留，新增外层资源校验、版本加载、签名调用、无执行预检、导出碰撞拒绝、状态恢复和网关。业务过程与原 UI 全保留，不进行版权代码改造。

与 anim_layer_key_runner、anim_layer_keyframe_bookmark、anim_layer_bookmark_trimmer 都会使用动画层/键，但各自选择和范围语义不同。可以用本工具查询区间/选择层后再按其他工具契约预检；没有跨工具或全版 UI 组合实测承诺。

普通 Python 8 项检查验证 6 资源字节/SHA、197/33 global 签名覆盖、Schema/类型/转义、无 source inventory、导出碰撞及无安装器/源改写。Maya 2025 隔离 8 项验证 NoUI 全声明加载、时间查询、数组/选择与 Undo、字面量、无写入预检、运行状态恢复及 batch 拦截。完整版/原菜单核心业务尚未实际加载/验收，因此记录 prepared_unverified；不把 NoUI 的部分通过扩展为整套通过。逐项人工验证见 acceptance.md。
