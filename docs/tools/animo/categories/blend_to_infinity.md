# 混合至 Infinity（Blend to Infinity）

按曲线 Infinity 行为混合动画。

- 状态：prepared_unverified，等待人工 Maya 直验。
- 输入：当前 Maya 选择、通道/Graph Editor 关键帧及时间区间；固定预设由下列脚本定义。
- 输出：候选 API 返回分派状态与操作后选择，不声称原算法已成功。
- 撤销：场景操作进入 Undo Chunk；外部文件、UI、插件、偏好不由 Maya Undo 撤回。

| operation ID | 原名称 | 执行源文件（相对 Animo_v10.6.0） | 具体用途/影响 |
| --- | --- | --- | --- |
| `blend_to_infinity.extend_left_10_percent_dea69fd2` | Extend Left 10% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Extend Left 10%.py` | 混合至 Infinity：Extend Left 10%。按曲线 Infinity 行为混合动画。；关键帧数值、时间或切线 |
| `blend_to_infinity.extend_left_100_percent_full_b8cd84c6` | Extend Left 100% (Full) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Extend Left 100% (Full).py` | 混合至 Infinity：Extend Left 100% (Full)。按曲线 Infinity 行为混合动画。；关键帧数值、时间或切线 |
| `blend_to_infinity.extend_left_25_percent_77d5a649` | Extend Left 25% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Extend Left 25%.py` | 混合至 Infinity：Extend Left 25%。按曲线 Infinity 行为混合动画。；关键帧数值、时间或切线 |
| `blend_to_infinity.extend_left_50_percent_30ebb096` | Extend Left 50% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Extend Left 50%.py` | 混合至 Infinity：Extend Left 50%。按曲线 Infinity 行为混合动画。；关键帧数值、时间或切线 |
| `blend_to_infinity.extend_left_75_percent_fceda6cb` | Extend Left 75% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Extend Left 75%.py` | 混合至 Infinity：Extend Left 75%。按曲线 Infinity 行为混合动画。；关键帧数值、时间或切线 |
| `blend_to_infinity.extend_left_90_percent_2e42ce8a` | Extend Left 90% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Extend Left 90%.py` | 混合至 Infinity：Extend Left 90%。按曲线 Infinity 行为混合动画。；关键帧数值、时间或切线 |
| `blend_to_infinity.extend_right_10_percent_b1b9e432` | Extend Right 10% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Extend Right 10%.py` | 混合至 Infinity：Extend Right 10%。按曲线 Infinity 行为混合动画。；关键帧数值、时间或切线 |
| `blend_to_infinity.extend_right_100_percent_full_fa51c2ec` | Extend Right 100% (Full) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Extend Right 100% (Full).py` | 混合至 Infinity：Extend Right 100% (Full)。按曲线 Infinity 行为混合动画。；关键帧数值、时间或切线 |
| `blend_to_infinity.extend_right_25_percent_c5a33509` | Extend Right 25% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Extend Right 25%.py` | 混合至 Infinity：Extend Right 25%。按曲线 Infinity 行为混合动画。；关键帧数值、时间或切线 |
| `blend_to_infinity.extend_right_50_percent_d7092f46` | Extend Right 50% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Extend Right 50%.py` | 混合至 Infinity：Extend Right 50%。按曲线 Infinity 行为混合动画。；关键帧数值、时间或切线 |
| `blend_to_infinity.extend_right_75_percent_8b359b0f` | Extend Right 75% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Extend Right 75%.py` | 混合至 Infinity：Extend Right 75%。按曲线 Infinity 行为混合动画。；关键帧数值、时间或切线 |
| `blend_to_infinity.extend_right_90_percent_5bc5b144` | Extend Right 90% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Extend Right 90%.py` | 混合至 Infinity：Extend Right 90%。按曲线 Infinity 行为混合动画。；关键帧数值、时间或切线 |

## 调用

```python
tool.run(dry_run=True, action="invoke", operation_id='blend_to_infinity.extend_left_10_percent_dea69fd2')
# 阅读预检结果后再执行：
# tool.run(action="invoke", operation_id='blend_to_infinity.extend_left_10_percent_dea69fd2')
```

所有入口的函数签名、顶层固定调用值及原索引别名见候选 `operations.json`；这些是静态证据，不表示运行兼容。
