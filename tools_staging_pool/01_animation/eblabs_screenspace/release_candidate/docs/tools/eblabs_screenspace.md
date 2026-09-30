# EB Labs ScreenSpace 完整候选

Eric Bates / EB Labs 原工具，Python 壳标 2021/1.0.5，完整 MEL 标 v2017-05-12；版权信息保留，未找到独立再分发授权，仅私人本地整理，不公开发布。148 个原文件逐字节随 upstream，包含原 MEL/启动器、EB Hub/UXFramework/PackageManager/Search、字体/图标/data/version/prefs。原 license manager/data/prefs 不改，不导入执行或写回；直接 MEL 原入口并无激活检查，本适配不添加绕过许可的逻辑。

原 Python 壳依赖 hybrid PackageData_310/39/37/27，当前缺少对应模块，不能在 Maya2025 直接靠该壳启动。独立候选使用随包完整 MEL，不依赖 scripts 安装目录、另一个待整理包、Hub importer 或缺失模块。保留原 installer 仅作归档，不自动建 shelf/弹安装框/读写用户 prefs/联网。上游辅助 Python 是归档资源，不承诺整个 Hub 可运行。

## 标准调用与条件

`eblabs_screenspace` / ScreenSpaceTool / category `animation` / BaseMayaTool；统一 run、ToolResult、parameters_schema 和 execute_tool。`inventory` 离线 catalog；`open_ui` 完整原双页 MEL 窗口（camera list、include orientation、Create、rig list、Delete、Smart/Full Bake、quick undo/redo、刷新及帮助）。私有 procedure/control 名称，不关闭其他窗口/主 pane，不改 namespace，原按钮通过标准 API；清理与回烘仅列本候选 owned rig。

create：明确 `camera` 唯一 perspective camera transform 或 shape，非实例、单 camera shape、nearClipPlane>0；camera 为只读输入，可来自引用。`objects` 明确有序 transform/joint 数组，空数组使用选择，camera 自身剔除。目标须本地可写/非实例；translationXYZ 可打键无锁、至少一 translation 关键帧；原 curve 驱动允许，其他 rig/layer/约束驱动拒绝。include_orientation=True 时 RX/Y/Z 也必须可打键無锁；没有任何旋转键时原算法自动降为无朝向，输出 orientation 反映实际值。跨度不超过100000；当前owned live/working/failed记录阻止重复接管。Undo必须开启。

回烘/清理：明确 `record_ids` UUID 数组，拒绝扫全场景猜命名。smart_bake/full_bake 需live rig、屏幕控制器有translation键，orientation模式需rotation键。只读 validate/dry_run 查节点/键/TR/资源，不 source MEL，不 bufferCurve/copy/paste/建节点/开窗。完整payload、注册/面板晋级单已预制，真实人工验收前不得转正。

```python
pre = tool.run(dry_run=True, action='create', camera='shotCam', objects=['hand_CTRL'])
result = tool.run(action='create', camera='shotCam', objects=['hand_CTRL'], include_orientation=True)
uid = result.data['results'][0]['record_uuid']
screen_control = result.data['results'][0]['control']
# 在备份中编辑屏幕控制器，再明确回烘或放弃：
tool.run(action='smart_bake', record_ids=[uid])
# tool.run(action='full_bake', record_ids=[uid])
# tool.run(action='cleanup', record_ids=[uid])
```

## 原算法与效果

保留21原MEL过程对应及完整核心函数：先bufferCurve overwrite源对象；创建跟随camera的rigGroup/controlGroup/aimGroup、depth locator、circle或cube curve控制器；原parent/aim/orient/point约束、旋转顺序、随机覆盖色、zDepth/planeAdjust/controlRadius/useOrientation、锁/ChannelBox状态保留。所有辅助用本次唯一prefix，目标/相机均独立UUID/message记录，不把原对象全DAG名称当辅助名。

在每个原translation通道的键时间查询源世界 rotate pivot，移控制器及depth locator，再用 |localZ| 归一化 XYZ；物体localZ>-1时改用目标-camera世界距离的模。零距离加明确错误防除零，不自造投影算法。取depth locator TX搬入zDepth，连接其深度、控制面缩放和半径；planeAdjust=nearClipPlane×1.1。原只在键时间采样，非逐帧投影，相机动态/摄像机缩放/透视/非零pivot/非均匀scale/镜头动画/穿过camera/大旋转均需视觉检查。

orientation有旋转键时在原rotation键时间用临时orientConstraint采样，删临时约束，最后屏幕控制器约束目标；无朝向控制器面向camera且旋转锁定。translation目标用depth locator pointConstraint。原buffer曲线和pairBlend可能出现，预检不操作，执行会改变。

Smart Bake：原控制器首键预打键、copy/paste各TR时序到源、按源各通道键时间读约束求值并交叉给XYZ打键，plateau切线，orientation模式Euler filter。原将目标TR键时序/切线替换/扩充，不保证保留原每通道细粒度时序。Full Bake：先从控制器第一到最后键按步长1逐时间打整个控制器键，再调用同一Smart Bake；起点可小数，保留原时间循环语义。zDepth-only的新键时间未必进入TR采样，应配合TR键并人工检查；两者均使用Maya动画剪贴板，clipboard状态不承诺由场景Undo恢复。

create结果每对象target/record_uuid/rig/control/orientation；回烘结果target/state=baked。清理仅删owned约束/helper，先把约束移出target再删，保护空控制器；保留原目标曲线、可能承载旧动画的pairBlend/aux、buffer与来源network记录。cleanup放弃屏幕编辑，通常恢复原动画连接，但不是完整回退：制作恢复优先Undo或原备份，不手删未知blend节点。原已有通道keyable/channelBox标记恢复，后创建的blendPoint等属性可能保留。

network Owner/token/UUID+message保存target/camera/control/rig、资源角色/状态；重命名与保存重载后回烘不按名字猜源。外部子节点/外部输出/后插驱动/锁/引用保护性拒绝。允许编辑已有 owned 控制器动画曲线；后续额外新动画/外部连接如需清理，必须明确解除，避免误删它们。失败可能部分写入，返回错误与可用record，立即Undo；内部 guard、时间/选择/原namespace在finally恢复。不写外部文件/偏好/刷新或OGS；所有标准写入使用一个Undo chunk，quick undo/redo直接正常Maya Undo且不隐藏UI。

## 复用、组合和证据

复用framework/标准Undo，不预先把原投影算法下沉core。可在已明确前置动画上进入屏幕编辑再回烘给滤波工具，但没有真实组合验收；多工具不能同时接管这些TR约束。静态依赖不意味着GUI/制作效果已通过。

普通Python2项、Maya2025隔离6项和临时正式布局注册/Schema/面板检查：148资源SHA、21过程来源、实际归一化0.4/-1、编辑控制器后目标移动、nearClip缩放、translation/rotation Smart/Full Bake稀疏/密集键与Undo、namespace/时间恢复、后代保护、重命名保存重载及部分失败Undo。没创建原GUI/调用原安装器/运行Hub/连接真实rig，prepared_unverified。检查曾在回烘后切帧再Undo，撤销的仅是该切帧；修正为只读带time求值后，整组Undo通过，不把旧检查异常当制作代码缺陷。
