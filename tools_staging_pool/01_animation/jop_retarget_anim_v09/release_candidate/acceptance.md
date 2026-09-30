# 真人Maya验收：JOP Retarget Anim

状态：not_run。所有检查仅隔离mayapy/普通Python，候选尚在待整理池。仅在备份场景进行，原许可不允许第三方分享。

1. 在真实Maya用launch_candidate.py的load_tool().show_ui()呼出窗口；确认Bake、Save、Retarget响应且Script Editor没有Fatal/Error。
2. 本地transform控制器六轴可写、degree/cm，测试两控制器含静态非零rotatePivot。保存稀疏动画；移动父级、变更六种rotateOrder，Retarget后在保存键逐点比较世界位置/朝向，再播放检查两键间轨迹。确认范围外曲线是否受到原Euler过滤影响。
3. Bake打开，对整数帧同样比较；记录目标scale/父级非均匀scale/负scale/shear、旋转圈数的真实表现。冻结分支保存世界pivot和单位scale，不能将其视为scale动画保存。非零rotateAxis/pivotTranslate/offsetParentMatrix应明确拒绝回放。
4. 保存后改控制器名称验证按UUID恢复；API快照JSON持久化后重开备份验证，窗口会话缓存无法跨重启。对象删除应失败，明确新目标数组应按记录顺序映射。
5. 锁通道、外部约束/层/表达式、共享曲线、动画pivot应拒绝；引用控制器只读采样可行，已有引用曲线回放应拒绝，可显式映射到本地控制器。不使用force接管驱动。
6. 操作后一次Undo恢复原曲线，时间/选择/AutoKey保持，无mtbJop_*辅助节点残留。故障时先Undo再检查，插件状态/UI/内存快照不由场景Undo恢复。
7. 记录Maya版本、场景fixture、实际结果/截图/报错。只有用户确认满意才运行预制promotion动作；之前不得搬入正式库、不得改正式注册。
