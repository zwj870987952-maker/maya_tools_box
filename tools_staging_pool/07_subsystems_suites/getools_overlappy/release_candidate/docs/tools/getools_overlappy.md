# GETools / Overlappy / CenterOfMass 完整候选

原池仅八个中文module，不是可运行完整GETools。候选保留原始bytes/SHA/MIT说明，补完整Settings、29+公共工具/物理/枚举/代码示例、预设和四图标，固定官方commit 45c4e17504fded01262941843ed186e9ac73c477。直接GitHub/git/raw下载超时，jsDelivr固定提交文件经目录SHA256+size全部复核，来源/每文件清单归档；未运行官方安装器、prototypes只归档不作为运行入口。所有中文module覆盖在完整独立bundle/GETOOLS_SOURCE，相对依赖无待整理路径；Shelf代码示例改正式完整package import。MIT声明/原数据保留。[官方来源](https://github.com/GenEugene/GETools/tree/45c4e17504fded01262941843ed186e9ac73c477)。

完整Transformations/Tools/Rigging/Overlappy point-aim-combo/nucleus-nParticle惯性/烘焙/层/预设/CenterOfMass约束投影与缓存/MotionTrail/Experimental UI和算法都保留。COM是原joint加加权pointConstraint定位近似，不计算网格体积/真实物理质量。Overlap依赖FPS，不同20/30/60结果不同，真实角色/单位/FPS/循环接缝与reference rig需人工确认；碰撞功能原TODO，不承诺可用。

GEToolsOverlappyTool继承Base/ToolResult/animation/JSON Schema。默认inspect只读完整来源与feature清单；show_ui/close显式候选窗口。create_com新joint，activate_com/targets=[唯一对象]绑定现有目标，add_com_targets/targets/weight连接现COM加权pointConstraint，project_com/axis跳过x/y/z的平面投影（完整原实现），delete_com只允许本实例创建UUID。setup_overlap/targets=[唯一transform]/mode point-aim-combo操作已打开窗口实际控件参数，bake_overlap/confirm_bake=True烘焙当前setup，clear_overlap清理当前自有group。schema没有泛化任意eval/method调用，全部原工具仍可在完整native UI使用；API明确范围不等于删除其他功能。

```python
from maya_toolkit.tools.getools_overlappy import GEToolsOverlappyTool
tool=GEToolsOverlappyTool()
tool.run(dry_run=True,action='create_com')
tool.run(action='create_com')
tool.run(action='add_com_targets',targets=['pelvis','chest'],weight=1)
tool.show_ui()
tool.run(action='setup_overlap',targets=['tailCtrl'],mode='point')
tool.run(action='bake_overlap',confirm_bake=True)
```

validate/dry不建窗口/节点/目录/预设/改变选择；UI需要真实Maya。API scene operations与核心native回调用现有UndoChunk分组，finally还原currentTime/playback bounds/selection/refresh suspend/cachedPlaybackEnable已有值。Undo不等于所有solver内部状态/缓存/层拓扑完全恢复，实际复杂physics Undo/Redo必须实测。原固定ovlpGroup删除改MTB_ovlp组且必须匹配本实例UUID，foreign同名拒绝；COMActivate可指向现有对象但候选不允许借用对象一键删除。中文模块原COM约束nested list错改targets+COM顺序。单个操作失败可能留下部分可Undo的场景结果，务必使用备份场景。

read_preset/preset_path与save_preset/preset_values支持绝对txt/1MiB/合法唯一键/ast.literal_eval，无exec/globals.update。save只新文件+已存在parent，不覆盖，dry不mkdir；原UI读preset也不污染globals，原默认写路径改Maya userAppDir/MTB_GETools_PRESETS，启动不自动创建目录/写文件；用户保存前自行创建新目录并选择新文件，default重复保存不覆盖。UI reload/强制quit保留但Cancel为默认的显式确认；启动不再自动关闭CachedPlayback/启用HelpPopup。原其他native Shelf/导出/层删除/scene实验菜单仍有外部或广范围影响，独立真实GUI验收及备份不可省，不能通过API验收推定整套功能均通过。

非Maya单测验证配置/预设，不等于真实GUI。隔离mayapy仅有限native import/COM/ownership检查；完整7模块真实UI/physics/solver/层烘焙/跨版本/默认保存/已有rig引用/Undo-Redo not_run。整体保留第三方依赖未未经直验下沉到core；共享UndoChunk/Base，未改正式库。全部代码/资源/文档/tests/注册已有promotion，真实Maya满意前不得转正。
