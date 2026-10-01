# 真实 Maya 验收（not_run）

1. 备份场景显式 show_ui，核对完整Euler/轴角/四分量/两个方向/旋转向量/Euler显示/应用/帮助和预检按钮，无 Error/Fatal Traceback。
2. Euler(10,20,30)、Z轴90度、X到Y/反方向/零方向、单位/零分量/Slerp API，核对原数学约定与当前显示。不把数字分量的不同符号等同不同姿态。
3. 选 XYZ 普通 transform 应用，预检无变化；一次 Undo/Redo 恢复旋转，时间/选区/AutoKey保持。将场景 angle unit 切 rad，姿态仍同一度制结果，单位不被工具更改。
4. 多对象坏后行、joint/非XYZ/rotateAxis/OPM/关键帧驱动/锁/引用/实例/组件拒绝前无写。父旋转/pivot/生产控制器与不同 Maya 版本备份逐项检查。
5. 满意后才预览/确认 plans/staging_run/promote_candidate.py --candidate 本目录；当前全部代码/资源/测试/知识/注册备齐但未迁正式。
