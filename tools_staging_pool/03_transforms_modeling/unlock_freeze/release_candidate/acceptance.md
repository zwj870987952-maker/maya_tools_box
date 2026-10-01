# 真实 Maya 验收（not_run）

1. 备份静态mesh/controller/joint场景加载并显式show_ui；预检不得改TRS/locks/选择/时间/Undo/AutoKey。Script Editor无Error/Fatal。
2. TRS非默认与局部锁，冻结后普通transform归零/单位scale，世界geometry/pivot/法线保持预期，仅TRS解锁，visibility/自定义锁保持；选择与AutoKey恢复，原锁恢复checkbox逐项验证。
3. 组包含mesh/nurbs后代，核对全部geometry世界位置和历史。joint原生rotate转JO、translate骨长保持，骨段世界位置不乱。一次Undo/Redo恢复全部几何/属性锁/历史/选区。
4. 坏后行/动画/约束/引用/locked后代/skin/blendShape/intermediate/sharedhistory/instance/OPM/根重叠拒绝无改动。生产pivot/法线/骨架与其它Maya版本单独验证；失败先Undo本调用。
5. 满意后才预览/确认晋级脚本；当前完整候选仍留待整理池。
