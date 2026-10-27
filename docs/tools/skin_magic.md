# SkinMagic 4.0 最终候选

状态：`prepared_unverified`。完整候选留在待整理池，未通过真实 Maya GUI 验收，未进入正式库。本机 Maya 2025 的 PyMel 缺失；批量权重 API 可用原生 cmds，完整原界面/LoD/Gore/Wrap 等算法必须在兼容 PyMel 的真实 Maya 中验收。不安装假依赖，不把 UI 资源检查算作 GUI 通过。

原作者 Yanbin Bai；原版 `version=40000`，自述测试 Maya 2014/2016/2020。原包 41 个文件、250 个函数定义（包含同名重复定义），全部归档并记录 SHA256，原始目录不改字节。没有单独许可文件；不推断发布权限。候选私有 Python 3 模块保留全部现有业务，而非只包装一个启动器；`native/skinMagic.py` 的来源覆盖和 `catalog.json` 可核对。

## 完整能力

| 原业务 | 输入与设置 | 输出 / 影响 |
|---|---|---|
| 权重工具 | 已蒙皮网格顶点、原界面的骨骼列表、0/0.1/0.25/0.5/0.75/0.9/1、自定义值 | 设定、增减、归一化、复制粘贴、平滑、裁剪、影响数检查、范围与连通选择 |
| 镜像与交换 | 原界面 X/Y/Z 方向、正负方向、部分顶点、交换骨骼 A/B | copySkinWeights、部分镜像、转移、交换/合并；Bind Pose 会影响连接的骨架 |
| 骨骼与显示 | 原界面添加/移除骨骼、选加权骨骼/顶点、颜色代理 | skin 影响与顶点颜色辅助；代理只按本会话 UUID 清理，恢复显示属性 |
| 文件 | `.VertexWeight` / `.BoneList` 安全 JSON，或 Maya XML | 权重及 LoD 映射往返；独占导出，不覆盖；外部文件不属于 Undo |
| LoD | 源/可选目标、删减骨骼→接收骨骼映射、批量、删除源/骨骼选项 | 合并权重、绑定目标、减少影响、可删除骨骼子树及源网格；只在备份场景验收 |
| Gore | `show_gore` 补充界面，源网格与目标列表，删除源选项 | 保留原 Gore 完整算法：清目标历史、绑定并复制源权重；原包未提供这些控件 |
| Rename | 搜索替换、大小写、前后缀、插入位置、序列模板、选择/层级/全场景 | 改名及预览；全场景须明确允许并列出范围，GUI 会显示确认节点数 |
| Misc | Bind Skin+、缩放关节、清自定义属性、网格清理、清非skin历史 | 原业务完整保留，可能丢失历史/用户属性，使用备份 |
| Deformer / BlendShape | 源/目标、时间段、选中网格/变形器、源 BS 与蒙皮选项 | 原 BBF_DeftoSeq MEL、Wrap 生成目标 BS、蒙皮转移；恢复源 BS 权重，拒绝与既有目标名字冲突 |
| Weight map | 已蒙皮网格与可选骨骼 | 原布局/颜色/标签完整输出；新着色器，不复用同名外国节点，不删除其他 annotation |
| UI | 原 4 套语言、原控件/图标、Gore 附加窗口 | callable 回调使用私有模块，不把函数塞进 `__main__`；支持显式 shelf 按钮 |

原文件还带 Spring 回调，但没有 Spring 算法、控件或标签页；候选保留这些不可达名字并返回明确缺项错误，未伪造 Spring 功能。需要弹簧算法时用独立 Spring Magic 候选，组合关系尚未实测。原 `testCmd` 缺失，改为状态信息；原 weightToolOn、loopSelection 缺失，分别接原 UI 更新和 Maya 原生边循环。Gore 的原算法在本包内，补充窗口让其完整可操作。

## 统一接口

继承 `BaseMayaTool`，`validate(**kwargs)` 仅生成只读计划，`execute(**kwargs)` 由基类 `run(dry_run=False, **kwargs)` 在 Undo Chunk 中调用，输出 `ToolResult`。category=`rigging`。注册和面板接入已在晋级清单预制；目前不修改正式注册表。Schema 导出支持 OpenAI/MCP，实际校验在工具内实现。

| action | 参数 | 返回 |
|---|---|---|
| `status` | 无 | 版本、资源/函数数、可调用 GUI command、PyMel 是否存在、GUI 验收 `not_run` |
| `inspect_skin` | `objects` 可省略使用选择；单网格或不重叠顶点 | 网格、唯一 skin、影响、逐顶点实际权重 |
| `set_weights` | `objects`；`weights={joint:weight}`，有限 [0,1] 且和=1 | 只修改指定顶点，未列影响清零；单次 Undo 恢复 |
| `export_weights` | `objects`；绝对 `path`，父目录已存在、目标不存在 | 完整精度 JSON，写入路径和顶点数；不改权重 |
| `import_weights` | `objects`；绝对 `path` | 对指定目标按顶点索引匹配源；拒绝文件索引超出所选目标、缺失/歧义/未绑定影响；单 Undo 恢复 |
| `show_ui` | `language='' / chn / eng / jpn` | 完整原 UI 窗口；需要真实交互式 Maya 和 PyMel |
| `show_gore` | 无 | 原 Gore 算法的补充窗口 |
| `ui_command` | `command` 为 Schema 中的枚举；可选 `allow_scene_scope` | 在已打开的本候选 UI 上调用完整原按钮业务，使用当前选择和界面已加载输入/缓存/设置；返回范围与结果选择 |
| `close_ui` | 无 | 关闭自有窗口、scriptJobs、代理，恢复打开前选择优先级 |

UI 命令的对象、比例、方向、时间、LoD 映射等来自已打开的原控件；不把任意 Python 函数/代码当参数。`objects` 只用于批量权重 action；需要从自动化选择 GUI 输入时，先显式选择场景对象，再调用对应 Load/Get 按钮 command，预检检查选区和已加载输入。`ui_command` dry-run 返回 `affected_nodes`，包括历史、skin 影响、LoD/Gore/BS 缓存和可能受 Bind Pose/骨骼删除影响的范围；不打开 UI，不切选择，不写权重/文件。

```python
from maya_toolkit.tools.skin_magic import SkinMagicTool
tool = SkinMagicTool()
args = dict(action='set_weights', objects=['body.vtx[0]'], weights={'root':0.4,'tip':0.6})
preview = tool.run(dry_run=True, **args)
if preview.success:
    print(tool.run(**args).to_dict())

tool.run(action='show_ui', language='chn')
# 在原界面加载 LoD 源、骨骼和接收者，检查删除选项后：
print(tool.run(dry_run=True, action='ui_command', command='lodMakeButtonCmd').to_dict())
# 用户在备份场景执行相同参数。
```

候选阶段先通过根目录 `launch_candidate.py` 的 `load_tool()` / `show_ui()` 加载，以免依赖仍未晋级的正式路径。晋级后统一 `maya_toolkit.execute_tool('skin_magic', args, dry_run=True)`。shelf 按钮仅在用户点击时创建，不执行原 installer；工作路径由候选或晋级后文件位置确定。

## 安全数据与行为变化

`.VertexWeight` / `.BoneList` 后缀继续使用，内容改为 UTF-8 JSON：`{"format":"skin_magic/1","kind":"weights","data":{"mesh.vtx[0]":[["joint",1.0]]}}`；LoD 为 `kind="lod", data={"removeJoint":"receiverJoint"}`。读取最多 64 MiB，仅数据，不执行 pickle/eval。**旧 pickle 文件不兼容**；只能在可信原运行环境先导出权重数值/字符串骨骼名，按上述格式转换，不由候选自动反序列化未知文件。原 GUI 导出仍按原算法四舍五入到两位，批量 `export_weights` 保持完整浮点精度。JSON 权重记录按索引重映射目标网格，顶点数量/布局和 Bind Pose 是否相符须人工确认；它不是最近点传权重。

XML 使用 Maya 原生 deformerWeights，输入查实体声明、影响、顶点数及点值。导出先在私有临时目录产生，再以 `xb` 独占写外部目标；内部 LoD/BS 等临时 XML 只在本操作目录使用，操作结束清理。已有 skin XML 导入先捕获完整权重，原生命令后 API 恢复原值，再用可撤销 skinPercent 回放导入值；隔离 mayapy 测试证明 Undo 恢复。跨版本仍须实测。

移除了导入时自动 UI/网络、切换语言覆盖 `.ui` / execfile、按 `annotation*` 全局删除、LoD/Gore 自动删除全场景未使用材质、按别名删除既有 BS 目标、按未知后缀搜索清理颜色代理。Unknown 删除仅限明确选中的 unknown 节点。UI 更新查询不改 weightDistribution；关闭恢复原选择优先级而非写死默认值。内部“Undo 两三次”改为目标权重快照恢复和删除确切临时网格；API/GUI 外层统一 Undo 分组，原代码不再撤销用户历史。恢复 Auto Key、当前时间、影响锁、视图 isolate 状态和源 BS 权重；场景失败可能已产生部分修改，应检查并 Undo 本次操作，不声明自动事务回滚。

只读源保留；批量写入拒绝引用、锁节点、实例、歧义/别名重复、不合适组件或锁住影响。完整 UI 的写入预检会保守拒绝范围内引用/锁节点；复杂生产 rig 的动画层、连接、约束、保留历史/拓扑行为仍需真实备份场景验收。

## 复用与组合

复用现有框架 `BaseMayaTool` / `ToolResult` / Undo Chunk；不改 core。项目当前公共层没有与 SkinMagic 完整 PyMel 套件等价的权重/LoD/Wrap 引擎；为保持原行为，将全部算法作为本工具私有运行时。与 Skin Info / Timal 的文件和权重能力重叠，但格式、精度、默认关联和影响范围不同，不强行替换原逻辑，也不依赖其他待整理候选的路径。

可在批量绑定后执行 inspect/export，在权重确认后执行 LoD/Gore，再导出；Schema 和本说明支持选择这些步骤，但尚无真实生产组合验证。LoD 删除骨骼可能影响共享其他 skin，预检列出连接范围，不把静态依赖当组合通过。

测试：`tests/test_skin_magic.py`（原文件指纹、250函数保留、4 UI/101回调/图标闭包、严格参数、安全 JSON/XML、原纯字符串算法）；`tests/test_skin_magic_maya.py`（隔离真实蒙皮、权重写/只读计划、文件保护、JSON/原生 XML 导入撤销、范围/锁/实例/GUI依赖拒绝）。真实 GUI、PyMel 引擎、Gore/LoD/BS/代理与生产 rig 均 `not_run`。
