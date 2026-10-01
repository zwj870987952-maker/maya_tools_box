# 真实 Maya 集中验收（not_run）

1. 在备份场景用 launch_candidate.py 的 show_ui 打开完整原生UI；检查两滑条/只key/复制粘贴/状态/进度。正式面板布局已隔离检查，当前不迁库。
2. 父/子反序选择复制，改世界位移旋转，再粘贴；检查原姿态、真实keys、一次Undo和原选区/时间/AutoKey。重命名/换父路径后验证UUID跟随；删除同名重建应不误写。
3. 选Channel Box tx/rx/其它通道/无通道，验证三个轴组语义。无高亮只写当前小数帧，高亮排他末端正确；有小数key的只key范围不丢失；无key明确当前帧fallback警告。
4. 使用joint JO、非XYZ、两pivot、父级缩放的备份生产资产，观察世界姿态与容差。快照与当前角度/线性单位或rotateOrder不一致应拒绝。试复杂约束/层/OPM/shear/实例/坏后行锁/共享animCurve全表拒绝，无早行写入。
5. 长范围交互取消，检查显示失败与已完成帧；一次Undo恢复。人为模拟动态写失败，finally时间/AutoKey恢复，部分写入如实留在Undo chunk。
6. API绝对临时JSON path save/load；dry不创建文件，不覆盖既有JSON；非法JSON拒绝；导入候选不自动读取/覆盖旧系统temp，不写用户偏好。
7. Script Editor 无致命错误、各按钮/滑条可用后记录版本与满意度，才能按 promotion.json 晋级并再验面板。
