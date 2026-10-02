# 文件脚本批量执行 V3

将拖入的 .ma/.mb/.fbx 场景按列表顺序打开，逐项执行所选 Python/MEL 脚本，按选项备份、另存或覆盖。保留原完整文件/脚本拖放、内部排序、自然文件名/时间/大小排序、执行全部/所选右键切换、Save、三个保存选项及日志；删除列表项只移除条目。原脚本完整 SHA 归档在 upstream，原入口不修改。标准协议类 `BatchProcessorV3Tool`，`tool_id=batch_processor_v3`，类别 pipeline_io。

## 调用与输出

默认 `action=inspect` 只读输出 tasks、scripts SHA、路径及数量。`action=process` 输入 1..1000 个绝对路径 files、按顺序执行的 scripts (.py/.mel，可空)、可选已存在 base_dir，save_backup/save_after/overwrite/remove_unknown 布尔值，execution_mode、error_policy 和每场景 timeout (10..3600秒，默认180)。输出 scenes 数组含逐脚本成功/耗时或错误、原始备份、结果格式和文件字节数，以及 processed/failed/cancelled。失败返回 ToolResult.fail，已经完成的其他输出保留。

```python
from maya_toolkit.tools.batch_processor_v3 import BatchProcessorV3Tool
tool=BatchProcessorV3Tool()
plan=tool.run(dry_run=True, files=['D:/temp/shot.mb'],scripts=['D:/temp/fix.py'],save_after=True)
result=tool.run(action='process', files=['D:/temp/shot.mb'],scripts=['D:/temp/fix.py'],save_backup=True,save_after=True)
```

`action=save_current` 只处理当前已有来源文件的场景。output 指向全新 .ma/.mb 文件可另存；output 留空保存原文件时必须显式 overwrite=True，强制生成原文件字节备份。新文件另存不改变当前场景路径，但 Maya 原生临时保存/改名可能改变 modified 标记。Save 界面有目录时输出 `<场景名>.ma`，留空表示明确保存当前文件；无效非空目录拒绝，不再误落为覆盖。

## 场景、文件和脚本影响

默认 isolated 每场景一个独立 mayapy，禁止场景 scriptNodes，调用者未保存场景、对象、选区、时间、AutoKey、Undo 队列保持。匹配 Maya 的 mayapy 缺失则前置拒绝，普通 Python 无法替代。脚本是真实用户可执行代码，Python支持编码声明/UTF8/GB18030和同目录import，提供 `__file__`、`__name__='__main__'`；MEL UTF8/GB18030。子进程不是文件系统沙箱，脚本可改写任意外部文件或调用其他程序，此类影响不受自动备份保护，也不能 Maya Undo。

interactive 为需要 GUI/Maya 会话依赖的脚本保留，必须真实 GUI 且调用者是已保存、无未保存修改的场景。批次后重新打开调用者源文件，恢复存在的选区/时间/AutoKey/namespace；场景打开清空 Undo，节点身份/插件/会话设置和脚本外部影响不能恢复。运行中重命名/切换场景后拒绝自动另存/覆盖，脚本自身的保存不能撤销。cancel 在交互模式仅能在场景边界响应，不能打断正在运行的任意 Python/MEL。界面关闭在批处理期间拒绝；默认 skip_file 出错跳过该文件剩余脚本/自动保存，stop_batch 出错停止；取消/timeout 杀死当前隔离 worker，可能保留已生成备份、脚本外部输出或本工具的独有临时文件，不能声称完整回滚。

Save Backup 精确复制输入磁盘文件原始字节到 `BF_Backup/<stem>__<source-path-hash8><原扩展名>`，不是重新保存成ASCII。Save After 输出 `backup/<stem>__<source-path-hash8>.ma`；同名不同目录使用不同hash，已有输出/备份一律拒绝。overwrite 仅 .ma/.mb，强制原始备份，实际编码匹配扩展名，替换前复核来源SHA，用同目录临时结果替换；并非对外部并发写入提供原子比较交换保障，请勿让其他进程同时改写输入。FBX可打开后另存 .ma，但覆盖 FBX 明确拒绝，需另行 FBX 导出流程。备份、临时目录、插件加载、文件写入不可由 Maya Undo 撤销。

unknown 删除默认关闭，只有显式 remove_unknown=True 才删除全部 unknown 节点；可能丢失缺失插件的数据，限备份场景验收。原稿自动删除 unknown、原始forceOpen丢未保存内容、MB/FBX扩展ASCII错配、已有备份输出静默覆盖、QPlainTextEdit.appendHtml 异常均做了对应修正。日志改 QTextEdit.append 富文本并转义消息。原稿记录 MGTools 自动保存导致崩溃：仍为 GUI 待验项，隔离默认降低当前场景切换影响，不宣称该插件问题已修复。

## 复用与验收

复用框架 ToolResult、ensure_maya_initialized、标准Schema导出及注册；文件批次自行 run 避免在 file-open 清空的队列上套 UndoChunk，不改框架。可先由 batch_importer_v3 在独立准备场景生成输入，处理后交给 abc_batch_exporter；这只是文件接口可衔接，尚非生产场景组合验收。Python/MEL执行器保留具体业务，不把任意脚本执行下沉公共core。

tests 包含原件SHA/schema/非法参数/同名输出/独占复制，隔离Maya2025真实子进程双场景/顺序Python-MEL/原始字节备份/原输入不变/dirty调用者不变、正确MB覆盖、脚本失败及场景切换不保存、save_current MA/MB、取消前无写入。GUI、交互脚本、实际FBX、timeout途中取消、MGTools及跨版本尚未实测，不能作为真实 Maya 直验通过。按 acceptance.md 集中使用备份场景验收后再晋级。
