# 真实 Maya 验收（not_run）

1. 备份两个polygon模型、不同UV集/UV数据/当前集，显式show_ui，核对联合旧名列表、新名输入/空字段跳过/水印/预检/刷新。预检不得改场景/UV名/current/选区/time/Undo。
2. map1改base、额外lightmap改名，仅拥有old的模型操作；交换/循环名称，保持原UV坐标/assignment/set index/current集身份。一次Undo/Redo准确恢复，没有临时mtbUV名残留。
3. 碰撞未改集/两新名相同/不存在old、坏后行锁、引用/实例/组件/多shape对象拒绝，全表前行无写。窗口打开后对象改名支持，删除/UV表改后提示重新刷新。
4. 检查真实材质UVChooser/按名UVLink/贴图显示、生产history/rig、导出固定map1假设及其它Maya版本；不把索引数据保持当材质关系自动修复。
5. 无Error/Fatal且满意后才预览/确认晋级脚本；完整代码/原资源/知识/测试/面板注册仍留待整理池。
