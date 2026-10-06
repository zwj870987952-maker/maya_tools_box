# 推拉幅度（Push and Pull）

增强或收缩动画相对差值。

- 状态：prepared_unverified，等待人工 Maya 直验。
- 输入：当前 Maya 选择、通道/Graph Editor 关键帧及时间区间；固定预设由下列脚本定义。
- 输出：候选 API 返回分派状态与操作后选择，不声称原算法已成功。
- 撤销：场景操作进入 Undo Chunk；外部文件、UI、插件、偏好不由 Maya Undo 撤回。

| operation ID | 原名称 | 执行源文件（相对 Animo_v10.6.0） | 具体用途/影响 |
| --- | --- | --- | --- |
| `push_and_pull.pull_10_percent_3bb24d26` | Pull 10% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Pull 10%.py` | 推拉幅度：Pull 10%。增强或收缩动画相对差值。；关键帧数值、时间或切线 |
| `push_and_pull.pull_100_percent_full_577b2424` | Pull 100% (Full) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Pull 100% (Full).py` | 推拉幅度：Pull 100% (Full)。增强或收缩动画相对差值。；关键帧数值、时间或切线 |
| `push_and_pull.pull_150_percent_overshoot_56462dbc` | Pull 150% (Overshoot) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Pull 150% (Overshoot).py` | 推拉幅度：Pull 150% (Overshoot)。增强或收缩动画相对差值。；关键帧数值、时间或切线 |
| `push_and_pull.pull_200_percent_extreme_overshoot_1c026d25` | Pull 200% (Extreme Overshoot) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Pull 200% (Extreme Overshoot).py` | 推拉幅度：Pull 200% (Extreme Overshoot)。增强或收缩动画相对差值。；关键帧数值、时间或切线 |
| `push_and_pull.pull_25_percent_7ead8326` | Pull 25% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Pull 25%.py` | 推拉幅度：Pull 25%。增强或收缩动画相对差值。；关键帧数值、时间或切线 |
| `push_and_pull.pull_50_percent_5c709c9e` | Pull 50% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Pull 50%.py` | 推拉幅度：Pull 50%。增强或收缩动画相对差值。；关键帧数值、时间或切线 |
| `push_and_pull.pull_75_percent_67e533ce` | Pull 75% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Pull 75%.py` | 推拉幅度：Pull 75%。增强或收缩动画相对差值。；关键帧数值、时间或切线 |
| `push_and_pull.pull_90_percent_14a55392` | Pull 90% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Pull 90%.py` | 推拉幅度：Pull 90%。增强或收缩动画相对差值。；关键帧数值、时间或切线 |
| `push_and_pull.push_10_percent_d50ca36f` | Push 10% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Push 10%.py` | 推拉幅度：Push 10%。增强或收缩动画相对差值。；关键帧数值、时间或切线 |
| `push_and_pull.push_100_percent_full_11d4b3e2` | Push 100% (Full) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Push 100% (Full).py` | 推拉幅度：Push 100% (Full)。增强或收缩动画相对差值。；关键帧数值、时间或切线 |
| `push_and_pull.push_150_percent_overshoot_b2f367cd` | Push 150% (Overshoot) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Push 150% (Overshoot).py` | 推拉幅度：Push 150% (Overshoot)。增强或收缩动画相对差值。；关键帧数值、时间或切线 |
| `push_and_pull.push_200_percent_extreme_overshoot_7c369e30` | Push 200% (Extreme Overshoot) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Push 200% (Extreme Overshoot).py` | 推拉幅度：Push 200% (Extreme Overshoot)。增强或收缩动画相对差值。；关键帧数值、时间或切线 |
| `push_and_pull.push_25_percent_c4b793cc` | Push 25% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Push 25%.py` | 推拉幅度：Push 25%。增强或收缩动画相对差值。；关键帧数值、时间或切线 |
| `push_and_pull.push_50_percent_b90f64c5` | Push 50% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Push 50%.py` | 推拉幅度：Push 50%。增强或收缩动画相对差值。；关键帧数值、时间或切线 |
| `push_and_pull.push_75_percent_29e980e1` | Push 75% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Push 75%.py` | 推拉幅度：Push 75%。增强或收缩动画相对差值。；关键帧数值、时间或切线 |
| `push_and_pull.push_90_percent_515575bf` | Push 90% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Push 90%.py` | 推拉幅度：Push 90%。增强或收缩动画相对差值。；关键帧数值、时间或切线 |

## 调用

```python
tool.run(dry_run=True, action="invoke", operation_id='push_and_pull.pull_10_percent_3bb24d26')
# 阅读预检结果后再执行：
# tool.run(action="invoke", operation_id='push_and_pull.pull_10_percent_3bb24d26')
```

所有入口的函数签名、顶层固定调用值及原索引别名见候选 `operations.json`；这些是静态证据，不表示运行兼容。
