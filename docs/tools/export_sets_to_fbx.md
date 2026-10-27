# export_sets_to_fbx (选择集批量导出 FBX 工具)

## 身份与用途

- tool_id: export_sets_to_fbx
- category: pipeline_io (资产管线与导入导出)
- version: 1.1.0
- 状态: 已转正
- 一句话用途: 根据 Maya 选择集 (Object Sets) 批量将关联的模型、骨骼与动画导出为独立 FBX 资产。
- 适用场景: 游戏引擎分块导出、按 LOD 选择集导出、角色部件分拆导出。
- 不适用场景: 未建立选择集的单体杂乱导出。

## 调用前提

- Maya 与 Python 实测版本: Maya 2023 / 2024 / 2025 (Python 3.9+)
- 必需插件: `fbxmaya` 插件（已加载）。
- 场景节点: 场景中存在合法的 `objectSet`。

## API

调用入口: `maya_toolkit.execute_tool("export_sets_to_fbx", arguments={...}, dry_run=True/False)`

| 参数 | 类型 | 必填 | 默认值 | 含义与限制 |
| --- | --- | --- | --- | --- |
| output_directory | string | 是 | 无 | 导出文件的目标绝对路径。 |
| set_names | array[string] | 否 | [] (全部导出集合) | 指定要导出的选择集名称列表。 |
| bake_animation | boolean | 否 | False | 是否烘焙动画曲线。 |
| time_range | array[number] | 否 | None | 烘焙动画帧范围 `[start, end]`。 |

### dry_run 会检查什么

- 检查输出目录有效性，检测选择集中的成员物体，生成预导出文件清单，不写磁盘。

### 返回结果

- data 字段包含: `exported_files`, `processed_sets`, `skipped_sets`。

## 操作影响与恢复

- 修改的 Maya 场景内容: 无。
- 写入、覆盖或导出的文件: 在 `output_directory` 下写入对应的 `.fbx` 文件。
- Maya Undo 可撤销的范围: 文件系统操作不可由 Maya Undo 撤销。

## 调用示例

```python
import maya_toolkit

args = {"output_directory": "D:/Export/FBX", "bake_animation": False}
preview = maya_toolkit.execute_tool("export_sets_to_fbx", args, dry_run=True)
if preview.success:
    result = maya_toolkit.execute_tool("export_sets_to_fbx", args)
    print(result.to_dict())
```
