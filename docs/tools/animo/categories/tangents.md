# 切线（Tangents）

按当前帧或全部范围设置 Auto、Linear、Stepped 等切线。

- 状态：prepared_unverified，等待人工 Maya 直验。
- 输入：当前 Maya 选择、通道/Graph Editor 关键帧及时间区间；固定预设由下列脚本定义。
- 输出：候选 API 返回分派状态与操作后选择，不声称原算法已成功。
- 撤销：场景操作进入 Undo Chunk；外部文件、UI、插件、偏好不由 Maya Undo 撤回。

| operation ID | 原名称 | 执行源文件（相对 Animo_v10.6.0） | 具体用途/影响 |
| --- | --- | --- | --- |
| `tangents.auto_tangent_all_keys_3c98327a` | Auto Tangent All Keys | `Animo_Data/Animo_Keys_Tangent/auto_tangent_all.py` | 切线：Auto Tangent All Keys。按当前帧或全部范围设置 Auto、Linear、Stepped 等切线。；关键帧切线 |
| `tangents.auto_tangent_selected_926fd06f` | Auto Tangent Selected | `Animo_Data/Animo_Keys_Tangent/auto_tangent_current.py` | 切线：Auto Tangent Selected。按当前帧或全部范围设置 Auto、Linear、Stepped 等切线。；关键帧切线 |
| `tangents.auto_tangent_set_default_ce14f2a0` | Auto Tangent Set Default | `Animo_Data/Animo_Keys_Tangent/auto_tangent_global.py` | 切线：Auto Tangent Set Default。按当前帧或全部范围设置 Auto、Linear、Stepped 等切线。；关键帧切线 |
| `tangents.linear_tangent_all_keys_60909626` | Linear Tangent All Keys | `Animo_Data/Animo_Keys_Tangent/linear_tangent_all.py` | 切线：Linear Tangent All Keys。按当前帧或全部范围设置 Auto、Linear、Stepped 等切线。；关键帧切线 |
| `tangents.linear_tangent_selected_35e5e278` | Linear Tangent Selected | `Animo_Data/Animo_Keys_Tangent/linear_tangent_current.py` | 切线：Linear Tangent Selected。按当前帧或全部范围设置 Auto、Linear、Stepped 等切线。；关键帧切线 |
| `tangents.linear_tangent_set_default_9bb2ee61` | Linear Tangent Set Default | `Animo_Data/Animo_Keys_Tangent/linear_tangent_global.py` | 切线：Linear Tangent Set Default。按当前帧或全部范围设置 Auto、Linear、Stepped 等切线。；关键帧切线 |
| `tangents.step_tangent_all_keys_e0782758` | Step Tangent All Keys | `Animo_Data/Animo_Keys_Tangent/step_tangent_all.py` | 切线：Step Tangent All Keys。按当前帧或全部范围设置 Auto、Linear、Stepped 等切线。；关键帧切线 |
| `tangents.step_tangent_selected_da6a106e` | Step Tangent Selected | `Animo_Data/Animo_Keys_Tangent/step_tangent_current.py` | 切线：Step Tangent Selected。按当前帧或全部范围设置 Auto、Linear、Stepped 等切线。；关键帧切线 |
| `tangents.step_tangent_set_default_19e15e1d` | Step Tangent Set Default | `Animo_Data/Animo_Keys_Tangent/step_tangent_global.py` | 切线：Step Tangent Set Default。按当前帧或全部范围设置 Auto、Linear、Stepped 等切线。；关键帧切线 |

## 调用

```python
tool.run(dry_run=True, action="invoke", operation_id='tangents.auto_tangent_all_keys_3c98327a')
# 阅读预检结果后再执行：
# tool.run(action="invoke", operation_id='tangents.auto_tangent_all_keys_3c98327a')
```

所有入口的函数签名、顶层固定调用值及原索引别名见候选 `operations.json`；这些是静态证据，不表示运行兼容。
