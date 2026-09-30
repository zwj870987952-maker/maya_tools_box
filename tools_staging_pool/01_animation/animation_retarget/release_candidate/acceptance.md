# 动画重定向真人验收

状态：GUI not_run，prepared_unverified。离线和隔离 mayapy 不能代替真实 Maya 图形界面。所有动作使用备份场景及新临时 JSON 文件，关闭原脚本窗口后打开候选。

```python
import runpy
candidate = runpy.run_path(r'E:\GitHub\maya_tools_box\tools_staging_pool\01_animation\animation_retarget\release_candidate\launch_candidate.py')
tool = candidate['load_tool']()
tool.show_ui()
```

1. 在实际 Maya 版本打开/关闭/重开窗口，验证 PySide2 或 PySide6、主窗口父级、颜色圆点、字体、右键位置和 UI 响应；观察 Script Editor 致命错误。
2. 建两个命名空间下的重复短名控制器，使用明确长路径配对；录入、拖动排序、文本编辑、删除、双击选择、清空、批量设模式。编辑文字仍重置到默认模式，保留原行为。
3. 在时间1、2.5、5给源 TRS 和自定义浮点/枚举/向量子通道打不同键，目标保持不同初值。只读预检前后比较节点、关键帧、选择、时间与 Undo 队列；应没有写入。
4. 对位默认 constraint，目标保持现有偏移并随源变化；检查三种约束与 network 记录，时间/选择恢复。一 Undo 撤回整次。重复对位受保护。用副本检测 joint、引用、锁定、已有约束和复杂绑定。
5. 将 rotate/other 设 numeric，translate=none，检查源帧并集和小数帧采样，未设 numeric 的通道没有复制；无源关键帧时不会造键。other 缺失/字符串应提示 skipped，不默认为成功复制。
6. 准备两对候选约束和一个其他工具的 Constraint_SelectionSet。仅选一对分别默认/智能烘焙，确认该目标曲线及偏移，其他配对和外部约束集合保持；一次 Undo 恢复。none 仍不限制 bake 对目标其他可烘焙通道的影响。
7. 重命名源、目标和候选约束，从信息节点读取配对，检查 UUID 追踪；删除原约束后创建同名外部约束应保持。重接约束输出后烘焙必须拒绝自动删除。
8. 用全部 none 模式记录初始姿态，包含逗号、冒号、引号字符串、向量、矩阵、TRS，修改后“应用位置信息”。检查源和目标恢复，锁定或被驱动属性提示 skipped；不要把 skipped 视为全恢复。测试旧 Rematch 信息读取和普通数值姿态，含分隔符旧字符串仅有限兼容。
9. 保存完整列表为新的临时 JSON，清空再加载，检查模式和排序；加载旧格式、UTF-8 BOM、无效字段/模式/缺失文件。已存在文件不可覆盖，保存 dry_run 不产生文件；Maya Undo 不删除 JSON 文件。
10. 查看 Script Editor、ToolResult warnings 和输出，确认核心按钮与实际动画结果满意。记录 Maya 版本、日期、验收人、逐步结果及当前候选哈希；发生问题先修改候选并重验。

真实验收通过后再创建记录（以下仅示例，不能把占位字段作为实测证据）：

```json
{"tool_id":"animation_retarget","passed":true,"maya_version":"实际版本","date":"实际日期","accepted_by":"验收人","candidate_sha256":"预览返回的当前候选哈希"}
```

先运行 `plans/staging_run/promote_candidate.py --candidate <候选绝对路径>` 获取只读预览；真人记录满足脚本契约后方可 --apply。原脚本不启动，候选无须再改业务代码即可晋级。工具代码、资源、说明、回归测试和注册同时放到正式目录，用户实测前不进行此动作。
