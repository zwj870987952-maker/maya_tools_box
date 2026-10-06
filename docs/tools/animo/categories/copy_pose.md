# 姿态传递（Copy Pose）

保存、读取姿态 JSON，按对象或命名空间应用。

- 状态：prepared_unverified，等待人工 Maya 直验。
- 输入：当前 Maya 选择、通道/Graph Editor 关键帧及时间区间；固定预设由下列脚本定义。
- 输出：候选 API 返回分派状态与操作后选择，不声称原算法已成功。
- 撤销：场景操作进入 Undo Chunk；外部文件、UI、插件、偏好不由 Maya Undo 撤回。

| operation ID | 原名称 | 执行源文件（相对 Animo_v10.6.0） | 具体用途/影响 |
| --- | --- | --- | --- |
| `copy_pose.copy_pose_17b14dc8` | Copy Pose | `Animo_Data/Animo_Transify/transify_action_copy_pose.py` | 姿态传递：Copy Pose。保存、读取姿态 JSON，按对象或命名空间应用。；属性及姿态 JSON 文件 |
| `copy_pose.paste_pose_91c5274c` | Paste Pose | `Animo_Data/Animo_Transify/transify_action_paste_pose.py` | 姿态传递：Paste Pose。保存、读取姿态 JSON，按对象或命名空间应用。；属性及姿态 JSON 文件 |
| `copy_pose.select_objects_fb4d5263` | Select Objects | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Select Objects.py` | 姿态传递：Select Objects。保存、读取姿态 JSON，按对象或命名空间应用。；属性及姿态 JSON 文件 |

## 调用

```python
tool.run(dry_run=True, action="invoke", operation_id='copy_pose.copy_pose_17b14dc8')
# 阅读预检结果后再执行：
# tool.run(action="invoke", operation_id='copy_pose.copy_pose_17b14dc8')
```

所有入口的函数签名、顶层固定调用值及原索引别名见候选 `operations.json`；这些是静态证据，不表示运行兼容。
