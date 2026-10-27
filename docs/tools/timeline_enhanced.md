# 时间轴方块规划：基础版/增强版

用途：在自己的界面上放置彩色方块，规划时序/镜头/动作事件。原工具不会创建/移动/删除 Maya 动画曲线关键帧；界面叫“关键帧”的 K 方块只是标签。候选完整携带两份 Python 和原说明，保留所有原类方法和布局，不补造说明提到但实际缺失的 example/hotkey setup 文件。

## API、输入与输出

`TimelineEnhancedTool.run(action='inspect', state=..., **参数)` 继承 BaseMayaTool，tool_id=`timeline_enhanced`，category=animation。所有行动返回 `ToolResult.data.state`，为新的规划文档；输入 state 不会原地变化，调用方需保存返回值。默认状态 `{start_frame:1, frame_count:100, blocks:{}, selected:[], clipboard:{}}`。blocks/clipboard 用规范整数字符串作键，颜色 RGB 0..1、label/name 最长256字；开始帧允许负帧，显示10..1000帧，最多10000方块。已有但显示范围外方块保留；动作不会因此写场景关键帧。

| action | 额外参数 | 行为 |
| --- | --- | --- |
| inspect | 无 | 返回完整规范文档及 not_run |
| configure | start_frame / frame_count | 改显示范围，保留隐藏方块 |
| add | frame, block 或 block_type, overwrite=False | 六类型或自定义颜色标签，默认拒覆盖 |
| edit | frame, block | 编辑已有颜色标签名称 |
| move | source_frame, frame, overwrite=False | 移动一个方块，保持其选中关系；同帧不删除 |
| select | frames | 选择真实存在的方块，不改变 Maya selection |
| copy | 无 | 深复制所选方块到文档内 clipboard |
| paste | frame, overwrite=False | 首个复制方块对齐 frame，保持相对时距，裁掉显示范围外项；冲突整批拒绝 |
| delete / clear | delete 可传 frames | 删除指定/所选，或全部规划方块 |
| load / save | path；save 可 overwrite=True | 显式绝对 JSON 路径，读取规范校验后才返回；保存已有文件需授权并保留旧字节 backup 文件 |
| sync | 无 | 读取整数 Maya playback 范围到规划文档，拒小数或超过1000帧，不改 Maya 范围 |
| set_current_frame | frame | 显式改变 Maya 当前时间 |
| play / stop | 无 | 显式播放/停止 Maya，play 拒 batch |

例如连续 `state = tool.run(action='add', frame=10).data['state']`；然后 `tool.run(action='move', state=state, source_frame=10, frame=15)`。该示例移动方块，动画关键帧不变。参数 Schema 有完整嵌套文档/颜色/类型/动作必填描述；运行仍做独立校验，因为框架不自动强制 Schema。

`validate`/`run(dry_run=True)` 做完整文档、操作冲突和文件检查，不写文件/偏好、不改节点/键/时间/选择/播放/Undo队列，不创建UI；load 干跑可只读指定 JSON。无隐式用户配置读取、没有默认源目录写入。严格 JSON 大小≤4MiB、拒重复键、无效帧/颜色/未知字段/不完整选择，读错不会清空已有文档。保存默认独占新建；显式替换先创建唯一旧字节备份，再临时文件替换，并检查原文件哈希没有并发变化；拒符号链接/junction，父目录必须已存在。磁盘故障可能留下备份或失败文件，应查看实际路径和结果，不能用 Maya Undo 恢复文件。

## 完整界面与行为修复

`tool.show_ui()` 增强版，`tool.show_ui(variant='basic')` 基础版，返回窗口控制器。基础随机色、点击开始拖拽/落下、起始帧/范围、水平滚动保留；增强菜单/工具栏、六方块类型、颜色与名称属性、Ctrl多选、复制粘贴、配置、同步/播放/停止、状态栏/帮助/关于全部保留。自有 Bridge 与 API 共享完整数据操作，原始代码逐字归档并提供完整 native 声明供追溯。

修复原 rowLayout columnWidth8（工具栏8、控制区实际9项）改 rowColumnLayout；属性 columnLayout 无效 margin 改 columnAttach；刷新时保存原 scroll parent，防止时间轴布局移出滚动区；属性窗口改私有名。负帧输入、统一范围1000、深复制clipboard、移动选中帧映射、目标替换默认取消、整批粘贴冲突保护和非法文件原子读取。源保存“成功”即使异常也提示的问题改为只显示真实 ToolResult，路径由选择器明确指定。原模式/fit/reset只有提示文字，现完成选择/添加/删除与默认拖拽模式、有限宽度fit（最小8像素仍水平滚动）和reset，不改变任何动画数据。

原帮助声称快捷键但没有实现；候选添加窗口内 QShortcut：Ctrl+A/C/V、Delete、Escape、Ctrl+Z、Ctrl+Shift+Z，不创建全局 Maya hotkey/运行时命令。窗口 Undo/Redo 记录最多100份深复制规划文档（包括本地clipboard），和 Maya scene Undo 分开；关闭窗口前明确保存 JSON，否则内存数据丢失。变更窗口/选择不表示生产动画重定时已验证。源帮助/关于原文保留，因此结合本说明理解其边界。

## 影响、依赖、组合与验收

标记编辑仅返回新数据或更新窗口内存，local Undo 可恢复窗口文档；文件、播放状态、时间和窗口关闭是不同影响，不以继承 UndoChunk 承诺完整可撤销。API不新增场景节点；基础/增强GUI使用 Maya原生cmds，窗口快捷键使用Qt5/Qt6，缺窗口pointer时保留菜单可用并提示。整个GUI/滑块/shortcut焦点/大范围滚动/真实播放未实测，跨Maya版本待验收。

没有与 core 重复的场景动画算法；可用输出 JSON 作为其他工具的计划输入，但没有自动将 K/B 方块转换为真实 key/breakdown，也未验证组合工作流。原自有脚本无独立许可文件，保留出处与原完整说明。晋级清单携带全部代码、原件、说明、测试和面板注册；真实 Maya 验收前留在待整理池。
