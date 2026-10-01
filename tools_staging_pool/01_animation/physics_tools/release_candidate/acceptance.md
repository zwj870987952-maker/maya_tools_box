# Physics Tools：真人 Maya 验收（尚未运行）

只在备份新场景、临时目录执行候选 launch_candidate.py，不 source 原文件。首选 Maya2025；保留现有原版窗口时检查私有窗口共存。先记录场景、当前工具/选择模式、时间/AutoKey/namespace/layer/editor；不要把以下步骤当作通过记录。

1. `load_tool()` 后 inspect/dry_run；核对 scene/文件/Undo 无变化，再 open_ui，完整分页/scroll/sliders 无致命 Traceback，默认 Allow reference edits 关闭。close_ui 只关候选窗口。
2. 一条平移有键的普通控制器，在1..24帧 PhysicsMagicButton 预览，调原 overlap/weight，再 BakeinfoController。控制器不能消失、他人 Physics/particle/nucleus/hair 节点不变，检查烘焙新层/结果和一次 Undo/Redo。隔离环境已修旧粒子删除连带控制器的危险，仍需实际 rig 复核。
3. 在另一新场景直接 preview→cleanup_session，核对目标存活、锁状态恢复、助手消失，Undo 恢复全部预览。cleanup 也删除本会话已烘焙层/曲线，想保留结果时不要执行它。
4. advanced 六主轴/正负/上向量、Aim locator/up locator、各刷新 slider→rotation bake；检查 rotateOrder、越轴和运动品质，不以定义编译代替。
5. SetupPhysics 与 SetupRotationsPhysics：Jiggle平面、follicle/createHair 原命名、softness/damping/weight 实时与烘焙；在已存在hairSystem1/nucleus1的备份场景核对原节点不被删。
6. CacheMe 只选临时父目录，确认仅新 owner 子目录有 .mcj；其他缓存 enable/文件不变；缓存开/关/RedoMe/BakePhysics 与 cleanup。文件不能 Undo，Redo也不自动重建被删文件。
7. 多目标平移10、旋转30、TR20、Localspace11的实际原容量和顺序，超限/空选择安全拒绝；相同leaf不同namespace、深层父级、局部空间/localspace bake/删除。
8. proxy球/方/locator、武器/手工作流、匹配/约束/pivot，源前目标后；对象层级及自有命名正确，重复点击不删他人助手，RemoveConstraints不会删共享外部约束。
9. track 01/02/03 与 Rivet/ghost/editor/Graph Editor/Euler/key-offset/播放速度，缺命令/资产时记录原错误，不宣称通过；浏览器按钮可单独选择验收。
10. 曲线循环比较前后键；1/2/5帧噪声在timeline选区/全范围、指定通道、新layer，对比端点/层合成和未选通道，Undo/Redo。
11. 锁/驱动/层/实例/joint/引用默认拒绝。需要引用编辑时显式复选，仅在备份引用场景检查产生的 edits。选区节点被重命名/删除、外部child接入助手/外部输出时拒绝cleanup，保留原对象。
12. 中途故障检查finally时间/选择/AutoKey/refresh/namespace/layer flag；显式选择工具与速度按钮允许留下原效果。selectMode/工具/editor/ghost属于会话状态，按记录手动恢复。

记录实际Maya/Python版本、每组成功/失败、Script Editor错误与运动观感；全部满意后才按promotion.json晋级。主GUI及完整hair/advanced/runtime-command/生产rig尚未验收。未附独立许可证，只本地个人候选，不发布。
