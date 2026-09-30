# Whiskey 真人 Maya 验收

当前 `not_run`。隔离 mayapy/静态通过不等于 GUI/生产 rig 验收，先复制场景。

1. Script Editor 执行下方启动，确认完整原 widget/slider 窗口打开，没有 Error/Fatal Traceback；试添加/移除 widget、Profile、固定选择和倍率。
2. 在关键帧 1/3/5 的简单控制器上试 Tween/自动补间/World Space/快照/In-Out/Pose Pusher/Multiply，分别比较原包数值，测试 AutoKey 开/关、ChannelBox 空/非空、当前帧位于键内/前/后、拖拽/按钮，并核验每次回调 Undo/Redo。
3. 在实际动画层、不同 namespace、父级动画与 rotationOrder 中复验 Tween 合成值/层分支、世界空间矩阵、快照重映射。共享曲线、引用/锁定及未选对象应拒绝写入；不要把安全拒绝当作兼容通过。
4. 在备份中检查彩色 key、rekey match-last（整个对象删改键）、子帧清理（含负时间）、平直曲线清理的两种首键策略及边界切线；用 Graph Editor 对照结果。
5. Smash Bake 只在临时约束/层场景运行 1..5 帧，检查所有原可用通道采样、断输入、层属性移除和 Undo/Redo；制作图中失败先 Undo。不自动删除上游节点。
6. 保存全局切线原值后试切线按钮并手动复原；确认视图隔离与 Undo 保持原状态、选择/时间/AutoKey/namespace/层选择恢复、原全局 prefs 文件未写入。显式导出到临时 JSON，重复导出应拒绝覆盖，明确 overwrite 后才可覆盖；导入/重新开 UI 验证 Profile。文件不归 Maya Undo。
7. 记录 Maya/Python/OS、操作步骤、现象、错误与满意度。真实 Maya 验收完成前保持在待整理池，不启动晋级 apply。

```python
import runpy
tool = runpy.run_path(r'E:\GitHub\maya_tools_box\tools_staging_pool\01_animation\eblabs_whiskey\release_candidate\launch_candidate.py')['load_tool']()
tool.show_ui()
```

完整操作差异、许可与参数见 `docs/tools/eblabs_whiskey.md`；原私有版权资源不公开发布。
