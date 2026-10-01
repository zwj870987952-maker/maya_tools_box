# GPU 缓存转实体候选

`prepared_unverified`；真实GPU视口、生产Alembic和跨版本未验收。原完整单文件字节SHA归档，去自动执行。原业务保留：遍历明确选中transform下leaf gpuCache形状或gpuCache本身，每个cache导入cacheFileName指向的**整份**Alembic文件，挂到原父transform，再默认隐藏原shape，不删原cache。cacheGeomPath、GPU display颜色/LOD等不会筛选导入内容；一份文件被多个cache引用仍按每个cache各导入一次，是原行为。

`GpuCacheToMeshTool`，category=`modeling_surfacing`，Base/ToolResult/Schema/只读validate/dry_run。`objects`省略用当前选择，否则唯一非空名称数组；`hide_original=True`可改False。对象须唯一whole shape/transform，无组件/通配符/别名/重叠parent-shape重复scope。全部任务预检，AbcImport已由用户环境明确加载、Undo开启、cache/parent无引用/node锁/真DAG实例、隐藏需要visibility可写无驱动。环境变量／相对cacheFileName按当前Maya workspace只读解析，必须存在.abc。返回实际路径/文件字节/shape和parent UUID/当前可见性，不加载插件、不建节点、不动选区/时间/Undo。

执行在每个cache的私有namespace与临时holder导入原AbcImport，再以relative parenting保留文件局部变换到原cache父级；Alembic animation连接保留。输出每个cache的路径/namespace/导入root/导入UUID及全体created UUID。目录和文件只读，不向磁盘导出或覆盖。执行finally恢复选择/time/namespace/AutoKey；失败只清理本次实际新增UUID并恢复原cache visibility，仍需检查native异常，不能保证坏Alembic解析器从不崩溃。

实际Maya2025发现原AbcImport Undo会留下AlembicNode，因此普通UndoChunk不足。候选提供自包含`gpu_cache_undo_command.py` MPxCommand：只在显式执行注册自己的命令，拒绝其它路径占用；同步native导入临时不记录子命令，保留原Undo队列，命令自己记录新增节点和原可见性。Undo用MDagModifier删除新增DAG/DG与还原visibility，Redo恢复同一实际节点及连接，无再次读文件/复制算法。所有源缓存保留、原来的Undo历史保留。必须保留候选包和插件加载状态直到Undo/Redo队列不再使用它；不设置autoload、不安装用户插件目录。验收或晋级更换加载路径时使用新Maya会话。Undo可留下空的私有namespace和已注册命令，场景几何/DG/visibility恢复；插件注册和文件reader缓存不是Maya Undo的scene对象。

```python
tool = load_tool()  # 候选launch_candidate.py
p = dict(objects=['gpu_cache_parent'], hide_original=True)
print(tool.run(dry_run=True, **p).to_dict())
print(tool.run(**p).to_dict())
# 单次Undo移除全部导入内容并恢复cache，再Redo恢复实体及动画。
```

UI提供当前选择预检/导入与原cache隐藏选项。框架协议/Undo复用，不改core；core没有相同native Alembic lifetime业务，不宣称与cache导出/其它工具组合已验证。完整代码/原归档/文档/测试/注册面板晋级清单预制，真实Maya通过才晋级。原无作者/许可授予，不推断公开发布权。

2离线检查证明原字节/Schema，3组隔离Maya2025使用真实gpuCache/AbcExport/AbcImport临时文件：真实cube8顶点、frame1/3动画位置、原父ty=10的相对挂载；dry全部scene/selection/time/Undo不变；单Undo完全无导入DG残留/还原原visibility和原Undo历史、重复Redo/Undo与动画；坏后行全表拒绝、重叠scope、visibility锁、hideFalse、batchGUI拒绝。隔离fixture必须关闭场景/flushUndo并卸载reader插件以释放Windows临时文件handle，此操作仅测试进程，候选不会卸载用户插件。实际GPU渲染、复杂Alembic schema/多root/大文件／transform缩放和其它Maya版本仍待验收。
