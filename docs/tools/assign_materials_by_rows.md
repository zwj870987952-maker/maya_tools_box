# assign_materials_by_rows (逐行指定材质工具)

## 身份与用途

- tool_id: assign_materials_by_rows
- category: modeling_surfacing (模型、外观与材质)
- version: 1.1.0
- 状态: 已转正
- 一句话用途: 根据空间排列阵列或列表规则，将指定材质球批量赋予模型行或组件。
- 适用场景: 阵列建筑外立面着色、色板测试排布、资产批次材质赋予。
- 不适用场景: 复杂的程序化分面材质网络烘焙。

## 调用前提

- Maya 与 Python 实测版本: Maya 2023 / 2024 / 2025 (Python 3.9+)
- 场景节点: 场景中存在合法的材质球（Shader）与其 ShadingEngine。

## API

调用入口: `maya_toolkit.execute_tool("assign_materials_by_rows", arguments={...}, dry_run=True/False)`

| 参数 | 类型 | 必填 | 默认值 | 含义与限制 |
| --- | --- | --- | --- | --- |
| objects | array[string] | 是 | 无 | 待赋予材质的目标模型列表。 |
| materials | array[string] | 是 | 无 | 赋予的材质球名称列表。 |
| row_axis | string | 否 | "Y" | 排列行识别的主轴向 ("X", "Y", "Z")。 |

### dry_run 会检查什么

- 检测物体与材质球是否存在，计算每个物体所属的行分组与对应指定的材质，不修改 shadingGroup。

### 返回结果

- data 字段包含: `assignments`, `total_assigned`。

## 操作影响与恢复

- 修改的 Maya 场景内容: 目标物体的 Shading Group 连接。
- 写入、覆盖或导出的文件: 无。
- Maya Undo 可撤销的范围: 单步 Undo 完全还原初始材质连接。

## 调用示例

```python
import maya_toolkit

args = {"objects": ["poly_row_01", "poly_row_02"], "materials": ["M_Red", "M_Blue"]}
preview = maya_toolkit.execute_tool("assign_materials_by_rows", args, dry_run=True)
if preview.success:
    result = maya_toolkit.execute_tool("assign_materials_by_rows", args)
    print(result.to_dict())
```
