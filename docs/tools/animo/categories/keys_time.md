# 关键帧时间传递（Keys Time）

复制/粘贴通道或姿势间的关键帧时间，清理时间分布。

- 状态：prepared_unverified，等待人工 Maya 直验。
- 输入：当前 Maya 选择、通道/Graph Editor 关键帧及时间区间；固定预设由下列脚本定义。
- 输出：候选 API 返回分派状态与操作后选择，不声称原算法已成功。
- 撤销：场景操作进入 Undo Chunk；外部文件、UI、插件、偏好不由 Maya Undo 撤回。

| operation ID | 原名称 | 执行源文件（相对 Animo_v10.6.0） | 具体用途/影响 |
| --- | --- | --- | --- |
| `keys_time.clean_keys_interactive_8f8159cf` | Clean Keys Interactive | `Animo_Data/Animo_Tools_Editor/tools_library/Keys Time/Clean Keys Interactive.py` | 关键帧时间传递：Clean Keys Interactive。复制/粘贴通道或姿势间的关键帧时间，清理时间分布。；关键帧时间及本机缓存 |
| `keys_time.copy_key_times_channels_b52d83c2` | Copy Key Times Channels | `Animo_Data/Animo_Tools_Editor/tools_library/Keys Time/Copy Key Times Channels.py` | 关键帧时间传递：Copy Key Times Channels。复制/粘贴通道或姿势间的关键帧时间，清理时间分布。；关键帧时间及本机缓存 |
| `keys_time.copy_key_times_pose_to_pose_f8b1fd99` | Copy Key Times Pose To Pose | `Animo_Data/Animo_Tools_Editor/tools_library/Keys Time/Copy Key Times Pose To Pose.py` | 关键帧时间传递：Copy Key Times Pose To Pose。复制/粘贴通道或姿势间的关键帧时间，清理时间分布。；关键帧时间及本机缓存 |
| `keys_time.copy_key_timing_minus_by_channel_a44d8f36` | Copy Key Timing - By Channel | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Copy Key Timing - By Channel.py` | 关键帧时间传递：Copy Key Timing - By Channel。复制/粘贴通道或姿势间的关键帧时间，清理时间分布。；关键帧时间及本机缓存 |
| `keys_time.copy_key_timing_minus_pose_to_pose_3c796b42` | Copy Key Timing - Pose to Pose | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Copy Key Timing - Pose to Pose.py` | 关键帧时间传递：Copy Key Timing - Pose to Pose。复制/粘贴通道或姿势间的关键帧时间，清理时间分布。；关键帧时间及本机缓存 |
| `keys_time.paste_key_times_channels_50758553` | Paste Key Times Channels | `Animo_Data/Animo_Tools_Editor/tools_library/Keys Time/Paste Key Times Channels.py` | 关键帧时间传递：Paste Key Times Channels。复制/粘贴通道或姿势间的关键帧时间，清理时间分布。；关键帧时间及本机缓存 |
| `keys_time.paste_key_times_pose_to_pose_800f1c1f` | Paste Key Times Pose To Pose | `Animo_Data/Animo_Tools_Editor/tools_library/Keys Time/Paste Key Times Pose To Pose.py` | 关键帧时间传递：Paste Key Times Pose To Pose。复制/粘贴通道或姿势间的关键帧时间，清理时间分布。；关键帧时间及本机缓存 |
| `keys_time.paste_key_timing_minus_by_channel_75c397eb` | Paste Key Timing - By Channel | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Paste Key Timing - By Channel.py` | 关键帧时间传递：Paste Key Timing - By Channel。复制/粘贴通道或姿势间的关键帧时间，清理时间分布。；关键帧时间及本机缓存 |
| `keys_time.paste_key_timing_minus_pose_to_pose_7f9fca44` | Paste Key Timing - Pose to Pose | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Paste Key Timing - Pose to Pose.py` | 关键帧时间传递：Paste Key Timing - Pose to Pose。复制/粘贴通道或姿势间的关键帧时间，清理时间分布。；关键帧时间及本机缓存 |

## 调用

```python
tool.run(dry_run=True, action="invoke", operation_id='keys_time.clean_keys_interactive_8f8159cf')
# 阅读预检结果后再执行：
# tool.run(action="invoke", operation_id='keys_time.clean_keys_interactive_8f8159cf')
```

所有入口的函数签名、顶层固定调用值及原索引别名见候选 `operations.json`；这些是静态证据，不表示运行兼容。
