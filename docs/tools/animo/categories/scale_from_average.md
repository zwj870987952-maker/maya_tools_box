# 从均值缩放（Scale from Average）

按原入口的均值参考缩放动画幅度。

- 状态：prepared_unverified，等待人工 Maya 直验。
- 输入：当前 Maya 选择、通道/Graph Editor 关键帧及时间区间；固定预设由下列脚本定义。
- 输出：候选 API 返回分派状态与操作后选择，不声称原算法已成功。
- 撤销：场景操作进入 Undo Chunk；外部文件、UI、插件、偏好不由 Maya Undo 撤回。

| operation ID | 原名称 | 执行源文件（相对 Animo_v10.6.0） | 具体用途/影响 |
| --- | --- | --- | --- |
| `scale_from_average.scale_average_exaggerate_10_percent_dc1907ed` | Scale Average Exaggerate 10% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Scale Average Exaggerate 10%.py` | 从均值缩放：Scale Average Exaggerate 10%。按原入口的均值参考缩放动画幅度。；关键帧数值、时间或切线 |
| `scale_from_average.scale_average_exaggerate_100_percent_full_c32b1de2` | Scale Average Exaggerate 100% (Full) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Scale Average Exaggerate 100% (Full).py` | 从均值缩放：Scale Average Exaggerate 100% (Full)。按原入口的均值参考缩放动画幅度。；关键帧数值、时间或切线 |
| `scale_from_average.scale_average_exaggerate_150_percent_overshoot_119ad459` | Scale Average Exaggerate 150% (Overshoot) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Scale Average Exaggerate 150% (Overshoot).py` | 从均值缩放：Scale Average Exaggerate 150% (Overshoot)。按原入口的均值参考缩放动画幅度。；关键帧数值、时间或切线 |
| `scale_from_average.scale_average_exaggerate_200_percent_extreme_overshoot_513067d0` | Scale Average Exaggerate 200% (Extreme Overshoot) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Scale Average Exaggerate 200% (Extreme Overshoot).py` | 从均值缩放：Scale Average Exaggerate 200% (Extreme Overshoot)。按原入口的均值参考缩放动画幅度。；关键帧数值、时间或切线 |
| `scale_from_average.scale_average_exaggerate_25_percent_7ec6d66f` | Scale Average Exaggerate 25% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Scale Average Exaggerate 25%.py` | 从均值缩放：Scale Average Exaggerate 25%。按原入口的均值参考缩放动画幅度。；关键帧数值、时间或切线 |
| `scale_from_average.scale_average_exaggerate_50_percent_3b972544` | Scale Average Exaggerate 50% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Scale Average Exaggerate 50%.py` | 从均值缩放：Scale Average Exaggerate 50%。按原入口的均值参考缩放动画幅度。；关键帧数值、时间或切线 |
| `scale_from_average.scale_average_exaggerate_75_percent_58525cf0` | Scale Average Exaggerate 75% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Scale Average Exaggerate 75%.py` | 从均值缩放：Scale Average Exaggerate 75%。按原入口的均值参考缩放动画幅度。；关键帧数值、时间或切线 |
| `scale_from_average.scale_average_exaggerate_90_percent_f74e577e` | Scale Average Exaggerate 90% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Scale Average Exaggerate 90%.py` | 从均值缩放：Scale Average Exaggerate 90%。按原入口的均值参考缩放动画幅度。；关键帧数值、时间或切线 |
| `scale_from_average.scale_average_reduce_10_percent_fd9a6ef0` | Scale Average Reduce 10% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Scale Average Reduce 10%.py` | 从均值缩放：Scale Average Reduce 10%。按原入口的均值参考缩放动画幅度。；关键帧数值、时间或切线 |
| `scale_from_average.scale_average_reduce_100_percent_full_44011429` | Scale Average Reduce 100% (Full) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Scale Average Reduce 100% (Full).py` | 从均值缩放：Scale Average Reduce 100% (Full)。按原入口的均值参考缩放动画幅度。；关键帧数值、时间或切线 |
| `scale_from_average.scale_average_reduce_150_percent_overshoot_2c5e9360` | Scale Average Reduce 150% (Overshoot) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Scale Average Reduce 150% (Overshoot).py` | 从均值缩放：Scale Average Reduce 150% (Overshoot)。按原入口的均值参考缩放动画幅度。；关键帧数值、时间或切线 |
| `scale_from_average.scale_average_reduce_200_percent_extreme_overshoot_cf0861c0` | Scale Average Reduce 200% (Extreme Overshoot) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Scale Average Reduce 200% (Extreme Overshoot).py` | 从均值缩放：Scale Average Reduce 200% (Extreme Overshoot)。按原入口的均值参考缩放动画幅度。；关键帧数值、时间或切线 |
| `scale_from_average.scale_average_reduce_25_percent_4cc068f6` | Scale Average Reduce 25% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Scale Average Reduce 25%.py` | 从均值缩放：Scale Average Reduce 25%。按原入口的均值参考缩放动画幅度。；关键帧数值、时间或切线 |
| `scale_from_average.scale_average_reduce_50_percent_9dd64da6` | Scale Average Reduce 50% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Scale Average Reduce 50%.py` | 从均值缩放：Scale Average Reduce 50%。按原入口的均值参考缩放动画幅度。；关键帧数值、时间或切线 |
| `scale_from_average.scale_average_reduce_75_percent_fdbc1501` | Scale Average Reduce 75% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Scale Average Reduce 75%.py` | 从均值缩放：Scale Average Reduce 75%。按原入口的均值参考缩放动画幅度。；关键帧数值、时间或切线 |
| `scale_from_average.scale_average_reduce_90_percent_3cbca30f` | Scale Average Reduce 90% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Scale Average Reduce 90%.py` | 从均值缩放：Scale Average Reduce 90%。按原入口的均值参考缩放动画幅度。；关键帧数值、时间或切线 |

## 调用

```python
tool.run(dry_run=True, action="invoke", operation_id='scale_from_average.scale_average_exaggerate_10_percent_dc1907ed')
# 阅读预检结果后再执行：
# tool.run(action="invoke", operation_id='scale_from_average.scale_average_exaggerate_10_percent_dc1907ed')
```

所有入口的函数签名、顶层固定调用值及原索引别名见候选 `operations.json`；这些是静态证据，不表示运行兼容。
