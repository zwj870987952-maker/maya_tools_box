# Back2Origin 真人验收

当前 prepared_unverified / GUI not_run。使用实际 Maya 的备份场景，关闭原 Back2Origin 窗口；候选不安装脚本，不运行原导入入口。先验收简单控制器，再在真实 rig 副本验收。

```python
import runpy
candidate = runpy.run_path(r'E:\GitHub\maya_tools_box\tools_staging_pool\01_animation\back2origin_v05_gaiv3\release_candidate\launch_candidate.py')
tool = candidate['load_tool']()
tool.show_ui()
```

1. 打开/关闭/重开窗口，检查五个控制器字段、Select/Clear/帮助、Clear All、Auto-Identify、Object namespace 菜单、帧范围、步长和两个转换按钮。Script Editor 不应有未处理致命错误，默认 scripts 文件夹不产生新文件。
2. 准备零变换 Main，RootX_M 是其子节点，IKLeg/PoleLeg/道具为 Root 下独立控制器。在1到5帧给 root X/Z 打不同键，记录各世界位置。填字段后调用 dry_run，确认节点、曲线、选择、时间、评估/刷新、范围和 Undo 队列无写入。
3. 正向转换所选 X/Z：root 局部归零、global 接收原世界数值，其他控制器按原相对位置重采样。检查 XYZ 曲线和动画视觉效果；一次 Maya Undo 恢复原键。没有 global 时只归零/重采样并给 warnings。
4. 反向 global→root：原 global 值替换 root，global 归零，IK/PV/道具世界位置保留；检查已存在 root 值被覆盖而非相加。一次 Undo 撤回。不要把此操作当作任意父级条件下正向的数学逆。
5. 用非零global、旋转/缩放父级、jointOrient、真实骨架和道具归属副本分别观察。原源码世界/局部数值约定保留，若效果不满意需记录问题，不能因简单场景通过就转正。
6. start=1/end=5/step=2，原算法保留首尾和偶数内部帧，删除第3帧的 translate 键，包括 root/global 未选平移轴。检查范围外键保持、旋转/缩放不变；测试负帧及非零起点取模，不按相对起点推断步长。
7. 测显式范围及 Bake from Timeslider：后者使用播放范围整数边界，不使用高亮片段。执行后原时间、选择/组件、四个播放范围、评估和刷新暂停值恢复；不要把范围变化视为输出。
8. 两个角色命名空间、嵌套命名空间及同叶短名，自动发现应返回明确长路径，root/global 多匹配不自动选第一项。切换namespace后旧字段清空，无匹配角色不会保留上一角色。
9. 引用对象、锁定通道、约束/表达式/动画层驱动、重复角色、缺失对象、无通道、零步长与倒置范围应预检失败。若执行中出错，检查部分键并 Undo；恢复 runtime 状态不代表自动回滚。
10. 确认两按钮视觉结果和 Maya 撤销满意，记录实际版本、日期、验收人及逐项结果。用于 Unity/Unreal 时另验导出后的根运动、轴向和引擎设置，不把本地曲线通过当成引擎验收。

真人通过后记录实际值（占位内容不构成验收）：

```json
{"tool_id":"back2origin_v05_gaiv3","passed":true,"maya_version":"实际版本","date":"实际日期","accepted_by":"验收人","candidate_sha256":"当前只读晋级预览哈希"}
```

先运行 plans/staging_run/promote_candidate.py --candidate <候选绝对路径> 获取预览；实际记录匹配后才执行 --acceptance <记录路径> --apply。代码、资源、说明、测试及注册同时晋级，不要求继续重构；真实验收之前不迁入正式库。
