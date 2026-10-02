# HM 未知节点、插件与视口回调清理候选

完整三功能（unknown nodes/unknownPlugin requires/ModelEditor editorChanged）与原一键按钮保留；原PyMel文件SHA归档，候选cmds/API2免PyMel，取消import即开窗。修复原检查字面量ls_unknownNodes导致不删除，以及未导入cmds；不把缺失插件生产数据称为确定垃圾/病毒。

Base/ToolResult/Schema/category scene_hygiene。inspect默认仅全表查询nodes UUID/锁/引用/descendants/original plugin、未知插件version/node/data types、受影响editor回调。clean删除局部unknown节点，include_unknown_dag=False保原unknown范围，可显式包含另外两类；locked默认拒绝，unlock_nodes=True才解锁；引用/default/含descendants/真实instance拒绝。requires列表默认只显示，remove_unknown_plugins=True+confirm_plugin_metadata_loss=True且先保存备份场景才删除（本机observed metadata不可Undo）；原一键默认改为显式范围以免误删元数据。callback_policy known默认仅CgAbBlastPanelOptChangeCallback，none不碰UI，all+confirm_all_callbacks=True保原清全ModelEditor功能且明确范围（包括用户正确回调）；batch不操作视口。所有kwargs与bool严格校验。

MDagModifier必须解锁后排队，includeParents=False保父对象，专用MPx命令生命周期、属性/连接/UUID/锁UndoRedo；callback原字串以自有command恢复/redo，关闭editor跳过，不重建UI；插件虽文档称undoable，本机fixture真实Undo不能恢复，明确元数据永久移除，需要已有备份scene恢复，外层UndoChunk也不提供metadata恢复。plugin仍被用native可能拒绝，返回fail/plugin_errors+此前nodes/plugin状态，不吞异常，不自动清数据；只有节点/回调可Undo。文件不保存、不删，依赖真实MayaUndo启用。known callback内容含其他空格/脚本不盲删，需要all明确操作；不通过eval执行未知回调。

```python
from maya_toolkit.tools.clean_junk_nodes import CleanJunkNodesTool
t=CleanJunkNodesTool()
t.run(dry_run=True,action='clean',unlock_nodes=True)
t.run(action='clean',unlock_nodes=True)
```

UI完整原一键按钮，补各范围checkbox/预检完整JSON/现场确认；用户真实Maya备份后操作，默认inspect也不打开UI。2mock/3隔离Maya2025（DG未知节点连接/锁/oneUndoRedo、后行locked全表拒绝、真实MA requires metadata显式确认与永久移除guard）与临时最终注册/domain/panel通过仅离线证据；真实GUI/引用/unknownDag/插件自定义payload/全部callback Undo待验。无需core改动，共用现有框架Undo/协议，仅持有自有command。

候选自包含upstream/cat/docs/tests/晋级注册信息；正式库未改。参考：[unknownPlugin](https://help.autodesk.com/cloudhelp/2025/ENU/Maya-Tech-Docs/CommandsPython/unknownPlugin.html)。Maya验收后需当前SHA版本操作者日期才能晋级；与文件清理器是不同范围，场景unknown清理不等于杀毒。
