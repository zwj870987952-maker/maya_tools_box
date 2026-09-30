# 人工验收：Directional Cycle Tool

尚未真实 GUI 验收；只在另存的循环场景执行，测试 rig 为本地可写而非引用。禁止直接导入原 upstream 入口覆盖真实动画。原许可 CC BY-SA 4.0，署名保留。

1. 用 `runpy.run_path(r'E:\GitHub\maya_tools_box\tools_staging_pool\01_animation\directional_cycle_tool_v1_1\release_candidate\launch_candidate.py')['load_tool']()` 取得 tool。`tool.run(action='open_ui')` 检查完整 Dockable 窗口、保存角色、足数/角度/烘焙/反旋转、左右后按钮及多次开关，没有 Error/Fatal Traceback。Maya2025 PySide2 和支持 PySide6 的目标版本分别检查。
2. 明确顺序 Master，feet，MainBody，Upperbody，Head；选基础层保存。未保存/错数/修改足数/锁通道/引用/外部驱动/未选 BaseAnimation 应在写入前失败。`dry_run=True` 前后节点、键、选择/时间、层选择、文件完全不变。
3. 一份备份各测 left/right，angle=0/45/90、两足/多足、counter_rotation 开关。bake=False 编辑 correction locator，看脚轨迹/接地/身体旋转和 head 固定世界点是否符合制作目的，尤其非零角色世界位置、父级缩放/jointOrient；逐帧看循环边界/脚滑移。Back 核验时间反转、骨盆层公式和层混合效果，勿假设恒定世界 Y-10；back 忽略 counter_rotation/angle，upperbody/master 用法不同。
4. bake=True 检查方向层/Back_Pelvis 保留且无本周期定位器/约束残留，目标自定义属性和 visibility 的整对象烘焙影响。场景已有 Left/Right/Back/Back_Pelvis 应完整保留；先单独静音其他活动层再查看输出，比较与原始场景。
5. 记录 ToolResult.data.record_uuid，cleanup 默认保留输出层；remove_layers=True 仅删本周期层。重命名定位器/控制器并另存重开后再清理；人为把外部物体 parent 到 helper 或接外部输出，应拒绝写入。自建 network 与必要旧动画载体允许保留，不手工删未知 blend 节点。
6. 每种执行/清理测试一次 Undo，失败立即 Undo 验证原场景。时间/选择/旧层 selected/preferred 需恢复；关闭 GUI 不应删除场景 helper。检查 Script Editor，无致命报错，记录制作 rig 的滑步/头向/层混合与需要修复的问题。

隔离 evidence：3 离线、7 mayapy2025、正式布局注册通过，不等于上述验收。验收后按 `plans/staging_run/promote_candidate.py --candidate <本目录>` 只读预览，再按其当前 hash/真实人工记录要求执行转正；本轮不会 apply。填写验收人、时间、Maya/Python/Qt 版本、备份场景与每项观察，真实通过后才许可迁入正式库。
