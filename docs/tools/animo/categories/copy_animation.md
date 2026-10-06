# 跨场景动画传递（Copy Animation）

保存 JSON 动画数据并插入或替换；分层对象可能要求先合并。

- 状态：prepared_unverified，等待人工 Maya 直验。
- 输入：当前 Maya 选择、通道/Graph Editor 关键帧及时间区间；固定预设由下列脚本定义。
- 输出：候选 API 返回分派状态与操作后选择，不声称原算法已成功。
- 撤销：场景操作进入 Undo Chunk；外部文件、UI、插件、偏好不由 Maya Undo 撤回。

| operation ID | 原名称 | 执行源文件（相对 Animo_v10.6.0） | 具体用途/影响 |
| --- | --- | --- | --- |
| `copy_animation.copy_all_animation_channels_b238a89e` | Copy All Animation Channels | `Animo_Data/Animo_Transify/transify_action_copy_all_channels.py` | 跨场景动画传递：Copy All Animation Channels。保存 JSON 动画数据并插入或替换；分层对象可能要求先合并。；曲线及动画 JSON 文件 |
| `copy_animation.copy_selected_channels_a6eb1e50` | Copy Selected Channels | `Animo_Data/Animo_Transify/transify_action_copy_selected_channels.py` | 跨场景动画传递：Copy Selected Channels。保存 JSON 动画数据并插入或替换；分层对象可能要求先合并。；曲线及动画 JSON 文件 |
| `copy_animation.insert_animation_c4466a33` | Insert Animation | `Animo_Data/Animo_Transify/transify_action_insert_animation.py` | 跨场景动画传递：Insert Animation。保存 JSON 动画数据并插入或替换；分层对象可能要求先合并。；曲线及动画 JSON 文件 |
| `copy_animation.replace_animation_e13a3e0a` | Replace Animation | `Animo_Data/Animo_Transify/transify_action_replace_animation.py` | 跨场景动画传递：Replace Animation。保存 JSON 动画数据并插入或替换；分层对象可能要求先合并。；曲线及动画 JSON 文件 |
| `copy_animation.select_objects_9b8a19f6` | Select Objects | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Select Objects.py` | 跨场景动画传递：Select Objects。保存 JSON 动画数据并插入或替换；分层对象可能要求先合并。；曲线及动画 JSON 文件 |

## 调用

```python
tool.run(dry_run=True, action="invoke", operation_id='copy_animation.copy_all_animation_channels_b238a89e')
# 阅读预检结果后再执行：
# tool.run(action="invoke", operation_id='copy_animation.copy_all_animation_channels_b238a89e')
```

所有入口的函数签名、顶层固定调用值及原索引别名见候选 `operations.json`；这些是静态证据，不表示运行兼容。
