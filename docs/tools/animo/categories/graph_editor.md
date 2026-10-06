# 曲线编辑器（Graph Editor）

打开或改变编辑器布局，过滤、循环、反转、平滑或裁剪曲线。

- 状态：prepared_unverified，等待人工 Maya 直验。
- 输入：当前 Maya 选择、通道/Graph Editor 关键帧及时间区间；固定预设由下列脚本定义。
- 输出：候选 API 返回分派状态与操作后选择，不声称原算法已成功。
- 撤销：场景操作进入 Undo Chunk；外部文件、UI、插件、偏好不由 Maya Undo 撤回。

| operation ID | 原名称 | 执行源文件（相对 Animo_v10.6.0） | 具体用途/影响 |
| --- | --- | --- | --- |
| `graph_editor.crop_animation_5b6152d3` | Crop Animation | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/CropAnimation.py` | 曲线编辑器：Crop Animation。打开或改变编辑器布局，过滤、循环、反转、平滑或裁剪曲线。；编辑器 UI、曲线或切线 |
| `graph_editor.delete_redundant_keys_b217c1bf` | Delete Redundant Keys | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Delete Redundant Keys.py` | 曲线编辑器：Delete Redundant Keys。打开或改变编辑器布局，过滤、循环、反转、平滑或裁剪曲线。；编辑器 UI、曲线或切线 |
| `graph_editor.euler_filter_ecea344b` | Euler Filter | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Euler Filter.py` | 曲线编辑器：Euler Filter。打开或改变编辑器布局，过滤、循环、反转、平滑或裁剪曲线。；编辑器 UI、曲线或切线 |
| `graph_editor.graph_editor_toolbar_3e285f81` | Graph Editor Toolbar | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Graph Editor Toolbar.py` | 曲线编辑器：Graph Editor Toolbar。打开或改变编辑器布局，过滤、循环、反转、平滑或裁剪曲线。；编辑器 UI、曲线或切线 |
| `graph_editor.make_cycle_post_d54fd051` | Make Cycle POST | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Make Cycle POST.py` | 曲线编辑器：Make Cycle POST。打开或改变编辑器布局，过滤、循环、反转、平滑或裁剪曲线。；编辑器 UI、曲线或切线 |
| `graph_editor.make_cycle_pre_a0cb8d4d` | Make Cycle PRE | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Make Cycle PRE.py` | 曲线编辑器：Make Cycle PRE。打开或改变编辑器布局，过滤、循环、反转、平滑或裁剪曲线。；编辑器 UI、曲线或切线 |
| `graph_editor.reverse_animation_8c005f99` | Reverse Animation | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Reverse Animation.py` | 曲线编辑器：Reverse Animation。打开或改变编辑器布局，过滤、循环、反转、平滑或裁剪曲线。；编辑器 UI、曲线或切线 |
| `graph_editor.smooth_selected_keys_86e559d4` | Smooth Selected Keys | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/AnimoSmoothKeysPlugin.py` | 曲线编辑器：Smooth Selected Keys。打开或改变编辑器布局，过滤、循环、反转、平滑或裁剪曲线。；编辑器 UI、曲线或切线 |
| `graph_editor.toggle_graph_editor_minus_minimize_a068de7c` | Toggle Graph Editor - Minimize | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Toggle Graph Editor - Minimize.py` | 曲线编辑器：Toggle Graph Editor - Minimize。打开或改变编辑器布局，过滤、循环、反转、平滑或裁剪曲线。；编辑器 UI、曲线或切线 |
| `graph_editor.toggle_graph_editor_273b555b` | Toggle Graph Editor | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Toggle Graph Editor.py` | 曲线编辑器：Toggle Graph Editor。打开或改变编辑器布局，过滤、循环、反转、平滑或裁剪曲线。；编辑器 UI、曲线或切线 |

## 调用

```python
tool.run(dry_run=True, action="invoke", operation_id='graph_editor.crop_animation_5b6152d3')
# 阅读预检结果后再执行：
# tool.run(action="invoke", operation_id='graph_editor.crop_animation_5b6152d3')
```

所有入口的函数签名、顶层固定调用值及原索引别名见候选 `operations.json`；这些是静态证据，不表示运行兼容。
