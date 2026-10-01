# 按 F 相机重置真实 Maya 验收

1. 备份场景，保存persp原局部TRS和视口状态；通过候选 `show_ui()` 呼出UI，检查字段/保留选择/预检/执行按钮，Script Editor无致命异常。
2. 预检不动节点、选择、时间、Undo、偏好。执行后局部T=(1,1,1)，旋转/缩放依据当前Reset Transformations偏好；原默认选中相机，一次Undo恢复姿态与之前选择。偏好保持关闭时相应R/S保持；API显式True可覆盖，Maya偏好本身不变。
3. 手动选测试模型按F，观察原问题是否实际解除、视口是否正常；单测只证明原重置等价，不能代替这一步。焦距/裁切/shape不应变化。父层级相机是局部重置，复杂rig不直接使用。
4. 锁/关键帧/驱动的相机、正交、含子transform/实例、歧义短名应被拒绝；AutoKey状态执行后恢复，默认persp和明确的自定义perspective各实测。记录Maya版本和F异常原因；满意后才按promotion晋级。所有候选留池，不同步Obsidian。
