# 真实 Maya 验收（not_run）

1. 备份场景为两个对象配置不同 overrideEnabled/overrideShading 和隐藏颜色，当前 panel 记录高亮开关，使用 object 与 component 各自初始模式。显式 show_ui。
2. Start 预检必须无改动；Start 应关闭目标视图高亮并切面模式。点击对象/面/同一对象不同面/空白，观察第一对象变化、同对象连续选择仍无 shading、旧对象两值准确恢复。Script Editor 无 Fatal/Error。
3. Stop 和关闭窗口、直接 deleteUI 均无遗留选择回调/形状覆盖，原 panel/模式/facet mask 恢复。多 panel 只改指定视图，反复开关/重复 Start 不增回调。
4. 期间 Undo/Redo 应暂停跟随，Stop 后可重新启动；Undo Stop 后使用最近停止记录恢复 override，不能认为 Undo 恢复 Python callbacks。锁/引用/实例/外部 override 冲突拒绝，关闭失败仍断回调，按提示解锁/恢复具体原值再 API Stop。
5. 重命名/删除 shape；新建/打开场景/退出 Maya 清回调，不向新场景写旧 UUID。保存前 Stop；完整 GUI 事件、生产模型、多视图和跨版本逐项记录。
6. 满意后才预览/确认 plans/staging_run/promote_candidate.py --candidate 本目录；当前保留待整理池。
