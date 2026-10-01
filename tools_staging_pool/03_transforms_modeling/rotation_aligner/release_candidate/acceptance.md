# 真实 Maya 验收（not_run）

1. 备份场景显式show_ui，核对完整单轴/完全、六有符号轴、限制axes、多对列表、三个时域、烘焙、迭代右键、单帧跳帧和控件联动；预检不得改场景/时间/选区/Undo。
2. 明确第一个source会被旋转，第二target只读；2/4对象API与UI列表，普通transform、JO/RA/非XYZ joint、旋转父级逐项比较朝向。6选择up原无实现，应拒绝而非假称支持。
3. 单帧轴限制/锁轴退化/小数时间与next+1，完整对齐剩余轴；单位deg/rad应同姿态不改单位。Script Editor检查Error/Fatal。
4. 临时动画range bake=True每整数帧写真实keys，False只参考target原keys包含小数；源原范围外keys保留，核对插值/切线/方向。一次Undo/Redo全表动画/时间/AutoKey/选区保持。
5. 坏后行、无可写axis、引用/共享curve/约束层/真实例/OPM/shear/负反射拒绝。未来帧坏几何若执行中发现，Undo本次回滚检查，不当预检保证全时域。
6. 生产骨骼长动画及跨版本满意后才预览/确认晋级脚本；当前候选完整留待整理池。
