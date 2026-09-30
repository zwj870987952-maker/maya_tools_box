# AniMirror v2.0 真人验收

当前 GUI not_run，prepared_unverified。在备份场景和实际 Maya 图形界面验收；隔离 mayapy 已通过的简单场景不能代替此步骤。关闭原 AniMirror 窗口，不运行原安装 MEL，不向生产场景安装 Shelf。

```python
import maya.cmds as cmds
# 仅在备份场景确认 Autodesk lookdevKit 已安装后显式加载；不是候选自动加载。
cmds.loadPlugin('lookdevKit', quiet=True)
import runpy
candidate = runpy.run_path(r'E:\GitHub\maya_tools_box\tools_staging_pool\01_animation\animirror_v2_0\release_candidate\launch_candidate.py')
tool = candidate['load_tool']()
tool.show_ui()
```

1. 开窗、关闭、重开，确认原布局、全部开关和四按钮响应。关闭/重开窗口不应丢失现有候选镜像记录。观察 Script Editor 致命报错。
2. 创建三个独立 transform，中心零变换，参考 (3,2,1)，目标无动画/锁定/驱动。按中心→参考→目标选择；先 tool.run(dry_run=True)，比较节点、选择、时间、Undo 队列，应无写入。缺少 floatMath 时应明确失败且不自动加载插件。
3. 在参考1、5帧 tx=3、5，点 Interactive Mirror，确认目标逐帧响应。分别 XZ/YX/ZY 位移按钮应按原 X/Y/Z 反转行为工作；不要仅按按钮文字理解镜像平面。测试旋转开关及关闭位移时目标位移保持。
4. 在中心非零变换、旋转父级、jointOrient、负缩放/非默认单位和真实 rig 副本上逐项观察结果。原指南提及 skeleton/AdvancedSkeleton 的能力仍待实际验证，不将简单 transform 通过视为全通过。
5. Maya Undo 一次应撤回整次 mirror；随后新建 mirror，确认旧 MEL 列表没有误用节点。点窗口 Undo 则是 clear，目标保留当前姿态，不恢复建镜像前姿态；再用 Maya Undo 应恢复清理前的辅助节点。
6. 创建两个累计镜像，检查 network、joint、floatMath 和约束。分别显式帧范围和高亮范围点 Bake，确认处理两目标、保留范围外键、删除静态曲线/filterCurve。检查高亮返回的上界包含行为和默认播放范围；TR 创建开关不限制 bake 的所有目标通道。
7. 单独测试 Mirror with Bake，确认创建和烘焙一次 Undo 撤回，目标没有丢失，辅助节点/记录已清理。保存备份场景再重新打开，现有实时镜像应可由 UUID 记录继续 bake/clear。
8. 重命名辅助节点后创建原名外部 joint，clear 应保留替身。给辅助节点加外部后代或输出消费连接，dry_run/clear 应拒绝删除。删除辅助节点只处理仍属于当前记录的 UUID，不删除其他工具节点。
9. 验证重复目标、缺失/重复名称、组件/通配符、锁定/已动画驱动/引用目标等预检失败。异常可能留下部分修改，先观察 ToolResult/Script Editor，再 Undo 或 clear；不要把失败当自动回滚。
10. 确认时间、对象/组件选择、刷新状态恢复，目标节点在 clear/bake 后存在，曲线和视觉结果满意。记录 Maya 版本、验收日期、验收人、逐项结果和当前候选哈希；有问题先修候选再验收。

真人通过后创建实际记录，禁止直接把占位内容当作通过：

```json
{"tool_id":"animirror_v2_0","passed":true,"maya_version":"实际版本","date":"实际日期","accepted_by":"验收人","candidate_sha256":"当前只读晋级预览的哈希"}
```

先运行 plans/staging_run/promote_candidate.py --candidate <候选绝对路径> 获取当前哈希与目标路径。记录匹配后才可使用 --acceptance <实际记录> --apply，复制代码、资源、说明、测试并合并当前注册表；未验收前不执行此动作。晋级不要求重新开发业务。
