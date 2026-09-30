# reset_pivot 真实 Maya 验收

状态：未运行 GUI 验收，尚未转正。只在副本场景或临时场景执行。离线报告不能代替此表。

## 候选启动

在 Maya Script Editor 的 Python 标签运行以下命令。此命令只加载本候选并打开其 UI，不将 reset_pivot 加入正式注册表。

```python
import os
candidate = r"E:\GitHub\maya_tools_box\tools_staging_pool\03_transforms_modeling\reset_pivot\release_candidate"
entry = os.path.join(candidate, "launch_candidate.py")
scope = {"__file__": entry, "__name__": "candidate_loader"}
with open(entry, "rb") as stream:
    exec(compile(stream.read(), entry, "exec"), scope)
tool = scope["load_tool"]()
tool.show_ui()
# 可直接调用：tool.run(dry_run=True, action="origin", target_nodes=["|group|cube"])
```

如果验收期间修改了候选，关闭其窗口并重新运行启动命令；load_tool 会重新加载候选模块。原始脚本仍在上一级，不要误把原脚本 UI 当成候选 UI 验收。

## 逐项检查

| 项目 | 操作 | 预期 | 实际 |
| --- | --- | --- | --- |
| UI | 打开、关闭、重复打开 | 窗口和 7 个按钮正常，无致命报错 | 待填 |
| 预检 | 勾选仅预检，逐个动作；记录节点属性、层级、选择与 Undo 状态 | 查询成功或明确拒绝，场景不变 | 待填 |
| 中心/原点/父轴心 | 对偏移轴心的网格分别执行；另测无父级目标 | centerPivots/世界原点/父旋转轴心符合原语义；无父级警告跳过 | 待填 |
| 重置轴/世界/完全重置 | 测普通物体、有子级物体、非均匀父缩放；观察几何与矩阵 | 结果符合文档；父级恢复；异常不遗失层级 | 待填 |
| 骨骼方向 | 先源后目标；另外用显式 source_joint/target_nodes | jointOrient 数值按原算法应用；不是任意世界姿态匹配 | 待填 |
| 多对象/重名 | 两个同名但不同父级对象用完整路径执行；测试重复目标 | 路径正确、不误改其他节点、重复目标只处理一次 | 待填 |
| 安全拒绝 | 空选择、非法参数、锁定/动画/驱动通道、引用、实例 | 清楚拒绝且场景不变 | 待填 |
| 撤销 | 每个动作执行一次 Undo；执行中断时检查层级与恢复 | 可撤销的场景修改恢复；无自动回滚承诺 | 待填 |
| 日志 | 查看 Script Editor | 无致命 traceback；警告和失败信息可理解 | 待填 |

记录 Maya/Python/Qt 版本、场景说明、日期、验收人和结果。任何项目失败先修复候选，再复验。

## 晋级

在仓库根目录运行预检（普通 Python 3）：

```text
python plans/staging_run/promote_candidate.py --candidate tools_staging_pool/03_transforms_modeling/reset_pivot/release_candidate
```

预检输出 candidate_sha256、目标路径和注册动作，不写正式文件。全部实测通过后，以当时预检指纹手工填写验收 JSON：

```json
{"tool_id":"reset_pivot","passed":true,"maya_version":"填实际版本","accepted_by":"填验收人","date":"填实际日期","candidate_sha256":"填预检输出"}
```

这里只是格式示例，不能把占位内容当成真实证据。保存用户实际记录后再执行：

```text
python plans/staging_run/promote_candidate.py --candidate tools_staging_pool/03_transforms_modeling/reset_pivot/release_candidate --acceptance <实际验收记录路径> --apply
```

晋级复制完整运行代码、文档和测试；合并当前正式注册表的导入、ALL_TOOL_CLASSES、公开导出。原始脚本和候选保留。已有目标文件或候选指纹变化时拒绝覆盖。晋级是文件写入，不能用 Maya Undo 撤回，需用 Git 审核恢复。

晋级后重启 Maya 或重新加载正式模块，确认 `maya_toolkit.show_ui()` 中出现工具，正式 `execute_tool` 的预检与执行正常，再记录正式版本复验结果。转正后的 Obsidian 同步按当时项目规范执行，不在本轮候选整理阶段运行。
