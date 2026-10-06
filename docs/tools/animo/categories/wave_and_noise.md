# 波形与噪声（Wave and Noise）

按预设强度向动画加入波形或噪声变化。

- 状态：prepared_unverified，等待人工 Maya 直验。
- 输入：当前 Maya 选择、通道/Graph Editor 关键帧及时间区间；固定预设由下列脚本定义。
- 输出：候选 API 返回分派状态与操作后选择，不声称原算法已成功。
- 撤销：场景操作进入 Undo Chunk；外部文件、UI、插件、偏好不由 Maya Undo 撤回。

| operation ID | 原名称 | 执行源文件（相对 Animo_v10.6.0） | 具体用途/影响 |
| --- | --- | --- | --- |
| `wave_and_noise.noise_10_percent_4f62436e` | Noise 10% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Noise 10%.py` | 波形与噪声：Noise 10%。按预设强度向动画加入波形或噪声变化。；关键帧数值、时间或切线 |
| `wave_and_noise.noise_100_percent_full_95682e4e` | Noise 100% (Full) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Noise 100% (Full).py` | 波形与噪声：Noise 100% (Full)。按预设强度向动画加入波形或噪声变化。；关键帧数值、时间或切线 |
| `wave_and_noise.noise_150_percent_overshoot_fed4e2c1` | Noise 150% (Overshoot) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Noise 150% (Overshoot).py` | 波形与噪声：Noise 150% (Overshoot)。按预设强度向动画加入波形或噪声变化。；关键帧数值、时间或切线 |
| `wave_and_noise.noise_200_percent_extreme_overshoot_e66cca0c` | Noise 200% (Extreme Overshoot) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Noise 200% (Extreme Overshoot).py` | 波形与噪声：Noise 200% (Extreme Overshoot)。按预设强度向动画加入波形或噪声变化。；关键帧数值、时间或切线 |
| `wave_and_noise.noise_25_percent_17978fa8` | Noise 25% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Noise 25%.py` | 波形与噪声：Noise 25%。按预设强度向动画加入波形或噪声变化。；关键帧数值、时间或切线 |
| `wave_and_noise.noise_50_percent_b45c9e33` | Noise 50% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Noise 50%.py` | 波形与噪声：Noise 50%。按预设强度向动画加入波形或噪声变化。；关键帧数值、时间或切线 |
| `wave_and_noise.noise_75_percent_ad71b274` | Noise 75% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Noise 75%.py` | 波形与噪声：Noise 75%。按预设强度向动画加入波形或噪声变化。；关键帧数值、时间或切线 |
| `wave_and_noise.noise_90_percent_14377f4d` | Noise 90% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Noise 90%.py` | 波形与噪声：Noise 90%。按预设强度向动画加入波形或噪声变化。；关键帧数值、时间或切线 |
| `wave_and_noise.wave_10_percent_45700f1e` | Wave 10% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Wave 10%.py` | 波形与噪声：Wave 10%。按预设强度向动画加入波形或噪声变化。；关键帧数值、时间或切线 |
| `wave_and_noise.wave_100_percent_full_29eead25` | Wave 100% (Full) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Wave 100% (Full).py` | 波形与噪声：Wave 100% (Full)。按预设强度向动画加入波形或噪声变化。；关键帧数值、时间或切线 |
| `wave_and_noise.wave_150_percent_overshoot_6dfc0617` | Wave 150% (Overshoot) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Wave 150% (Overshoot).py` | 波形与噪声：Wave 150% (Overshoot)。按预设强度向动画加入波形或噪声变化。；关键帧数值、时间或切线 |
| `wave_and_noise.wave_200_percent_extreme_overshoot_ffd2278d` | Wave 200% (Extreme Overshoot) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Wave 200% (Extreme Overshoot).py` | 波形与噪声：Wave 200% (Extreme Overshoot)。按预设强度向动画加入波形或噪声变化。；关键帧数值、时间或切线 |
| `wave_and_noise.wave_25_percent_9d7522a3` | Wave 25% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Wave 25%.py` | 波形与噪声：Wave 25%。按预设强度向动画加入波形或噪声变化。；关键帧数值、时间或切线 |
| `wave_and_noise.wave_50_percent_103d3a57` | Wave 50% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Wave 50%.py` | 波形与噪声：Wave 50%。按预设强度向动画加入波形或噪声变化。；关键帧数值、时间或切线 |
| `wave_and_noise.wave_75_percent_95b2be96` | Wave 75% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Wave 75%.py` | 波形与噪声：Wave 75%。按预设强度向动画加入波形或噪声变化。；关键帧数值、时间或切线 |
| `wave_and_noise.wave_90_percent_ccd6585a` | Wave 90% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Wave 90%.py` | 波形与噪声：Wave 90%。按预设强度向动画加入波形或噪声变化。；关键帧数值、时间或切线 |

## 调用

```python
tool.run(dry_run=True, action="invoke", operation_id='wave_and_noise.noise_10_percent_4f62436e')
# 阅读预检结果后再执行：
# tool.run(action="invoke", operation_id='wave_and_noise.noise_10_percent_4f62436e')
```

所有入口的函数签名、顶层固定调用值及原索引别名见候选 `operations.json`；这些是静态证据，不表示运行兼容。
