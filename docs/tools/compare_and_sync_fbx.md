# compare_and_sync_fbx (FBX外部资产深度比对与同步工具)

## 身份与用途

- tool_id: compare_and_sync_fbx
- category: pipeline_io (资产管线与导入导出)
- version: 1.3.0
- 状态: 已转正
- 一句话用途: 纯内存直接解析外部 FBX 文件并与当前 Maya 场景模型进行拓扑、UV、材质与位姿深度比对与精准同步。
- 适用场景: 美术资产版本迭代核对、下游动画资产与最新建模网格同步、材质分面差异排查。
- 不适用场景: 非 FBX 格式的私有二进制资产。

## 调用前提

- Maya 与 Python 实测版本: Maya 2023 / 2024 / 2025 (Python 3.9+)
- 必需插件: FBX SDK / `fbxmaya` 插件支持。
- 输入条件: 外部 `.fbx` 文件有效存在。

## API

调用入口: `maya_toolkit.execute_tool("compare_and_sync_fbx", arguments={...}, dry_run=True/False)`

| 参数 | 类型 | 必填 | 默认值 | 含义与限制 |
| --- | --- | --- | --- | --- |
| fbx_path | string | 是 | 无 | 待比对的外部 FBX 文件的绝对路径。 |
| action | string | 否 | "diff_only" | "diff_only", "sync_materials", "sync_transforms", "sync_all"。 |
| match_by_short_name | boolean | 否 | True | 是否通过短名匹配同名模型。 |

### dry_run 会检查什么

- 解析 FBX 结构并比对场景节点，生成差异分析报告（包括顶点数差异、面数差异、材质分面匹配），不修改场景。

### 返回结果

- data 字段包含: `diff_summary`, `matched_nodes`, `topology_differences`, `material_differences`, `transform_differences`。

## 操作影响与恢复

- 修改的 Maya 场景内容: 当 action 不为 "diff_only" 时，同步目标物体的空间变换或材质连接。
- 写入、覆盖或导出的文件: 无。
- Maya Undo 可撤销的范围: 处于 UndoChunk 保护内，单步 Undo 可恢复。

## 调用示例

```python
import maya_toolkit

args = {"fbx_path": "D:/Assets/hero_v2.fbx", "action": "diff_only"}
preview = maya_toolkit.execute_tool("compare_and_sync_fbx", args, dry_run=True)
if preview.success:
    result = maya_toolkit.execute_tool("compare_and_sync_fbx", args)
    print(result.to_dict())
```
