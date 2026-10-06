# 围绕左侧缩放（Scale Left）

围绕左侧参考值调整动画幅度。

- 状态：prepared_unverified，等待人工 Maya 直验。
- 输入：当前 Maya 选择、通道/Graph Editor 关键帧及时间区间；固定预设由下列脚本定义。
- 输出：候选 API 返回分派状态与操作后选择，不声称原算法已成功。
- 撤销：场景操作进入 Undo Chunk；外部文件、UI、插件、偏好不由 Maya Undo 撤回。

| operation ID | 原名称 | 执行源文件（相对 Animo_v10.6.0） | 具体用途/影响 |
| --- | --- | --- | --- |
| `scale_left.scale_left_exaggerate_10_percent_5fe3bf68` | Scale Left Exaggerate 10% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Scale Left Exaggerate 10%.py` | 围绕左侧缩放：Scale Left Exaggerate 10%。围绕左侧参考值调整动画幅度。；关键帧数值、时间或切线 |
| `scale_left.scale_left_exaggerate_100_percent_full_d505f00e` | Scale Left Exaggerate 100% (Full) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Scale Left Exaggerate 100% (Full).py` | 围绕左侧缩放：Scale Left Exaggerate 100% (Full)。围绕左侧参考值调整动画幅度。；关键帧数值、时间或切线 |
| `scale_left.scale_left_exaggerate_150_percent_overshoot_a92b5fed` | Scale Left Exaggerate 150% (Overshoot) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Scale Left Exaggerate 150% (Overshoot).py` | 围绕左侧缩放：Scale Left Exaggerate 150% (Overshoot)。围绕左侧参考值调整动画幅度。；关键帧数值、时间或切线 |
| `scale_left.scale_left_exaggerate_200_percent_extreme_overshoot_6a06e7b6` | Scale Left Exaggerate 200% (Extreme Overshoot) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Scale Left Exaggerate 200% (Extreme Overshoot).py` | 围绕左侧缩放：Scale Left Exaggerate 200% (Extreme Overshoot)。围绕左侧参考值调整动画幅度。；关键帧数值、时间或切线 |
| `scale_left.scale_left_exaggerate_25_percent_dcbe2c77` | Scale Left Exaggerate 25% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Scale Left Exaggerate 25%.py` | 围绕左侧缩放：Scale Left Exaggerate 25%。围绕左侧参考值调整动画幅度。；关键帧数值、时间或切线 |
| `scale_left.scale_left_exaggerate_50_percent_6f8e5e27` | Scale Left Exaggerate 50% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Scale Left Exaggerate 50%.py` | 围绕左侧缩放：Scale Left Exaggerate 50%。围绕左侧参考值调整动画幅度。；关键帧数值、时间或切线 |
| `scale_left.scale_left_exaggerate_75_percent_dbc0b3cb` | Scale Left Exaggerate 75% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Scale Left Exaggerate 75%.py` | 围绕左侧缩放：Scale Left Exaggerate 75%。围绕左侧参考值调整动画幅度。；关键帧数值、时间或切线 |
| `scale_left.scale_left_exaggerate_90_percent_6a6bd8fa` | Scale Left Exaggerate 90% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Scale Left Exaggerate 90%.py` | 围绕左侧缩放：Scale Left Exaggerate 90%。围绕左侧参考值调整动画幅度。；关键帧数值、时间或切线 |
| `scale_left.scale_left_reduce_10_percent_f48252f2` | Scale Left Reduce 10% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Scale Left Reduce 10%.py` | 围绕左侧缩放：Scale Left Reduce 10%。围绕左侧参考值调整动画幅度。；关键帧数值、时间或切线 |
| `scale_left.scale_left_reduce_100_percent_full_d5b8f4b2` | Scale Left Reduce 100% (Full) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Scale Left Reduce 100% (Full).py` | 围绕左侧缩放：Scale Left Reduce 100% (Full)。围绕左侧参考值调整动画幅度。；关键帧数值、时间或切线 |
| `scale_left.scale_left_reduce_150_percent_overshoot_5b9c231f` | Scale Left Reduce 150% (Overshoot) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Scale Left Reduce 150% (Overshoot).py` | 围绕左侧缩放：Scale Left Reduce 150% (Overshoot)。围绕左侧参考值调整动画幅度。；关键帧数值、时间或切线 |
| `scale_left.scale_left_reduce_200_percent_extreme_overshoot_812882ff` | Scale Left Reduce 200% (Extreme Overshoot) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Scale Left Reduce 200% (Extreme Overshoot).py` | 围绕左侧缩放：Scale Left Reduce 200% (Extreme Overshoot)。围绕左侧参考值调整动画幅度。；关键帧数值、时间或切线 |
| `scale_left.scale_left_reduce_25_percent_e177b856` | Scale Left Reduce 25% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Scale Left Reduce 25%.py` | 围绕左侧缩放：Scale Left Reduce 25%。围绕左侧参考值调整动画幅度。；关键帧数值、时间或切线 |
| `scale_left.scale_left_reduce_50_percent_326e1e38` | Scale Left Reduce 50% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Scale Left Reduce 50%.py` | 围绕左侧缩放：Scale Left Reduce 50%。围绕左侧参考值调整动画幅度。；关键帧数值、时间或切线 |
| `scale_left.scale_left_reduce_75_percent_10931c50` | Scale Left Reduce 75% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Scale Left Reduce 75%.py` | 围绕左侧缩放：Scale Left Reduce 75%。围绕左侧参考值调整动画幅度。；关键帧数值、时间或切线 |
| `scale_left.scale_left_reduce_90_percent_f4182bf2` | Scale Left Reduce 90% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Scale Left Reduce 90%.py` | 围绕左侧缩放：Scale Left Reduce 90%。围绕左侧参考值调整动画幅度。；关键帧数值、时间或切线 |

## 调用

```python
tool.run(dry_run=True, action="invoke", operation_id='scale_left.scale_left_exaggerate_10_percent_5fe3bf68')
# 阅读预检结果后再执行：
# tool.run(action="invoke", operation_id='scale_left.scale_left_exaggerate_10_percent_5fe3bf68')
```

所有入口的函数签名、顶层固定调用值及原索引别名见候选 `operations.json`；这些是静态证据，不表示运行兼容。
