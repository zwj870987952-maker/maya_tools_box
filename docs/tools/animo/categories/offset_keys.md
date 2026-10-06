# 关键帧偏移（Offset Keys）

按固定步长或交互选项偏移关键帧。

- 状态：prepared_unverified，等待人工 Maya 直验。
- 输入：当前 Maya 选择、通道/Graph Editor 关键帧及时间区间；固定预设由下列脚本定义。
- 输出：候选 API 返回分派状态与操作后选择，不声称原算法已成功。
- 撤销：场景操作进入 Undo Chunk；外部文件、UI、插件、偏好不由 Maya Undo 撤回。

| operation ID | 原名称 | 执行源文件（相对 Animo_v10.6.0） | 具体用途/影响 |
| --- | --- | --- | --- |
| `offset_keys.offset_scale_sequentially_39b73e60` | Offset SCALE Sequentially | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Offset SCALE Sequentially.py` | 关键帧偏移：Offset SCALE Sequentially。按固定步长或交互选项偏移关键帧。；关键帧时间或数值 |
| `offset_keys.offset_time_sequentially_left_0_1_frame_86ad3322` | Offset TIME Sequentially Left 0.1 Frame | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Offset Sequentially Left 0.1 Frame.py` | 关键帧偏移：Offset TIME Sequentially Left 0.1 Frame。按固定步长或交互选项偏移关键帧。；关键帧时间或数值 |
| `offset_keys.offset_time_sequentially_left_0_5_frame_f4699a56` | Offset TIME Sequentially Left 0.5 Frame | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Offset Sequentially Left 0.5 Frame.py` | 关键帧偏移：Offset TIME Sequentially Left 0.5 Frame。按固定步长或交互选项偏移关键帧。；关键帧时间或数值 |
| `offset_keys.offset_time_sequentially_left_1_frame_ba402270` | Offset TIME Sequentially Left 1 Frame | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Offset Sequentially Left 1 Frame.py` | 关键帧偏移：Offset TIME Sequentially Left 1 Frame。按固定步长或交互选项偏移关键帧。；关键帧时间或数值 |
| `offset_keys.offset_time_sequentially_left_2_frames_1b77fdd4` | Offset TIME Sequentially Left 2 Frames | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Offset Sequentially Left 2 Frames.py` | 关键帧偏移：Offset TIME Sequentially Left 2 Frames。按固定步长或交互选项偏移关键帧。；关键帧时间或数值 |
| `offset_keys.offset_time_sequentially_right_0_1_frame_adf29900` | Offset TIME Sequentially Right 0.1 Frame | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Offset Sequentially Right 0.1 Frame.py` | 关键帧偏移：Offset TIME Sequentially Right 0.1 Frame。按固定步长或交互选项偏移关键帧。；关键帧时间或数值 |
| `offset_keys.offset_time_sequentially_right_0_5_frame_9bd89905` | Offset TIME Sequentially Right 0.5 Frame | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Offset Sequentially Right 0.5 Frame.py` | 关键帧偏移：Offset TIME Sequentially Right 0.5 Frame。按固定步长或交互选项偏移关键帧。；关键帧时间或数值 |
| `offset_keys.offset_time_sequentially_right_1_frame_567c8867` | Offset TIME Sequentially Right 1 Frame | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Offset Sequentially Right 1 Frame.py` | 关键帧偏移：Offset TIME Sequentially Right 1 Frame。按固定步长或交互选项偏移关键帧。；关键帧时间或数值 |
| `offset_keys.offset_time_sequentially_right_2_frames_4822f860` | Offset TIME Sequentially Right 2 Frames | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Offset Sequentially Right 2 Frames.py` | 关键帧偏移：Offset TIME Sequentially Right 2 Frames。按固定步长或交互选项偏移关键帧。；关键帧时间或数值 |

## 调用

```python
tool.run(dry_run=True, action="invoke", operation_id='offset_keys.offset_scale_sequentially_39b73e60')
# 阅读预检结果后再执行：
# tool.run(action="invoke", operation_id='offset_keys.offset_scale_sequentially_39b73e60')
```

所有入口的函数签名、顶层固定调用值及原索引别名见候选 `operations.json`；这些是静态证据，不表示运行兼容。
