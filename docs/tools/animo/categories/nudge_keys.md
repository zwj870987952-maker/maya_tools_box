# 关键帧微移（Nudge Keys）

按入口预设偏移关键帧时间。

- 状态：prepared_unverified，等待人工 Maya 直验。
- 输入：当前 Maya 选择、通道/Graph Editor 关键帧及时间区间；固定预设由下列脚本定义。
- 输出：候选 API 返回分派状态与操作后选择，不声称原算法已成功。
- 撤销：场景操作进入 Undo Chunk；外部文件、UI、插件、偏好不由 Maya Undo 撤回。

| operation ID | 原名称 | 执行源文件（相对 Animo_v10.6.0） | 具体用途/影响 |
| --- | --- | --- | --- |
| `nudge_keys.nudge_left_1_frame_4ffc171e` | Nudge Left 1 Frame | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Nudge Left 1 Frame.py` | 关键帧微移：Nudge Left 1 Frame。按入口预设偏移关键帧时间。；关键帧时间 |
| `nudge_keys.nudge_left_2_frames_3484ac44` | Nudge Left 2 Frames | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Nudge Left 2 Frames.py` | 关键帧微移：Nudge Left 2 Frames。按入口预设偏移关键帧时间。；关键帧时间 |
| `nudge_keys.nudge_left_3_frames_5695b18c` | Nudge Left 3 Frames | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Nudge Left 3 Frames.py` | 关键帧微移：Nudge Left 3 Frames。按入口预设偏移关键帧时间。；关键帧时间 |
| `nudge_keys.nudge_left_4_frames_e50f2d50` | Nudge Left 4 Frames | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Nudge Left 4 Frames.py` | 关键帧微移：Nudge Left 4 Frames。按入口预设偏移关键帧时间。；关键帧时间 |
| `nudge_keys.nudge_left_5_frames_0018af6b` | Nudge Left 5 Frames | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Nudge Left 5 Frames.py` | 关键帧微移：Nudge Left 5 Frames。按入口预设偏移关键帧时间。；关键帧时间 |
| `nudge_keys.nudge_right_1_frame_47f3603b` | Nudge Right 1 Frame | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Nudge Right 1 Frame.py` | 关键帧微移：Nudge Right 1 Frame。按入口预设偏移关键帧时间。；关键帧时间 |
| `nudge_keys.nudge_right_2_frames_9b7be34e` | Nudge Right 2 Frames | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Nudge Right 2 Frames.py` | 关键帧微移：Nudge Right 2 Frames。按入口预设偏移关键帧时间。；关键帧时间 |
| `nudge_keys.nudge_right_3_frames_9ede6ab5` | Nudge Right 3 Frames | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Nudge Right 3 Frames.py` | 关键帧微移：Nudge Right 3 Frames。按入口预设偏移关键帧时间。；关键帧时间 |
| `nudge_keys.nudge_right_4_frames_fdb5ffbd` | Nudge Right 4 Frames | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Nudge Right 4 Frames.py` | 关键帧微移：Nudge Right 4 Frames。按入口预设偏移关键帧时间。；关键帧时间 |
| `nudge_keys.nudge_right_5_frames_33a51df5` | Nudge Right 5 Frames | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Nudge Right 5 Frames.py` | 关键帧微移：Nudge Right 5 Frames。按入口预设偏移关键帧时间。；关键帧时间 |
| `nudge_keys.open_nudge_keys_ui_6644916c` | Open Nudge Keys UI | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Open Nudge Keys UI.py` | 关键帧微移：Open Nudge Keys UI。按入口预设偏移关键帧时间。；关键帧时间 |

## 调用

```python
tool.run(dry_run=True, action="invoke", operation_id='nudge_keys.nudge_left_1_frame_4ffc171e')
# 阅读预检结果后再执行：
# tool.run(action="invoke", operation_id='nudge_keys.nudge_left_1_frame_4ffc171e')
```

所有入口的函数签名、顶层固定调用值及原索引别名见候选 `operations.json`；这些是静态证据，不表示运行兼容。
