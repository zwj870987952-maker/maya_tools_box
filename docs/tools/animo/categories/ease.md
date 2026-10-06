# 缓入缓出（Ease）

改变关键帧数值分布的缓动形态。

- 状态：prepared_unverified，等待人工 Maya 直验。
- 输入：当前 Maya 选择、通道/Graph Editor 关键帧及时间区间；固定预设由下列脚本定义。
- 输出：候选 API 返回分派状态与操作后选择，不声称原算法已成功。
- 撤销：场景操作进入 Undo Chunk；外部文件、UI、插件、偏好不由 Maya Undo 撤回。

| operation ID | 原名称 | 执行源文件（相对 Animo_v10.6.0） | 具体用途/影响 |
| --- | --- | --- | --- |
| `ease.ease_plus_10_percent_2e92ea41` | Ease +10% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Ease +10%.py` | 缓入缓出：Ease +10%。改变关键帧数值分布的缓动形态。；关键帧数值、时间或切线 |
| `ease.ease_plus_100_percent_full_bb7fbdc5` | Ease +100% (Full) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Ease +100% (Full).py` | 缓入缓出：Ease +100% (Full)。改变关键帧数值分布的缓动形态。；关键帧数值、时间或切线 |
| `ease.ease_plus_150_percent_overshoot_6369eb2d` | Ease +150% (Overshoot) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Ease +150% (Overshoot).py` | 缓入缓出：Ease +150% (Overshoot)。改变关键帧数值分布的缓动形态。；关键帧数值、时间或切线 |
| `ease.ease_plus_200_percent_extreme_overshoot_d488215e` | Ease +200% (Extreme Overshoot) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Ease +200% (Extreme Overshoot).py` | 缓入缓出：Ease +200% (Extreme Overshoot)。改变关键帧数值分布的缓动形态。；关键帧数值、时间或切线 |
| `ease.ease_plus_25_percent_af7798d5` | Ease +25% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Ease +25%.py` | 缓入缓出：Ease +25%。改变关键帧数值分布的缓动形态。；关键帧数值、时间或切线 |
| `ease.ease_plus_50_percent_2f29fe30` | Ease +50% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Ease +50%.py` | 缓入缓出：Ease +50%。改变关键帧数值分布的缓动形态。；关键帧数值、时间或切线 |
| `ease.ease_plus_75_percent_bdcae100` | Ease +75% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Ease +75%.py` | 缓入缓出：Ease +75%。改变关键帧数值分布的缓动形态。；关键帧数值、时间或切线 |
| `ease.ease_plus_90_percent_e2679e29` | Ease +90% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Ease +90%.py` | 缓入缓出：Ease +90%。改变关键帧数值分布的缓动形态。；关键帧数值、时间或切线 |
| `ease.ease_minus_10_percent_4ebc9d58` | Ease -10% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Ease -10%.py` | 缓入缓出：Ease -10%。改变关键帧数值分布的缓动形态。；关键帧数值、时间或切线 |
| `ease.ease_minus_100_percent_full_5dca6be2` | Ease -100% (Full) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Ease -100% (Full).py` | 缓入缓出：Ease -100% (Full)。改变关键帧数值分布的缓动形态。；关键帧数值、时间或切线 |
| `ease.ease_minus_150_percent_overshoot_c00a8498` | Ease -150% (Overshoot) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Ease -150% (Overshoot).py` | 缓入缓出：Ease -150% (Overshoot)。改变关键帧数值分布的缓动形态。；关键帧数值、时间或切线 |
| `ease.ease_minus_200_percent_extreme_overshoot_44082a64` | Ease -200% (Extreme Overshoot) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Ease -200% (Extreme Overshoot).py` | 缓入缓出：Ease -200% (Extreme Overshoot)。改变关键帧数值分布的缓动形态。；关键帧数值、时间或切线 |
| `ease.ease_minus_25_percent_9fd43b6b` | Ease -25% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Ease -25%.py` | 缓入缓出：Ease -25%。改变关键帧数值分布的缓动形态。；关键帧数值、时间或切线 |
| `ease.ease_minus_50_percent_dc8fe31a` | Ease -50% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Ease -50%.py` | 缓入缓出：Ease -50%。改变关键帧数值分布的缓动形态。；关键帧数值、时间或切线 |
| `ease.ease_minus_75_percent_4040a433` | Ease -75% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Ease -75%.py` | 缓入缓出：Ease -75%。改变关键帧数值分布的缓动形态。；关键帧数值、时间或切线 |
| `ease.ease_minus_90_percent_b7a64229` | Ease -90% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Ease -90%.py` | 缓入缓出：Ease -90%。改变关键帧数值分布的缓动形态。；关键帧数值、时间或切线 |

## 调用

```python
tool.run(dry_run=True, action="invoke", operation_id='ease.ease_plus_10_percent_2e92ea41')
# 阅读预检结果后再执行：
# tool.run(action="invoke", operation_id='ease.ease_plus_10_percent_2e92ea41')
```

所有入口的函数签名、顶层固定调用值及原索引别名见候选 `operations.json`；这些是静态证据，不表示运行兼容。
