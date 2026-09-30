# 轴心点与轴向重置

- tool_id：`reset_pivot`
- category：`modeling_surfacing`
- version：`1.0.0`
- 状态：待整理候选，尚未真实 Maya GUI 验收，尚未注册到正式库。
- 原始来源：本项目 `tools_staging_pool/03_transforms_modeling/reset_pivot/maya_reset_pivot.py`，原文件标注作者 Claude。未发现独立许可证；原文件保留。

用于普通、可编辑、非实例化 transform/joint 的轴心位置与轴向整理。保留原脚本七种动作，并提供一致的 API 和预检。涉及冻结旋转的动作会影响几何与子级；请在副本场景验收。此工具不处理动画曲线、引用角色或任意世界朝向求解。

## 参数与行为

`ResetPivotTool().run(dry_run=False, **arguments)` 返回 ToolResult。转正后统一入口为 `maya_toolkit.execute_tool("reset_pivot", arguments, dry_run)`；当前候选须按 acceptance.md 直接加载类，不能依赖尚未发生的正式注册。

| 参数 | 类型 | 必填/默认 | 含义 |
| --- | --- | --- | --- |
| action | string | 默认 center | 下表中的一种动作 |
| target_nodes | array[string] | 省略时当前选择 | transform/joint 节点名或完整 DAG 路径；显式空列表非法；重名短名称非法；重复目标去重 |
| source_joint | string | joint 动作需要 | 显式指定目标时必须指定源骨骼；其他动作不接受该参数 |

joint 动作省略全部节点参数时，按当前选择顺序读取源骨骼、单个目标；选择必须恰好两个。显式传参允许一个源骨骼对应多个目标。源骨骼不能同时是目标。建议 API 调用使用显式节点参数。

| action | 实际动作 | 主要影响 |
| --- | --- | --- |
| center | Maya `centerPivots=True` | 移动轴心；未改为原脚本未实际使用的自算世界包围盒中心 |
| origin | 世界轴心设置为 0,0,0 | 移动轴心，保持旋转 |
| parent | 世界轴心设为父物体旋转轴心 | 无父级目标按原脚本跳过并警告 |
| reset_axes | 临时挂世界，冻结旋转，恢复位置/缩放/轴心并恢复父级 | 冻结可能改变几何、子级及旋转通道 |
| world | 临时挂世界，设世界旋转为零，恢复位置/缩放/轴心并恢复父级 | 修改朝向，可能旋转几何与子级 |
| joint | 把源 jointOrient 数值作为目标世界 Euler 旋转 | 保留原脚本语义；不是源骨骼实际世界朝向匹配算法 |
| complete | 临时挂世界，冻结旋转、轴心居中、世界旋转为零，再恢复位置/缩放和父级 | 保留综合动作执行顺序与影响 |

## 无副作用预检

校验 action、未知参数、目标列表、唯一 DAG 路径、节点类型、引用/节点锁、实例化、可写属性与输入连接，以及需要恢复的父级是否可编辑。冻结动作额外拒绝多父级实例化 shape。预检只查询，不改选择、父级、属性或文件，不打开 UI，也不创建 Undo Chunk。

针对会写入的 rotate、pivot、pivotTranslate 通道进行检查；涉及层级的动作还检查 translate、scale、shear。锁定、驱动或动画输入连接会被拒绝，即使 Maya getAttr(settable=True) 对动画通道返回真。该限制属于新增安全边界；原脚本未提前拒绝这些情况。

预检不保证真实执行一定成功：执行前重新查询条件，Maya 命令仍可能因场景状态、对象类型和版本失败。

## 输出与恢复

预检 data：`action`、`target_nodes`、`target_count`。执行成功 data：`action`、`processed_nodes`（操作完成后的完整路径）、`processed_count`。批内失败 data：`action`、已完成的 `processed_nodes`、`failed_node`、`failed_uuid`、`partial_changes_possible=True`。

errors 包含参数/节点/连接问题或 Maya 命令错误。warnings 包含无父级跳过、冻结或临时 reparent 影响，以及 jointOrient 算法限制。

执行由基类 run 分组到一个 Undo Chunk。异常时尽力恢复原父级，稳定 UUID 解决 reparent 后旧长路径失效的问题；恢复父级不等于回滚属性、几何或已完成目标。失败后检查层级并执行一次 Maya Undo；Undo 被禁用或恢复命令也失败时不能承诺撤销成功。工具不写外部文件。不要直接调用 execute 绕过基类预检与 Undo。

## 关联与组合

候选输出节点路径可作为后续工具输入，但当前没有经过用户实测的工具组合。静态依赖只有 framework 及其既有 Undo 支撑，不新增 core 实现。不能把代码复用关系描述为已验证的业务组合。

转正后单项示例：

```python
import maya_toolkit
arguments = {"action": "origin", "target_nodes": ["|group|mesh"]}
preview = maya_toolkit.execute_tool("reset_pivot", arguments, dry_run=True)
if preview.success:
    print(maya_toolkit.execute_tool("reset_pivot", arguments).to_dict())
```

## 演进与验证

2026-09-30 候选：保留原 UI 的七个动作；移除没有参与运算的 bbox 中心计算；使用 UUID 重新定位节点；finally 恢复父级；结构化参数、结果、警告与失败信息；新增引用/实例/连接/锁定安全预检和 UI 仅预检选项。原始文件未改。

离线验证记录以 `plans/staging_run/manifest.json` 及测试报告为准。Maya2025 mayapy 的隔离 standalone 场景测试与 mock 测试用于回归，不表示 GUI、其他版本、复杂父缩放或角色场景已通过验收。Python 2 兼容入口未实测；回归测试使用 Python 3。真实 Maya GUI 验收记录待用户填写 acceptance.md。
