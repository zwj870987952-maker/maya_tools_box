# 快速烘焙（Fast Bake）

按入口标注的帧间隔烘焙动画；输入帧区间由原工具读取。

- 状态：prepared_unverified，等待人工 Maya 直验。
- 输入：当前 Maya 选择、通道/Graph Editor 关键帧及时间区间；固定预设由下列脚本定义。
- 输出：候选 API 返回分派状态与操作后选择，不声称原算法已成功。
- 撤销：场景操作进入 Undo Chunk；外部文件、UI、插件、偏好不由 Maya Undo 撤回。

| operation ID | 原名称 | 执行源文件（相对 Animo_v10.6.0） | 具体用途/影响 |
| --- | --- | --- | --- |
| `fast_bake.fast_bake_minus_every_1_frame_881a4303` | Fast Bake - Every 1 Frame | `Animo_Data/Animo_Fast_Bake/fast_bake_1s.py` | 快速烘焙：Fast Bake - Every 1 Frame。按入口标注的帧间隔烘焙动画；输入帧区间由原工具读取。；生成/替换关键帧 |
| `fast_bake.fast_bake_minus_every_2_frames_e89c7241` | Fast Bake - Every 2 Frames | `Animo_Data/Animo_Fast_Bake/fast_bake_2s.py` | 快速烘焙：Fast Bake - Every 2 Frames。按入口标注的帧间隔烘焙动画；输入帧区间由原工具读取。；生成/替换关键帧 |
| `fast_bake.fast_bake_minus_every_3_frames_43529ef9` | Fast Bake - Every 3 Frames | `Animo_Data/Animo_Fast_Bake/fast_bake_3s.py` | 快速烘焙：Fast Bake - Every 3 Frames。按入口标注的帧间隔烘焙动画；输入帧区间由原工具读取。；生成/替换关键帧 |
| `fast_bake.fast_bake_minus_every_4_frames_7c7abe4b` | Fast Bake - Every 4 Frames | `Animo_Data/Animo_Fast_Bake/fast_bake_4s.py` | 快速烘焙：Fast Bake - Every 4 Frames。按入口标注的帧间隔烘焙动画；输入帧区间由原工具读取。；生成/替换关键帧 |
| `fast_bake.fast_bake_minus_every_5_frames_466c21a1` | Fast Bake - Every 5 Frames | `Animo_Data/Animo_Fast_Bake/fast_bake_5s.py` | 快速烘焙：Fast Bake - Every 5 Frames。按入口标注的帧间隔烘焙动画；输入帧区间由原工具读取。；生成/替换关键帧 |
| `fast_bake.fast_bake_minus_every_6_frames_76f6988f` | Fast Bake - Every 6 Frames | `Animo_Data/Animo_Fast_Bake/fast_bake_6s.py` | 快速烘焙：Fast Bake - Every 6 Frames。按入口标注的帧间隔烘焙动画；输入帧区间由原工具读取。；生成/替换关键帧 |
| `fast_bake.fast_bake_minus_every_7_frames_71a0d71c` | Fast Bake - Every 7 Frames | `Animo_Data/Animo_Fast_Bake/fast_bake_7s.py` | 快速烘焙：Fast Bake - Every 7 Frames。按入口标注的帧间隔烘焙动画；输入帧区间由原工具读取。；生成/替换关键帧 |

## 调用

```python
tool.run(dry_run=True, action="invoke", operation_id='fast_bake.fast_bake_minus_every_1_frame_881a4303')
# 阅读预检结果后再执行：
# tool.run(action="invoke", operation_id='fast_bake.fast_bake_minus_every_1_frame_881a4303')
```

所有入口的函数签名、顶层固定调用值及原索引别名见候选 `operations.json`；这些是静态证据，不表示运行兼容。
