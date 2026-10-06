# 从右侧缩放（Scale from Right）

按右侧参考缩放动画幅度。

- 状态：prepared_unverified，等待人工 Maya 直验。
- 输入：当前 Maya 选择、通道/Graph Editor 关键帧及时间区间；固定预设由下列脚本定义。
- 输出：候选 API 返回分派状态与操作后选择，不声称原算法已成功。
- 撤销：场景操作进入 Undo Chunk；外部文件、UI、插件、偏好不由 Maya Undo 撤回。

| operation ID | 原名称 | 执行源文件（相对 Animo_v10.6.0） | 具体用途/影响 |
| --- | --- | --- | --- |
| `scale_from_right.scale_right_exaggerate_10_percent_ecb932f0` | Scale Right Exaggerate 10% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Scale Right Exaggerate 10%.py` | 从右侧缩放：Scale Right Exaggerate 10%。按右侧参考缩放动画幅度。；关键帧数值、时间或切线 |
| `scale_from_right.scale_right_exaggerate_100_percent_full_eec3bf00` | Scale Right Exaggerate 100% (Full) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Scale Right Exaggerate 100% (Full).py` | 从右侧缩放：Scale Right Exaggerate 100% (Full)。按右侧参考缩放动画幅度。；关键帧数值、时间或切线 |
| `scale_from_right.scale_right_exaggerate_150_percent_overshoot_bc2e4203` | Scale Right Exaggerate 150% (Overshoot) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Scale Right Exaggerate 150% (Overshoot).py` | 从右侧缩放：Scale Right Exaggerate 150% (Overshoot)。按右侧参考缩放动画幅度。；关键帧数值、时间或切线 |
| `scale_from_right.scale_right_exaggerate_200_percent_extreme_overshoot_7b36bc2e` | Scale Right Exaggerate 200% (Extreme Overshoot) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Scale Right Exaggerate 200% (Extreme Overshoot).py` | 从右侧缩放：Scale Right Exaggerate 200% (Extreme Overshoot)。按右侧参考缩放动画幅度。；关键帧数值、时间或切线 |
| `scale_from_right.scale_right_exaggerate_25_percent_1b2bc613` | Scale Right Exaggerate 25% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Scale Right Exaggerate 25%.py` | 从右侧缩放：Scale Right Exaggerate 25%。按右侧参考缩放动画幅度。；关键帧数值、时间或切线 |
| `scale_from_right.scale_right_exaggerate_50_percent_6b3a588b` | Scale Right Exaggerate 50% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Scale Right Exaggerate 50%.py` | 从右侧缩放：Scale Right Exaggerate 50%。按右侧参考缩放动画幅度。；关键帧数值、时间或切线 |
| `scale_from_right.scale_right_exaggerate_75_percent_46a3f265` | Scale Right Exaggerate 75% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Scale Right Exaggerate 75%.py` | 从右侧缩放：Scale Right Exaggerate 75%。按右侧参考缩放动画幅度。；关键帧数值、时间或切线 |
| `scale_from_right.scale_right_exaggerate_90_percent_cffcfd03` | Scale Right Exaggerate 90% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Scale Right Exaggerate 90%.py` | 从右侧缩放：Scale Right Exaggerate 90%。按右侧参考缩放动画幅度。；关键帧数值、时间或切线 |
| `scale_from_right.scale_right_reduce_10_percent_2caca212` | Scale Right Reduce 10% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Scale Right Reduce 10%.py` | 从右侧缩放：Scale Right Reduce 10%。按右侧参考缩放动画幅度。；关键帧数值、时间或切线 |
| `scale_from_right.scale_right_reduce_100_percent_full_5e134c39` | Scale Right Reduce 100% (Full) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Scale Right Reduce 100% (Full).py` | 从右侧缩放：Scale Right Reduce 100% (Full)。按右侧参考缩放动画幅度。；关键帧数值、时间或切线 |
| `scale_from_right.scale_right_reduce_150_percent_overshoot_5062abb9` | Scale Right Reduce 150% (Overshoot) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Scale Right Reduce 150% (Overshoot).py` | 从右侧缩放：Scale Right Reduce 150% (Overshoot)。按右侧参考缩放动画幅度。；关键帧数值、时间或切线 |
| `scale_from_right.scale_right_reduce_200_percent_extreme_overshoot_eda3c68a` | Scale Right Reduce 200% (Extreme Overshoot) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Scale Right Reduce 200% (Extreme Overshoot).py` | 从右侧缩放：Scale Right Reduce 200% (Extreme Overshoot)。按右侧参考缩放动画幅度。；关键帧数值、时间或切线 |
| `scale_from_right.scale_right_reduce_25_percent_ed02ca12` | Scale Right Reduce 25% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Scale Right Reduce 25%.py` | 从右侧缩放：Scale Right Reduce 25%。按右侧参考缩放动画幅度。；关键帧数值、时间或切线 |
| `scale_from_right.scale_right_reduce_50_percent_ec528e46` | Scale Right Reduce 50% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Scale Right Reduce 50%.py` | 从右侧缩放：Scale Right Reduce 50%。按右侧参考缩放动画幅度。；关键帧数值、时间或切线 |
| `scale_from_right.scale_right_reduce_75_percent_5a2208ff` | Scale Right Reduce 75% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Scale Right Reduce 75%.py` | 从右侧缩放：Scale Right Reduce 75%。按右侧参考缩放动画幅度。；关键帧数值、时间或切线 |
| `scale_from_right.scale_right_reduce_90_percent_55279387` | Scale Right Reduce 90% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Scale Right Reduce 90%.py` | 从右侧缩放：Scale Right Reduce 90%。按右侧参考缩放动画幅度。；关键帧数值、时间或切线 |

## 调用

```python
tool.run(dry_run=True, action="invoke", operation_id='scale_from_right.scale_right_exaggerate_10_percent_ecb932f0')
# 阅读预检结果后再执行：
# tool.run(action="invoke", operation_id='scale_from_right.scale_right_exaggerate_10_percent_ecb932f0')
```

所有入口的函数签名、顶层固定调用值及原索引别名见候选 `operations.json`；这些是静态证据，不表示运行兼容。
