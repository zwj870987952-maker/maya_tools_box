# 围绕均值缩放（Scale Average）

围绕均值调整动画幅度。

- 状态：prepared_unverified，等待人工 Maya 直验。
- 输入：当前 Maya 选择、通道/Graph Editor 关键帧及时间区间；固定预设由下列脚本定义。
- 输出：候选 API 返回分派状态与操作后选择，不声称原算法已成功。
- 撤销：场景操作进入 Undo Chunk；外部文件、UI、插件、偏好不由 Maya Undo 撤回。

| operation ID | 原名称 | 执行源文件（相对 Animo_v10.6.0） | 具体用途/影响 |
| --- | --- | --- | --- |
| `scale_average.scale_average_exaggerate_10_percent_094610db` | Scale Average Exaggerate 10% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Scale Average Exaggerate 10%.py` | 围绕均值缩放：Scale Average Exaggerate 10%。围绕均值调整动画幅度。；关键帧数值、时间或切线 |
| `scale_average.scale_average_exaggerate_100_percent_full_a375894c` | Scale Average Exaggerate 100% (Full) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Scale Average Exaggerate 100% (Full).py` | 围绕均值缩放：Scale Average Exaggerate 100% (Full)。围绕均值调整动画幅度。；关键帧数值、时间或切线 |
| `scale_average.scale_average_exaggerate_150_percent_overshoot_1a54cacb` | Scale Average Exaggerate 150% (Overshoot) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Scale Average Exaggerate 150% (Overshoot).py` | 围绕均值缩放：Scale Average Exaggerate 150% (Overshoot)。围绕均值调整动画幅度。；关键帧数值、时间或切线 |
| `scale_average.scale_average_exaggerate_200_percent_extreme_overshoot_74584a04` | Scale Average Exaggerate 200% (Extreme Overshoot) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Scale Average Exaggerate 200% (Extreme Overshoot).py` | 围绕均值缩放：Scale Average Exaggerate 200% (Extreme Overshoot)。围绕均值调整动画幅度。；关键帧数值、时间或切线 |
| `scale_average.scale_average_exaggerate_25_percent_311a14d5` | Scale Average Exaggerate 25% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Scale Average Exaggerate 25%.py` | 围绕均值缩放：Scale Average Exaggerate 25%。围绕均值调整动画幅度。；关键帧数值、时间或切线 |
| `scale_average.scale_average_exaggerate_50_percent_ce4acdbd` | Scale Average Exaggerate 50% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Scale Average Exaggerate 50%.py` | 围绕均值缩放：Scale Average Exaggerate 50%。围绕均值调整动画幅度。；关键帧数值、时间或切线 |
| `scale_average.scale_average_exaggerate_75_percent_6fb6cf7a` | Scale Average Exaggerate 75% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Scale Average Exaggerate 75%.py` | 围绕均值缩放：Scale Average Exaggerate 75%。围绕均值调整动画幅度。；关键帧数值、时间或切线 |
| `scale_average.scale_average_exaggerate_90_percent_51ceaa0e` | Scale Average Exaggerate 90% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Scale Average Exaggerate 90%.py` | 围绕均值缩放：Scale Average Exaggerate 90%。围绕均值调整动画幅度。；关键帧数值、时间或切线 |
| `scale_average.scale_average_reduce_10_percent_6926afc3` | Scale Average Reduce 10% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Scale Average Reduce 10%.py` | 围绕均值缩放：Scale Average Reduce 10%。围绕均值调整动画幅度。；关键帧数值、时间或切线 |
| `scale_average.scale_average_reduce_100_percent_full_7e9315f2` | Scale Average Reduce 100% (Full) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Scale Average Reduce 100% (Full).py` | 围绕均值缩放：Scale Average Reduce 100% (Full)。围绕均值调整动画幅度。；关键帧数值、时间或切线 |
| `scale_average.scale_average_reduce_150_percent_overshoot_1d99b1a3` | Scale Average Reduce 150% (Overshoot) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Scale Average Reduce 150% (Overshoot).py` | 围绕均值缩放：Scale Average Reduce 150% (Overshoot)。围绕均值调整动画幅度。；关键帧数值、时间或切线 |
| `scale_average.scale_average_reduce_200_percent_extreme_overshoot_9a5771c8` | Scale Average Reduce 200% (Extreme Overshoot) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Scale Average Reduce 200% (Extreme Overshoot).py` | 围绕均值缩放：Scale Average Reduce 200% (Extreme Overshoot)。围绕均值调整动画幅度。；关键帧数值、时间或切线 |
| `scale_average.scale_average_reduce_25_percent_fba73a2b` | Scale Average Reduce 25% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Scale Average Reduce 25%.py` | 围绕均值缩放：Scale Average Reduce 25%。围绕均值调整动画幅度。；关键帧数值、时间或切线 |
| `scale_average.scale_average_reduce_50_percent_780ec9e2` | Scale Average Reduce 50% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Scale Average Reduce 50%.py` | 围绕均值缩放：Scale Average Reduce 50%。围绕均值调整动画幅度。；关键帧数值、时间或切线 |
| `scale_average.scale_average_reduce_75_percent_d9c98a60` | Scale Average Reduce 75% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Scale Average Reduce 75%.py` | 围绕均值缩放：Scale Average Reduce 75%。围绕均值调整动画幅度。；关键帧数值、时间或切线 |
| `scale_average.scale_average_reduce_90_percent_e6ccc30c` | Scale Average Reduce 90% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Scale Average Reduce 90%.py` | 围绕均值缩放：Scale Average Reduce 90%。围绕均值调整动画幅度。；关键帧数值、时间或切线 |

## 调用

```python
tool.run(dry_run=True, action="invoke", operation_id='scale_average.scale_average_exaggerate_10_percent_094610db')
# 阅读预检结果后再执行：
# tool.run(action="invoke", operation_id='scale_average.scale_average_exaggerate_10_percent_094610db')
```

所有入口的函数签名、顶层固定调用值及原索引别名见候选 `operations.json`；这些是静态证据，不表示运行兼容。
