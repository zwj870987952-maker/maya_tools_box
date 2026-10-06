# 时间偏移（Time Offset）

移动动画时间，固定入口的数值由脚本预设。

- 状态：prepared_unverified，等待人工 Maya 直验。
- 输入：当前 Maya 选择、通道/Graph Editor 关键帧及时间区间；固定预设由下列脚本定义。
- 输出：候选 API 返回分派状态与操作后选择，不声称原算法已成功。
- 撤销：场景操作进入 Undo Chunk；外部文件、UI、插件、偏好不由 Maya Undo 撤回。

| operation ID | 原名称 | 执行源文件（相对 Animo_v10.6.0） | 具体用途/影响 |
| --- | --- | --- | --- |
| `time_offset.time_offset_plus_10_percent_29a99f86` | Time Offset +10% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Time Offset +10%.py` | 时间偏移：Time Offset +10%。移动动画时间，固定入口的数值由脚本预设。；关键帧数值、时间或切线 |
| `time_offset.time_offset_plus_100_percent_full_a289bd64` | Time Offset +100% (Full) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Time Offset +100% (Full).py` | 时间偏移：Time Offset +100% (Full)。移动动画时间，固定入口的数值由脚本预设。；关键帧数值、时间或切线 |
| `time_offset.time_offset_plus_150_percent_overshoot_663cb7e2` | Time Offset +150% (Overshoot) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Time Offset +150% (Overshoot).py` | 时间偏移：Time Offset +150% (Overshoot)。移动动画时间，固定入口的数值由脚本预设。；关键帧数值、时间或切线 |
| `time_offset.time_offset_plus_200_percent_extreme_overshoot_92eaa5c5` | Time Offset +200% (Extreme Overshoot) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Time Offset +200% (Extreme Overshoot).py` | 时间偏移：Time Offset +200% (Extreme Overshoot)。移动动画时间，固定入口的数值由脚本预设。；关键帧数值、时间或切线 |
| `time_offset.time_offset_plus_25_percent_19926e57` | Time Offset +25% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Time Offset +25%.py` | 时间偏移：Time Offset +25%。移动动画时间，固定入口的数值由脚本预设。；关键帧数值、时间或切线 |
| `time_offset.time_offset_plus_50_percent_6d78dd48` | Time Offset +50% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Time Offset +50%.py` | 时间偏移：Time Offset +50%。移动动画时间，固定入口的数值由脚本预设。；关键帧数值、时间或切线 |
| `time_offset.time_offset_plus_75_percent_c1abdd31` | Time Offset +75% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Time Offset +75%.py` | 时间偏移：Time Offset +75%。移动动画时间，固定入口的数值由脚本预设。；关键帧数值、时间或切线 |
| `time_offset.time_offset_plus_90_percent_bd51e495` | Time Offset +90% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Time Offset +90%.py` | 时间偏移：Time Offset +90%。移动动画时间，固定入口的数值由脚本预设。；关键帧数值、时间或切线 |
| `time_offset.time_offset_minus_10_percent_7e8e17ac` | Time Offset -10% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Time Offset -10%.py` | 时间偏移：Time Offset -10%。移动动画时间，固定入口的数值由脚本预设。；关键帧数值、时间或切线 |
| `time_offset.time_offset_minus_100_percent_full_93b54740` | Time Offset -100% (Full) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Time Offset -100% (Full).py` | 时间偏移：Time Offset -100% (Full)。移动动画时间，固定入口的数值由脚本预设。；关键帧数值、时间或切线 |
| `time_offset.time_offset_minus_150_percent_overshoot_e9fb8b8e` | Time Offset -150% (Overshoot) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Time Offset -150% (Overshoot).py` | 时间偏移：Time Offset -150% (Overshoot)。移动动画时间，固定入口的数值由脚本预设。；关键帧数值、时间或切线 |
| `time_offset.time_offset_minus_200_percent_extreme_overshoot_e77f0b43` | Time Offset -200% (Extreme Overshoot) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Time Offset -200% (Extreme Overshoot).py` | 时间偏移：Time Offset -200% (Extreme Overshoot)。移动动画时间，固定入口的数值由脚本预设。；关键帧数值、时间或切线 |
| `time_offset.time_offset_minus_25_percent_7b570fcd` | Time Offset -25% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Time Offset -25%.py` | 时间偏移：Time Offset -25%。移动动画时间，固定入口的数值由脚本预设。；关键帧数值、时间或切线 |
| `time_offset.time_offset_minus_50_percent_a1368874` | Time Offset -50% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Time Offset -50%.py` | 时间偏移：Time Offset -50%。移动动画时间，固定入口的数值由脚本预设。；关键帧数值、时间或切线 |
| `time_offset.time_offset_minus_75_percent_22d988bd` | Time Offset -75% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Time Offset -75%.py` | 时间偏移：Time Offset -75%。移动动画时间，固定入口的数值由脚本预设。；关键帧数值、时间或切线 |
| `time_offset.time_offset_minus_90_percent_1c58c620` | Time Offset -90% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Time Offset -90%.py` | 时间偏移：Time Offset -90%。移动动画时间，固定入口的数值由脚本预设。；关键帧数值、时间或切线 |

## 调用

```python
tool.run(dry_run=True, action="invoke", operation_id='time_offset.time_offset_plus_10_percent_29a99f86')
# 阅读预检结果后再执行：
# tool.run(action="invoke", operation_id='time_offset.time_offset_plus_10_percent_29a99f86')
```

所有入口的函数签名、顶层固定调用值及原索引别名见候选 `operations.json`；这些是静态证据，不表示运行兼容。
