# Maya ASCII 脚本/声明过滤候选

原批量目录递归、拖放多目录列表/清除/反馈/进度/取消、备份/过滤.ma功能全部保留。原文件SHA归档。原直接覆盖输入/errors=ignore/固定_backup覆盖改为完全新output_dir内过滤MA、history字节原副本与report.json，不改源或当前Maya场景，无自动import/UI。不能把结构过滤称为完整杀毒；自定义表达式/scriptJob/插件代码/恶意MEL外部命令/其它节点可能仍存在。

Base/Schema/ToolResult/scene_hygiene；scan默认纯文件读取，不执行任何源MEL/脚本，不在Maya打开源。files/directories（递归排history/release_candidate/.git与symlink目录）最多10000；MA header和128MB每file界限；output_dir clean必须显式不存在且父目录存在，不得在递归输入根内，全部预检后mkdir独占。原路径哈希后缀防跨目录同名输出碰撞；SHA/size/changes/目标/备份一览。取消或中途失败保留已生成files/backup/report，不称整批事务，文件不Undo。源在写前SHA复核，失败不覆已有，自己的partial output删除、原备份保留。

默认known只按准确script_names=[vaccine_gene,breed_gene]删除节点，名字匹配只是用户约定而非病毒证明。script_policy none不删，all_scripts+confirm_broad_removal=True保留原广泛过滤能力，会删除合法其他脚本；sceneConfigurationScriptNode/uiConfigurationScriptNode两默认保留（原仅scene保留，额外ui保留明确改变）。remove_plugin_requires=False保全部插件，True+confirm_broad_removal仅移除非maya requires单条；仍有该插件节点会无法正确加载，禁止当成通用加速操作。与原行为相比默认范围缩小，广泛模式明确可选。

自有bytes MEL命令lexer识别双引号/escape/行注释/block注释/分号，脚本内容嵌分号/createNode不冒充外部命令；不decode/reencode整文件，保UTF8/ANSI未知字节/换行。移除节点create与setAttr/addAttr/rename/lockBlock，后续显式select与指向该节点的connect/disconnect/setAttr一并处理，避免留下裸引用。混select/语法引号或block不闭/非comment尾缺分号/不明确attribute拒绝改写。限定Maya生成ASCII常规命令；手工复杂MEL/未知全名/间接script依赖仍须Maya读回审查，不宣称完整MEL语义解析。

```python
from maya_toolkit.tools.scene_virus_cleaner import SceneVirusCleanerTool
t=SceneVirusCleanerTool()
t.run(dry_run=True,action='clean',directories=[r'D:/ReviewScenes'],output_dir=r'D:/CleanCandidate')
t.run(action='clean',directories=[r'D:/ReviewScenes'],output_dir=r'D:/CleanCandidate')
```

UI保完整路径drag/list/clear与进度取消，补output/policy/requires/preview、broad确认，处理时拒绝close或重复start。Qt5/6与真实Maya parent，未创建额外QApplication。取消仅文件间，不打断单file lexer/IO；结果显示真实已完成/失败/取消，不像原返回失败仍“全部完毕”。共用框架协议，纯字节解析/文件IO不适合正式core下沉；所有代码自包含、知识/tests/晋级注册预制。

3离线真实bytes/backup/cancel/坏后file预检+1隔离Maya2025真实保存/过滤/ScriptNodes=False读回模型属性与合法script仍存，临时布局/注册/panel通过仅离线证据；真实GUI/复杂生产MA/插件/node-data semantics/跨版本not_run。原场景健康清理/未知节点工具不是这个磁盘范围；输出仍需用户复核和真实Maya验收，不覆盖原scene。
