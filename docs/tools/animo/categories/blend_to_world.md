# 混合至世界空间（Blend to World）

调整世界空间相关动画值。

- 状态：prepared_unverified，等待人工 Maya 直验。
- 输入：当前 Maya 选择、通道/Graph Editor 关键帧及时间区间；固定预设由下列脚本定义。
- 输出：候选 API 返回分派状态与操作后选择，不声称原算法已成功。
- 撤销：场景操作进入 Undo Chunk；外部文件、UI、插件、偏好不由 Maya Undo 撤回。

| operation ID | 原名称 | 执行源文件（相对 Animo_v10.6.0） | 具体用途/影响 |
| --- | --- | --- | --- |
| `blend_to_world.blend_to_world_plus_10_percent_ad765313` | Blend to World +10% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Blend to World +10%.py` | 混合至世界空间：Blend to World +10%。调整世界空间相关动画值。；关键帧数值、时间或切线 |
| `blend_to_world.blend_to_world_plus_100_percent_full_78e1ec1d` | Blend to World +100% (Full) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Blend to World +100% (Full).py` | 混合至世界空间：Blend to World +100% (Full)。调整世界空间相关动画值。；关键帧数值、时间或切线 |
| `blend_to_world.blend_to_world_plus_150_percent_overshoot_145f629c` | Blend to World +150% (Overshoot) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Blend to World +150% (Overshoot).py` | 混合至世界空间：Blend to World +150% (Overshoot)。调整世界空间相关动画值。；关键帧数值、时间或切线 |
| `blend_to_world.blend_to_world_plus_200_percent_extreme_overshoot_365de357` | Blend to World +200% (Extreme Overshoot) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Blend to World +200% (Extreme Overshoot).py` | 混合至世界空间：Blend to World +200% (Extreme Overshoot)。调整世界空间相关动画值。；关键帧数值、时间或切线 |
| `blend_to_world.blend_to_world_plus_25_percent_651fbe4a` | Blend to World +25% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Blend to World +25%.py` | 混合至世界空间：Blend to World +25%。调整世界空间相关动画值。；关键帧数值、时间或切线 |
| `blend_to_world.blend_to_world_plus_50_percent_c706fdef` | Blend to World +50% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Blend to World +50%.py` | 混合至世界空间：Blend to World +50%。调整世界空间相关动画值。；关键帧数值、时间或切线 |
| `blend_to_world.blend_to_world_plus_75_percent_9582daa5` | Blend to World +75% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Blend to World +75%.py` | 混合至世界空间：Blend to World +75%。调整世界空间相关动画值。；关键帧数值、时间或切线 |
| `blend_to_world.blend_to_world_plus_90_percent_92efd7f1` | Blend to World +90% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Blend to World +90%.py` | 混合至世界空间：Blend to World +90%。调整世界空间相关动画值。；关键帧数值、时间或切线 |
| `blend_to_world.blend_to_world_minus_10_percent_cc42a1fa` | Blend to World -10% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Blend to World -10%.py` | 混合至世界空间：Blend to World -10%。调整世界空间相关动画值。；关键帧数值、时间或切线 |
| `blend_to_world.blend_to_world_minus_100_percent_full_f1bc8f94` | Blend to World -100% (Full) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Blend to World -100% (Full).py` | 混合至世界空间：Blend to World -100% (Full)。调整世界空间相关动画值。；关键帧数值、时间或切线 |
| `blend_to_world.blend_to_world_minus_150_percent_overshoot_4d1bc93f` | Blend to World -150% (Overshoot) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Blend to World -150% (Overshoot).py` | 混合至世界空间：Blend to World -150% (Overshoot)。调整世界空间相关动画值。；关键帧数值、时间或切线 |
| `blend_to_world.blend_to_world_minus_200_percent_extreme_overshoot_488f3a10` | Blend to World -200% (Extreme Overshoot) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Blend to World -200% (Extreme Overshoot).py` | 混合至世界空间：Blend to World -200% (Extreme Overshoot)。调整世界空间相关动画值。；关键帧数值、时间或切线 |
| `blend_to_world.blend_to_world_minus_25_percent_e8b4b6fd` | Blend to World -25% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Blend to World -25%.py` | 混合至世界空间：Blend to World -25%。调整世界空间相关动画值。；关键帧数值、时间或切线 |
| `blend_to_world.blend_to_world_minus_50_percent_7125eb72` | Blend to World -50% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Blend to World -50%.py` | 混合至世界空间：Blend to World -50%。调整世界空间相关动画值。；关键帧数值、时间或切线 |
| `blend_to_world.blend_to_world_minus_75_percent_1d18c32a` | Blend to World -75% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Blend to World -75%.py` | 混合至世界空间：Blend to World -75%。调整世界空间相关动画值。；关键帧数值、时间或切线 |
| `blend_to_world.blend_to_world_minus_90_percent_c737385e` | Blend to World -90% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Blend to World -90%.py` | 混合至世界空间：Blend to World -90%。调整世界空间相关动画值。；关键帧数值、时间或切线 |

## 调用

```python
tool.run(dry_run=True, action="invoke", operation_id='blend_to_world.blend_to_world_plus_10_percent_ad765313')
# 阅读预检结果后再执行：
# tool.run(action="invoke", operation_id='blend_to_world.blend_to_world_plus_10_percent_ad765313')
```

所有入口的函数签名、顶层固定调用值及原索引别名见候选 `operations.json`；这些是静态证据，不表示运行兼容。
