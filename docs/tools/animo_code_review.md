# Animo V10.6.0 静态代码初审

初审日期：2026-10-05；发布与协议复核：2026-10-06。来源：[Ehsan Bayat 官方 Gumroad 页面](https://ehsanbayat.gumroad.com/l/Animo)。

已从官方免费领取并下载原包，保留完整素材和配置，在待整理库解压。已完成静态检查、重点模块阅读及项目候选适配；候选包含 55 类、553 个固定入口，20 项离线边界测试通过。用户已确认取得作者授权并要求上传全套。未安装到 Maya、导入或执行供应方代码，未进行 Maya 直验，不代表生产可用或全面安全审计通过。统一说明与检验入口见 [animo.md](animo.md)。

## 下载位置与检查范围

- 原包：[Animo_v10.6.0.zip](../../tools_staging_pool/07_subsystems_suites/animo/archives/Animo_v10.6.0.zip)。
- 解压目录：`tools_staging_pool/07_subsystems_suites/animo/upstream/Animo_v10.6.0/`。
- 完整文件/函数/类清单：[source_inventory.json](../../tools_staging_pool/07_subsystems_suites/animo/source_inventory.json)。
- 可重复运行的纯静态扫描：[inspect_static.py](../../tools_staging_pool/07_subsystems_suites/animo/inspect_static.py)。扫描不 import 上游工具。
- 压缩包大小：100,221,983 bytes；ZIP CRC 校验无错误。
- SHA256：`0a99ff64227047a6423f6c6e2a2ac081acbdfb58dd53e5fad6de9879b987c502`。
- 1,315 个 `.py`，合计 136,337 行（含空行、注释、重复封装与 UI）；全部通过本机 Python 3.12.14 的 `ast.parse`。这仅验证语法，不验证 Maya API、模块路径和 Qt 运行行为。
- `tools_library/` 有 54 个分类、540 个 Python 入口；还存在 `animo_tools/tools/` 执行脚本层。因此文件数和入口数不能当作独立算法数量。
- 另有 8 个 `.pyc` 缓存、2 份 PDF、10 个 JSON、图标/动画素材，以及 Windows/macOS/Linux 的 FFmpeg 程序。核心可读 Python 源码无需反编译。
- 官方包标注支持 Maya 2022–2026；代码多处兼容 PySide2/PySide6、shiboken2/shiboken6，实际跨版本兼容性尚未验证。

## 许可与项目存放方式

初审时原包 `Animo License & Usage.pdf` 允许个人、专业、商业项目使用，限制修改、再分发、转售、再许可及公开发布原工具/源码。2026-10-06 复核确认：解压目录中的许可 PDF 已由用户删除，而未改动的 [原始 ZIP](../../tools_staging_pool/07_subsystems_suites/animo/archives/Animo_v10.6.0.zip) 内仍保留这份历史许可。

用户在本次对话明确确认“已有作者授权，按新许可上传全套”，这是此次公开同步的依据，见 [授权确认记录](../../tools_staging_pool/07_subsystems_suites/animo/AUTHOR_PERMISSION.md)。完整作者授权文本尚未入库，不自行生成新的开源许可，也不将删除旧许可文本作为授权依据。仍不并入原有开源工具计数。供应方算法和素材没有迁移到 `maya_toolkit.core`；候选运行副本只做两处本机启动管理调整。

此前供应方文件通过 `.gitignore` 保留本机；本次按用户确认的授权移除 Animo 专项排除，完整源码、素材、原包和静态库存随仓库同步。`.gitattributes` 禁用供应方文件换行转换以保留哈希，Python 缓存和本机运行状态继续排除。知识库生成项仍仅描述静态扫描，不表示 Maya 已验证。

## 主要结构

以下路径均相对解压目录，功能判断来自所列源码；关联功能尚未做真实 Maya 组合验证。

| 模块 | 核心入口/实现 | 作用与实现方式 |
| --- | --- | --- |
| 安装器 | `Animo_Drag_and_Drop_installer.py` | 拖放 UI，复制数据目录，创建 Shelf 按钮。|
| 主工具栏 | `Animo_Data/Animo_Launcher/toggle.py`、`Animo_Launcher.py` | 显隐、模块路径和重载、停靠 UI、启动配置；主文件 7,677 行。|
| 动画滑块 | `Animo_Sliders/tween_slider.py`、`slider_utils.py` 及各滑块文件 | 缓存曲线、关键帧索引和原值，通过 API 快速更新，处理单位与撤销提交。|
| Spacify | `Animo_Space_Switcher/WorldSpace.py`、`CameraSpace.py`、`NewPivot.py`、`TempIK.py`、`CleanAndBake.py` | 临时 Locator/控制器、约束、世界/相对/摄像机空间、临时 IK/FK、烘焙清理。|
| 镜像 | `Animo_Launcher/mirror_launcher.py` | 名称/token 配对、几何兜底配对、镜像轴表、当前姿势/时间区间/Graph Editor 关键帧。|
| Tracify | `Animo_Launcher/tracify.py`、`tracify_node.py` | 自定义 Python Locator 插件，缓存轨迹数据，Viewport 2.0 draw override 绘制。|
| Transify | `Animo_Transify/transify_engine.py` | 动画/姿态序列化 JSON，切线、Infinity、旋转顺序、命名空间映射、插入/替换。|
| Vectorify | `Animo_Launcher/vectorify_launcher.py` | 动画重新沿路径行进的大型独立模块，7,411 行；本轮只检查结构，未逐函数审查。|
| Tools Editor | `Animo_Tools_Editor/animo_tools/` 与 `tools_library/` | 工具索引、搜索、快捷键、Shelf 和动态脚本执行。|
| Graph Editor UI | `Animo_UI/graphSliderMod.py` | Graph Editor 嵌入行、滑块与工具按钮；500 ms QTimer 检查附着状态，并提供停止方法。|
| Reference Dropper | `Animo_Reference_Dropper/anim_ref_dropper_plugin.py` | Maya 拖放插件；视频/GIF 通过 FFmpeg 转图片序列，图片创建参考内容。|

## 重点算法阅读结论

### Tween 滑块

`tween_slider.py:111` 在交互开始时缓存目标曲线、关键帧和边界值。没有选择关键帧时，会在当前时间插入关键帧，而不是只移动已有关键帧。

`execute_tween_on_curves`（206 行）使用 `left + (right - left) * bias` 调整所选关键帧数值；这里的 bias 来源于滑块位置，并不是按照各关键帧时间计算插值比例。多个选中关键帧可以被推向相同的边界插值值。

拖动预览通过 `MFnAnimCurve.setValue`，61 行起的 reader/setter 将当前角度和长度单位转换为 API 内部单位。释放时 `commit_tween_on_curves`（246 行）先还原原值，再用 `cmds.keyframe` 写入最终值，配合 Undo Chunk 建立命令层撤销记录。这是性能与可撤销性折中的具体实现；本轮没有测量性能或确认撤销结果。

### 空间切换

`WorldSpace.smart_bake` 支持完整区间烘焙或按源对象已有关键帧采样。`btl_ctrl_mode` 创建带 `_esn_ctrl` 后缀的临时 Locator，放在 `SPACIFY` 组中，利用约束转移运动，`CleanAndBake` 按对象集合识别不同临时系统并烘焙清理。它会修改场景节点、连接与关键帧，不是只改 UI。

### 镜像

`buildPairs`（639 行）和 `geometricFallbackPairs`（591 行）结合名称与几何位置配对；`buildMirrorTableData`（766 行）记录镜像行为；`applyMirror`（1665 行）根据选区调用当前姿势、Graph Editor 或时间区间路径。代码包含动画层曲线查找和旋转顺序不匹配检查。需在真实 Rig 上验证命名空间、左右轴和层权重结果。

### 动画传递

`AnimationCopyPasteJson` 保存对象/通道关键帧、切线、Infinity、旋转顺序和时间范围，并支持命名空间重映射。单位转换针对 linear 属性，并对切线角度做缩放。

**动画层支持有范围限制**：`check_objects_in_animation_layers`（765 行）检测非根层成员，提示合并；`copy_all_animation_to_json`（1401 行）会调用该检查。因此不能根据套件其他模块支持动画层，推断 Transify 能无损保留和跨场景迁移完整动画层结构。需要核验具体复制/粘贴入口的分支。

## 已确认行为与潜在问题

| 项目 | 源码位置 | 影响及后续验证 |
| --- | --- | --- |
| 首次启动修改环境 | `Animo_Launcher/Animo_Launcher.py:52`、1141、1236 | 导入主启动器即调用函数，将 `startupScriptIsEnabled` 设为 1；非 macOS 首次运行会向 `userSetup.py` 写入启动代码并记录配置。仅打开工具也会产生文件/配置副作用，Maya Undo 无法撤销这些文件写入。|
| 可能关闭无关工具窗口 | `Animo_Launcher/toggle.py:12`、169 | 关闭/隐藏 Animo 的分支调用清理函数，遍历 Maya 主窗口子对象，条件仅为 `objectName().endswith("UIWindow")`，未校验 Animo 前缀/类型；其他工具采用同后缀时可能被关闭。调用路径已确认，影响尚未实测。|
| 覆盖安装会删除旧目录 | `Animo_Drag_and_Drop_installer.py:537`、615 | 保存部分偏好后 `rmtree` 已存在的 `Animo_Data` 再复制原包。若用户在旧目录放了额外脚本或未列入保留项的数据，会随旧目录被清除。|
| 导入路径与全局状态耦合 | 多处 `sys.path`/`sys.modules` 操作 | 依赖 `Documents/maya/scripts/Animo_Data` 及短模块名，不适合直接作为无副作用库 import；重载与其他短名模块之间需检查冲突。|
| 异常清理边界 | `Animo_Sliders/tween_slider.py:301` | release 的 finally 恢复 refresh，但关闭 Undo Chunk 在 finally 后面；若执行/提交抛出未捕获异常，则可能跳过关闭 Chunk 与状态清理。是静态风险，不是已复现故障。|
| FFmpeg 额外副作用 | `Animo_Reference_Dropper/anim_ref_dropper_plugin.py` | 启动外部进程、输出图片序列；macOS 路径还尝试移除包内 FFmpeg 的 quarantine 属性。本轮未运行。|
| 动态执行为工具设计 | `Animo_Tools_Editor/animo_tools/widget_tool_item.py:345` | 原脚本使用 `exec`/`.pyc` fallback 来运行工具；不应把它当作受限命令执行环境。当前分析只读取文本。|

## 与现有项目能力的比对

- Undo 和刷新控制与 `maya_toolkit.core.context.UndoChunkContext`、`SuspendRefreshContext` 重复；后续自有实现可复用现有 core。不能据此直接搬运受限源码。
- 镜像、滑块、弧线与空间切换，与 `animbot_copy`、`the_key_machine`、`eblabs_screenspace`、`fd_multi_space`、`brs_loc_transfer` 等待整理能力存在概念重叠；这仅是静态功能比较，尚未验证互操作。
- Transify 与待整理 `copy_animation`/重定向工具有重叠，但这里按对象/属性/命名空间传递，不等于不同 Rig 的通用动画重定向。
- 现有正式 `euler_winding` 针对欧拉旋转问题，不能替代 Animo 的镜像或空间切换。未来组合时仍需检验曲线、旋转顺序与约束关系。

## 候选适配与当前检验状态

Animo 是源码可读、此次由用户确认取得作者发布授权的第三方动画套件；大量入口脚本、固定预设与 UI 逻辑使文件数高于独立算法数。按待整理规范创建 `release_candidate/`，保留原包、算法与素材；没有安装到 Maya、转正或持久挂载正式面板。

候选 `AnimoTool` 继承项目基类，提供只读预检、固定白名单调用、统一 `ToolResult`、OpenAI/MCP Schema、查询和人工检验面板。安装动作仅新建目录并逐文件校验，不调用原覆盖安装器；短模块冲突会拒绝执行，不卸载其他工具。

候选运行副本两处调整：主启动器移除导入时启用启动脚本和首次写 `userSetup.py` 的顶层调用；窗口清理条件增加 Animo 前缀。原显式配置函数保留，逐文件 SHA 与 [差异记录](../../tools_staging_pool/07_subsystems_suites/animo/release_candidate/patches.json) 可追溯。

20 项离线测试覆盖索引/Schema、参数与节点检查、只读预检、新目录复制、已有目录保护、代码/资源完整性和 `SystemExit` 处理。此次新增缺少运行副本时不自动写入、预检不冒充 Maya 实测两项回归，并修复对应改动。[验证记录](../../tools_staging_pool/07_subsystems_suites/animo/release_candidate/verification.json) 不包含供应方算法执行证据。按 [人工验收](../../tools_staging_pool/07_subsystems_suites/animo/release_candidate/acceptance.md) 在真实 Maya 中检查 UI、按钮/滑块、选择与场景修改、Undo 和 Script Editor；未运行项目保持 `not_run`。
