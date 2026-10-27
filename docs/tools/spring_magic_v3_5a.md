# Spring Magic 3.5a 候选工具

tool_id: `spring_magic_v3_5a`；分类 animation；状态 prepared_unverified。完整原包来自本仓库 `springmagic/`，作者 Yanbin Bai，3.5a tension/inertia 修复见原 history.txt，署名 Benoit Degand。本包未提供独立许可，保留全部署名和 46 个原始文件的字节与 SHA256，只供本地整理，不据此宣称可分发。没有安装依赖、联网下载、购买或转正。

运行依赖真实 Maya 与兼容其 Python 的 PyMel。原始 PyNode、Vector、UI 接口使用广泛，候选保留完整引擎，没有使用虚构的 PyMel 替代层。本机 Maya 2025 mayapy 缺少 PyMel，完整求解、碰撞、绑定和 GUI **未执行**。需要用户在目标 Maya 准备兼容 PyMel 后验收；具体版本不作未经实测的保证。

## 用途、输入与输出

对选定父子链计算 spring、twist、tension、extend、inertia，保留风力正弦变化、胶囊线段碰撞、平面三角检测、fast move、loop 两轮计算、pose match 源姿态采样、subdivision 与整数帧 bake。所有 SpringData 算法、约束缓存、pairBlend、几何创建和控制器代理链保持完整。根骨骼无父节点时按原算法只作驱动，不参与求解。选择须为无分支链，子节点沿父节点正 local X，短名称唯一；分支、零长度、引用、实例、锁定或不支持的输入驱动拒绝执行。原引擎并不适合任意受约束 rig，使用生成的代理骨骼计算，再 Bake 回控制器。

所有场景命令经 `SpringMagicTool.run()` 或转正后的统一调度返回 ToolResult。`validate`/`dry_run` 只读取参数、所有权、源哈希及场景；不加载完整引擎、创建网络节点、移动时间或改选择。`status` 无需 PyMel，返回是否有依赖、session、owned_nodes、上次是否失败、gui_acceptance=not_run。操作输出含 session、完整 owned_nodes 与 UUID bindings。新增胶囊、平面、风源或控制链后 GUI 选中对应资源便于调整；API 恢复原选择。

| action | 输入及影响 |
|---|---|
| compute | objects 或当前选择；start/end 默认播放区间，end>start；spring/twist 是 UI 阻尼值，实际传给原引擎 1-value；tension/extend/inertia 0..1，subdivision 1..100，loop/pose_match/collision/fast_move/clear_subframes；碰撞关时原算法 subdivision=1。总步数最多 200000。|
| add_capsule | 选中骨骼根据 first child 创建完整 NURBS 柱/半球/隐藏端点/约束；空选在原点创建；保留原尺寸和连接算法。|
| remove_capsule / clear_collision | 前者删除选中的本候选胶囊，并按原版移除平面；后者移除本 session 全部胶囊和平面。其他工具和旧版碰撞物不接管。|
| add_plane / add_wind | 建立本 session 的完整平面或 wind cone；新平面替换本 session 旧平面；只允许一个风源，MaxForce/MinForce/Frequency 可动画。平面须保持四顶点与 unit world Y。|
| bind_controls | 有序至少两个可写控制器；linked_chains 可按原版层级排序；创建完整 joint proxy、方向设置和 parentConstraint；同一 session 先 bake 再重新 bind。|
| bake_controls | 选择完整已记录代理链；start/end 默认播放区间；原生 bakeResults 回录至 UUID 对应控制器，删除本次代理与其约束。控制器改名后仍可定位。|
| copy_pose / paste_pose | 本地 translate/rotate 按对象 UUID 保存到 session 网络节点再回写；支持改名与存盘重开，不覆盖其他对象的姿态。|
| straight | 原包调用缺失 straightBonePose；候选明确补为选中 joint rotate=(0,0,0)，不改 jointOrient/rotateAxis。须 Maya 验收。|
| bind_pose | 保留原版 GoToBindPose；需要 allow_bind_pose_hierarchy=True，GUI 有影响说明，因为可能影响连接的 skin/bind-pose 层级。|

## 关键操作影响与恢复

普通 compute（pose_match=False）原版 `cutKey` 会删除处理 parent/child **所有可关键帧通道**在 [start,end+0.99999] 内的键，随后写旋转和 extend 的 tx，clear_subframes=True 使用原 bakeResults 参数。API 默认拒绝此行为，须显式 allow_key_cleanup=True；GUI 点击计算时解释并确认。只在备份场景使用。Pose Match 会先缓存原始动画，不据此宣称所有 rig/layer 均安全。候选保守拒绝非 animCurve 的 keyable 驱动和共享至其他对象的动画曲线；animBlend/动画层受约束组合须单独验收，不直接放宽检查。

BaseMayaTool 使用共用 UndoChunkContext 分组。取消、异常不会自动回滚已有 key；返回失败，记录 failed 状态，必须 Undo 整组后再继续。正常结束或异常均用记录 UUID 清理自己新建的计算 locator/aimConstraint/proxy，不依赖 Python GC，不删全场景 `_SpringNull` 通配符。源 pairBlend/动画数据依旧保留为实际结果，不能为了整洁删掉有效连接。

原名风源/平面/胶囊和控制代理现带 session 随机标识；实际操作通过网络节点内 UUID 追踪，避免接管旧版同名节点。平面/胶囊/代理删除前检查子节点、后续连接、锁定和所有权；附加外部对象则拒绝删除。删除流程不能用于清理原始旧工具创建的节点。时间、选择、namespace、autokey 在操作 finally 中恢复；进度条改为调用时建立、finally 结束、恢复等待光标。UI/Prefs 的创建和浏览器操作不是 Maya 场景 Undo 内容。

## 界面和原包完整性

私有 `native/` 保留原来 37 个 core、17 个 springMath、6 个 utility、39 个 UI、10 个 decorator 函数；全部原始文件在 upstream 下，旧 `.py` 保存为 `.py.original` 防止误作 Python3 入口。数学函数 AST 未改变。`mkDevTools.py` 是 Python2 全局 reload/compile 开发助手，完整留档，不作为生产依赖。

四份 Qt Designer UI、全部 icons 和操作/历史说明同时携带。语言切换直接读取相应 `.ui` XML，图标路径指向当前包绝对位置；不覆盖 .ui、不写临时资源。打开窗口不访问旧版本网站；网站、LinkedIn、教程、捐赠等保留明确点击的浏览器行为，没有自动转账。原 checkUpdate 的过时网页抓取改为明确打开作者更新页。Shelf 按钮使用候选 launcher 或转正包入口，只有点击后才写 Maya shelf UI 偏好。

原 Floor 高度与 Subs 控件未被 3.5a 引擎读取，候选保留界面布局但禁用，真实平面碰撞使用 Add Plane 与 collision；不伪造 Floor 算法。原 apply 失败后按钮/进度条状态现 finally 恢复。原 import/sys.path 与 generator.next/Python2 urllib/unicode 改为私有相对 import/Python3。未删除实际碰撞或风力功能以规避依赖。

## 示例与组合关系

```python
tool.run(action='status', dry_run=True)
tool.run(action='bind_controls', objects=['ctrlA','ctrlB','ctrlC'])
# GUI 选中完整代理链；普通模式明确接受区间所有通道清键
tool.run(action='compute', objects=proxy_chain, start=1, end=48,
         spring=0.7, twist=0.7, tension=0.5, inertia=0.2,
         collision=True, subdivision=4, allow_key_cleanup=True)
tool.run(action='bake_controls', objects=proxy_chain, start=1, end=48)
```

潜在衔接为先 bind controls→编辑风/胶囊/平面→对代理链 compute→bake controls→曲线检查或精简。与正式 core 的复用限于框架协议和 Undo，Spring 专用完整数学保留本包；与其他候选组合尚未实测，不标为已验证组合。所有最终迁移文件、注册 ALL_TOOL_CLASSES 和面板接入由 promotion.json/统一晋级脚本预制，验收前不执行 apply。
