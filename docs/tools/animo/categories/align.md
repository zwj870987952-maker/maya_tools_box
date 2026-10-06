# 对齐（Align）

根据选择顺序将前面的对象对齐到目标对象，可针对时间范围。

- 状态：prepared_unverified，等待人工 Maya 直验。
- 输入：当前 Maya 选择、通道/Graph Editor 关键帧及时间区间；固定预设由下列脚本定义。
- 输出：候选 API 返回分派状态与操作后选择，不声称原算法已成功。
- 撤销：场景操作进入 Undo Chunk；外部文件、UI、插件、偏好不由 Maya Undo 撤回。

| operation ID | 原名称 | 执行源文件（相对 Animo_v10.6.0） | 具体用途/影响 |
| --- | --- | --- | --- |
| `align.align_range_rotate_1cf4d97e` | Align Range Rotate | `Animo_Data/Animo_Tools_Editor/tools_library/Align/Align Range Rotate.py` | 对齐：Align Range Rotate。根据选择顺序将前面的对象对齐到目标对象，可针对时间范围。；变换或关键帧 |
| `align.align_range_translate_e2fb39f7` | Align Range Translate | `Animo_Data/Animo_Tools_Editor/tools_library/Align/Align Range Translate.py` | 对齐：Align Range Translate。根据选择顺序将前面的对象对齐到目标对象，可针对时间范围。；变换或关键帧 |
| `align.align_range_b306c521` | Align Range | `Animo_Data/Animo_Tools_Editor/tools_library/Align/Align Range.py` | 对齐：Align Range。根据选择顺序将前面的对象对齐到目标对象，可针对时间范围。；变换或关键帧 |
| `align.align_rotate_006361f2` | Align Rotate | `Animo_Data/Animo_Tools_Editor/tools_library/Align/Align Rotate.py` | 对齐：Align Rotate。根据选择顺序将前面的对象对齐到目标对象，可针对时间范围。；变换或关键帧 |
| `align.align_translate_e85d5e20` | Align Translate | `Animo_Data/Animo_Tools_Editor/tools_library/Align/Align Translate.py` | 对齐：Align Translate。根据选择顺序将前面的对象对齐到目标对象，可针对时间范围。；变换或关键帧 |
| `align.align_d0583f43` | Align | `Animo_Data/Animo_Tools_Editor/tools_library/Align/Align.py` | 对齐：Align。根据选择顺序将前面的对象对齐到目标对象，可针对时间范围。；变换或关键帧 |

## 调用

```python
tool.run(dry_run=True, action="invoke", operation_id='align.align_range_rotate_1cf4d97e')
# 阅读预检结果后再执行：
# tool.run(action="invoke", operation_id='align.align_range_rotate_1cf4d97e')
```

所有入口的函数签名、顶层固定调用值及原索引别名见候选 `operations.json`；这些是静态证据，不表示运行兼容。
