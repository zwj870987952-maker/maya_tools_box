# clean_namespaces (命名空间清理工具)

## 身份与用途

- tool_id: clean_namespaces
- category: scene_hygiene (场景健康)
- version: 1.1.0
- 状态: 已转正
- 一句话用途: 清理指定节点或当前选中节点的命名空间，支持本地合并与 Top-level Reference 引用节点迁移。
- 适用场景: 资产重命名、多资产合并、清理冗余命名空间、规范化导出前的场景整理。
- 不适用场景: 存在命名严重冲突且不可自动重命名的嵌套私有命名空间。

## 调用前提

- Maya 与 Python 实测版本: Maya 2023 / 2024 / 2025 (Python 3.9+)
- 必需插件、场景节点或选择: 无特殊插件依赖，Maya cmds 原生支持。
- 输入条件: 目标节点存在于场景中。

## API

调用入口: `maya_toolkit.execute_tool("clean_namespaces", arguments={...}, dry_run=True/False)`

| 参数 | 类型 | 必填 | 默认值 | 含义与限制 |
| --- | --- | --- | --- | --- |
| nodes | array[string] | 否 | [] (当前选中) | 要清理命名空间的目标节点列表。若为空自动使用视口当前选中节点。 |
| process_all_scene | boolean | 否 | False | 是否处理全场景中所有本地命名空间。 |

### dry_run 会检查什么

- 检查目标节点是否存在，提取并统计即将被移除或重命名的命名空间列表，不修改场景 DAG。

### 返回结果

- data 字段包含: `processed_nodes`, `namespaces_removed`, `reference_nodes_migrated` 等处理统计。

## 操作影响与恢复

- 修改的 Maya 场景内容: 节点的命名空间被重命名或合并至根命名空间 (`:`)。
- 写入、覆盖或导出的文件: 无。
- Maya Undo 可撤销的范围: 处于 UndoChunk 保护内，单步 Undo 可恢复节点命名。

## 调用示例

```python
import maya_toolkit

# 1. 预检
preview = maya_toolkit.execute_tool("clean_namespaces", {"process_all_scene": False}, dry_run=True)
print(preview.to_dict())

# 2. 执行清理
if preview.success:
    result = maya_toolkit.execute_tool("clean_namespaces", {"process_all_scene": False})
    print(result.to_dict())
```
