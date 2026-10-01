# WorldSpaceTools 真实 Maya 验收

1. 备份有动画的测试rig，记录Maya/Python/scene单位/rotateOrder。通过候选show_ui开启完整Spaces/Extras/Paths/Copy页，全部按钮/菜单/滑条、选项和时间字段响应，无Fatal Traceback。仅打开不修改场景，session偏好不写用户AppDir、不隐藏pane/isolate。inventory与dry不改节点/选区/时间/Undo/偏好。
2. 单／多控制器world、parent、局部回烘，在原有key与逐帧范围分别比较每个keytime的世界矩阵/旋转／tangent／特殊tick。原commonAttributes边界、颜色／尺寸／父空间偏移符合原业务，修改新控制器后回烘保留动画，原对象重命名继续可找UUID。每步单Undo恢复节点和动画；不存在对象选择恢复有说明。
3. 两／三节点IK chain及旋转Offset、附加parent／child COG，多rotateOrder Gimbal完整报告；使用测试层级，检查每个按钮的实际scene影响和Undo。原算法复杂生产rig效果不得用窗口能打开代替。
4. Paths生成、rebuild 6..20 spans、curve+对象path locator、toPath原功能，核对采样范围末帧不含的原行为、nearestPoint/motionPath正确和Undo。Copy第一来源→多个目标、Snap、maintainOffset、选择通道、高亮区间和options全部验收。API与UI时间规则不同，分别记录结果。
5. 锁／引用／实例／共享曲线／动画层／外部约束拒绝；world helper增加外部child/连接，local预检应拒绝且不动。非本候选旧helper禁止自动清理，勿复制owner标记；真正拥有的完整辅助树可清理，不误删其它节点。API失败检查Undo，clipboard/buffer/UI有原副作用。
6. session偏好导出到新临时JSON、导入，已有输出拒绝；文件不由Undo回撤。原自动文件写和eval不应发生。Beta Hub仅在有完整合法EB发行和支持Python/Qt的环境验收，传beta_root后原授权检查保持；当前包缺专用模块和Python3.11不匹配必须明确报错，不绕过许可。
7. 保存版本/测试场景/Script Editor错误、未验证项及满意结果。全部真实功能通过后才晋级注册面板；当前prepared_unverified，仅保留待整理池，GUI验收not_run。
