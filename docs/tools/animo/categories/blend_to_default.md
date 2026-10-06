# 混合至默认值（Blend to Default）

将动画数值混合至默认属性。

- 状态：prepared_unverified，等待人工 Maya 直验。
- 输入：当前 Maya 选择、通道/Graph Editor 关键帧及时间区间；固定预设由下列脚本定义。
- 输出：候选 API 返回分派状态与操作后选择，不声称原算法已成功。
- 撤销：场景操作进入 Undo Chunk；外部文件、UI、插件、偏好不由 Maya Undo 撤回。

| operation ID | 原名称 | 执行源文件（相对 Animo_v10.6.0） | 具体用途/影响 |
| --- | --- | --- | --- |
| `blend_to_default.blend_to_default_away_10_percent_12110883` | Blend to Default Away 10% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Blend to Default Away 10%.py` | 混合至默认值：Blend to Default Away 10%。将动画数值混合至默认属性。；关键帧数值、时间或切线 |
| `blend_to_default.blend_to_default_away_100_percent_full_91ad765f` | Blend to Default Away 100% (Full) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Blend to Default Away 100% (Full).py` | 混合至默认值：Blend to Default Away 100% (Full)。将动画数值混合至默认属性。；关键帧数值、时间或切线 |
| `blend_to_default.blend_to_default_away_150_percent_overshoot_8eb3fd2c` | Blend to Default Away 150% (Overshoot) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Blend to Default Away 150% (Overshoot).py` | 混合至默认值：Blend to Default Away 150% (Overshoot)。将动画数值混合至默认属性。；关键帧数值、时间或切线 |
| `blend_to_default.blend_to_default_away_200_percent_extreme_overshoot_b0307e3c` | Blend to Default Away 200% (Extreme Overshoot) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Blend to Default Away 200% (Extreme Overshoot).py` | 混合至默认值：Blend to Default Away 200% (Extreme Overshoot)。将动画数值混合至默认属性。；关键帧数值、时间或切线 |
| `blend_to_default.blend_to_default_away_25_percent_f9a2cdab` | Blend to Default Away 25% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Blend to Default Away 25%.py` | 混合至默认值：Blend to Default Away 25%。将动画数值混合至默认属性。；关键帧数值、时间或切线 |
| `blend_to_default.blend_to_default_away_50_percent_d4eca4a6` | Blend to Default Away 50% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Blend to Default Away 50%.py` | 混合至默认值：Blend to Default Away 50%。将动画数值混合至默认属性。；关键帧数值、时间或切线 |
| `blend_to_default.blend_to_default_away_75_percent_2e99a4fd` | Blend to Default Away 75% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Blend to Default Away 75%.py` | 混合至默认值：Blend to Default Away 75%。将动画数值混合至默认属性。；关键帧数值、时间或切线 |
| `blend_to_default.blend_to_default_away_90_percent_72120c34` | Blend to Default Away 90% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Blend to Default Away 90%.py` | 混合至默认值：Blend to Default Away 90%。将动画数值混合至默认属性。；关键帧数值、时间或切线 |
| `blend_to_default.blend_to_default_toward_10_percent_9430c451` | Blend to Default Toward 10% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Blend to Default Toward 10%.py` | 混合至默认值：Blend to Default Toward 10%。将动画数值混合至默认属性。；关键帧数值、时间或切线 |
| `blend_to_default.blend_to_default_toward_100_percent_full_07121761` | Blend to Default Toward 100% (Full) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Blend to Default Toward 100% (Full).py` | 混合至默认值：Blend to Default Toward 100% (Full)。将动画数值混合至默认属性。；关键帧数值、时间或切线 |
| `blend_to_default.blend_to_default_toward_150_percent_overshoot_0329f847` | Blend to Default Toward 150% (Overshoot) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Blend to Default Toward 150% (Overshoot).py` | 混合至默认值：Blend to Default Toward 150% (Overshoot)。将动画数值混合至默认属性。；关键帧数值、时间或切线 |
| `blend_to_default.blend_to_default_toward_200_percent_extreme_overshoot_da482c4a` | Blend to Default Toward 200% (Extreme Overshoot) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Blend to Default Toward 200% (Extreme Overshoot).py` | 混合至默认值：Blend to Default Toward 200% (Extreme Overshoot)。将动画数值混合至默认属性。；关键帧数值、时间或切线 |
| `blend_to_default.blend_to_default_toward_25_percent_36180a69` | Blend to Default Toward 25% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Blend to Default Toward 25%.py` | 混合至默认值：Blend to Default Toward 25%。将动画数值混合至默认属性。；关键帧数值、时间或切线 |
| `blend_to_default.blend_to_default_toward_50_percent_cd19a081` | Blend to Default Toward 50% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Blend to Default Toward 50%.py` | 混合至默认值：Blend to Default Toward 50%。将动画数值混合至默认属性。；关键帧数值、时间或切线 |
| `blend_to_default.blend_to_default_toward_75_percent_0ea80525` | Blend to Default Toward 75% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Blend to Default Toward 75%.py` | 混合至默认值：Blend to Default Toward 75%。将动画数值混合至默认属性。；关键帧数值、时间或切线 |
| `blend_to_default.blend_to_default_toward_90_percent_88273bc8` | Blend to Default Toward 90% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Blend to Default Toward 90%.py` | 混合至默认值：Blend to Default Toward 90%。将动画数值混合至默认属性。；关键帧数值、时间或切线 |

## 调用

```python
tool.run(dry_run=True, action="invoke", operation_id='blend_to_default.blend_to_default_away_10_percent_12110883')
# 阅读预检结果后再执行：
# tool.run(action="invoke", operation_id='blend_to_default.blend_to_default_away_10_percent_12110883')
```

所有入口的函数签名、顶层固定调用值及原索引别名见候选 `operations.json`；这些是静态证据，不表示运行兼容。
