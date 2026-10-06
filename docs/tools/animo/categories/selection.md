# 选择管理（Selection）

改变对象或曲线选择，供后续动画编辑使用。

- 状态：prepared_unverified，等待人工 Maya 直验。
- 输入：当前 Maya 选择、通道/Graph Editor 关键帧及时间区间；固定预设由下列脚本定义。
- 输出：候选 API 返回分派状态与操作后选择，不声称原算法已成功。
- 撤销：场景操作进入 Undo Chunk；外部文件、UI、插件、偏好不由 Maya Undo 撤回。

| operation ID | 原名称 | 执行源文件（相对 Animo_v10.6.0） | 具体用途/影响 |
| --- | --- | --- | --- |
| `selection.add_select_opposite_controls_844447f4` | Add Select Opposite Controls | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Add Select Opposite Controls.py` | 选择管理：Add Select Opposite Controls。改变对象或曲线选择，供后续动画编辑使用。；当前选择 |
| `selection.select_all_animation_data_in_scene_417d0e8f` | Select All Animation Data In Scene | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Select All Animation Data In Scene.py` | 选择管理：Select All Animation Data In Scene。改变对象或曲线选择，供后续动画编辑使用。；当前选择 |
| `selection.select_all_rig_controls_478c3dcb` | Select All Rig Controls | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Select All Rig Controls.py` | 选择管理：Select All Rig Controls。改变对象或曲线选择，供后续动画编辑使用。；当前选择 |
| `selection.select_hierachy_joints_only_8ae6a3f7` | Select Hierachy Joints Only | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Select Hierachy Joints Only.py` | 选择管理：Select Hierachy Joints Only。改变对象或曲线选择，供后续动画编辑使用。；当前选择 |
| `selection.select_hierachy_locators_only_ecf137e6` | Select Hierachy Locators Only | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Select Hierachy Locators Only.py` | 选择管理：Select Hierachy Locators Only。改变对象或曲线选择，供后续动画编辑使用。；当前选择 |
| `selection.select_hierachy_nurbs_curves_only_17197871` | Select Hierachy Nurbs Curves Only | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Select Hierachy Nurbs Curves Only.py` | 选择管理：Select Hierachy Nurbs Curves Only。改变对象或曲线选择，供后续动画编辑使用。；当前选择 |
| `selection.select_hierachy_b766e98c` | Select Hierachy | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Select Hierachy.py` | 选择管理：Select Hierachy。改变对象或曲线选择，供后续动画编辑使用。；当前选择 |
| `selection.select_objects_from_keys_febcf72a` | Select Objects From Keys | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Select Objects From Keys.py` | 选择管理：Select Objects From Keys。改变对象或曲线选择，供后续动画编辑使用。；当前选择 |
| `selection.select_opposite_controls_3b00b0ab` | Select Opposite Controls | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Select Opposite Controls.py` | 选择管理：Select Opposite Controls。改变对象或曲线选择，供后续动画编辑使用。；当前选择 |

## 调用

```python
tool.run(dry_run=True, action="invoke", operation_id='selection.add_select_opposite_controls_844447f4')
# 阅读预检结果后再执行：
# tool.run(action="invoke", operation_id='selection.add_select_opposite_controls_844447f4')
```

所有入口的函数签名、顶层固定调用值及原索引别名见候选 `operations.json`；这些是静态证据，不表示运行兼容。
