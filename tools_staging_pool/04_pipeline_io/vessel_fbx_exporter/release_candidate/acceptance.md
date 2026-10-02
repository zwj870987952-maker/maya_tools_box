# 真实 Maya 直验（not_run）

1. 使用备份舰船scene，确认All_joints/Reset_Trans/_FBXExport集合、引用资产/相对workspace路径可读，打开候选UI。只读预览全场引用、每集成员、Reset清全部keys、范围/filename必须准确；未保存scene用明确目录。
2. snapshot处理前记录原scene节点、引用path/load、keys、namespace、Undo/dirty、选区/time/AutoKey，全部应保持。处理只在独立mayapy副本，原脚本的全场引用import/namespace merge不触碰当前scene。
3. 启用save_prepared_scene，用另一个备份Maya会话打开新MA检查import全部references、All_joints烘焙、Reset TRS=-90rx及custom动画清空/首帧key、namespace全部成员搬迁、root rename原时序。
4. 检查多导出集/嵌套集/空集、AAA keyword、同名/非法filename碰撞拒绝；已有file不覆盖。将FBX导入Maya/UE核对root名称/mesh/skin/morph/animation/axis/embedded材质，首份与后份root名称差异记录。
5. reference_results仅在副本引用生成file，prepared MA若含结果reference确认可读。非loaded/missing refs/锁/nonanim Reset驱动应前置拒绝；失败/timeout只检查临时结果，不能以Undo撤销已导出file。
6. 动态模拟/复杂引用/插件、真实GUI及跨版本集中验收后promotion；候选不提前转正。
