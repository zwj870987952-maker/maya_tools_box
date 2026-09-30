# Anim Mirror Helper 集中验收

状态：prepared_unverified；Maya 2025 standalone 七项通过，其中选择预检用 GUI 标志 shim 而没有创建界面；真实 Maya GUI `not_run`，其他版本待验收。不要拖放原安装器，先使用备份场景和可写的临时绑定。

1. 在 Maya Script Editor Python 运行本候选绝对路径的 `launch_candidate.py`：

```python
import runpy
candidate = runpy.run_path(r'E:\GitHub\maya_tools_box\tools_staging_pool\01_animation\anim_mirror_helper_v1_1\release_candidate\launch_candidate.py')
tool = candidate['load_tool']()
tool.show_ui()
```

2. 候选入口能打开且不 source 原 MEL；inventory 检查 90 个过程及六项素材。load 的 dry-run 不改节点、选择、键、Undo、窗口或全局图标。开原始界面检查各折叠栏、三个镜像轴、侧名输入、按钮和 BMP 视口图标。
3. 建一个简单可写动画测试绑定，源有位置/旋转关键帧和自定义浮点属性，两侧处于对称姿势。选源控制器，create_system 预检后执行；核对新 locator、系统组、Offset/Cycled 属性、视口按钮，Undo 撤销再重做。完整 rig 正式使用前单独测 namespace、引用和异向轴；常用 API 对引用/锁定的选择拒绝，勿在正式引用文件上强行绕过。
4. 设置 _L/_R 或实际侧名，依次测 Symmetric 与 SymmetricRotate。观察另一侧位置/旋转、IK/FK 属性连接；错误侧名应不会误连无关对象。动画改动后 calculate，再点视口按钮对比。测试 Offset=0、半周期、负值、非整数、Cycled=0/1 和边界帧。
5. 测 add_items：新增对象在前、system locator 最后；追加后手动连接。attach_pairs 对 parent/orient/point 各测一对及多对，顺序正确，奇数选择在候选入口拒绝。测 copy/paste、180 与零旋转、select_pairs 和同名属性连接；注意 select_pairs 原脚本可能设键。
6. 从原英文指南检查相对基组：让 system 总组随角色根运动、让肩部 Bpiv/Mpiv 跟胸部、旋转镜像基组、正 scale 同侧错帧传递，以及手动 scaleConstraint。确认约束、组、动画层及自定义属性影响符合预期。AdvSkel 隐藏分支仅在对应测试 rig 上单独验收。
7. 选最终控制器，bake_selected，核对实际 animationStartTime/animationEndTime 的全帧曲线；曲线范围须包括要求的输出。烘焙后才 delete_system，核对动画保留且只删除当前系统。无选择、错误 locator、锁定/引用节点、禁用 Undo 时入口给出明确错误。
8. 成功与人工触发失败后检查 Evaluation、刷新、timeSlider；Script Editor 无致命错误。原 UI/视口回调不经过外层恢复；如错误时 Maya 仍暂停，记录复现，候选保持未验收。Undo 恢复场景操作；确认 MEL/窗口/剪贴板/tool context 不由它恢复。
9. 当前机器的 standalone 检查不能验证 2–8 的实际效果。其他 Maya 版本逐项复测。仅在满意后填写晋级预览输出 SHA 对应的 acceptance JSON（tool_id/passed=true/candidate_sha256/maya_version/date/accepted_by），交由 `plans/staging_run/promote_candidate.py --candidate <本候选> --apply --acceptance <验收文件>`。该脚本把 promotion.json 所列文件和注册接入正式库；验收前只运行预览。

原六个文件、许可和英俄指南随候选保留。晋级不是公开发布许可。
