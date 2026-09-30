# 动画层关键帧区间书签生成器

工具 ID：`anim_layer_keyframe_bookmark`；类别 Animation；候选版本 1.1.0。
来源是同名单元的自有 Python/README，完整原文保存在运行包 `upstream/`，原始文件未修改。源文件未提供第三方许可，本轮不额外声明第三方授权。

## 用途与条件

将一个动画层上所选对象的键时间合并，每两个相邻时间生成一个 Time Slider Bookmark。四色板保持原始 RGB 值，按列表循环交替；相邻新书签颜色不同。工具还提供检查键时间与清空全部书签的 API。

创建/删除需要已加载 Maya 内置 `timeSliderBookmark` 插件并已启用 Undo；预检不加载插件、不改变 writeRequires、不创建/删除书签、不改键、时间或选择。API 运行前明确 `cmds.loadPlugin('timeSliderBookmark', quiet=True)`；UI 启动时明确加载插件。inspect 查询不需要该插件或 Undo。依赖 cmds、Python 3 和现有 framework/core，资源无第三方 Python 包或待整理池路径依赖。

## 参数

| 参数 | 默认 | 含义 |
| --- | --- | --- |
| action | generate | generate 创建、clear 删除全部书签、inspect 查询关键帧 |
| objects | null | 当前选择；支持唯一节点名或非空节点名数组，去重，拒绝组件/歧义名 |
| layer | auto | 当前高亮自定义层优先，否则 BaseAnimation；也可指定具体层或 All |
| palette_name | dual | dual/vibrant/pastel/cyberpunk，四套原始色板 |
| prefix | BM | 非空显示名前缀，最多 240 字符 |
| clear_existing | false | 生成前删除场景全部书签，不按对象/前缀/动画层筛选 |
| max_bookmarks | 10000 | 创建数量上限，整数 [1,100000] |

上述参数均接受真实类型检查，不只靠 Schema；未知参数、无效层、无效色板、错误类型、非有限键时间与数量超限会失败。generate 至少需要两个不同时间；未满足时，即使 clear_existing=true 也不得删除旧书签。clear 不需要选择对象；inspect 可以返回空键列表，成功并 count=0。

对象可来自引用或锁定节点，因为只读键时间；本工具不修改控制器曲线。删除前检查所有待删除书签，引用或锁定节点会阻止整次删除/替换，避免静默跳过。clear/clear_existing 是全场景作用，不仅清理本工具创建的书签。API 默认保留旧书签，原 UI 的“生成前清空场景所有已有书签”默认勾选保持不变，操作前应看清该选项。

## 键、区间、颜色和名称

通过可动画属性的 findCurveForPlug 精确查每层曲线；规范 Maya 单字符串返回。有层时基础动画不借其他层曲线回退；无层时只查对象属性直接 animCurve 连接。All 逐层合并，支持时间驱动 animCurveTA/TL/TU/TT。本工具不加播放范围过滤，使用该层所有键时间。

保留原四位小数四舍五入和完全相同时间去重；不同于 anim_layer_key_runner，本工具**不使用 0.001 帧容差合并**，例如 1 与 1.0005 仍生成很短的区间。精度低于四位小数的差异可能合并。相邻区间共享端点，每个新书签 start/stop 保留这些浮点时间；priority 按新列表从 0 开始。

原显示名格式 `{prefix}_{int(round(start))}_{int(round(stop))}` 保持不变，因此子帧区间可能显示为 BM_1_1 或不同区间出现相同显示名；节点名由 Maya 自动分配，不等于显示名。新旧书签可能复用节点名，删除计划同时记录 UUID，异常报告按 UUID 判断原节点是否已删除。默认不清空时重复执行会新增书签，非幂等；新书签颜色交替不保证与已有邻接书签颜色不同，也不检测旧书签重叠。

## 返回、场景影响与撤销

正式调用用继承的 `run(dry_run=False, **kwargs)` 或转正后的 `maya_toolkit.execute_tool`，返回 ToolResult；`dry_run=True` 返回计划而不写场景。

data 含 action、objects、layer、curves、keyframes、intervals（name/start/stop/color/priority）、deleted_bookmarks 和 deletion_targets（node/uuid）。count 在 generate 为计划/实际创建数，在 clear 为计划/实际删除数，在 inspect 为键时间数。执行额外返回 bookmarks 和 created_bookmark_uuids。失败可能已创建一个仅部分属性配置的节点，bookmarks/count 代表已创建节点，不能当作完成配置的数量；success/errors 决定是否成功。

创建使用 skipSelect 保持对象选择；不切换当前时间，不修改原动画。清空若删除了选中的书签，自然会影响选择。框架 UndoChunk 包含删除和生成，一次 Undo 撤回整次场景修改。异常不自动回滚，返回部分创建/删除信息，应检查并 Undo。

创建时沿用原脚本的 pluginInfo(writeRequires=True)，保证插件保存要求；这是插件会话设置，Maya Undo 不保证恢复它。插件加载同样不能当作场景 Undo。工具自身不保存/导出场景、没有文件写入或覆盖；书签节点随后由用户保存场景。真实 GUI 的书签显示、颜色辨识和点击行为仍需人工验收。

## 示例与复用

转正后：

```python
import maya.cmds as cmds
import maya_toolkit
cmds.loadPlugin('timeSliderBookmark', quiet=True)
args = dict(objects=['ctrl_root'], layer='Walk', palette_name='vibrant',
            prefix='步行', clear_existing=False, max_bookmarks=200)
preview = maya_toolkit.execute_tool('anim_layer_keyframe_bookmark', args, dry_run=True)
if preview.success:
    result = maya_toolkit.execute_tool('anim_layer_keyframe_bookmark', args)
```

候选阶段通过 launch_candidate.py 的 load_tool()，不注册候选进正式面板。窗口保留层刷新、四色板、命名、生成、清空、检查控件；三种操作都调用框架。检查按钮先列键，再在键足够时打印生成/删除预检；若删除检查失败明确显示，不偷偷执行。

复用已有 BaseMayaTool/ToolResult/UndoChunkContext。层查询采用逐帧候选已经审阅/隔离验证过的逻辑，复制为本运行包内独立模块，并保持本工具的精度规则；正式包不导入其他候选或待整理路径。公共 core 本轮未改动。后续是否下沉层查询，仍须考虑两工具不同去重契约。

输出的 bookmark 节点/区间可供 anim_layer_bookmark_trimmer 查询，是自然的候选组合：生成相邻键区间后，修剪器 all 模式保留这些边界；重新优化会改变动画效果。该跨工具组合需单独真人验收，不将共享查询或静态导入视为已验证组合。

## 演进与验证

保留四色板、显示名、priority、四位小数键时间和原生 UI；修复基础层混入其他层键/长短节点名历史匹配漏选，改为确切层属性查询。补 generate/clear/inspect Schema、无写入预检、数量上限、锁定/引用删除检查、部分失败记录和 UUID 身份；插件加载移到显式启动。直接“清空所有书签”现在也走框架 UndoChunk，原入口没有额外统一分组。创建 skipSelect 避免原 createNode 改变选择。

离线 8 项测试覆盖参数/Schema、原色板、循环边界、子帧命名、非法区间、原档一致和 UI 路由；Maya 2025 隔离 8 项测试覆盖四种色板、预检查询、层/全层、清空/替换 Undo、空键/上限、锁定书签、插件未加载及部分属性写入失败。真实窗口/时间滑块、引用书签删除、其他 Maya/Python 版本仍待验收。
