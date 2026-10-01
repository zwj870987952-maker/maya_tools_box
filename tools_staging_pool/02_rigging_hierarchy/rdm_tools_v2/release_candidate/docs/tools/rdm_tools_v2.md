# RdM Tools v2

用途：完整旧版骨骼、自动绑定、面部、蒙皮、控制器、Picker和节点辅助套件。原出处renderdemartes，ShowUI注释提供EULA链接，当前无法读取该页面；保留原出处与全部版权/注释，不推断公开再分发权利，本次不发布或购买。原164文件完整SHA归档在vendor，包括86份Python的.py.original、原MEL、两份主UI/Picker UI、全部图标、PDF/docx手册、安装说明和外层启动文档/图片。native是可运行Python3候选，不依赖用户scripts目录或旧安装路径。

## 完整功能保留与兼容变化

86个Python模块、126个模块函数、3个界面类及全部方法保留；全功能主界面与原原型Picker不是简化替代。catalog给出每个原模块的函数签名、默认值、required参数数、类方法、内部依赖和显式脚本动作。范围包括：

- AutoRig与AutoRigV2：FK/IKFK脊柱、头、手臂、腿、手指、FootRoll、完整组合/连接、改进部位、蒙皮入口。
- 曲线与显示：11种Joint/Locator/Circle XYZ/Sphere/Cube/Hand/Foot/EyeVisor/Pringle控制器，Box/Fist/Foot独立脚本、Root/Auto/Offset组、滑条/文字曲线、颜色与骨骼轴/显示。
- 工具：SimpleFK、IKFK、Twist/Bendy Ribbon、MirrorBehavior、约束/连接/匹配、重命名/前后缀/搜索替换、属性显隐/Global属性、参考平面/follicle/JointResizer。
- Skin/Blend/Nodes/Quadruped：bind/mirror/move绑定骨骼、influence查询、SkinHelp、四肢IKFK/隔离头、节点属性辅助、四足脚/腿。
- Facial：顶点关节、edge curve、face/NURBS、额外面部骨骼/控制器、嘴部与眉毛系统、blendshape辅助。
- 完整主Qt界面与Picker、曲线JSON导出与可选UI→Python开发导出、原所有资源与手册。

Python2 print/long/迭代等完整转成Python3，原混合tab依8列展开以消除TabError。原AddRemoveJoints含无法解析的cmds.skinCluster=(...)及漏导入mel；仅在候选改为cmds.skinCluster(SkinCluster,e=True,lw=True,ai=joints)并补导入，原件SHA不变；该工具的真实蒙皮修改仍not_run。

原导入会直接运行cmds.curve/create/delete/选择/场景读取或示例；候选模块导入仅定义函数/类和字面常量，所有其他语句按原顺序保存到显式run_script，原__main__ UI块也成为显式动作。run_script重置原常量后重放，避免重复JSON导出累积旧数据。原GUI reload改为legacy_reload：定义已加载，再显式执行原脚本动作，避免首次import+reload双次创建。完整函数算法没有删减；原脚本中的演示/固定rig名仍需单独审阅，不能仅因模块名为工具就执行。

全部内部RdMToolsV2 import重定向到本候选私有native包，避免覆盖外部同名安装。Qt6/PySide6+shiboken6优先、Qt5/PySide2回退；QDialog默认parent=maya_main_window()改为构造时才读取Maya父窗口，不在import时读取/创建GUI。主界面RmdTools_Path由随包路径模块替代，不写用户RmdTools_Path.py；internalVar(usd)资源定位也改为随包native。主界面所有控件引用已与RdMV2.ui对象名静态对齐。

原ImportLegacy按钮需要另一个未随原包提供的RdMTools.RdMMenu；旧PickerUI的RdMTools/icons/ModelJesusRef.png和通用QT/LoadUI_Py模板Folder/name.ui也未随原包提供。这些旧独立入口保留并列缺失依赖，不声称已补齐作者未交付资产；主RdMV2.ui与完整自身Resources存在。原PyMel算法不伪造替代，本机Maya2025无PyMel，相关AutoRig/Facial等需在真实环境准备依赖后验收；可选UItoPY还需要pyside2uic。没有安装依赖或执行原安装器。

## API、输入与结果

候选launch_candidate.py的load_tool()取得RdmToolsTool，show_ui()显式打开完整RdMV2主界面；晋级后通过maya_toolkit.execute_tool('rdm_tools_v2', arguments,dry_run)。注册/rigging域/面板接口已预制且只在临时未来布局验证。

| 参数 | 条件 | 含义 |
| --- | --- | --- |
| action | inspect默认 / call / script | 完整清单、调用原函数、显式运行原导入脚本 |
| module | catalog枚举 | 原完整模块名；run_RdMTools安装模块不能调用 |
| function | call必填 | catalog中的原模块函数；不接受eval或任意代码 |
| arguments | call命名参数对象，默认{} | 精确原签名；普通JSON值，限制深度/数组/有限数值，拒绝命令/转义文本 |
| objects | 可选1..1000有序whole输入 | 默认当前选择；API拒绝组件、别名重复、多父DAG实例、锁/引用 |
| allow_native_scope | 默认false | 五项函数及两个隔离脚本之外，承认原更广泛父子/全场景/固定名/GUI影响，在备份场景使用 |
| output_path | 两个原导出脚本必填 | 明确绝对新.json/.py文件，目录须存在，拒绝已有文件/链接/覆盖 |
| input_ui | UItoPY必填 | 明确绝对现存.ui文件，不用原作者本机模板路径 |

```python
tool = load_tool()
tool.run(action='inspect', dry_run=True)
tool.run(action='call', module='RdMToolsV2.RiggingTools.Curves.CurveColors',
         function='colorShape', arguments={'Color': 17}, objects=['joint1'], dry_run=True)
tool.run(action='call', module='RdMToolsV2.RiggingTools.Curves.curveOnSelection',
         function='curveOnSelectionFunc', arguments={'mode': 'Cube', 'offset': True}, objects=['control1'])
```

inspect/validate/dry_run只读，不导入旧业务模块、开窗、执行脚本、改scene/time/select/options/Undo、安装或写文件。返回ToolResult，call/script数据包含native_result、created_node_uuids、native_result_selection、原签名/作用、output_path和batch支持标记。脚本原void返回None时，用真实新节点UUID和选择检查结果，不伪造输出。

隔离允许五项函数：colorShape、rootAuto、offsetGrp、curveOnSelectionFunc、setAxisDisplay；两个脚本BoxCurve和CurveToJson。对这些功能检查非空scope、颜色0..31/RGB/锁或驱动、轴显示只接受明确joint避免空选择退到全场景、原生成组名称/短名唯一/父节点编辑条件，以及原曲线会删除mode名字节点的风险（存在Cube/Hand等同名场景节点时拒绝）。其他完整原函数/脚本要求allow_native_scope与真实交互Maya；批处理不会模拟缺少的UI/原工具。PyMel缺失明确失败。数学/命名/几何/rig预设参数语义仍按原函数条件，不把通用JSON检查当作完整算法正确证明。

## 撤销、文件与原行为边界

API用框架UndoChunk，监测原嵌套Undo开关，异常只补关本次内部chunk。finally恢复时间、selection UUID、namespace、autokey、选择顺序偏好、symmetry与soft selection开关；返回操作结束选择可供后续衔接。不会自动回滚原部分失败；原catch/命名硬编码/全场景/宽连接删除/示例保持可追溯，错误须检查Script Editor与一次Undo。GUI回调按原完整代码运行，GUI/prefs/global状态不承诺scene Undo；API不是沙箱。

CurveToJson保留原API1全场景曲线CV遍历/数据结构，scope为全场景所有曲线，非仅objects；只把原作者硬编码C:Users/...输出改成显式上下文、独占x模式新文件。UItoPY同样保留原compileUi流程，输入输出明确，无本机硬编码写入。已有文件绝不覆盖，导出后的文件不由Maya Undo撤回；失败可能留下新建但未写完的文件，需检查并自行处理。原Maya ExportSkinWeightMaps/ImportSkinWeightMaps GUI按钮保留原交互式对话框，真实验收只使用临时目录。原run_RdMTools.py与install.mel不执行；不删写用户scripts/RmdTools_Path、不迁正式库。

## 验证与晋级

两组普通Python检查164原资源SHA、86模块/126函数/3类及全部方法保留、全源可解析/无顶层scene动作、UI资源、签名参数/注入/独占文件。七组真实隔离Maya2025验证无依赖模块import不动scene/上下文、显式Box曲线创建/UndoRedo、防覆盖，真实颜色/局部轴/dry/Undo，全部11控制器形状真实创建/位置/Undo，Root/Auto/Offset真实分组/Undo，真实曲线全场景JSON重复导出不累积/不覆盖、真实实例/锁/空scope/缺PyMel与GUI拒绝。最初测试假定source名字，Maya实际返回source1，fixture按实际返回名修正；完整import检查发现依赖旧scene变量的常量误留顶层，已只保留字面量与Qt类型别名，实际重跑通过。临时正式布局/注册/Schema/面板单独验证；不触真实GUI。

完整AutoRig/Facial/skin/IKFK/PyMel/Qt按钮生产工作流、旧可选依赖与跨版本not_run，状态prepared_unverified。可把骨骼/控制器输出交给蒙皮或层级分析工具，但实际组合尚未实测。逐项真实验收见acceptance.md，验收JSON必须对应当前候选精确指纹；用现有promote_candidate.py一次晋级，此前注册/正式库/Obsidian保持原状。
