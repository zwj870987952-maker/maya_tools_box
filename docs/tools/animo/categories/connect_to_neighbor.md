# 衔接邻帧（Connect To Neighbor）

按邻帧边界调整动画衔接。

- 状态：prepared_unverified，等待人工 Maya 直验。
- 输入：当前 Maya 选择、通道/Graph Editor 关键帧及时间区间；固定预设由下列脚本定义。
- 输出：候选 API 返回分派状态与操作后选择，不声称原算法已成功。
- 撤销：场景操作进入 Undo Chunk；外部文件、UI、插件、偏好不由 Maya Undo 撤回。

| operation ID | 原名称 | 执行源文件（相对 Animo_v10.6.0） | 具体用途/影响 |
| --- | --- | --- | --- |
| `connect_to_neighbor.connect_to_neighbor_minus_10_07537870` | Connect To Neighbor -10 | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Cascade Collapse 10%.py` | 衔接邻帧：Connect To Neighbor -10。按邻帧边界调整动画衔接。；关键帧数值、时间或切线 |
| `connect_to_neighbor.connect_to_neighbor_minus_100_full_8492c649` | Connect To Neighbor -100 (Full) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Cascade Collapse 100% (Full).py` | 衔接邻帧：Connect To Neighbor -100 (Full)。按邻帧边界调整动画衔接。；关键帧数值、时间或切线 |
| `connect_to_neighbor.connect_to_neighbor_minus_25_b002cd0f` | Connect To Neighbor -25 | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Cascade Collapse 25%.py` | 衔接邻帧：Connect To Neighbor -25。按邻帧边界调整动画衔接。；关键帧数值、时间或切线 |
| `connect_to_neighbor.connect_to_neighbor_minus_50_91fd024e` | Connect To Neighbor -50 | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Cascade Collapse 50%.py` | 衔接邻帧：Connect To Neighbor -50。按邻帧边界调整动画衔接。；关键帧数值、时间或切线 |
| `connect_to_neighbor.connect_to_neighbor_minus_75_67076629` | Connect To Neighbor -75 | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Cascade Collapse 75%.py` | 衔接邻帧：Connect To Neighbor -75。按邻帧边界调整动画衔接。；关键帧数值、时间或切线 |
| `connect_to_neighbor.connect_to_neighbor_minus_90_0771697c` | Connect To Neighbor -90 | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Cascade Collapse 90%.py` | 衔接邻帧：Connect To Neighbor -90。按邻帧边界调整动画衔接。；关键帧数值、时间或切线 |
| `connect_to_neighbor.connect_to_neighbor_10_b5acf169` | Connect To Neighbor 10 | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Cascade Expand 10%.py` | 衔接邻帧：Connect To Neighbor 10。按邻帧边界调整动画衔接。；关键帧数值、时间或切线 |
| `connect_to_neighbor.connect_to_neighbor_100_full_1b49622e` | Connect To Neighbor 100 (Full) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Cascade Expand 100% (Full).py` | 衔接邻帧：Connect To Neighbor 100 (Full)。按邻帧边界调整动画衔接。；关键帧数值、时间或切线 |
| `connect_to_neighbor.connect_to_neighbor_25_22e3cac9` | Connect To Neighbor 25 | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Cascade Expand 25%.py` | 衔接邻帧：Connect To Neighbor 25。按邻帧边界调整动画衔接。；关键帧数值、时间或切线 |
| `connect_to_neighbor.connect_to_neighbor_50_a94768a7` | Connect To Neighbor 50 | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Cascade Expand 50%.py` | 衔接邻帧：Connect To Neighbor 50。按邻帧边界调整动画衔接。；关键帧数值、时间或切线 |
| `connect_to_neighbor.connect_to_neighbor_75_4a83c82c` | Connect To Neighbor 75 | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Cascade Expand 75%.py` | 衔接邻帧：Connect To Neighbor 75。按邻帧边界调整动画衔接。；关键帧数值、时间或切线 |
| `connect_to_neighbor.connect_to_neighbor_90_e92af452` | Connect To Neighbor 90 | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Cascade Expand 90%.py` | 衔接邻帧：Connect To Neighbor 90。按邻帧边界调整动画衔接。；关键帧数值、时间或切线 |

## 调用

```python
tool.run(dry_run=True, action="invoke", operation_id='connect_to_neighbor.connect_to_neighbor_minus_10_07537870')
# 阅读预检结果后再执行：
# tool.run(action="invoke", operation_id='connect_to_neighbor.connect_to_neighbor_minus_10_07537870')
```

所有入口的函数签名、顶层固定调用值及原索引别名见候选 `operations.json`；这些是静态证据，不表示运行兼容。
