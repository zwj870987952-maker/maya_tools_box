# 滑块弹出面板（Tweenify (Sliders Quick Pop Up)）

打开包含滑块的轻量交互界面。

- 状态：prepared_unverified，等待人工 Maya 直验。
- 输入：当前 Maya 选择、通道/Graph Editor 关键帧及时间区间；固定预设由下列脚本定义。
- 输出：候选 API 返回分派状态与操作后选择，不声称原算法已成功。
- 撤销：场景操作进入 Undo Chunk；外部文件、UI、插件、偏好不由 Maya Undo 撤回。

| operation ID | 原名称 | 执行源文件（相对 Animo_v10.6.0） | 具体用途/影响 |
| --- | --- | --- | --- |
| `tweenify_sliders_quick_pop_up.tweenify_quick_pop_up_e170ef1b` | Tweenify Quick Pop Up | `Animo_Data/Animo_Launcher/tweenify_launcher.py` | 滑块弹出面板：Tweenify Quick Pop Up。打开包含滑块的轻量交互界面。；UI 及使用滑块时的曲线 |

## 调用

```python
tool.run(dry_run=True, action="invoke", operation_id='tweenify_sliders_quick_pop_up.tweenify_quick_pop_up_e170ef1b')
# 阅读预检结果后再执行：
# tool.run(action="invoke", operation_id='tweenify_sliders_quick_pop_up.tweenify_quick_pop_up_e170ef1b')
```

所有入口的函数签名、顶层固定调用值及原索引别名见候选 `operations.json`；这些是静态证据，不表示运行兼容。
