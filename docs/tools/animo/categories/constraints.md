# 约束（Constraints）

为选定对象创建 Point/Orient/Scale 或组合约束。

- 状态：prepared_unverified，等待人工 Maya 直验。
- 输入：当前 Maya 选择、通道/Graph Editor 关键帧及时间区间；固定预设由下列脚本定义。
- 输出：候选 API 返回分派状态与操作后选择，不声称原算法已成功。
- 撤销：场景操作进入 Undo Chunk；外部文件、UI、插件、偏好不由 Maya Undo 撤回。

| operation ID | 原名称 | 执行源文件（相对 Animo_v10.6.0） | 具体用途/影响 |
| --- | --- | --- | --- |
| `constraints.smart_constraint_924021bf` | Smart Constraint | `Animo_Data/Animo_Tools_Editor/tools_library/Constraints/Smart Constraint.py` | 约束：Smart Constraint。为选定对象创建 Point/Orient/Scale 或组合约束。；约束节点与连接 |
| `constraints.smart_orient_constraint_67850264` | Smart_Orient_Constraint | `Animo_Data/Animo_Tools_Editor/tools_library/Constraints/Smart_Orient_Constraint.py` | 约束：Smart_Orient_Constraint。为选定对象创建 Point/Orient/Scale 或组合约束。；约束节点与连接 |
| `constraints.smart_point_constraint_73dd02d6` | Smart_Point_Constraint | `Animo_Data/Animo_Tools_Editor/tools_library/Constraints/Smart_Point_Constraint.py` | 约束：Smart_Point_Constraint。为选定对象创建 Point/Orient/Scale 或组合约束。；约束节点与连接 |
| `constraints.smart_scale_constraint_e4c5a978` | Smart_Scale_Constraint | `Animo_Data/Animo_Tools_Editor/tools_library/Constraints/Smart_Scale_Constraint.py` | 约束：Smart_Scale_Constraint。为选定对象创建 Point/Orient/Scale 或组合约束。；约束节点与连接 |

## 调用

```python
tool.run(dry_run=True, action="invoke", operation_id='constraints.smart_constraint_924021bf')
# 阅读预检结果后再执行：
# tool.run(action="invoke", operation_id='constraints.smart_constraint_924021bf')
```

所有入口的函数签名、顶层固定调用值及原索引别名见候选 `operations.json`；这些是静态证据，不表示运行兼容。
