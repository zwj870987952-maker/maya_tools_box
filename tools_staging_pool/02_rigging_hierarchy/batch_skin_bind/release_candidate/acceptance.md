# 批量绑骨头/生成代理 真实验收

not_run；使用新场景或备份模型，隔离mayapy不代替GUI与生产场景验收。

1. launch_candidate.py的show_ui()打开完整三代理UI；检查无选择、Skinning对非joint模式提示、重复窗口、批量绑定窗口与骨骼/模型两次独立捕获。列表长度不同/类型错误拒绝，不同时读取一次选择冒充两个列表。
2. 分别Joint/Locator/Cube创建，模型初始姿态和运动跟随正确，原动画保留；重名生成真实后缀，不动已有对象/ISS/GOS集合。选中父组不自动处理所有孩子。检查一次Undo/Redo及选择/时间/autokey/namespace恢复。
3. 创建两骨骼/两独立未蒙皮模型，按有序pairs绑定，逐项确认正确影响、权重与新skinCluster。已有蒙皮/锁引用/实例/父子目标整批拒绝，无第一项先写入的残留。
4. 测试unit静态scale无动画祖先的polygon，源tx帧1/2/3/4=0/2/4/6，明确Skinning包含源全部动画删除；已有同名body_joint时新后缀骨骼的键正确且含末帧，原同名对象不改。源transform固定起始姿态，代理约束删除，mesh顶点world运动吻合原动画；一次Undo恢复原键/mesh/节点。另查旋转/pivot/静态父姿态和实际模型刚性运动。
5. 自定义属性/visibility及区间外键也会被原cutKey全部删除，必须在备份场景核对；非unit/动画scale、带动画父层、驱动/层/共享键或复杂绑定应拒绝，不在生产源上尝试放开限制。故障后检查部分变更并Undo。
6. Script Editor无Fatal，记录Maya/Python/Qt/实际步骤与限制。通过后用户实测JSON含passed=true、tool_id=batch_skin_bind、最新promotion预览candidate_sha256、maya_version/accepted_by/date；先预览，再plans/staging_run/promote_candidate.py --candidate 此目录 --acceptance 实测记录.json --apply。此前只留staging。
