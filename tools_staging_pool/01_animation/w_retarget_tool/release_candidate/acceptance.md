# W Retarget Tool 人工 Maya 验收

状态：not_run。隔离 mayapy 结果不等于真实 Maya 界面或生产绑定验收。

1. 打开备份或新 Maya 场景；使用候选 launch_candidate.py 的 show_ui()。检查四行 source/target/Copy Anim、Copy All、Delete Place Holders、帧区间、全部 FBX 选项、进度条、帮助和作者窗口。关闭再开，原窗口/其他工具不能被覆盖或自动安装。
2. 无选择点选择按钮、取消文件夹对话框、空行/半行/倒置区间/非独立对象应提示且不改场景。四行单独复制和 Copy All 均需响应；清空按钮只清字段，不删除物体。
3. 源 tx 帧1/2/3为0/2/4，目标初始10，区间1..4：目标为10/12/14、结束4无新键、scale代理值通常1。检查源不变、时间/选择/autokey恢复、无wRetarget辅助节点残留。一次Undo撤回整个批次，Redo恢复。
4. 在备份生产绑定检查不同初始姿态、namespace/长路径、父动画、rotateOrder、jointOrient、旋转翻转、pivot、父缩放及插值；约束/动画层/引用/锁目标应预检拒绝，不强制解锁或断开。检查已有区间外键保留。
5. 手动加载fbxmaya，仅选择临时导出目录。分别试Y/Z、Binary/ASCII、2020/2019/2018、Bake开关，确认正确节点/帧区间/新文件。再次同路径导出必须失败且原文件不变；选项和选择恢复。重导入到另一临时场景核对动画和轴，确认FBX文件不随场景Undo删除。
6. 若操作报错，检查消息、辅助节点、部分目标键及一次Undo；不在真实外部目录测试失败路径。把Maya/Python/Qt版本、结果、截图或错误写入独立验收记录。

验收通过后才执行 plans/staging_run/promote_candidate.py --candidate 此目录 --acceptance 用户实测JSON记录 --apply；JSON须包含passed=true、tool_id=w_retarget_tool、预览返回的candidate_sha256及maya_version/accepted_by/date。先不带 --apply 预览完整目标文件与注册接入。未通过则修候选并重新检查。
