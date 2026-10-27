# BB Tools 完整套件候选

`tool_id=bb_tools`，分类 `rigging`，类 `BBToolsTool`。本包只位于待整理池；真实 Maya GUI 验收为 **not_run**，不可把隔离 mayapy 的编译或单测当成转正验收。

## 来源与完整性

原始 `bb_Tools/` 的 81 个文件、图标、QC Word 说明、权重 XML、ADV 的三份 `.ma` 资产全部逐字节复制到 `vendor/`，SHA256 记录在 `catalog.json`。主工具选择 `Script/` 内的版本，与原主面板菜单一致；根目录旧版重复脚本、安装脚本和 QC 旧目录仍完整归档，不加载安装器，不改 Shelf、userSetup 或系统脚本搜索路径。`DelDJJ.mel` 和 `OutlineError.mel` 的重复功能由最新 `bb_FixError.mel` 保留；独立原文件也归档。

保留 LiuBen、Nilesh Jadhav、CGTOOLKIT、Brendan Ross、Crow Yeh、Highend3D 等原始头部和版权信息。未找到适用于整个集合的单独许可，不能从下载元信息推导公开再分发权，本次未发布、购买或改写版权。

31 个活动 MEL 文件的原 297 个过程全部保留，JB PerVert 的顶层界面单独包装为显式入口，因此候选另增加一个界面过程。完整业务涵盖重命名、批量约束/蒙皮/连接、控制器、属性、曲线、BS、QC、ADV 修复、FBX 引用转换、纠正形状、对称、权重到变形器、毛囊、动态链、softMod、选择、历史、蒙皮列表、贴图管理和批量复制。被原面板注释的自动裙摆及附带 masterCreate、PerVert 可通过 `runtime.show_member(member)` 明确启动；菜单路径见 `inspect` 的 `entries`。

## 适配与行为变化

- 活动过程名和回调中的过程引用加 `bbstg_` 前缀，避免覆盖旧版及第三方 MEL 过程。原过程名称仍用于 API 参数与清单检索。原原始控制名、optionVar、场景命名约定保留；旧原界面与候选界面不要同开。
- 候选 MEL 保存 UTF-8，通过 Python `mel.eval` 传入 Unicode 定义；主菜单直接调用已加载的过程，QC/ADV 的依赖也提前加载。Windows Maya 的 `source` 对 UTF-8 中文出现未闭合字符串错误已在隔离检查中复现并修复。资源根目录由候选模块定位，支持搬到正式库后使用，不再分割 `whatIs` 的路径或依赖待整理池路径。
- 移除原自动打开界面的顶层调用；`validate` 和 dry-run 不 source/eval、不创建临时目录、不注册 Python bridge、不打开 UI。实际执行时才加载全套声明。加载会初始化原 MEL 全局变量，不修改场景。
- 权重转换每次使用本会话独立临时子目录；不覆盖随包 XML，不写正式工具目录。只允许删除该工具拥有的 `bb_skin2Deform_weight*.xml`。转换算法、XML 权重拆分和 index 导入仍来自原过程。
- QC 配置写入先独占创建新 `.bb` 文件，拒绝覆盖。导入配置前检查全部行；只接收固定的六个 checkBox、四个 textField、两个 textScrollList 的数据命令，转为 `cmds` 写 UI 值，禁止任意 MEL/Python 执行。原配置字段保留，保存时转义字符串。临时配置菜单存于本会话目录；需长期留存时导出到用户选择的目录，下次用加载配置按钮导入。
- FileTextureManager 的 Copy/Move/Set、自动/手动目录、替换、前后缀及 UI 算法保留。原 `system` 被解析为限定的 mkdir/copy/move 文件操作，无 shell 执行；每个目标拒绝覆盖，复制核对 SHA256，再移除原文件。失败可能保留已完成的文件；不承诺整批原子回滚。
- FixError 的 Outliner 修复改用 `maya.cmds`，无需额外 PyMel。保留模型编辑器回调清理。病毒清理改为明确的文件列表：用户选择具体 vaccine/userSetup 文件和已有隔离目录后，保留校验过的恢复副本再移除原文件，拒绝覆盖；不再按文件名直接删除个人 `userSetup.py`。场景感染节点有单独可 Undo 按钮。隔离与 UI 回调修改无法用场景 Undo 恢复。

## API、Schema 与输出

继承 `BaseMayaTool`，实现 `validate(**kwargs)`、`execute(**kwargs)`；外部使用继承 `run(dry_run=False, **kwargs)` 或转正后的 `maya_toolkit.execute_tool`，输出 `ToolResult`。Schema 可经 `to_openai_tool` / `to_mcp_tool` 导出。

| 参数 | 含义 |
| --- | --- |
| `action` | 默认 `inspect`；返回全套过程、参数类型、原路径、资源、直接作用和界面入口；`call` 执行一个声明过的全局过程 |
| `procedure` | 原始全局过程名称枚举，不接受任意 MEL，也不导出 local 过程 |
| `arguments` | 原始签名的有序类型化参数；有界整数/有限数、字符串和数组，拒绝控制字符与命令转义 |
| `objects` | 有序唯一完整节点；默认当前选择。拒绝组件、通配符、重名、实例；写调用拒绝引用/锁定节点与形状 |
| `allow_scene_scope` | 默认 false。六项已检查的 API 子集以外需 true，并且只能在交互 Maya 中执行；表示原过程可能扩展至连接节点、层级或全场景，不构成范围隔离保证 |

六项无 UI API 子集：`bb_CtrlTool_createShape`、`bb_CtrlTool_changeColorApply`、`bb_attr_addAttr`、`bb_returnSkinList`、`wpRename_js_replaceHash`、`bb_QC_shapes2transforms`。后面三项读取原数据/算法；写接口通过 Base 的 UndoChunk 分组。`bb_attr_addAttr` 的 `attrInfo` 是六个字符串：`[name, type, minOrEnum, max, minEnabled, maxEnabled]`，类型为 Int/Float/Boolean/Enum。Enum 用逗号分隔简单标签。控制器可用 16 个 `CtrlShape_*` 样式，颜色索引 0..31；新名称和既有属性受保护，锁定或受驱动的形状覆盖颜色受保护。

调用结果含 `native_result`、实际原过程产生的选择、创建节点 UUID、预检范围、签名及影响描述。API 保存时间、选择 UUID、namespace 和 AutoKey 并在 finally 恢复。原界面交互则保留原操作的选择和 UI 意图；界面回调不经过 `Base.run`，其具体 Undo 行为需人工检查。不要把直接作用的静态列表当完整的传递影响分析。

```python
tool.run(dry_run=True, action="call", procedure="bb_CtrlTool_createShape",
         arguments=["CtrlShape_cube", "main_ctrl"])
tool.run(action="call", procedure="bb_CtrlTool_createShape",
         arguments=["CtrlShape_cube", "main_ctrl"])
tool.run(action="call", procedure="bb_CtrlTool_changeColorApply",
         arguments=["main_ctrl", 13], objects=["main_ctrl"])
tool.run(action="call", procedure="bb_returnSkinList",
         arguments=["body"], objects=["body"])
tool.show_ui()
```

## 使用条件、影响与组合

ADV 方法按原 AdvancedSkeleton 5.74 名称/层级编写；用三份附带资产，但不代表支持任意角色。FBX 面板主要执行引用加载、转换、解除连接和 Bake，原脚本没有独立最终 FBX 文件导出按钮；不可宣传成新增的通用 FBX 导出器。它可能扫描全场景关节/BS/locator、移除旧引用、修改 upAxis，`delete -icn` 会删除输入节点，使用备份场景。需要 Maya 自带的 fbxmaya，候选不安装插件。

QC 清理、历史删除、父子关系更改、动态链、毛囊、权重导入、softMod 和绑定均可影响原生业务对象以外的连接/子层级。全套按钮仍需逐项真实 Maya 验收。界面、scriptJob、optionVar、运行时插件、引用和文件副作用不都归入普通 Maya Undo；错误不会自动 rollback，检查局部结果后 Undo，外部文件按记录恢复。

控制器生成结果可传给候选 BB 色彩/属性接口；蒙皮骨骼查询结果可用于用户明确选择的后续绑定/权重工具。这里是输入输出兼容说明，跨工具自动组合尚未实测。现有 `core` 已有 Undo/DAG/mesh/skin 能力；候选复用正式 Undo 和框架契约，完整 MEL 算法保留在工具包，未提前下沉 core 或改变正式注册表。

## 已做检查与待验收

隔离 Maya 2025 可编译完整活动定义，无原自动 UI 及场景写入；实际创建全部 16 种曲线、单次 Undo/Redo，验证颜色、Float 属性上下限、编号零填充、真实 skinCluster 骨骼查询，以及锁/名称/交互过程预检拒绝。普通 Python 检查完整资源散列、类型/MEL 注入拒绝、临时文件范围、复制/移动/覆盖保护、限制 QC 数据。正式目录模拟检查注册、Schema、分类、面板入口和不依赖 staging 路径。

真实 GUI、多版本 Maya、ADV 5.74 生产角色、FBX 引用替换、QC UI 保存往返、纹理批处理、动力链/权重拆分、感染样本检测及每个原按钮均 not_run。详见 `acceptance.md`。本包是最终代码候选，实测发现问题时只修对应候选，验收通过才由晋级脚本迁入正式库。
