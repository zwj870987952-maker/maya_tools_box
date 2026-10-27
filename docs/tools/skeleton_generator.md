# 选区生成骨骼链

工具 ID `skeleton_generator`，类别 `rigging`。原脚本完整功能是把所选 joint 和 locator transform 转成新的 posed joint 森林：新名加 suffix，仅当原直接父节点也在选择中时保留该边，匹配世界位置/旋转、不复制 scale，对 joint 复制 radius/drawStyle，最后选择新骨架。没有自动遍历未选子孙、插入缺失中间关节、复制动画/蒙皮/bindPose 或 jointOrient 通道的功能。原件与完整函数保留并去掉自动执行；未提供署名/许可，不推断发布许可。

`action=create` 默认；`objects` 可指定 1..10000 个唯一完整 joint/locator transform，省略时按原行为筛选当前选择。显式普通 transform、组件、locator shape、歧义节点、别名重复或真实 DAG 实例拒绝。源节点只读；引用/锁定源可作为姿态来源，不解锁或修改它。`suffix='_copy'` 必须下划线后带 1..63 字母/数字/下划线；目标沿用原叶名和 namespace，名字冲突整体拒绝，不自动追加数字。缺选中父节点的对象成为新世界根，原父层级仍然不变。

`select_result=True` 保留原最后选择新骨架行为；False 恢复调用者选择 UUID。API 恢复调用者 namespace/autokey，不改变当前帧；创建时暂关 autokey。创建采用迭代树排序，避免原递归在深骨架上超出 Python 栈。创建后按 parent-first 匹配 pose，scale 保持 1。`dry_run` 返回 objects、roots、rows（source UUID、name、parent_source、world TR、radius/drawStyle）、scope/影响，不创建节点或改 selection/Undo。执行附 mapping 和 created_uuids。`inspect` 只返回原功能与资源清单。

场景影响是创建 joints 和可选改选择，由框架单 Undo chunk 分组，一次 Undo 删除本次骨架；不会改变原 skeleton、locator、动画或文件。错误可能留下本次部分新节点，使用 Undo 撤回。不输出外部文件。不把复杂缩放 rig 的世界姿态匹配解释为 skin/bind 兼容；需真实场景验收。

```python
tool.run(dry_run=True, objects=['rig:root','rig:hand','rig:pivot_locator'], suffix='_new')
tool.run(objects=['rig:root','rig:hand','rig:pivot_locator'], suffix='_new', select_result=False)
```

可先用 hierarchy_analyzer 比对明确选择和边界；新 mapping 可传给后续 orient/绑定流程，但本工具不自动修正 orient 或蒙皮。接口可衔接条件不等于组合已经实测。使用现有 BaseMayaTool Undo/结果/Schema；core 当前没有等价完整 selected-forest 操作，本轮不改 core。候选带完整 UI、文档、测试和注册晋级清单，真实 GUI/生产混合与缩放 rig/其它 Maya 版本均 not_run。
