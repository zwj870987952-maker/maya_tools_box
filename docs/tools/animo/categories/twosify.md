# 风格化动画（Twosify）

通过动画层、步进或间隔处理制作有限帧数风格动画。

- 状态：prepared_unverified，等待人工 Maya 直验。
- 输入：当前 Maya 选择、通道/Graph Editor 关键帧及时间区间；固定预设由下列脚本定义。
- 输出：候选 API 返回分派状态与操作后选择，不声称原算法已成功。
- 撤销：场景操作进入 Undo Chunk；外部文件、UI、插件、偏好不由 Maya Undo 撤回。

| operation ID | 原名称 | 执行源文件（相对 Animo_v10.6.0） | 具体用途/影响 |
| --- | --- | --- | --- |
| `twosify.add_selected_to_anim_layer_3f0e35b7` | Add Selected to Anim Layer | `Animo_Data/Animo_Twosify/add_selections_to_animlayer.py` | 风格化动画：Add Selected to Anim Layer。通过动画层、步进或间隔处理制作有限帧数风格动画。；动画层和关键帧 |
| `twosify.open_twosify_ui_b88a2727` | Open Twosify UI | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Open Twosify UI.py` | 风格化动画：Open Twosify UI。通过动画层、步进或间隔处理制作有限帧数风格动画。；动画层和关键帧 |
| `twosify.select_objects_in_anim_layer_271f9f82` | Select Objects in Anim Layer | `Animo_Data/Animo_Twosify/quick_select_objects_in_animlayer.py` | 风格化动画：Select Objects in Anim Layer。通过动画层、步进或间隔处理制作有限帧数风格动画。；动画层和关键帧 |
| `twosify.update_selected_layer_6ee7fcd1` | Update Selected Layer | `Animo_Data/Animo_Twosify/update_selected_layer.py` | 风格化动画：Update Selected Layer。通过动画层、步进或间隔处理制作有限帧数风格动画。；动画层和关键帧 |

## 调用

```python
tool.run(dry_run=True, action="invoke", operation_id='twosify.add_selected_to_anim_layer_3f0e35b7')
# 阅读预检结果后再执行：
# tool.run(action="invoke", operation_id='twosify.add_selected_to_anim_layer_3f0e35b7')
```

所有入口的函数签名、顶层固定调用值及原索引别名见候选 `operations.json`；这些是静态证据，不表示运行兼容。
