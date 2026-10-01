# 未完成候选包恢复说明

此目录是第 50 项的工作断点，**尚未构成完整候选包，不可晋级或执行 UI**。manifest 的 candidate_complete 保持 false，Maya 验收保持 not_run。

已完成：阅读原始 WretargetTool.py；初步编写 tool.py、runtime.py、exporter.py 和 __init__.py。原始脚本没有修改。这些候选代码尚未运行验证；依赖的 engine.py、ui.py 仍未生成。

下一轮先阅读原始脚本及这四个文件，再完成：

1. 完整保留原始源码和署名，提取 CopyAnim 业务逻辑及全部原始界面。保留起止姿态偏移、父层约束和矩阵算法；原始采样区间是 [start, end)，辅助节点 scale 通常为 1，不能宣称直接复制源缩放。
2. 生成 engine.py 和完整 UI 适配。修复源/目标长 DAG 路径造成辅助节点命名问题、无选择与取消文件夹操作、控制名称覆盖 CopyAll/DeletePlaceHolders 方法、逐帧矩阵节点泄漏以及静默吞掉写入异常。DeletePlaceHolders 原始行为只清空八个文本字段，不能变成删除场景节点。
3. 检查整批预检、目标 animCurve 输入与时间驱动、异常时只清理自己创建的节点、恢复时间/选择/autokey，以及单次 Undo。部分写入异常应诚实记录并可用 Undo 撤回，不能宣称自动原子回滚。
4. 完成 FBX 导出 UI 和参数映射。原脚本 mel.eval 名称错误且强制覆盖文件；候选要求插件已加载、明确导出节点、新文件路径、恢复 FBX 设置与选择。仅在隔离 mayapy 的临时目录验证插件和导出，不操作真实安装或场景。
5. 完成正式知识文档候选、静态/隔离 Maya 测试、完整 promotion.json/晋级脚本与面板注册、人工验收说明。运行时依赖必须在候选包中齐全。Qt/Maya 真实窗口仍需人工验收，不在 standalone 中创建 QApplication。
6. 检查通过后重新扫描源指纹，再 record_candidate，更新索引和日志，按工具提交。不能把当前四个文件算成已完成项。

额度断点：本次实际读取 5 小时已用 96%、周已用 15%；不消费重置卡，不购买额度。heartbeat 恢复为 ACTIVE，只有 5 小时剩余高于 95%、周额度允许且无其他整理回合时才继续。
