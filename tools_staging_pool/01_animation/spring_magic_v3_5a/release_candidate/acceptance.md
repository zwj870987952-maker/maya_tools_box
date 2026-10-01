# Spring Magic 3.5a 人工 Maya 验收

当前 GUI、完整求解与控制器流程均 not_run。本机 Maya 2025 缺少兼容 PyMel；仅做实际 mayapy 的依赖/零写入/UUID 与恢复检查，不能替代真实 Maya。46 原始文件完整留档，生产库未迁入。

1. 在目标 Maya 备份场景确认兼容 PyMel 可导入；不执行原 springMagic.py 自动入口。在 Script Editor 用 runpy.run_path(候选包绝对路径/launch_candidate.py)['load_tool']().show_ui() 打开。检查窗口、全部图标、中文/英文/日文切换、反复打开及关闭；目录 .ui SHA 不应变化；无打开时联网/报错。Floor/Subs 为源代码未实现字段，禁用；平面碰撞用 Add Plane。
2. 创建正 X 方向 root→j1→j2→j3，root 上录驱动键。选链、指定 1..24；先 dry_run 看范围和全通道清键影响，比较节点、键、时间、选择、Undo 栈不变。普通模式先备份并明确 allow_key_cleanup；检查旋转、twist/tension/inertia/extend、整数帧 bake，范围外键、一次 Undo/Redo。额外 scale/custom 可键通道需验证原版全通道清键行为。
3. Pose Match 与 Loop 分别运行，对照原包备份结果。启用胶囊 collision/subdivision=4，Add Capsule 修改端点/半径、fast_move 快运动；检查柱体/半球、约束与半径连接、碰撞穿透/内外起点/高速运动。零轴或半径拒绝。测试 Add Plane 单面与四顶点三角碰撞、旋转/平移，非 unit world Y 拒绝；非均匀缩放的数值正确性列为专项未验证，不能默认正确。
4. Add Wind 调整 MaxForce/MinForce/Frequency 并录键，确认完整原版时间正弦风力。对 session 内 wind/plane/capsule 改名、存盘重开，再 compute；不要自动接管旧 spring_wind 或 _collision_capsule。增加外部 child/history/下游连接后 Clear 应拒绝，旧版同名对象必须保留。
5. 顺序选择独立控制器，Bind 生成完整代理，按代理正 X 链计算再选择完整代理链 Bake。检查控制器动画、代理/约束删除、名字变更后的 UUID 映射、区间外键、Undo/Redo。linked_chains 两层级各验证；部分链 Bake 拒绝。动画层/已有约束需检查安全拒绝与代理工作法，不能未经测试放宽。
6. Copy/Paste 本地姿态、改名、保存/重开，检查 UUID 数据；Straight 只置 joint.rotate=0；BindPose 仅在带 skin 的备份上确认连接层级影响。对应操作 Undo/Redo 应一致。
7. Esc 取消计算、注入失败、缺依赖、锁定/引用/实例/同短名/分支/负 X/共享曲线：失败应明确，时间/选择/autokey 恢复，计算自身 locator/constraint 清理，无 wildcard 删除。取消/异常可能留下部分动画，整组 Undo 后恢复；未 Undo 的 failed session 应阻止后续写入。检查 waiting cursor 与主 progressbar。
8. 只有明确点击才打开作者网站/教程/捐赠链接；不实际付款。Shelf 按钮创建后重启 Maya 验证入口，在备份 prefs 环境使用；该 UI 偏好写入不由场景 Undo 撤回。
9. 验收结果、目标 Maya/Python/PyMel 版本和发现的数值差异记录后才执行 plans/staging_run/promote_candidate.py --candidate <此目录> 的预览；真正 apply 需用户验收通过。面板/注册临时布局检查不能当 Maya GUI 通过。
