# DOF Control 人工验收

只在另存备份相机场景，完整 MEL 图候选已备，真实界面/渲染未验收。

1. `runpy.run_path(r'E:\GitHub\maya_tools_box\tools_staging_pool\01_animation\dof_control_v1_0\release_candidate\launch_candidate.py')['load_tool']()` 得到 tool，`tool.run(action='open_ui')`。核验创建、记录列表、模板/正常显示、清理/刷新、重复开关；原无 UI，本窗口是标准动作入口。确认没有 Error/Fatal Traceback。
2. 使用 camera transform/shape、namespace、多台相机，检查 cube 相对 parent、锁通道、时间/选择恢复。初始厘米场景焦距等于 -tz，fStop 等于 sz；移 tz/改 sz 看实际相机与画面变化。depthOfField 原开关应不变，需按目标 renderer 手动启用并实测近/远景深。
3. 验证 shaded/template/wireframe、原四 render flags、真实渲染不出现 cube；不同 Maya/renderer 自有 visibility、负 XY 缩放、非厘米单位、父 camera scale/移动/旋转、多个 shape 都分别检查。32×32 XPM 保留，真实显示兼容性待查。
4. dry_run 对比节点/连接/键/选择/文件零写入。已有焦距动画/驱动、引用/锁、歧义/实例camera、非camera组与已有本工具记录必须拒绝。不要为通过预检强制解除制作 rig 的连接。
5. 将 cube/camera 重命名，保存备份再开；cleanup 用返回的明确 record UUID，恢复**创建前** focusDistance/fStop，camera存活，owned mesh/reverse/add/unitConversion/network 清空。外部子对象/连接/动画/改接必须拒绝，Undo或明确解除后再清理。cleanup 不保留创建后编辑焦距值，必要时先记下。
6. create、template、cleanup 各 Undo 一次、必要时 redo；模拟失败立即 Undo 保证还原，不删未知节点来掩盖问题。关闭窗口不删除 graph。填验收人/日期/Maya及renderer/单位/备份场景/每项结果。

2项离线与6项隔离 mayapy 和临时注册通过，不等于人工。真实通过后用 plans/staging_run/promote_candidate.py 当前 hash 人工记录按规则晋级；本轮只准备，不 apply。
