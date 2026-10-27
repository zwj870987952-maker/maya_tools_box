# Joint Optimal Pro 4.1

用途：Barnev Pavel 的完整骨骼创建、插入/删除链关节、精确三点创建、父子重排、对齐/平滑/分布、路径选择、自动/手动朝向、显示颜色与命名工具集。原六文件完整保存在 vendor：160240字节MEL、安装脚本、PDF操作手册、READ_ME、License与图标；catalog记录逐文件SHA。许可原文保留：禁止修改或再分发、商业使用要求购买；本次仅制作自用独立适配，不运行安装、不购买、不发布。

原引擎144个global声明、143个独立过程完整保留，顶层仅声明，没有自动开窗。一个顶点中心过程重复声明按作者原顺序保留。完整三页主界面、镜像选项界面与所有业务都在原代码中。142个原签名可通过typed API调用，唯一排除的通用find会执行system("load ...")；此函数仍作为原资产保存，适配层不调用。catalog为哈希过程提供原UI引用行/注释，避免编造新语义名称。

## 入口、参数与输出

候选运行launch_candidate.py，通过load_tool()取得工具，显式show_ui()打开完整原窗口。晋级后使用maya_toolkit.execute_tool('joint_optimal_pro_v4_1', arguments, dry_run)。代码只引用自身vendor路径，完整图标/手册可随目标目录使用，不依赖池外安装位置。原Shelf拖放安装器仅归档，不执行。

| 参数 | 条件 | 含义 |
| --- | --- | --- |
| action | 默认inspect，或call | 读取完整资源/原过程说明，或真实原算法调用 |
| procedure | call必填，Schema枚举142项 | 以inspect返回的原签名和ui_references选择功能 |
| arguments | 默认[]，位置数须符合声明 | int、有限float、纯string、各类型数组、三值vector、4×4matrix；长度和数值有界，拒绝MEL指令/转义 |
| objects | 可选，1..1000个有序唯一whole节点 | 默认当前选择；API只接受transform/joint，顶点组件等完整功能用原GUI |
| allow_native_scope | 默认false | 除隔离验证的五项过程外，承认原算法可能扩大到父子/连接对象、全场景、共享偏好和UI的范围；必须备份场景 |

inspect返回所有资源/SHA、142签名、声明数、重复名、原UI引用、直接影响关键词与许可。validate/dry_run不source、不创建窗口或节点，不改选择/当前帧/Undo/options/全局或文件。所有API结果为ToolResult；call数据含native_result、native_result_selection、created_node_uuids、signature、objects、arguments以及原范围说明。原void/空输出和catchQuiet保留，不把“返回无异常”解释为完整成功。

```python
tool = load_tool()  # 通过候选launch_candidate.py取得
tool.run(action='inspect', dry_run=True)
tool.run(action='call',
         procedure='JOPA_4_1_92de112c5c170c44ad9daf4d48b1acdd',
         arguments=[2.0], objects=['joint1'], dry_run=True)
```

## 安全边界与行为说明

原始源码唯一非ASCII字节位于321行“rotate Х”提示中，为CP1251字母。Windows本机CP936直接source误吞引号而报Unterminated string；适配层完整原字节只在内存decode('cp1251')后传给mel.eval，没有过滤、抽取、重写或改算法。全部143个名字在隔离Maya2025真实编译通过。MEL whatIs因Unicode loader显示entered interactively，适配器仅识别本模块完成加载后记录的源码SHA；加载前外来同名过程拒绝。重新加载Python模块、手工重定义同名过程或其他Barnev套件共享find等名字时，应使用新的Maya会话，不能保证检测已运行期间的手工重新定义。

五项可隔离调用的原过程是：radius设置、indexed颜色、displayHandle、按有序选择创建关节、带严格小于limit的创建入口。拒绝空选择、重复别名、真实多父DAG实例、锁或引用节点；radius还要求真实joint及未锁/未驱动radius，颜色检查RGB模式与override属性，Handle检查目标属性。原color会解锁通道但API预检先拒绝锁，保留原GUI逻辑另实测；原颜色过程不切换overrideRGBColors，API拒绝RGB模式防止“已改indexed但画面无变化”。creation原limit条件是选择数严格小于limit，相等会原生警告no-op，API提前拒绝。

其他142签名范围内的函数完整保留，通过allow_native_scope及真实交互Maya调用，默认拒绝宽范围操作，batch不伪造modelPanel/时间线/原控件。某些纯数学或查询helper也保守归入此组。API不是执行沙箱；typed literal阻止直接注入，不证明原内部eval/Python、正则和数学输入、链方向/退化几何等所有语义安全，必须按PDF和原UI注释准备输入。原创建关节/改变层级可能影响connected/children；原skin移动模式可影响场景所有skinCluster；freeze/orient、自动朝向、命名和mirror会改变节点/连接/名称或optionVars。原选择、camera依赖、Vertex/curve工作流的全部行为不以whole API替代，使用完整GUI验收。

标准call由框架UndoChunk分组；监测本次原嵌套Undo开关，异常补关本次未关闭的内部chunk，不关闭未知外部chunk。API在finally恢复调用者时间、namespace、autokey、选择UUID及顺序偏好、高亮偏好、四个mirror optionVars与Undo状态；返回原操作结束时选择供后续工具使用。原MEL声明、共享全局和Python定义会保留，不承诺Undo恢复。错误可能留下部分场景操作，需查Script Editor并一次Undo；没有自动回滚承诺。原完整UI启动会设置trackSelectionOrder，UI回调可改高亮/镜像偏好，其行为不受独立API恢复控制，也不由scene Undo覆盖。

适配器不写外部文件，不触Shelf/userSetup或正式库；原installer/find不执行。许可证、PDF、原完整MEL与图标不修改。

## 验证、组合与晋级

两组普通Python验证完整六文件SHA、143独立过程/142签名Schema与类型/注入检查；四组隔离Maya验证全部加载无scene/UI副作用、真实radius/color/handle的scope与Undo/Redo、真实有序关节位置/namespace/选择恢复及Undo/Redo、锁/驱动/真实DAG实例/limit拒绝与交互流程明确失败。原codepage失败报告保留在运行日志目录，最终报告与候选fingerprint对应。临时正式布局验证注册、rigging域、Schema与面板入口。

真实Maya GUI、插入/删除非线性链、三点朝向、freeze/mirror/reparent/rebake、组件、命名、生产rig和其他版本全部not_run；prepared_unverified。可把已生成骨骼用于后续蒙皮工具或层级分析，但尚未验证实际跨工具组合；与OverRig共用find等MEL名，预检冲突需新的Maya会话。acceptance.md列逐项验收，通过后用现有promote_candidate.py和精确候选指纹/实测JSON一次晋级，无需另重构；此前正式目录、注册、面板不变。
