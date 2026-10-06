# 关键帧颜色（Color Keys）

调整关键帧的显示标记。

- 状态：prepared_unverified，等待人工 Maya 直验。
- 输入：当前 Maya 选择、通道/Graph Editor 关键帧及时间区间；固定预设由下列脚本定义。
- 输出：候选 API 返回分派状态与操作后选择，不声称原算法已成功。
- 撤销：场景操作进入 Undo Chunk；外部文件、UI、插件、偏好不由 Maya Undo 撤回。

| operation ID | 原名称 | 执行源文件（相对 Animo_v10.6.0） | 具体用途/影响 |
| --- | --- | --- | --- |
| `color_keys.color_key_green_65d7307a` | Color Key Green | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Color Key Green.py` | 关键帧颜色：Color Key Green。调整关键帧的显示标记。；关键帧显示属性 |
| `color_keys.color_key_red_199b95ba` | Color Key Red | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Color Key Red.py` | 关键帧颜色：Color Key Red。调整关键帧的显示标记。；关键帧显示属性 |
| `color_keys.color_key_yellow_3dafe2ba` | Color Key Yellow | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Color Key Yellow.py` | 关键帧颜色：Color Key Yellow。调整关键帧的显示标记。；关键帧显示属性 |

## 调用

```python
tool.run(dry_run=True, action="invoke", operation_id='color_keys.color_key_green_65d7307a')
# 阅读预检结果后再执行：
# tool.run(action="invoke", operation_id='color_keys.color_key_green_65d7307a')
```

所有入口的函数签名、顶层固定调用值及原索引别名见候选 `operations.json`；这些是静态证据，不表示运行兼容。
