# 动画复制与自动对齐真人验收

prepared_unverified，真实Qt not_run。只用真实Maya备份场景，不执行原入口。

```python
import runpy
candidate = runpy.run_path(r'E:\GitHub\maya_tools_box\tools_staging_pool\01_animation\copy_animation\release_candidate\launch_candidate.py')
tool = candidate['load_tool']()
tool.show_ui()
```

1. 完整原窗口开/关/重开，录入两个有序对象、重复组提示、彩色四圆点/批量切换、右键模式/删除、拖拽、双击选择正常；没有Qt fatal traceback。
2. 列表编辑已有/新增/减行、取消及非法格式，不访问已删除C++item；原按行复用模式正确。清空列表不自动删scene helper。
3. TRS各frame/constraint/numeric/none和other numeric：frame只在源对应组整数帧有键时写，保留初始target-source偏移；numeric每整数帧本地数值，缺属性/非标量原跳过；constraint maintainOffset并持续。明确比较父级不同、nonuniform scale、jointOrient、大角度旋转、动画层及小数帧键。
4. 生成/更新helper、编辑target locator、执行复用、强制重建当前偏移；Source/Target/Locator/Constraint私有set内容、多个pair和同叶名全路径对应正确。
5. dry_run比较场景/键/时间/选择/Undo无变化；一次Undo撤回所有写入。frame→constraint→numeric模式切换、已有目标曲线、旧blend载体保留检查，不声明所有rig同样支持。
6. 目标/源/helper改名、保存重载、重开UI后记录仍可执行/清理。外部同名group/set、后代/消费者/message或约束改接应拒绝；引用目标/锁/外部驱动拒绝，不接管旧工具节点。
7. cleanup仅本候选选中pair，空列表cleanup清全部owned记录；删驱动前确认是否需人工烘焙，清理后空目标存活、空组删除、集合为空，Undo可还原。外部新增孩子保护，不能直接强删。
8. 配置保存/读取、覆盖No/Yes、坏JSON/模式拒绝，原格式兼容，不自动生成节点；文件不能靠Maya Undo删除。逐帧错误返回失败并提示部分写入，检查状态后Undo。

记录实际Maya版本、日期、验收人、逐项结果；修候选后重验。通过后建立真实当前哈希记录：

```json
{"tool_id":"copy_animation","passed":true,"maya_version":"实际版本","date":"实际日期","accepted_by":"验收人","candidate_sha256":"当前只读晋级预览哈希"}
```

plans/staging_run/promote_candidate.py --candidate <候选绝对路径> 先预览目标与哈希；匹配真人记录后才 --acceptance <记录> --apply。之前只留待整理库。
