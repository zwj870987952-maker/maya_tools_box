# 真实 Maya 验收（not_run）

1. 在备份场景建立带直接 shape 的父对象、两级子 transform、原本隐藏子对象及无关隐藏对象；运行 launch_candidate.py 并显式 show_ui。窗口预检不得改场景/选区/时间/Undo。
2. 选父对象隔离：父自身 mesh 可见，未选子 transform 隐藏；父加深层子同时选，连接祖先路径和两者 shape 可见。查看核心按钮、Script Editor Error/Fatal Traceback。
3. 恢复后仅本次 visibility 回原值，原隐形子和无关隐形对象仍隐形；原先启用的 isolate 集合包括组件应准确恢复。原面板 isolate 关闭时恢复应关闭。
4. 隔离与恢复分别一次 Undo/Redo，检查真实 modelPanel 状态/集合、场景 visibility 和 receipt；不能只看离线 adapter。另试空旧集合、多视图、相机视角、实例、锁/引用及生产 rig。
5. 隔离后重命名子对象，再保存临时场景/重新打开；用明确 receipt 和实际新 panel 恢复。删除成员、改拓扑、改 visibility、损坏 snapshot 应在写入前拒绝，不自动清记录。意外失败先 Undo 本调用并人工确认视口。
6. 检验满意后才执行 plans/staging_run/promote_candidate.py --candidate 本目录的预览及确认晋级；当前不会移入正式库。
