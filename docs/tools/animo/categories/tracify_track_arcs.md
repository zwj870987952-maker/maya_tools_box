# 运动弧线（Tracify (Track Arcs)）

跟踪世界或摄像机空间运动轨迹，调整缓存和显示。

- 状态：prepared_unverified，等待人工 Maya 直验。
- 输入：当前 Maya 选择、通道/Graph Editor 关键帧及时间区间；固定预设由下列脚本定义。
- 输出：候选 API 返回分派状态与操作后选择，不声称原算法已成功。
- 撤销：场景操作进入 Undo Chunk；外部文件、UI、插件、偏好不由 Maya Undo 撤回。

| operation ID | 原名称 | 执行源文件（相对 Animo_v10.6.0） | 具体用途/影响 |
| --- | --- | --- | --- |
| `tracify_track_arcs.cycle_tracify_color_mode_76a63b0f` | Cycle Tracify Color Mode | `Animo_Data/Animo_Tools_Editor/tools_library/Tracify (Track Arcs)/Cycle Tracify Color Mode.py` | 运动弧线：Cycle Tracify Color Mode。跟踪世界或摄像机空间运动轨迹，调整缓存和显示。；插件节点、轨迹缓存和视口 |
| `tracify_track_arcs.reset_tracify_to_default_f3840831` | Reset Tracify To Default | `Animo_Data/Animo_Tools_Editor/tools_library/Tracify (Track Arcs)/Reset Tracify To Default.py` | 运动弧线：Reset Tracify To Default。跟踪世界或摄像机空间运动轨迹，调整缓存和显示。；插件节点、轨迹缓存和视口 |
| `tracify_track_arcs.toggle_tracify_camera_space_7b390308` | Toggle Tracify Camera Space | `Animo_Data/Animo_Tools_Editor/tools_library/Tracify (Track Arcs)/Toggle Tracify Camera Space.py` | 运动弧线：Toggle Tracify Camera Space。跟踪世界或摄像机空间运动轨迹，调整缓存和显示。；插件节点、轨迹缓存和视口 |
| `tracify_track_arcs.track_arcs_88e434d1` | Track Arcs | `Animo_Data/Animo_Tools_Editor/tools_library/Tracify (Track Arcs)/Track Arcs.py` | 运动弧线：Track Arcs。跟踪世界或摄像机空间运动轨迹，调整缓存和显示。；插件节点、轨迹缓存和视口 |

## 调用

```python
tool.run(dry_run=True, action="invoke", operation_id='tracify_track_arcs.cycle_tracify_color_mode_76a63b0f')
# 阅读预检结果后再执行：
# tool.run(action="invoke", operation_id='tracify_track_arcs.cycle_tracify_color_mode_76a63b0f')
```

所有入口的函数签名、顶层固定调用值及原索引别名见候选 `operations.json`；这些是静态证据，不表示运行兼容。
