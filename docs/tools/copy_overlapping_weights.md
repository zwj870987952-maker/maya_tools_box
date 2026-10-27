# copy_overlapping_weights (重叠位置顶点蒙皮权重复制工具)

## 身份与用途

- tool_id: copy_overlapping_weights
- category: rigging (角色绑定与变形)
- version: 1.2.0
- 状态: 已转正
- 一句话用途: 基于空间网格哈希算法快速匹配模型重叠顶点并精准复制蒙皮权重。
- 适用场景: 身体与贴身服装、缝合边界顶点权重传递、重拓扑局部贴合部件权重对齐。
- 不适用场景: 空间距离过远或拓扑/姿态完全不重叠的两个独立模型。

## 调用前提

- Maya 与 Python 实测版本: Maya 2023 / 2024 / 2025 (Python 3.9+)
- 必需插件: Maya API 2.0 (OpenMaya / OpenMayaAnim)
- 输入条件: 源模型必须带有有效的 `skinCluster`。

## API

调用入口: `maya_toolkit.execute_tool("copy_overlapping_weights", arguments={...}, dry_run=True/False)`

| 参数 | 类型 | 必填 | 默认值 | 含义与限制 |
| --- | --- | --- | --- | --- |
| source | string | 是 | 无 | 源网格节点名称。 |
| target | string | 是 | 无 | 目标网格节点名称。 |
| tolerance | number | 否 | 0.001 | 空间重叠判定的最大欧氏距离。 |
| space | string | 否 | "world" | 坐标空间，"world" 或 "object"。 |
| auto_bind | boolean | 否 | True | 目标若无蒙皮是否自动绑定源骨骼。 |
| add_missing_influences | boolean | 否 | True | 目标蒙皮若缺少部分骨骼是否自动补充。 |

### dry_run 会检查什么

- 验证源与目标节点有效性，计算重叠匹配顶点对数量及骨骼对应清单，不写入权重。

### 返回结果

- data 字段包含: `matched_vertices`, `total_target_vertices`, `source_influences`, `target_skin_cluster`。

## 操作影响与恢复

- 修改的 Maya 场景内容: 目标对象的蒙皮权重或新增蒙皮簇。
- 写入、覆盖或导出的文件: 无。
- Maya Undo 可撤销的范围: 处于 UndoChunk 保护内，单步 Undo 完整恢复。

## 调用示例

```python
import maya_toolkit

args = {"source": "body_mesh", "target": "cloth_mesh", "tolerance": 0.005}
preview = maya_toolkit.execute_tool("copy_overlapping_weights", args, dry_run=True)
if preview.success:
    result = maya_toolkit.execute_tool("copy_overlapping_weights", args)
    print(result.to_dict())
```
