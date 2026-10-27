# 动画层书签修剪与曲线优化器

工具 ID：`anim_layer_bookmark_trimmer`；类别：Animation；候选版本：1.1.0。
来源是待整理池同名单元的自有 Python 脚本与 README，完整原文保存在运行包 `upstream/`，该存档不会被自动执行。原文件未提供第三方许可证；本轮按自有工具整理，不额外宣称第三方再分发授权。

## 用途与运行条件

在一个动画层上按 Time Slider Bookmark 保留端点关键帧，或在各书签区间优化连续动画曲线。目标须有匹配的时间驱动 `animCurveTA/TL/TU`，书签插件 `timeSliderBookmark` 已加载，Maya Undo 已启用。预检不加载插件、建窗口、打关键帧、写文件或修改选中对象。

API 使用前可明确执行 `cmds.loadPlugin('timeSliderBookmark')`；候选窗口启动时会加载该插件，这属于启动准备而非 dry_run。无第三方 Python 数值库依赖。Python 3 适配；Maya 2025 mayapy 已验证部分行为，真实窗口、其他 Maya 版本与 Python 2 未验证。

## 参数

| 参数 | 默认 | 作用 |
| --- | --- | --- |
| action | trim | `trim` 修剪；`optimize` 优化 |
| objects | null | 当前选择；也接受单个节点名或非空节点名数组。歧义名、组件、引用或锁定节点拒绝 |
| layer | auto | 当前选中的非基础动画层优先；否则 BaseAnimation；可指定层名 |
| scope | all | `all`、`playback`、`selected`，详见范围语义 |
| mode | smooth | 六种优化模式，仅 action=optimize 使用 |
| strength / bias | 0.5 / 0.5 | 有限数值 [0,1]；偏置调节缓动分布 |
| include_translate / include_rotate | true / true | 位移、旋转通道 |
| include_scale / include_others | false / false | 缩放、其他连续浮点属性；other 与位移旋转可同时生效 |
| channel_box_priority | true | 有 Channel Box 高亮时优先使用该属性集合，仍排除离散属性 |
| ensure_keys_at_bounds | false | 修剪前插入缺少的端点键；false 时不会凭空保留不存在的端点键 |
| ease_bounds | true | smooth/simplify/tangents 可叠加端点缓动；ease/multikey_ease/smart 自带缓动 |

所有参数有 JSON Schema，执行前另行检查类型、非有限数值、未知参数、插件、对象、层、曲线锁定/引用、输出连接和键数据。无匹配曲线会失败，不改其他层兜底寻找。优化拒绝时长 ≤0.002 帧或实质重叠的书签，避免后一个区间修改前一个区间的内部端点。

## 范围与优化语义

`all` 修剪会删除整条所选曲线上除全部书签端点以外的键，包括书签之外的键。`playback` 选择与播放范围相交的**完整书签**；修剪范围是这些书签的最早起点至最晚终点，包括中间空隙，不裁切到播放边界。`selected` 优先用时间滑块框选范围选书签，其次使用光标所在书签；无命中时沿用原脚本的最近书签回退。批处理环境没有时间滑块，使用光标回退。优化对各匹配书签分别操作，中间空隙的键值不直接重塑。

六种模式保持原算法：smooth 为非均匀时间加权平滑；simplify 调用 Maya simplify；multikey_ease 按 Smootherstep/Bias 重塑内部键值；ease 也会重塑内部键值并设置端点切线，并非仅修改手柄；tangents 设置 spline，默认还叠加 ease；smart 顺序执行平滑、抽稀、多帧缓动、切线与端点缓动。

优化会插入缺失的书签端点，保留**本层曲线**在该时刻的值。这不等于动画层混合后的世界姿态锁定。端点切线可能被改，部分模式还设置整条曲线的 weightedTangents，因此范围外插值可能改变，即使范围外键的时间和值保持不变。力度为 0 仍可能插入端点或修改切线；ease_bounds=false 不会关闭 ease/multikey_ease/smart 自带的缓动。重复执行可能继续改变值和手柄，非幂等。

## 返回与影响

外部通过继承的 `run(dry_run=False, **kwargs)` 或转正后的 `maya_toolkit.execute_tool` 调用，返回 `ToolResult`。`data` 保留原脚本统计，并补充 `curves`、`bookmarks`：修剪预检含 `keys_to_delete`，执行含 `deleted_keys`、`remaining_keys`；优化含 mode/strength/bias，预检给内部键估计，执行给 smoothed_points/simplified_keys/eased_multikey_count/eased_bounds_count。统计里的帧列表是各曲线合并去重的时间点，不能当作逐曲线键数。优化统计是原算法计数，不保证对应唯一实际变化键数。

`dry_run` 不承诺优化后的精确数值，只查询范围与估计。执行使用框架外层 UndoChunk，原内部 chunk 嵌套；一次 Maya Undo 撤回整次场景操作。异常会返回失败，不自动回滚；应检查场景并 Undo。无文件导出/覆盖、无外部文件写入。窗口的刷新与控件显示只影响 UI。插件加载不能等同于场景 Undo。

## 示例

```python
import maya.cmds as cmds
import maya_toolkit
cmds.loadPlugin('timeSliderBookmark', quiet=True)
args = dict(action='optimize', objects=['ctrl_root'], layer='Walk',
            scope='playback', mode='smooth', strength=0.35,
            include_rotate=False, channel_box_priority=False, ease_bounds=False)
preview = maya_toolkit.execute_tool('anim_layer_bookmark_trimmer', args, dry_run=True)
if preview.success:
    result = maya_toolkit.execute_tool('anim_layer_bookmark_trimmer', args)
```

以上为转正后示例。验收前使用 candidate `launch_candidate.py` 的 `load_tool().run(...)`，不修改正式注册表。

## 复用与组合

复用已有 BaseMayaTool、ToolResult 和 UndoChunkContext；书签、层查询与本业务算法保留在工具包，没有充分理由改动公共 core。可以先预检修剪，再选定一种优化模式；两次调用各有 Undo 分组。与 anim_filters 的连续曲线滤波存在用途交集，可将本工具返回的曲线与明确时间范围作为候选输入，但 Graph Editor 选择协议不同，不能仅凭静态 import 宣称两者组合已通过 Maya 实测。`fix_rotation_winding` 与曲线平滑也应按各自输入约束单独预检。

## 演进与验证

1. 原算法和原生控件拆分到 operations/native_ui，四个操作入口统一经过框架预检。
2. 查询不再隐式加载插件；UI 启动明确准备插件。
3. 修复单字符串曲线返回的遍历、other 通道与标准通道同时勾选的漏选；无层时基础动画只查询直接 animCurve 连接，禁止跨层兜底。
4. 缺少端点的优化预检改为曲线求值，避免空列表索引，内部键按实际开区间计数；端点插入失败直接报告，不再吞掉。
5. 书签范围、最近书签回退、全曲线加权切线和重复运行影响在文档中明确；重叠/退化区间预检拒绝。

离线 `tests/test_anim_layer_bookmark_trimmer.py` 检查输入与 Schema、无加载查询、曲线筛选、错误传播、资源原样与四个 UI 操作的框架路由。Maya 隔离测试检查修剪/优化、六模式、缺端点、通道排除、局部范围、双向层隔离及单步 Undo。测试只使用临时 scene，不创建真实 GUI；候选仍须按 acceptance.md 验收，不能据此转正。
