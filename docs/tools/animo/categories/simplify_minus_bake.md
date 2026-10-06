# 简化与烘焙（Simplify - Bake）

减少关键帧或补充采样关键帧。

- 状态：prepared_unverified，等待人工 Maya 直验。
- 输入：当前 Maya 选择、通道/Graph Editor 关键帧及时间区间；固定预设由下列脚本定义。
- 输出：候选 API 返回分派状态与操作后选择，不声称原算法已成功。
- 撤销：场景操作进入 Undo Chunk；外部文件、UI、插件、偏好不由 Maya Undo 撤回。

| operation ID | 原名称 | 执行源文件（相对 Animo_v10.6.0） | 具体用途/影响 |
| --- | --- | --- | --- |
| `simplify_minus_bake.bake_10_percent_688963fc` | Bake 10% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Bake 10%.py` | 简化与烘焙：Bake 10%。减少关键帧或补充采样关键帧。；关键帧数值、时间或切线 |
| `simplify_minus_bake.bake_100_percent_full_fc4b3e3f` | Bake 100% (Full) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Bake 100% (Full).py` | 简化与烘焙：Bake 100% (Full)。减少关键帧或补充采样关键帧。；关键帧数值、时间或切线 |
| `simplify_minus_bake.bake_25_percent_86841fe7` | Bake 25% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Bake 25%.py` | 简化与烘焙：Bake 25%。减少关键帧或补充采样关键帧。；关键帧数值、时间或切线 |
| `simplify_minus_bake.bake_50_percent_4ae7dd45` | Bake 50% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Bake 50%.py` | 简化与烘焙：Bake 50%。减少关键帧或补充采样关键帧。；关键帧数值、时间或切线 |
| `simplify_minus_bake.bake_75_percent_98d4e2ed` | Bake 75% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Bake 75%.py` | 简化与烘焙：Bake 75%。减少关键帧或补充采样关键帧。；关键帧数值、时间或切线 |
| `simplify_minus_bake.bake_90_percent_7597768c` | Bake 90% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Bake 90%.py` | 简化与烘焙：Bake 90%。减少关键帧或补充采样关键帧。；关键帧数值、时间或切线 |
| `simplify_minus_bake.simplify_10_percent_620992d7` | Simplify 10% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Simplify 10%.py` | 简化与烘焙：Simplify 10%。减少关键帧或补充采样关键帧。；关键帧数值、时间或切线 |
| `simplify_minus_bake.simplify_100_percent_full_f95595c6` | Simplify 100% (Full) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Simplify 100% (Full).py` | 简化与烘焙：Simplify 100% (Full)。减少关键帧或补充采样关键帧。；关键帧数值、时间或切线 |
| `simplify_minus_bake.simplify_25_percent_b470f6eb` | Simplify 25% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Simplify 25%.py` | 简化与烘焙：Simplify 25%。减少关键帧或补充采样关键帧。；关键帧数值、时间或切线 |
| `simplify_minus_bake.simplify_50_percent_e919f2a0` | Simplify 50% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Simplify 50%.py` | 简化与烘焙：Simplify 50%。减少关键帧或补充采样关键帧。；关键帧数值、时间或切线 |
| `simplify_minus_bake.simplify_75_percent_9c616110` | Simplify 75% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Simplify 75%.py` | 简化与烘焙：Simplify 75%。减少关键帧或补充采样关键帧。；关键帧数值、时间或切线 |
| `simplify_minus_bake.simplify_90_percent_418d7986` | Simplify 90% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Simplify 90%.py` | 简化与烘焙：Simplify 90%。减少关键帧或补充采样关键帧。；关键帧数值、时间或切线 |

## 调用

```python
tool.run(dry_run=True, action="invoke", operation_id='simplify_minus_bake.bake_10_percent_688963fc')
# 阅读预检结果后再执行：
# tool.run(action="invoke", operation_id='simplify_minus_bake.bake_10_percent_688963fc')
```

所有入口的函数签名、顶层固定调用值及原索引别名见候选 `operations.json`；这些是静态证据，不表示运行兼容。
