# 补间（Tween）

按左右边界值调整所选关键帧；不是按关键帧时间比例插值。

- 状态：prepared_unverified，等待人工 Maya 直验。
- 输入：当前 Maya 选择、通道/Graph Editor 关键帧及时间区间；固定预设由下列脚本定义。
- 输出：候选 API 返回分派状态与操作后选择，不声称原算法已成功。
- 撤销：场景操作进入 Undo Chunk；外部文件、UI、插件、偏好不由 Maya Undo 撤回。

| operation ID | 原名称 | 执行源文件（相对 Animo_v10.6.0） | 具体用途/影响 |
| --- | --- | --- | --- |
| `tween.tween_minus_100_percent_923cca84` | Tween -100% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Tween -100%.py` | 补间：Tween -100%。按左右边界值调整所选关键帧；不是按关键帧时间比例插值。；关键帧数值、时间或切线 |
| `tween.tween_minus_120_percent_eb75b47e` | Tween -120% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Tween -120%.py` | 补间：Tween -120%。按左右边界值调整所选关键帧；不是按关键帧时间比例插值。；关键帧数值、时间或切线 |
| `tween.tween_minus_150_percent_df43933d` | Tween -150% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Tween -150%.py` | 补间：Tween -150%。按左右边界值调整所选关键帧；不是按关键帧时间比例插值。；关键帧数值、时间或切线 |
| `tween.tween_minus_200_percent_010be054` | Tween -200% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Tween -200%.py` | 补间：Tween -200%。按左右边界值调整所选关键帧；不是按关键帧时间比例插值。；关键帧数值、时间或切线 |
| `tween.tween_100_percent_ba3c0855` | Tween 100% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Tween 100%.py` | 补间：Tween 100%。按左右边界值调整所选关键帧；不是按关键帧时间比例插值。；关键帧数值、时间或切线 |
| `tween.tween_120_percent_ac286061` | Tween 120% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Tween 120%.py` | 补间：Tween 120%。按左右边界值调整所选关键帧；不是按关键帧时间比例插值。；关键帧数值、时间或切线 |
| `tween.tween_13_percent_e4174579` | Tween 13% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Tween 13%.py` | 补间：Tween 13%。按左右边界值调整所选关键帧；不是按关键帧时间比例插值。；关键帧数值、时间或切线 |
| `tween.tween_150_percent_767d9647` | Tween 150% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Tween 150%.py` | 补间：Tween 150%。按左右边界值调整所选关键帧；不是按关键帧时间比例插值。；关键帧数值、时间或切线 |
| `tween.tween_17_percent_dbeb5a89` | Tween 17% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Tween 17%.py` | 补间：Tween 17%。按左右边界值调整所选关键帧；不是按关键帧时间比例插值。；关键帧数值、时间或切线 |
| `tween.tween_200_percent_b6c0a38e` | Tween 200% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Tween 200%.py` | 补间：Tween 200%。按左右边界值调整所选关键帧；不是按关键帧时间比例插值。；关键帧数值、时间或切线 |
| `tween.tween_25_percent_13f45698` | Tween 25% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Tween 25%.py` | 补间：Tween 25%。按左右边界值调整所选关键帧；不是按关键帧时间比例插值。；关键帧数值、时间或切线 |
| `tween.tween_33_percent_3b284a67` | Tween 33% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Tween 33%.py` | 补间：Tween 33%。按左右边界值调整所选关键帧；不是按关键帧时间比例插值。；关键帧数值、时间或切线 |
| `tween.tween_50_percent_76b2f496` | Tween 50% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Tween 50%.py` | 补间：Tween 50%。按左右边界值调整所选关键帧；不是按关键帧时间比例插值。；关键帧数值、时间或切线 |
| `tween.tween_67_percent_9e416c79` | Tween 67% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Tween 67%.py` | 补间：Tween 67%。按左右边界值调整所选关键帧；不是按关键帧时间比例插值。；关键帧数值、时间或切线 |
| `tween.tween_75_percent_9ef7e29b` | Tween 75% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Tween 75%.py` | 补间：Tween 75%。按左右边界值调整所选关键帧；不是按关键帧时间比例插值。；关键帧数值、时间或切线 |
| `tween.tween_83_percent_e3e345dc` | Tween 83% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Tween 83%.py` | 补间：Tween 83%。按左右边界值调整所选关键帧；不是按关键帧时间比例插值。；关键帧数值、时间或切线 |
| `tween.tween_88_percent_03684ac5` | Tween 88% | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Tween 88%.py` | 补间：Tween 88%。按左右边界值调整所选关键帧；不是按关键帧时间比例插值。；关键帧数值、时间或切线 |

## 调用

```python
tool.run(dry_run=True, action="invoke", operation_id='tween.tween_minus_100_percent_923cca84')
# 阅读预检结果后再执行：
# tool.run(action="invoke", operation_id='tween.tween_minus_100_percent_923cca84')
```

所有入口的函数签名、顶层固定调用值及原索引别名见候选 `operations.json`；这些是静态证据，不表示运行兼容。
