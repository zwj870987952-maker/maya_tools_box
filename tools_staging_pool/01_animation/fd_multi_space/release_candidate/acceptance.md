# FD Multi Space 真人验收

当前 `not_run`。先复制场景，mayapy通过不是界面或制作 rig 验收。

1. Script Editor 启动下面候选，确认主窗口两种模式与各自三步窗口完整打开，无 Error/Fatal Traceback。
2. 本地模式选 driven/属性、Prepare，检查group/pivot与原动画姿势；选driver/Add driver，再Connect，检查0/1及中间值、driver位移/旋转/maintainOffset。每步Undo/Redo，累计多个不同driver/属性，确认只使用一条自有多target约束，权重混合与原行为一致。
3. reference模式使用既有父级，本地或真实引用rig均复验。默认引用编辑应拒绝；仅在备份且明确勾选时创建，检查引用edit、父级子树影响、保存重载、两个相同文件的独立引用、重命名/namespace。local模式不能重父级引用节点。
4. 在第二/第三步之间给controller增加其他自定义属性，确认最终接原指定属性和实际driver weight，绝不靠最后属性或force覆盖。保存/重载后从记录UUID继续。重复属性/driver、锁定、外部父级驱动、循环和外部target变化应拒绝。
5. 动画控制器、非均匀父级scale、joint、不同rotationOrder逐一核验。失败先Undo/检查局部改动；不要删除network当作清理。检查时间/选择/AutoKey/namespace/Undo状态保持预期。
6. 记录Maya/Python/OS、场景、操作、效果与报错；确认满意后再运行已预制晋级，当前不执行apply，不公开发布原All Rights Reserved资源。

```python
import runpy
tool = runpy.run_path(r'E:\GitHub\maya_tools_box\tools_staging_pool\01_animation\fd_multi_space\release_candidate\launch_candidate.py')['load_tool']()
tool.show_ui()
```
