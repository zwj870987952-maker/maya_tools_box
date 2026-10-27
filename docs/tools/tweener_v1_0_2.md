# Tweener 1.0.2 完整候选

Morten Andersen 的 Tweener，用相邻键或曲线形状快速调整插值，完整保留 1.0.2 套件和 GPL LICENSE。27 原文件逐字 SHA 留档，包含完整 plugin、9个mods文件、14张图标与安装器。全部运行代码以私有包移植，不依赖旧 mods/sys.path；原网络安装器（会下载最新包、删旧安装、覆盖module、autoload和建Shelf）仅存 `.py.original`，框架直接使用完整本地 plugin，无需运行该安装器。原135类/函数声明完整移植（选择获取函数以 _original 前缀保留并加安全scope桥），没有缩减到单一线性算法。

## 协议与参数

`TweenerTool.run(action='tween', objects=[...], blend=0, mode='between', ...) -> ToolResult`，tool_id=`tweener_v1_0_2`。`objects` 与 `curves` 二选一，可省略后使用当前whole DAG选择；对象路径唯一、不含属性/components，拒引用/锁。对象方式保留源动画层“最佳层”选择与交互channelBox过滤；需要完全确定的属性范围可显式传 curves。每条曲线只允许一个唯一的 DAG 输出属性，支持完整原层曲线解析，拒共享输出、锁层/锁目标、非time曲线、不支持的驱动/转换图和timeWarp。曲线显式许可仍须通过输出检查。

`time_range=[start,end]` 是闭区间；或 `key_indices={curve:[index,...]}` 对每条曲线给出唯一非负索引，不能同时使用range。API未传两者时使用当前帧并忽略全局选择的外部keys；交互原UI保留Graph Editor/DopeSheet选择与Time Slider优先规则（时间滑块上限减1）。干跑仅查询完整影响范围，不能调用会插键的 animdata.prepare；不source/加载plugin、不改键/scene/时间/选择/UI/Undo。当前帧无键时完整原算法插入评估值后调整，若帧在已有键范围外则拒绝原不安全endpoint插入。

五种 `mode`：between 将 blend [-1,1] 映射 [0,1] 并在相邻外边界插值；towards 从当前值向左/右邻值移动；average 从当前值朝平均或反向平均移动（多选平均为本curve整个所选KeyGroup平均，单键为邻键平均）；curve 保留全部双段/单段Bézier切线控制点和原立方权重；default 基于真实目标属性默认值与原API单位。API blend [-2,2] 包含overshoot，原鼠标模式启用overshoot后依鼠标距离可超此UI滑块范围，实际按原unclamped算法执行。模式绝不以重新实现简化公式代替源引擎，七个完整数值函数AST仅替换dict.iteritems→items。

`action='keyhammer'` 按作用域各曲线已有键的时间并集，在没有键的位置用原曲线evaluate值补齐，全部每curve的值先求后添加。保留原进度/取消流程，batch不创建进度UI；修复源range遍历漏掉endIndex，目标上限现在闭区间。限定keys时仅来自所选范围内curve的indices，不从外部curve借时间。取消/失败通过本命令MAnimCurveChange撤销本次API写入，finally关本次进度。

`action='tick', special=True/False` 指定scope/range/indices改变key tick颜色，不写曲线值；原版本明确其tick颜色不保证可Undo，跨版本须实测。`action='activate_tool'` 只带action，明确创建/切换私有dragger context；真实交互Maya必需，鼠标读取完整原prefs。默认tween可直接执行，不会先安装用户module或热键。

## Undo与完整实时预览

BaseMayaTool 的 UndoChunk 不会自动记录 API2 setValue/addKey。候选加载完整原 `MPxCommand` 插件，命令采用私有名 stagingTweener/stagingTweenerUI/stagingKeyHammer/stagingTweenerTool，原 MAnimCurveChange 存在每个命令对象上，undoIt/redoIt 真正恢复值和插键；外层框架把业务组到单次Undo。初次plugin注册是独立环境影响，不设置autoload，不强卸载已有插件；同名私有插件路径不匹配拒绝，晋级后请重启清掉旧候选加载。

完整Live Preview：press 建立完整原prepare与API change cache，拖动继续基于初始KeyGroup评估；不关闭全局Undo；release将这份已有cache交给原MPxCommand只登记一次。取消/关闭/换模式/鼠标finalize或出错时Undo未登记preview cache；finally恢复busy、移除本窗口idle callback。缓存UUID/输出/锁检查避免错误地操作已变对象；显式API不能在preview期间启动另一操作。已经登记的cache不再被preview取消使用。原idle绘制节流、视口刷新、拖拽灵敏度150px/overshoot完整保留，鼠标press初始化dragPosition防无拖动release沿用旧位置。

GUI仍 not_run：Qt5/6切换、long→int、QApplication进程事件、QPainter不重复begin/drawPie整型、重复layout父对象修正；五模式工具栏/normal-special tick/live/overshoot、九预设、分数饼图、滑块值标签、右键Toolbar/Preset与dock restore完整保留。原预设按钮标签更新但callback旧值不更新，候选改读取当前fraction，Between才做[-1,1]映射；signed模式直接使用fraction。可显式调用原Shelf按钮函数，命令改指向完整候选show_ui；本轮不建Shelf。原prefs使用optionVars，打开GUI可写模式/overshoot/live/toolbar/preset偏好，属于Undo外影响。

## 限制与组合

候选未改core/正式库；复用已有Base/ToolResult/UndoChunk，完整第三方算法保留在自身包。可在曲线筛选/其他动画编辑前后人工组合，但不同weighted tangent、嵌套层、mute/solo/覆盖旋转、引用rig、DopeSheet焦点、现场drag终止、层锁中途改变及Maya版本需真实验收。离线Maya检查不替代上述GUI/生产验收。

输出含计划curve UUID/目标、selected indices、原键数量、是否插当前键、range、engine/Undo/GUI not_run，不宣称动画正确性。API dry不注册plugin；整个原UI只在show_ui显式入口创建。不要卸载仍有Undo记录的插件；遇错保留场景备份和错误日志。JSON Schema/目标文档/测试/全部资源和panel注册在 promotion.json 中齐备，用户真实验收后才晋级。
