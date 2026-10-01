# GPU cache 转实体真实 Maya 验收

1. 备份测试scene和cache，确认gpuCache和匹配AbcImport已显式加载、Undo开启。通过候选UI当前选择预检，完整文件路径/父级/UUID正确，选择/time/Undo/scene不动；坏后cache文件、引用、锁、实例、重叠scope拒绝全表。
2. 单／多GPU cache、不同父级和同文件不同cacheGeomPath实测：导入的是每cache对应完整文件，cacheGeomPath不筛选。实体网格、曲线和动画逐关键帧与Alembic一致，局部变换到原父级，namespace私有；检查原父旋转/缩放及实际GPU渲染。
3. 默认隐藏原cache shape，hide_original=False保持；源cache不删，选区/time/namespace/AutoKey恢复。一次Undo移除导入全部DAG/DG，包括AlembicNode，原可见性和先前Undo历史恢复；两次以上Undo/Redo后动画和材质连接继续正确。空私有namespace和注册命令可保留；不要在相关Undo历史仍存在时卸载候选插件。
4. 大文件、多root、Alembic geometry类型/UV/材质/动画及损坏文件仅用临时备份测试；错误要明确报ToolResult而非假通过。文件只读不覆盖、生产cache reader可能持有文件handle属于原生行为。切换候选/正式路径时新会话，核对Script Editor无Fatal Traceback。
5. 记录Maya/插件/场景与视口结果，满意后才晋级注册面板。当前prepared_unverified，全包仍在待整理池，实际GUI not_run。
