# 物理辅助（Physics）

调用原工具的物理运动辅助入口。

- 状态：prepared_unverified，等待人工 Maya 直验。
- 输入：当前 Maya 选择、通道/Graph Editor 关键帧及时间区间；固定预设由下列脚本定义。
- 输出：候选 API 返回分派状态与操作后选择，不声称原算法已成功。
- 撤销：场景操作进入 Undo Chunk；外部文件、UI、插件、偏好不由 Maya Undo 撤回。

| operation ID | 原名称 | 执行源文件（相对 Animo_v10.6.0） | 具体用途/影响 |
| --- | --- | --- | --- |
| `physics.bounce_tool_02195a10` | Bounce Tool | `Animo_Data/Animo_Launcher/bounce_tool_launcher.py` | 物理辅助：Bounce Tool。调用原工具的物理运动辅助入口。；辅助节点或关键帧，具体输出待实测 |

## 调用

```python
tool.run(dry_run=True, action="invoke", operation_id='physics.bounce_tool_02195a10')
# 阅读预检结果后再执行：
# tool.run(action="invoke", operation_id='physics.bounce_tool_02195a10')
```

所有入口的函数签名、顶层固定调用值及原索引别名见候选 `operations.json`；这些是静态证据，不表示运行兼容。
