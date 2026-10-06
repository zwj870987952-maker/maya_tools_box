# 世界变换（Xform World）

复制/粘贴世界空间变换、烘焙区间或锁定脚部。

- 状态：prepared_unverified，等待人工 Maya 直验。
- 输入：当前 Maya 选择、通道/Graph Editor 关键帧及时间区间；固定预设由下列脚本定义。
- 输出：候选 API 返回分派状态与操作后选择，不声称原算法已成功。
- 撤销：场景操作进入 Undo Chunk；外部文件、UI、插件、偏好不由 Maya Undo 撤回。

| operation ID | 原名称 | 执行源文件（相对 Animo_v10.6.0） | 具体用途/影响 |
| --- | --- | --- | --- |
| `xform_world.copy_xform_48c2b4d8` | Copy_XForm | `Animo_Data/Animo_Space_Switcher/xform_copy.py` | 世界变换：Copy_XForm。复制/粘贴世界空间变换、烘焙区间或锁定脚部。；变换、关键帧或缓存文件 |
| `xform_world.copy_xform_range_128f9648` | Copy_XForm_Range | `Animo_Data/Animo_Space_Switcher/xform_copy_range.py` | 世界变换：Copy_XForm_Range。复制/粘贴世界空间变换、烘焙区间或锁定脚部。；变换、关键帧或缓存文件 |
| `xform_world.foot_locker_f22af0e9` | Foot Locker | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Foot Locker.py` | 世界变换：Foot Locker。复制/粘贴世界空间变换、烘焙区间或锁定脚部。；变换、关键帧或缓存文件 |
| `xform_world.paste_xform_2b2ace4d` | Paste_XForm | `Animo_Data/Animo_Space_Switcher/xform_paste.py` | 世界变换：Paste_XForm。复制/粘贴世界空间变换、烘焙区间或锁定脚部。；变换、关键帧或缓存文件 |
| `xform_world.paste_xform_range_a53c952e` | Paste_XForm_Range | `Animo_Data/Animo_Space_Switcher/xform_paste_range.py` | 世界变换：Paste_XForm_Range。复制/粘贴世界空间变换、烘焙区间或锁定脚部。；变换、关键帧或缓存文件 |
| `xform_world.toggle_bake_onlykeys_64e96a58` | Toggle_Bake_OnlyKeys | `Animo_Data/Animo_Tools_Editor/tools_library/Xform World/Toggle_Bake_OnlyKeys.py` | 世界变换：Toggle_Bake_OnlyKeys。复制/粘贴世界空间变换、烘焙区间或锁定脚部。；变换、关键帧或缓存文件 |

## 调用

```python
tool.run(dry_run=True, action="invoke", operation_id='xform_world.copy_xform_48c2b4d8')
# 阅读预检结果后再执行：
# tool.run(action="invoke", operation_id='xform_world.copy_xform_48c2b4d8')
```

所有入口的函数签名、顶层固定调用值及原索引别名见候选 `operations.json`；这些是静态证据，不表示运行兼容。
