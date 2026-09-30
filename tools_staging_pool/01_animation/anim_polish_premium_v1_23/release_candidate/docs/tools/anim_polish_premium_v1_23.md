# AnimPolish Premium v1.23 候选知识说明

tool_id: `anim_polish_premium_v1_23`；Animation；适配版本 `1.23.1-adapter`；作者 Frigging Awesome Studios / Josh Sobel。

这是完整的动画后期变形套件，包括 Sculpt/Pose-To-Pose、Wrap、Subdue、Grow/Shrink、Iron、Sticky Mod/Rivet、缓存、颜色、烘焙、属性复制和预览辅助。目标是完成动画之后的几何润色，也允许按原工作流更新上游动画。主要对象为 polygon mesh，部分黏附工具支持 nurbsCurve；不适合任意不同拓扑网格之间直接传雕刻偏移。

## 来源、覆盖与架构

`upstream/` 保留原始 17 个 Python 文件、README 和完整 Word 指南共 19 文件，`catalog.json` 带资源 SHA256。原始源码没有修改。未附独立再分发许可；版权属于原作者，原件和声明保留在本地，不赋予公开发布或重许可权。

`vendor/animPolish/` 是独立运行副本，业务算法完整保留；导入和原 UI callback 转到私有 namespace `maya_toolkit.tools.anim_polish_premium_v1_23.vendor.animPolish`，不占用或覆盖用户原有 `animPolish`。全部 160 个原函数签名可查 `anim_polish_premium_v1_23_functions.md`。其中 157 个支持 JSON invoke；两个旧 user_settings 的 run 和接收实时文件句柄的 saveSettings_run 是内部状态辅助，完整源码保留，但不作为 JSON 专家入口。旧 `user_copyPasteAttrs.py` 的场景写入发生在 import 顶层，候选不会自动导入它。

候选复用现有 BaseMayaTool、ToolResult 和 UndoChunk。第三方内部算法暂不下沉 core；多处场景命名、Channel Box、绘画上下文、stock MEL 和 UI 控件依赖仍遵循原套件，不能用“纯函数”概括这些调用。

## 有意的修复与变化

完整差异在 `anim_polish_runtime_changes.diff`。除了私有导入和 callback 的 `importlib.reload`，运行副本有以下修复：

1. Grow/Shrink、Iron、Wrap、缓存参数既接受原 literal 数组字符串，也接受原生 JSON 数组；Grow/Shrink 与 Iron 的默认空 deform verts 表示整个 mesh。原默认空 list 被 literal_eval 拒绝的问题修复。
2. 原 Python 3 的 exec 局部变量回写失效：颜色打印改用 literal_eval；设置保存改为 JSON 查询已知控件，恢复只允许目录定义的字段。运行副本移除已不需要的 imp import。
3. Copy/Paste Attrs 改用 JSON，补字符串、scalar、vector 和 matrix 类型写入，明确返回不支持/锁定/连接属性的跳过列表；不执行旧属性 Python 文件。默认文件在 Maya 用户目录的 `maya_toolkit_data/anim_polish`，不会写回源码目录；显式 path 可为另一个绝对数据目录。
4. 缓存 UI 的 New Version 分支在已有版本时漏调用 exp_geos 已补齐；swap 使用传入目录的 geometry.abc，修复忽略新目录、只替换旧路径版本字符串的问题。
5. exp_cams、exp_geos、imp_cams、imp_geos、swap 自带文件入口保护，即使原 UI reload 后仍生效。已有 cameras.ma / geometry.abc 的导出拒绝覆盖，选择 New Version 或新目录。原确认框的 Yes 也不能解除此保护。
6. Subdue 使用原 Maya 几何缓存命令，但目录改为用户数据目录下 `subdue_cache/<uuid>` 的全新目录，防止写进或覆盖当前项目缓存。UUID 目录和 .xml/.mcx 文件不能用 Maya Undo 删除；仍需真实 GUI 验证完整缓存链。
7. 原 sortCB 的 deleteAttr/Undo 会与框架正在打开的撤销组冲突。候选把同一排序算法安排到 UI idle 后执行，并以 UUID 捕获目标、恢复用户选择。立即执行的雕刻/设键仍由框架分组；属性排序另行执行，不宣称与雕刻一起原子撤销。返回 `deferred=true` 时必须等待界面空闲，不能马上把排序当完成。

这些修改不更改原雕刻 cluster 偏移、P2P 键算法、Wrap/blendShape、Grow/Shrink/polyMoveVertex、Iron/polyAverageVertex 或 Sticky Mod 的求解方式。它们的命名、四位坐标舍入、整帧雕刻命名、例外吞掉行为仍来自原套件，跨版本待实测。

## 统一参数与结果

使用 `AnimPolishTool().run(dry_run=True/False, **kwargs)`；转正后可用 `maya_toolkit.execute_tool`。action 为 inventory（默认）、open_ui、invoke。function 为原模块名加函数名；arguments 是对应关键词参数对象；dock 为 0/1（默认 0，不停靠）。参数及默认值由 catalog 精确列出，拒绝不在签名中的键、缺少必填、非有限数值以及错误类型；辅助函数仍需遵循其真实对象/顺序/域。

inventory 不需要 Maya，不导入业务模块，返回完整函数、原签名和素材。validate/dry_run 查询场景输入、插件、文件、选择及 Evaluation，不 reload、建网格、创建目录、写 JSON 或加载插件。UI/Channel Box/paint 依赖过程在 standalone 中拒绝；可用的 headless 白名单是按原依赖保守开放，不是整个套件已通过 headless 的承诺。

返回 ToolResult，内含 function、原返回值、错误、运行状态恢复错误；预检含绑定后的参数、选择及已知文件影响。原函数许多返回 None 或自行捕获异常，成功返回只能证明没有逃逸异常，不能证明全部对象都处理成功。

## 工作流与选择约定

| 功能 | 常用函数 | 选择、参数及影响 |
| --- | --- | --- |
| 雕刻开始/中止 | sculptPose.sculpt_sel / sculptFromZero_sel / abortSculpt | 选 mesh，生成带 origGeo 的临时 sculpt；可隐藏原 shape、换材质；中止只清理相应 sculpt 并恢复原可见性 |
| 标准、单帧、P2P 应用 | sculptPose.apply_sel(mode='standard') / apply_1f_sel / apply_p2p_sel | 选带 origGeo 的 sculpt；写 X/Y/Z clusters 和原 mesh 属性，删除 sculpt；单帧键 0-1-0；P2P 调整本 level 内互斥键 |
| P2P/编辑/删除 | createP2PZero_sel / createP2PHold_sel / editSculpt_sel / applyEdit_sel / delete_sel | Level 为正整数；Channel Box 选择须对应本 mesh，allP2P 会删除完整本 level 系统；保留原拓扑/连线限制 |
| 包裹 | wrap.wrapToMesh_sel / wrapToWorld_sel / extractFaces | To Mesh：选被驱动对象，最后选 driver；To World：静态复制后 blendShape；提取：同一 mesh 的 faces，保留动画连接 |
| Subdue | subdue.run(rate=4,smooth=3) | 选 mesh/vertices，DG/off Evaluation；重采样顶点动画、生成几何缓存并 blend 回源；会写外部文件及改变选择 |
| Grow/Shrink、Iron | growShrink.run_sel / iron.run_sel，或显式 run(geo=...) | Deform Verts 决定实际变形范围，Flood Verts 决定初始权重和平滑；部分顶点/绘画流程需要真实界面 |
| 黏附控制器 | rivetStuff.run_sel / run_vtx / run_cp 及管理函数 | 同 mesh 的 vertices 或单个 curve point；选序有意义；创建 softMod、rivet、offset、控制图形、组与显示层 |
| 缓存 | caching.exp_geos / exp_cams / imp_geos / imp_cams / attach / attach_sel / swap / delete | 几何导出是 animation start/end；相机导出仅依原参数选择 roots；导入可改变时间范围并建 _ABC_CTRL；attach 基于 origGeo/顺序/拓扑，delete 清理相关节点 |
| 颜色/预览/烘焙 | assignColors、smoothPreview.run、quickBake、cycleCam | 改材质或平滑预览、按 playback min/max 烘焙；rivet/plane bake 基于一个顶点；camera cycle 改当前 viewport |
| 属性/设置 | copyPasteAttrs.copy/paste；ui.saveSettings/loadSettings/defaultSettings | JSON 文件外部写入不能 Undo；paste 的场景属性变动可 Undo；Legacy Python 用户状态不自动执行 |

完整调用目录比这张表更细，未删任何业务模块。核心实例：

```python
# tool 由验收启动器 load_tool() 获取
tool.run(action='invoke',function='growShrink.run',
         arguments={'geo':'testMesh','dfrmverts':['testMesh.vtx[0]']},dry_run=True)
tool.run(action='invoke',function='growShrink.run',
         arguments={'geo':'testMesh','dfrmverts':['testMesh.vtx[0]']})
tool.run(action='invoke',function='copyPasteAttrs.copy',arguments={'k':1})
# 另选目标对象后
tool.run(action='invoke',function='copyPasteAttrs.paste')
```

## 场景、文件与撤销

框架 run 对立即发生的场景写入分组，异常后不自动回滚。外层 finally 恢复 Evaluation、refresh suspend、trackSelectionOrder 和 currentTime；明确的 toggleAnimEval/fixViewport 保留其预期状态修改，缓存 import 保留原 setToStartFrame 行为。原 UI callback 直接调用运行副本，不经过框架预检/finally；其文件保护、JSON 状态和延后排序仍由运行副本自带。原生 UI 内的其他失败仍需用 Fix Viewport 或手动恢复状态。

场景影响包括隐藏/复制/删除网格、创建 deformers、属性、约束、材质、组、显示层、keys，以及选择/绘画上下文/viewport 改变。reference、lock、拓扑和旧 node 名称组合无法由通用签名检查穷尽，使用可写备份 rig 实测；不能把本 API 当权限沙箱。

文件包括 cameras.ma、geometry.abc、Subdue geometry cache、settings.json、attributes.json。导出只用绝对路径；原 MEL cache 路径不支持空格或命令标点；允许新版本目录，禁止已有目标覆盖。AbcExport/AbcImport 需用户显式加载，预检不加载插件。导入 .ma 或 .abc 改场景，外部文件不受场景 Undo；原 cache UI Refresh/Browse 也可能创建目录、场景 metadata。失败可能留下新目录或部分缓存，保留供诊断，不自动删除其他文件。

## 证据与组合

Maya 2025 隔离检查验证库导入/reload、Wrap/Grow/Shrink/Iron 的实际节点及单步 Undo、Sculpt start/abort、平滑预览、JSON 字符串属性复制/Undo、相机临时导出及防覆盖、材质/颜色打印、异常恢复。三个 Sculpt apply 模式使用真实 Maya cluster/keys，只有 UI prefix 和排序调度是 stub；设置 JSON 控件和 Subdue MEL 调用是 stub。真实窗口、绘画、排序 idle、完整 Subdue cache、Alembic、Sticky Mod、复杂 P2P/编辑/缓存附着链仍未验证，prepared_unverified。

可在动画完成后创建缓存再润色，或由已有 animation layer 工具调整上游动画，再按原套件刷新/重算；输出的 keys、mesh attributes、deformers 可以提供给后续检查/导出。尚未实际验证这些跨工具组合，不宣称能自动混用 anim_filters、镜像系统、P2P 删除或全场景书签清理。
