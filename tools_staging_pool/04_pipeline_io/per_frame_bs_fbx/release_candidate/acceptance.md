# 真实 Maya 直验（not_run）

1. 在备份场景选择单个有多个mesh、父运动和真实deformer动画的group，launch_candidate.show_ui()。预检无时间/Undo/scene/file变更；检查范围、step、输出组、copyMaterial/ASCII按钮。
2. 生成后逐采样帧对比源与导出mesh世界顶点、UV/材质face分配、rootJoint/skin权重、BS weights与linear脉冲。检查两个mesh名字不同、无临时target残留；一次Undo/Redo全group与DG回退，原source曲线/选区/time/AutoKey/namespace保持。
3. 既有输出group/坏采样网格/空mesh/共享实例应拒绝。拓扑切换和失败清理只用可丢弃场景测，动态模拟需先预热，不能把采样插值等同原模拟。
4. 手动选新group导FBX，或新路径build_export；导回Maya核对形变/skin/父运动。已有FBX拒绝覆盖，Undo场景不删FBX，失败保留可查看BS组。
5. UE真实导入morph曲线/骨骼和帧数、长序列内存与单位轴转换、源引用材质SG membership影响均需生产备份样例验收。其他Maya版本也记录。
6. 全部满意后才promotion转正，候选留待整理池，mayapy不能冒充真实GUI验收。
