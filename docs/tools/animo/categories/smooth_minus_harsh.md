# 平滑与强化（Smooth - Harsh）

平滑或强化动画数值变化。

- 状态：prepared_unverified，等待人工 Maya 直验。
- 输入：当前 Maya 选择、通道/Graph Editor 关键帧及时间区间；固定预设由下列脚本定义。
- 输出：候选 API 返回分派状态与操作后选择，不声称原算法已成功。
- 撤销：场景操作进入 Undo Chunk；外部文件、UI、插件、偏好不由 Maya Undo 撤回。

| operation ID | 原名称 | 执行源文件（相对 Animo_v10.6.0） | 具体用途/影响 |
| --- | --- | --- | --- |
| `smooth_minus_harsh.harsh_10_percent_b0355692` | Harsh 10% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Harsh 10%.py` | 平滑与强化：Harsh 10%。平滑或强化动画数值变化。；关键帧数值、时间或切线 |
| `smooth_minus_harsh.harsh_100_percent_full_60e82b57` | Harsh 100% (Full) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Harsh 100% (Full).py` | 平滑与强化：Harsh 100% (Full)。平滑或强化动画数值变化。；关键帧数值、时间或切线 |
| `smooth_minus_harsh.harsh_25_percent_d4e7b21b` | Harsh 25% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Harsh 25%.py` | 平滑与强化：Harsh 25%。平滑或强化动画数值变化。；关键帧数值、时间或切线 |
| `smooth_minus_harsh.harsh_50_percent_fab7ca54` | Harsh 50% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Harsh 50%.py` | 平滑与强化：Harsh 50%。平滑或强化动画数值变化。；关键帧数值、时间或切线 |
| `smooth_minus_harsh.harsh_75_percent_b223b146` | Harsh 75% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Harsh 75%.py` | 平滑与强化：Harsh 75%。平滑或强化动画数值变化。；关键帧数值、时间或切线 |
| `smooth_minus_harsh.harsh_90_percent_15de0616` | Harsh 90% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Harsh 90%.py` | 平滑与强化：Harsh 90%。平滑或强化动画数值变化。；关键帧数值、时间或切线 |
| `smooth_minus_harsh.smooth_10_percent_b36f241a` | Smooth 10% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Smooth 10%.py` | 平滑与强化：Smooth 10%。平滑或强化动画数值变化。；关键帧数值、时间或切线 |
| `smooth_minus_harsh.smooth_100_percent_full_cd7bd602` | Smooth 100% (Full) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Smooth 100% (Full).py` | 平滑与强化：Smooth 100% (Full)。平滑或强化动画数值变化。；关键帧数值、时间或切线 |
| `smooth_minus_harsh.smooth_25_percent_2acd2b77` | Smooth 25% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Smooth 25%.py` | 平滑与强化：Smooth 25%。平滑或强化动画数值变化。；关键帧数值、时间或切线 |
| `smooth_minus_harsh.smooth_50_percent_99d7ce6a` | Smooth 50% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Smooth 50%.py` | 平滑与强化：Smooth 50%。平滑或强化动画数值变化。；关键帧数值、时间或切线 |
| `smooth_minus_harsh.smooth_75_percent_6c41ecab` | Smooth 75% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Smooth 75%.py` | 平滑与强化：Smooth 75%。平滑或强化动画数值变化。；关键帧数值、时间或切线 |
| `smooth_minus_harsh.smooth_90_percent_1f021dcc` | Smooth 90% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Smooth 90%.py` | 平滑与强化：Smooth 90%。平滑或强化动画数值变化。；关键帧数值、时间或切线 |

## 调用

```python
tool.run(dry_run=True, action="invoke", operation_id='smooth_minus_harsh.harsh_10_percent_b0355692')
# 阅读预检结果后再执行：
# tool.run(action="invoke", operation_id='smooth_minus_harsh.harsh_10_percent_b0355692')
```

所有入口的函数签名、顶层固定调用值及原索引别名见候选 `operations.json`；这些是静态证据，不表示运行兼容。
