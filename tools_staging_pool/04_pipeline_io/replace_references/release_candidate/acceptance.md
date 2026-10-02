# 真实 Maya 直验（not_run）

1. 使用备份资产和备份场景，打开launch_candidate.show_ui()，分别检查EN/原MEL式/批量三窗口，所有浏览/增删/动态替换条目保留。
2. 多选同RN内多个对象/shape加其他RN，只替换两份完整引用；preview检查全部节点、新path/SHA/namespace计划。RN字符在namespace中不被误删，重复basename规范后追加序号。
3. MA↔MB、多namespace、unloaded、标准RN锁，一步Undo/Redo恢复源/目标path、namespace/load及有效原选区/time/AutoKey。nested/edited/不可读源、后行失败应全表先拒绝。
4. Undo前外部换引用/改源file/占原namespace/新增reference edits只用可丢弃场景测，明确拒绝及受限恢复记录，不在真实生产场景做此风险实验。
5. batch原文件SHA记录、dirty当前场景保留、字面规则、一个引用多命中应失败不保存；MA/MB结果正确新路径及格式，0匹配报告准确；已有output前拒绝。打开新结果验证引用目标真实正确，超时可能遗留结果/自有临时文件需检查。
6. 真实GUI/长批次/复杂插件/Maya版本确认满意后promotion，候选留池内，不以mayapy当真人GUI验收。
