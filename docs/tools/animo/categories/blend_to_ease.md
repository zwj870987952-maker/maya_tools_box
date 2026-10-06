# 混合至缓动（Blend to Ease）

向缓动曲线形态混合动画。

- 状态：prepared_unverified，等待人工 Maya 直验。
- 输入：当前 Maya 选择、通道/Graph Editor 关键帧及时间区间；固定预设由下列脚本定义。
- 输出：候选 API 返回分派状态与操作后选择，不声称原算法已成功。
- 撤销：场景操作进入 Undo Chunk；外部文件、UI、插件、偏好不由 Maya Undo 撤回。

| operation ID | 原名称 | 执行源文件（相对 Animo_v10.6.0） | 具体用途/影响 |
| --- | --- | --- | --- |
| `blend_to_ease.blend_to_ease_in_10_percent_8d63b12a` | Blend to Ease In 10% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Blend to Ease In 10%.py` | 混合至缓动：Blend to Ease In 10%。向缓动曲线形态混合动画。；关键帧数值、时间或切线 |
| `blend_to_ease.blend_to_ease_in_100_percent_full_f3542376` | Blend to Ease In 100% (Full) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Blend to Ease In 100% (Full).py` | 混合至缓动：Blend to Ease In 100% (Full)。向缓动曲线形态混合动画。；关键帧数值、时间或切线 |
| `blend_to_ease.blend_to_ease_in_25_percent_7b092294` | Blend to Ease In 25% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Blend to Ease In 25%.py` | 混合至缓动：Blend to Ease In 25%。向缓动曲线形态混合动画。；关键帧数值、时间或切线 |
| `blend_to_ease.blend_to_ease_in_50_percent_a0dfd02d` | Blend to Ease In 50% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Blend to Ease In 50%.py` | 混合至缓动：Blend to Ease In 50%。向缓动曲线形态混合动画。；关键帧数值、时间或切线 |
| `blend_to_ease.blend_to_ease_in_75_percent_173310db` | Blend to Ease In 75% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Blend to Ease In 75%.py` | 混合至缓动：Blend to Ease In 75%。向缓动曲线形态混合动画。；关键帧数值、时间或切线 |
| `blend_to_ease.blend_to_ease_in_90_percent_d961e88e` | Blend to Ease In 90% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Blend to Ease In 90%.py` | 混合至缓动：Blend to Ease In 90%。向缓动曲线形态混合动画。；关键帧数值、时间或切线 |
| `blend_to_ease.blend_to_ease_out_10_percent_13373581` | Blend to Ease Out 10% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Blend to Ease Out 10%.py` | 混合至缓动：Blend to Ease Out 10%。向缓动曲线形态混合动画。；关键帧数值、时间或切线 |
| `blend_to_ease.blend_to_ease_out_100_percent_full_7fb6b77b` | Blend to Ease Out 100% (Full) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Blend to Ease Out 100% (Full).py` | 混合至缓动：Blend to Ease Out 100% (Full)。向缓动曲线形态混合动画。；关键帧数值、时间或切线 |
| `blend_to_ease.blend_to_ease_out_25_percent_798f6ca9` | Blend to Ease Out 25% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Blend to Ease Out 25%.py` | 混合至缓动：Blend to Ease Out 25%。向缓动曲线形态混合动画。；关键帧数值、时间或切线 |
| `blend_to_ease.blend_to_ease_out_50_percent_a7c490fd` | Blend to Ease Out 50% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Blend to Ease Out 50%.py` | 混合至缓动：Blend to Ease Out 50%。向缓动曲线形态混合动画。；关键帧数值、时间或切线 |
| `blend_to_ease.blend_to_ease_out_75_percent_35ac32c3` | Blend to Ease Out 75% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Blend to Ease Out 75%.py` | 混合至缓动：Blend to Ease Out 75%。向缓动曲线形态混合动画。；关键帧数值、时间或切线 |
| `blend_to_ease.blend_to_ease_out_90_percent_59be67d6` | Blend to Ease Out 90% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Blend to Ease Out 90%.py` | 混合至缓动：Blend to Ease Out 90%。向缓动曲线形态混合动画。；关键帧数值、时间或切线 |

## 调用

```python
tool.run(dry_run=True, action="invoke", operation_id='blend_to_ease.blend_to_ease_in_10_percent_8d63b12a')
# 阅读预检结果后再执行：
# tool.run(action="invoke", operation_id='blend_to_ease.blend_to_ease_in_10_percent_8d63b12a')
```

所有入口的函数签名、顶层固定调用值及原索引别名见候选 `operations.json`；这些是静态证据，不表示运行兼容。
