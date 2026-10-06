# 关键帧操作（Keys）

对当前对象、通道或所选关键帧进行增删、复制和编辑。

- 状态：prepared_unverified，等待人工 Maya 直验。
- 输入：当前 Maya 选择、通道/Graph Editor 关键帧及时间区间；固定预设由下列脚本定义。
- 输出：候选 API 返回分派状态与操作后选择，不声称原算法已成功。
- 撤销：场景操作进入 Undo Chunk；外部文件、UI、插件、偏好不由 Maya Undo 撤回。

| operation ID | 原名称 | 执行源文件（相对 Animo_v10.6.0） | 具体用途/影响 |
| --- | --- | --- | --- |
| `keys.clear_animation_e200b66b` | Clear Animation | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Clear Animation.py` | 关键帧操作：Clear Animation。对当前对象、通道或所选关键帧进行增删、复制和编辑。；关键帧或选择 |
| `keys.jump_to_next_frame_58d3c741` | Jump to Next Frame | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Jump to Next Frame.py` | 关键帧操作：Jump to Next Frame。对当前对象、通道或所选关键帧进行增删、复制和编辑。；关键帧或选择 |
| `keys.jump_to_next_keyframe_smart_3f7e4c45` | Jump to Next Keyframe (Smart) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Jump to Next Keyframe (Smart).py` | 关键帧操作：Jump to Next Keyframe (Smart)。对当前对象、通道或所选关键帧进行增删、复制和编辑。；关键帧或选择 |
| `keys.jump_to_previous_frame_e14ded79` | Jump to Previous Frame | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Jump to Previous Frame.py` | 关键帧操作：Jump to Previous Frame。对当前对象、通道或所选关键帧进行增删、复制和编辑。；关键帧或选择 |
| `keys.jump_to_previous_keyframe_smart_df421fbe` | Jump to Previous Keyframe (Smart) | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Jump to Previous Keyframe (Smart).py` | 关键帧操作：Jump to Previous Keyframe (Smart)。对当前对象、通道或所选关键帧进行增删、复制和编辑。；关键帧或选择 |
| `keys.keyframe_reducer_75d84405` | Keyframe Reducer | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Keyframe Reducer.py` | 关键帧操作：Keyframe Reducer。对当前对象、通道或所选关键帧进行增删、复制和编辑。；关键帧或选择 |
| `keys.share_keys_b7f40e5f` | Share Keys | `Animo_Data/Animo_Share_Keys/share_keys.py` | 关键帧操作：Share Keys。对当前对象、通道或所选关键帧进行增删、复制和编辑。；关键帧或选择 |
| `keys.smart_copy_keys_5d18162d` | Smart Copy Keys | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Smart Copy Keys.py` | 关键帧操作：Smart Copy Keys。对当前对象、通道或所选关键帧进行增删、复制和编辑。；关键帧或选择 |
| `keys.smart_delete_keys_0ed8d6ff` | Smart Delete Keys | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Smart Delete Keys.py` | 关键帧操作：Smart Delete Keys。对当前对象、通道或所选关键帧进行增删、复制和编辑。；关键帧或选择 |
| `keys.smart_paste_keys_relative_317b0dba` | Smart Paste Keys Relative | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Smart Paste Keys Relative.py` | 关键帧操作：Smart Paste Keys Relative。对当前对象、通道或所选关键帧进行增删、复制和编辑。；关键帧或选择 |
| `keys.smart_paste_keys_d16a0163` | Smart Paste Keys | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Smart Paste Keys.py` | 关键帧操作：Smart Paste Keys。对当前对象、通道或所选关键帧进行增删、复制和编辑。；关键帧或选择 |
| `keys.smart_set_keyframes_0be1395a` | Smart Set Keyframes | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Smart Set Keyframe.py` | 关键帧操作：Smart Set Keyframes。对当前对象、通道或所选关键帧进行增删、复制和编辑。；关键帧或选择 |

## 调用

```python
tool.run(dry_run=True, action="invoke", operation_id='keys.clear_animation_e200b66b')
# 阅读预检结果后再执行：
# tool.run(action="invoke", operation_id='keys.clear_animation_e200b66b')
```

所有入口的函数签名、顶层固定调用值及原索引别名见候选 `operations.json`；这些是静态证据，不表示运行兼容。
