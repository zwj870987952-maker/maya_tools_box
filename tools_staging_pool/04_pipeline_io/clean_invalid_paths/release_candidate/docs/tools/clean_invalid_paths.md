# 路径字符策略检查与清理

保留原完整主窗/结果窗、节点类型和路径详情、单选/全部选择、刷新、单个/全部删除及作者标注。默认按原稿ASCII兼容策略审查，但中文、重音字母是合法Unicode路径，不能称为已损坏或文件不存在。policy 可选 ascii（全部非ASCII）、cjk（原CJK基本汉字区）、replacement（Unicode替换字符 U+FFFD）。空路径忽略，ASCII缺失文件不会标记；不访问或删除外部资源文件。原代码和README完整SHA归档。

## 协议、作用范围

`CleanInvalidPathsTool` / tool_id `clean_invalid_paths` / pipeline_io。默认 action=scan 只读；nodes 可省略扫描全部已可用支持节点类型，或传唯一精确名称/UUID（1..10000、无通配/组件）。参数还有 policy 和 allow_reference_removal（默认False）。返回 issues（实际所有者 node/uuid/type/attribute/path/reasons）、containers上下游所有者映射、count、file_existence_checked=False、external_files_modified=False。扫描不会加载renderer/plugins、打开窗口、修改选区或Undo。select只选择标记的所有者，未发现时保持原选区；delete明确删除实际路径所有者并断开其连接，返回 delete_nodes（后代及connections）和 references（全部文件引用影响）。

```python
from maya_toolkit.tools.clean_invalid_paths import CleanInvalidPathsTool
tool=CleanInvalidPathsTool()
audit=tool.run(policy='replacement')
preview=tool.run(dry_run=True,action='delete',nodes=['badTexture'],policy='ascii')
result=tool.run(action='delete',nodes=['badTexture'],policy='ascii')
```

完整原标准纹理、PS/电影/Substance/noise/mentalray、imagePlane、Arnold、V-Ray、Redshift、RenderMan、Alembic/gpuCache/cacheFile/audio/fluid/环境节点类型及已加载renderer附加类型保留；枚举已可用类型避免未知类型噪音。收集实际存在的全部字符串路径属性，cacheFile同时cachePath/cacheName、Alembic优先真实abc_File。layeredTexture/VRayMtl循环有界追溯全部上游，而非原第一条路径；输出实际路径owner，容器仅报告上下游。明确传容器进行删除会拒绝，避免原稿因file路径删除整个材质容器。文件名被审查不代表其当前版本路径解析一定正确，第三方版本属性须人工实测。

## 删除和Undo边界

复用BaseMayaTool/ToolResult/Schema和外层UndoChunk。删除前全表重新扫描、锁/default/引用owner/引用后代/真实共享DAG实例检查，后行失败不先删前行。非引用节点由自有MPxCommand和MDagModifier保留原UUID及连接生命周期，一步Undo/Redo，包括DAG shape；保留shape父transform而非原cmds.delete可能产生的扩大删除。原选区中仍存在对象、时间、AutoKey、namespace保持；被删除对象不可能继续处于选中，Undo恢复有效原选区。删除路径节点可能断开材质、缓存、灯光等数据网络，请先备份场景。

reference路径可扫描，删除默认拒绝。明确 allow_reference_removal=True 才移除整份引用文件，包括该文件所有对象而非只删RN；preview列出来源SHA、namespace、load状态、全部参考节点。仅无reference edits、无嵌套子/父引用、简单namespace、原来源文件可读范围。原生RN通常元数据locked，不以这个标准锁误拒绝原生file removal。专用命令Undo重新引用同SHA来源，恢复load状态、原RN名称和metadata lock；节点UUID可变，源文件不可用/改变、原名称或namespace被占用时Undo拒绝，不能保证任意生产引用图恢复。Redo只删除该命令恢复的明确UUID，不影响其他引用；参考batch_importer_v3同语义，自包含helpers随候选复制，不依赖另一个待整理路径。

原所有UI字符串command替换函数绑定，单行删除绑定UUID并重新读取路径/策略，避免Script Editor缺全局函数、缓存名称删除错误对象。删除前保留原默认“否”确认窗口，列出本次节点数及完整引用数；主窗可改策略并显式允许完整引用。无模块导入自动创建UI；原 create_ui/show_invalid_path_nodes/get_file_nodes/get_path_from_node/is_path_valid/find_invalid_path_nodes/remove_invalid_path_nodes 兼容入口在ui中，仅GUI懒加载，核心API无Qt依赖。

## 复用、验证、待验

只读取场景路径，scan输出可交给资产清单、人工路径修复或batch_processor_v3的审查脚本；不能将检查等同于材质可用/文件存在/合法Unicode错误。core现无此文件策略映射，无必要下沉业务renderer表。不修改正式框架或注册，promotion预制代码/资源/docs/tests和registry/panel接入。

离线schema、参数/字符规则/原始SHA，隔离Maya2025实际混合file路径、非ASCII重音与中文、容器第二条上游、readonly dry、删除纹理连接UndoRedo、gpuCache/imagePlane shape及父节点、锁后行拒绝、完整中文来源reference删除UndoRedo/edited拒绝。GUI、全部renderer类型/生产嵌套图/源文件变化Undo拒绝/复杂插件副作用/跨版本尚未直验。candidate为prepared_unverified，按acceptance.md集中验收后晋级。
