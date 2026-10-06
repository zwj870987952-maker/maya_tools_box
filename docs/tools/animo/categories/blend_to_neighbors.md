# 混合至邻帧（Blend to Neighbors）

将所选数值向相邻关键帧混合。

- 状态：prepared_unverified，等待人工 Maya 直验。
- 输入：当前 Maya 选择、通道/Graph Editor 关键帧及时间区间；固定预设由下列脚本定义。
- 输出：候选 API 返回分派状态与操作后选择，不声称原算法已成功。
- 撤销：场景操作进入 Undo Chunk；外部文件、UI、插件、偏好不由 Maya Undo 撤回。

| operation ID | 原名称 | 执行源文件（相对 Animo_v10.6.0） | 具体用途/影响 |
| --- | --- | --- | --- |
| `blend_to_neighbors.blend_to_neighbors_plus_10_percent_c1bc1af8` | Blend to Neighbors +10% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Blend to Neighbors +10%.py` | 混合至邻帧：Blend to Neighbors +10%。将所选数值向相邻关键帧混合。；关键帧数值、时间或切线 |
| `blend_to_neighbors.blend_to_neighbors_plus_100_percent_full_ba8b1851` | Blend to Neighbors +100% (Full) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Blend to Neighbors +100% (Full).py` | 混合至邻帧：Blend to Neighbors +100% (Full)。将所选数值向相邻关键帧混合。；关键帧数值、时间或切线 |
| `blend_to_neighbors.blend_to_neighbors_plus_150_percent_overshoot_79a6ab5e` | Blend to Neighbors +150% (Overshoot) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Blend to Neighbors +150% (Overshoot).py` | 混合至邻帧：Blend to Neighbors +150% (Overshoot)。将所选数值向相邻关键帧混合。；关键帧数值、时间或切线 |
| `blend_to_neighbors.blend_to_neighbors_plus_200_percent_extreme_overshoot_6387aca8` | Blend to Neighbors +200% (Extreme Overshoot) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Blend to Neighbors +200% (Extreme Overshoot).py` | 混合至邻帧：Blend to Neighbors +200% (Extreme Overshoot)。将所选数值向相邻关键帧混合。；关键帧数值、时间或切线 |
| `blend_to_neighbors.blend_to_neighbors_plus_25_percent_11b4eb5a` | Blend to Neighbors +25% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Blend to Neighbors +25%.py` | 混合至邻帧：Blend to Neighbors +25%。将所选数值向相邻关键帧混合。；关键帧数值、时间或切线 |
| `blend_to_neighbors.blend_to_neighbors_plus_50_percent_5e3ea4f2` | Blend to Neighbors +50% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Blend to Neighbors +50%.py` | 混合至邻帧：Blend to Neighbors +50%。将所选数值向相邻关键帧混合。；关键帧数值、时间或切线 |
| `blend_to_neighbors.blend_to_neighbors_plus_75_percent_76e62391` | Blend to Neighbors +75% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Blend to Neighbors +75%.py` | 混合至邻帧：Blend to Neighbors +75%。将所选数值向相邻关键帧混合。；关键帧数值、时间或切线 |
| `blend_to_neighbors.blend_to_neighbors_plus_90_percent_82c42af7` | Blend to Neighbors +90% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Blend to Neighbors +90%.py` | 混合至邻帧：Blend to Neighbors +90%。将所选数值向相邻关键帧混合。；关键帧数值、时间或切线 |
| `blend_to_neighbors.blend_to_neighbors_minus_10_percent_f580a898` | Blend to Neighbors -10% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Blend to Neighbors -10%.py` | 混合至邻帧：Blend to Neighbors -10%。将所选数值向相邻关键帧混合。；关键帧数值、时间或切线 |
| `blend_to_neighbors.blend_to_neighbors_minus_100_percent_full_feb7e380` | Blend to Neighbors -100% (Full) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Blend to Neighbors -100% (Full).py` | 混合至邻帧：Blend to Neighbors -100% (Full)。将所选数值向相邻关键帧混合。；关键帧数值、时间或切线 |
| `blend_to_neighbors.blend_to_neighbors_minus_150_percent_overshoot_e0c1e41e` | Blend to Neighbors -150% (Overshoot) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Blend to Neighbors -150% (Overshoot).py` | 混合至邻帧：Blend to Neighbors -150% (Overshoot)。将所选数值向相邻关键帧混合。；关键帧数值、时间或切线 |
| `blend_to_neighbors.blend_to_neighbors_minus_200_percent_extreme_overshoot_f07102ba` | Blend to Neighbors -200% (Extreme Overshoot) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Blend to Neighbors -200% (Extreme Overshoot).py` | 混合至邻帧：Blend to Neighbors -200% (Extreme Overshoot)。将所选数值向相邻关键帧混合。；关键帧数值、时间或切线 |
| `blend_to_neighbors.blend_to_neighbors_minus_25_percent_12029ab9` | Blend to Neighbors -25% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Blend to Neighbors -25%.py` | 混合至邻帧：Blend to Neighbors -25%。将所选数值向相邻关键帧混合。；关键帧数值、时间或切线 |
| `blend_to_neighbors.blend_to_neighbors_minus_50_percent_87206da2` | Blend to Neighbors -50% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Blend to Neighbors -50%.py` | 混合至邻帧：Blend to Neighbors -50%。将所选数值向相邻关键帧混合。；关键帧数值、时间或切线 |
| `blend_to_neighbors.blend_to_neighbors_minus_75_percent_fa3699cf` | Blend to Neighbors -75% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Blend to Neighbors -75%.py` | 混合至邻帧：Blend to Neighbors -75%。将所选数值向相邻关键帧混合。；关键帧数值、时间或切线 |
| `blend_to_neighbors.blend_to_neighbors_minus_90_percent_fbb5e45b` | Blend to Neighbors -90% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Blend to Neighbors -90%.py` | 混合至邻帧：Blend to Neighbors -90%。将所选数值向相邻关键帧混合。；关键帧数值、时间或切线 |

## 调用

```python
tool.run(dry_run=True, action="invoke", operation_id='blend_to_neighbors.blend_to_neighbors_plus_10_percent_c1bc1af8')
# 阅读预检结果后再执行：
# tool.run(action="invoke", operation_id='blend_to_neighbors.blend_to_neighbors_plus_10_percent_c1bc1af8')
```

所有入口的函数签名、顶层固定调用值及原索引别名见候选 `operations.json`；这些是静态证据，不表示运行兼容。
