# 混合至镜像（Blend to Mirror）

按镜像配对结果混合姿态或动画。

- 状态：prepared_unverified，等待人工 Maya 直验。
- 输入：当前 Maya 选择、通道/Graph Editor 关键帧及时间区间；固定预设由下列脚本定义。
- 输出：候选 API 返回分派状态与操作后选择，不声称原算法已成功。
- 撤销：场景操作进入 Undo Chunk；外部文件、UI、插件、偏好不由 Maya Undo 撤回。

| operation ID | 原名称 | 执行源文件（相对 Animo_v10.6.0） | 具体用途/影响 |
| --- | --- | --- | --- |
| `blend_to_mirror.diverge_10_percent_ce890b94` | Diverge 10% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Diverge 10%.py` | 混合至镜像：Diverge 10%。按镜像配对结果混合姿态或动画。；关键帧数值、时间或切线 |
| `blend_to_mirror.diverge_100_percent_full_95061fe4` | Diverge 100% (Full) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Diverge 100% (Full).py` | 混合至镜像：Diverge 100% (Full)。按镜像配对结果混合姿态或动画。；关键帧数值、时间或切线 |
| `blend_to_mirror.diverge_25_percent_659a6e66` | Diverge 25% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Diverge 25%.py` | 混合至镜像：Diverge 25%。按镜像配对结果混合姿态或动画。；关键帧数值、时间或切线 |
| `blend_to_mirror.diverge_50_percent_1c37af89` | Diverge 50% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Diverge 50%.py` | 混合至镜像：Diverge 50%。按镜像配对结果混合姿态或动画。；关键帧数值、时间或切线 |
| `blend_to_mirror.diverge_75_percent_0964ac9b` | Diverge 75% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Diverge 75%.py` | 混合至镜像：Diverge 75%。按镜像配对结果混合姿态或动画。；关键帧数值、时间或切线 |
| `blend_to_mirror.diverge_90_percent_a2b17357` | Diverge 90% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Diverge 90%.py` | 混合至镜像：Diverge 90%。按镜像配对结果混合姿态或动画。；关键帧数值、时间或切线 |
| `blend_to_mirror.mirror_10_percent_a6783c24` | Mirror 10% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Mirror 10%.py` | 混合至镜像：Mirror 10%。按镜像配对结果混合姿态或动画。；关键帧数值、时间或切线 |
| `blend_to_mirror.mirror_100_percent_full_22d554f3` | Mirror 100% (Full) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Mirror 100% (Full).py` | 混合至镜像：Mirror 100% (Full)。按镜像配对结果混合姿态或动画。；关键帧数值、时间或切线 |
| `blend_to_mirror.mirror_25_percent_29dfd212` | Mirror 25% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Mirror 25%.py` | 混合至镜像：Mirror 25%。按镜像配对结果混合姿态或动画。；关键帧数值、时间或切线 |
| `blend_to_mirror.mirror_50_percent_7183d7ff` | Mirror 50% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Mirror 50%.py` | 混合至镜像：Mirror 50%。按镜像配对结果混合姿态或动画。；关键帧数值、时间或切线 |
| `blend_to_mirror.mirror_75_percent_f8123aaf` | Mirror 75% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Mirror 75%.py` | 混合至镜像：Mirror 75%。按镜像配对结果混合姿态或动画。；关键帧数值、时间或切线 |
| `blend_to_mirror.mirror_90_percent_710c26c3` | Mirror 90% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Mirror 90%.py` | 混合至镜像：Mirror 90%。按镜像配对结果混合姿态或动画。；关键帧数值、时间或切线 |

## 调用

```python
tool.run(dry_run=True, action="invoke", operation_id='blend_to_mirror.diverge_10_percent_ce890b94')
# 阅读预检结果后再执行：
# tool.run(action="invoke", operation_id='blend_to_mirror.diverge_10_percent_ce890b94')
```

所有入口的函数签名、顶层固定调用值及原索引别名见候选 `operations.json`；这些是静态证据，不表示运行兼容。
