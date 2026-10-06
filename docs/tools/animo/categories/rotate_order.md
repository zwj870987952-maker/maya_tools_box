# 旋转顺序（Rotate Order）

为整段旋转动画转换至入口指定的 Euler 顺序。

- 状态：prepared_unverified，等待人工 Maya 直验。
- 输入：当前 Maya 选择、通道/Graph Editor 关键帧及时间区间；固定预设由下列脚本定义。
- 输出：候选 API 返回分派状态与操作后选择，不声称原算法已成功。
- 撤销：场景操作进入 Undo Chunk；外部文件、UI、插件、偏好不由 Maya Undo 撤回。

| operation ID | 原名称 | 执行源文件（相对 Animo_v10.6.0） | 具体用途/影响 |
| --- | --- | --- | --- |
| `rotate_order.rotate_order_minus_xyz_whole_animation_35ce1b1f` | Rotate Order - XYZ (Whole Animation) | `Animo_Data/Animo_Tools_Editor/tools_library/Rotate Order/Rotate Order - XYZ (Whole Animation).py` | 旋转顺序：Rotate Order - XYZ (Whole Animation)。为整段旋转动画转换至入口指定的 Euler 顺序。；rotateOrder 和旋转关键帧 |
| `rotate_order.rotate_order_minus_xzy_whole_animation_780fe8c4` | Rotate Order - XZY (Whole Animation) | `Animo_Data/Animo_Tools_Editor/tools_library/Rotate Order/Rotate Order - XZY (Whole Animation).py` | 旋转顺序：Rotate Order - XZY (Whole Animation)。为整段旋转动画转换至入口指定的 Euler 顺序。；rotateOrder 和旋转关键帧 |
| `rotate_order.rotate_order_minus_yxz_whole_animation_1df6943a` | Rotate Order - YXZ (Whole Animation) | `Animo_Data/Animo_Tools_Editor/tools_library/Rotate Order/Rotate Order - YXZ (Whole Animation).py` | 旋转顺序：Rotate Order - YXZ (Whole Animation)。为整段旋转动画转换至入口指定的 Euler 顺序。；rotateOrder 和旋转关键帧 |
| `rotate_order.rotate_order_minus_yzx_whole_animation_4e07aa76` | Rotate Order - YZX (Whole Animation) | `Animo_Data/Animo_Tools_Editor/tools_library/Rotate Order/Rotate Order - YZX (Whole Animation).py` | 旋转顺序：Rotate Order - YZX (Whole Animation)。为整段旋转动画转换至入口指定的 Euler 顺序。；rotateOrder 和旋转关键帧 |
| `rotate_order.rotate_order_minus_zxy_whole_animation_15dee1aa` | Rotate Order - ZXY (Whole Animation) | `Animo_Data/Animo_Tools_Editor/tools_library/Rotate Order/Rotate Order - ZXY (Whole Animation).py` | 旋转顺序：Rotate Order - ZXY (Whole Animation)。为整段旋转动画转换至入口指定的 Euler 顺序。；rotateOrder 和旋转关键帧 |
| `rotate_order.rotate_order_minus_zyx_whole_animation_4da00e6f` | Rotate Order - ZYX (Whole Animation) | `Animo_Data/Animo_Tools_Editor/tools_library/Rotate Order/Rotate Order - ZYX (Whole Animation).py` | 旋转顺序：Rotate Order - ZYX (Whole Animation)。为整段旋转动画转换至入口指定的 Euler 顺序。；rotateOrder 和旋转关键帧 |

## 调用

```python
tool.run(dry_run=True, action="invoke", operation_id='rotate_order.rotate_order_minus_xyz_whole_animation_35ce1b1f')
# 阅读预检结果后再执行：
# tool.run(action="invoke", operation_id='rotate_order.rotate_order_minus_xyz_whole_animation_35ce1b1f')
```

所有入口的函数签名、顶层固定调用值及原索引别名见候选 `operations.json`；这些是静态证据，不表示运行兼容。
