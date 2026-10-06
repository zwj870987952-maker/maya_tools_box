# 动画层（Animation Layers）

创建、选择、管理或合并动画层；合并可能改变原层结构。

- 状态：prepared_unverified，等待人工 Maya 直验。
- 输入：当前 Maya 选择、通道/Graph Editor 关键帧及时间区间；固定预设由下列脚本定义。
- 输出：候选 API 返回分派状态与操作后选择，不声称原算法已成功。
- 撤销：场景操作进入 Undo Chunk；外部文件、UI、插件、偏好不由 Maya Undo 撤回。

| operation ID | 原名称 | 执行源文件（相对 Animo_v10.6.0） | 具体用途/影响 |
| --- | --- | --- | --- |
| `animation_layers.add_selected_to_anim_layer_3f1e6c3f` | Add Selected To Anim Layer | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Add Selected To Anim Layer.py` | 动画层：Add Selected To Anim Layer。创建、选择、管理或合并动画层；合并可能改变原层结构。；动画层、成员与关键帧 |
| `animation_layers.bake_selected_to_override_layer_c409153a` | Bake Selected To Override Layer | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Bake Selected To Override Layer.py` | 动画层：Bake Selected To Override Layer。创建、选择、管理或合并动画层；合并可能改变原层结构。；动画层、成员与关键帧 |
| `animation_layers.create_anim_layer_1f3dabe2` | Create Anim Layer | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Create Anim Layer.py` | 动画层：Create Anim Layer。创建、选择、管理或合并动画层；合并可能改变原层结构。；动画层、成员与关键帧 |
| `animation_layers.create_override_anim_layer_826e210f` | Create Override Anim Layer | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Create Override Anim Layer.py` | 动画层：Create Override Anim Layer。创建、选择、管理或合并动画层；合并可能改变原层结构。；动画层、成员与关键帧 |
| `animation_layers.merge_all_anim_layers_28db4700` | Merge All Anim Layers | `Animo_Data/Animo_Animation_Layers/merge_all_anim_layers.py` | 动画层：Merge All Anim Layers。创建、选择、管理或合并动画层；合并可能改变原层结构。；动画层、成员与关键帧 |
| `animation_layers.merge_selected_anim_layers_5f374531` | Merge Selected Anim Layers | `Animo_Data/Animo_Animation_Layers/merge_selected_anim_layers.py` | 动画层：Merge Selected Anim Layers。创建、选择、管理或合并动画层；合并可能改变原层结构。；动画层、成员与关键帧 |
| `animation_layers.remove_selected_from_anim_layer_fddcbbb0` | Remove Selected From Anim Layer | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Remove Selected From Anim Layer.py` | 动画层：Remove Selected From Anim Layer。创建、选择、管理或合并动画层；合并可能改变原层结构。；动画层、成员与关键帧 |
| `animation_layers.set_selected_layers_additive_29bde9c8` | Set Selected Layers Additive | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Set Selected Layers Additive.py` | 动画层：Set Selected Layers Additive。创建、选择、管理或合并动画层；合并可能改变原层结构。；动画层、成员与关键帧 |
| `animation_layers.set_selected_layers_override_ca129ed6` | Set Selected Layers Override | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Set Selected Layers Override.py` | 动画层：Set Selected Layers Override。创建、选择、管理或合并动画层；合并可能改变原层结构。；动画层、成员与关键帧 |
| `animation_layers.smart_merge_all_anim_layers_ccba6c95` | Smart Merge All Anim Layers | `Animo_Data/Animo_Animation_Layers/smart_merge_all_anim_layers.py` | 动画层：Smart Merge All Anim Layers。创建、选择、管理或合并动画层；合并可能改变原层结构。；动画层、成员与关键帧 |
| `animation_layers.smart_merge_selected_anim_layers_81acfb82` | Smart Merge Selected Anim Layers | `Animo_Data/Animo_Animation_Layers/smart_merge_selected_anim_layers.py` | 动画层：Smart Merge Selected Anim Layers。创建、选择、管理或合并动画层；合并可能改变原层结构。；动画层、成员与关键帧 |

## 调用

```python
tool.run(dry_run=True, action="invoke", operation_id='animation_layers.add_selected_to_anim_layer_3f1e6c3f')
# 阅读预检结果后再执行：
# tool.run(action="invoke", operation_id='animation_layers.add_selected_to_anim_layer_3f1e6c3f')
```

所有入口的函数签名、顶层固定调用值及原索引别名见候选 `operations.json`；这些是静态证据，不表示运行兼容。
