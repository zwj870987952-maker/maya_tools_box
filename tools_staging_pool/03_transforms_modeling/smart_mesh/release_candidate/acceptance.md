# 真实 Maya 验收（not_run）

1. 备份多材质/UV场景显式show_ui，核对四操作、内置图标/文字fallback、逐操作命名/预检/Shelf/Hotkey、窗口Shelf和About，Script Editor无Error/Fatal。
2. combine选mesh/含多mesh组，正确数量/UV/材质/居中pivot/多数父组/原组无关child保持，重名/世界顶层不破坏原名，单Undo/Redo准确原结构/history/选择。
3. separate不同位置多shell并设置不同rotate/scale pivot，正确父组/命名/pivot。single-shell/mesh-child/外部消费者/锁引用真实例写动作应拒绝无变。
4. extract/duplicate face/vertex/edge/UV及非连续面，一个输出；extract仅原选面去除，all-faces拒绝；duplicate all-faces不空delete，rig源skin/history/子控制器保持。实际引用/实例源只读duplicate、复杂UV/材质/变形rig单独备份验收。Undo复原场景/选择/AutoKey。
5. persistent安装当前候选未晋级应拒绝且预检不写shelf/hotkey。正式验收转正后在临时Maya偏好测试四动作/窗口Shelf、空闲热键Alt/Ctrl/大小写/碰撞拒绝；取消确认不得写。这些配置无法sceneUndo，手动偏好清理，不误当场景验证。
6. 满意后才预览/确认晋级；全部候选留待整理池，不整理时安装MEL/shelf/热键。
