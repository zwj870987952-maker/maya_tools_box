# 操纵器（Manipulator）

调整 Move/Rotate/Scale 工具的坐标系或轴向行为。

- 状态：prepared_unverified，等待人工 Maya 直验。
- 输入：当前 Maya 选择、通道/Graph Editor 关键帧及时间区间；固定预设由下列脚本定义。
- 输出：候选 API 返回分派状态与操作后选择，不声称原算法已成功。
- 撤销：场景操作进入 Undo Chunk；外部文件、UI、插件、偏好不由 Maya Undo 撤回。

| operation ID | 原名称 | 执行源文件（相对 Animo_v10.6.0） | 具体用途/影响 |
| --- | --- | --- | --- |
| `manipulator.axis_orientation_to_camera_space_734d7b68` | Axis Orientation To Camera Space | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Axis Orientation To Camera Space.py` | 操纵器：Axis Orientation To Camera Space。调整 Move/Rotate/Scale 工具的坐标系或轴向行为。；Maya 工具设置 |
| `manipulator.axis_orientation_toggle_71bb8345` | Axis Orientation Toggle | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Axis Orientation Toggle.py` | 操纵器：Axis Orientation Toggle。调整 Move/Rotate/Scale 工具的坐标系或轴向行为。；Maya 工具设置 |
| `manipulator.micro_manipulator_tool_f5c8d87c` | Micro Manipulator Tool | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Micro Manip Tool.py` | 操纵器：Micro Manipulator Tool。调整 Move/Rotate/Scale 工具的坐标系或轴向行为。；Maya 工具设置 |

## 调用

```python
tool.run(dry_run=True, action="invoke", operation_id='manipulator.axis_orientation_to_camera_space_734d7b68')
# 阅读预检结果后再执行：
# tool.run(action="invoke", operation_id='manipulator.axis_orientation_to_camera_space_734d7b68')
```

所有入口的函数签名、顶层固定调用值及原索引别名见候选 `operations.json`；这些是静态证据，不表示运行兼容。
