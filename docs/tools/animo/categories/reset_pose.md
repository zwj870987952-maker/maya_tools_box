# 姿态复位（Reset Pose）

恢复原工具记录的默认属性，支持位移、旋转、缩放或全部。

- 状态：prepared_unverified，等待人工 Maya 直验。
- 输入：当前 Maya 选择、通道/Graph Editor 关键帧及时间区间；固定预设由下列脚本定义。
- 输出：候选 API 返回分派状态与操作后选择，不声称原算法已成功。
- 撤销：场景操作进入 Undo Chunk；外部文件、UI、插件、偏好不由 Maya Undo 撤回。

| operation ID | 原名称 | 执行源文件（相对 Animo_v10.6.0） | 具体用途/影响 |
| --- | --- | --- | --- |
| `reset_pose.reset_pose_81d353b8` | Reset Pose | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Reset Pose.py` | 姿态复位：Reset Pose。恢复原工具记录的默认属性，支持位移、旋转、缩放或全部。；属性或关键帧 |
| `reset_pose.reset_rotate_00e87645` | Reset Rotate | `Animo_Data/Animo_Tools_Editor/tools_library/Reset Pose/Reset Rotate.py` | 姿态复位：Reset Rotate。恢复原工具记录的默认属性，支持位移、旋转、缩放或全部。；属性或关键帧 |
| `reset_pose.reset_scale_a9b49c85` | Reset Scale | `Animo_Data/Animo_Tools_Editor/tools_library/Reset Pose/Reset Scale.py` | 姿态复位：Reset Scale。恢复原工具记录的默认属性，支持位移、旋转、缩放或全部。；属性或关键帧 |
| `reset_pose.reset_transforms_f23231bd` | Reset Transforms | `Animo_Data/Animo_Tools_Editor/tools_library/Reset Pose/Reset Transforms.py` | 姿态复位：Reset Transforms。恢复原工具记录的默认属性，支持位移、旋转、缩放或全部。；属性或关键帧 |
| `reset_pose.reset_translate_5b70cc03` | Reset Translate | `Animo_Data/Animo_Tools_Editor/tools_library/Reset Pose/Reset Translate.py` | 姿态复位：Reset Translate。恢复原工具记录的默认属性，支持位移、旋转、缩放或全部。；属性或关键帧 |

## 调用

```python
tool.run(dry_run=True, action="invoke", operation_id='reset_pose.reset_pose_81d353b8')
# 阅读预检结果后再执行：
# tool.run(action="invoke", operation_id='reset_pose.reset_pose_81d353b8')
```

所有入口的函数签名、顶层固定调用值及原索引别名见候选 `operations.json`；这些是静态证据，不表示运行兼容。
