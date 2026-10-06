# 错开时间（Time Offset Stagger）

按对象顺序错开动画时间。

- 状态：prepared_unverified，等待人工 Maya 直验。
- 输入：当前 Maya 选择、通道/Graph Editor 关键帧及时间区间；固定预设由下列脚本定义。
- 输出：候选 API 返回分派状态与操作后选择，不声称原算法已成功。
- 撤销：场景操作进入 Undo Chunk；外部文件、UI、插件、偏好不由 Maya Undo 撤回。

| operation ID | 原名称 | 执行源文件（相对 Animo_v10.6.0） | 具体用途/影响 |
| --- | --- | --- | --- |
| `time_offset_stagger.time_offset_stagger_plus_10_percent_a7a8e7c8` | Time Offset Stagger +10% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Time Offset Stagger +10%.py` | 错开时间：Time Offset Stagger +10%。按对象顺序错开动画时间。；关键帧数值、时间或切线 |
| `time_offset_stagger.time_offset_stagger_plus_100_percent_full_3eac4fca` | Time Offset Stagger +100% (Full) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Time Offset Stagger +100% (Full).py` | 错开时间：Time Offset Stagger +100% (Full)。按对象顺序错开动画时间。；关键帧数值、时间或切线 |
| `time_offset_stagger.time_offset_stagger_plus_150_percent_overshoot_c715e667` | Time Offset Stagger +150% (Overshoot) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Time Offset Stagger +150% (Overshoot).py` | 错开时间：Time Offset Stagger +150% (Overshoot)。按对象顺序错开动画时间。；关键帧数值、时间或切线 |
| `time_offset_stagger.time_offset_stagger_plus_200_percent_extreme_overshoot_00dcb90e` | Time Offset Stagger +200% (Extreme Overshoot) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Time Offset Stagger +200% (Extreme Overshoot).py` | 错开时间：Time Offset Stagger +200% (Extreme Overshoot)。按对象顺序错开动画时间。；关键帧数值、时间或切线 |
| `time_offset_stagger.time_offset_stagger_plus_25_percent_0a1d13d8` | Time Offset Stagger +25% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Time Offset Stagger +25%.py` | 错开时间：Time Offset Stagger +25%。按对象顺序错开动画时间。；关键帧数值、时间或切线 |
| `time_offset_stagger.time_offset_stagger_plus_50_percent_100cccda` | Time Offset Stagger +50% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Time Offset Stagger +50%.py` | 错开时间：Time Offset Stagger +50%。按对象顺序错开动画时间。；关键帧数值、时间或切线 |
| `time_offset_stagger.time_offset_stagger_plus_75_percent_55221da5` | Time Offset Stagger +75% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Time Offset Stagger +75%.py` | 错开时间：Time Offset Stagger +75%。按对象顺序错开动画时间。；关键帧数值、时间或切线 |
| `time_offset_stagger.time_offset_stagger_plus_90_percent_0e59f3f1` | Time Offset Stagger +90% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Time Offset Stagger +90%.py` | 错开时间：Time Offset Stagger +90%。按对象顺序错开动画时间。；关键帧数值、时间或切线 |
| `time_offset_stagger.time_offset_stagger_minus_10_percent_d80dfb00` | Time Offset Stagger -10% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Time Offset Stagger -10%.py` | 错开时间：Time Offset Stagger -10%。按对象顺序错开动画时间。；关键帧数值、时间或切线 |
| `time_offset_stagger.time_offset_stagger_minus_100_percent_full_afe1b759` | Time Offset Stagger -100% (Full) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Time Offset Stagger -100% (Full).py` | 错开时间：Time Offset Stagger -100% (Full)。按对象顺序错开动画时间。；关键帧数值、时间或切线 |
| `time_offset_stagger.time_offset_stagger_minus_150_percent_overshoot_c193a93e` | Time Offset Stagger -150% (Overshoot) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Time Offset Stagger -150% (Overshoot).py` | 错开时间：Time Offset Stagger -150% (Overshoot)。按对象顺序错开动画时间。；关键帧数值、时间或切线 |
| `time_offset_stagger.time_offset_stagger_minus_200_percent_extreme_overshoot_4ed0ee33` | Time Offset Stagger -200% (Extreme Overshoot) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Time Offset Stagger -200% (Extreme Overshoot).py` | 错开时间：Time Offset Stagger -200% (Extreme Overshoot)。按对象顺序错开动画时间。；关键帧数值、时间或切线 |
| `time_offset_stagger.time_offset_stagger_minus_25_percent_4262bfab` | Time Offset Stagger -25% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Time Offset Stagger -25%.py` | 错开时间：Time Offset Stagger -25%。按对象顺序错开动画时间。；关键帧数值、时间或切线 |
| `time_offset_stagger.time_offset_stagger_minus_50_percent_fb3a31e7` | Time Offset Stagger -50% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Time Offset Stagger -50%.py` | 错开时间：Time Offset Stagger -50%。按对象顺序错开动画时间。；关键帧数值、时间或切线 |
| `time_offset_stagger.time_offset_stagger_minus_75_percent_aab25fec` | Time Offset Stagger -75% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Time Offset Stagger -75%.py` | 错开时间：Time Offset Stagger -75%。按对象顺序错开动画时间。；关键帧数值、时间或切线 |
| `time_offset_stagger.time_offset_stagger_minus_90_percent_6dda88ea` | Time Offset Stagger -90% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Time Offset Stagger -90%.py` | 错开时间：Time Offset Stagger -90%。按对象顺序错开动画时间。；关键帧数值、时间或切线 |

## 调用

```python
tool.run(dry_run=True, action="invoke", operation_id='time_offset_stagger.time_offset_stagger_plus_10_percent_a7a8e7c8')
# 阅读预检结果后再执行：
# tool.run(action="invoke", operation_id='time_offset_stagger.time_offset_stagger_plus_10_percent_a7a8e7c8')
```

所有入口的函数签名、顶层固定调用值及原索引别名见候选 `operations.json`；这些是静态证据，不表示运行兼容。
