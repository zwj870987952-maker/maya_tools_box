# W Retarget Tool 1.0

用途：把源对象的动画运动以初始姿态偏移方式重定向到目标对象，支持完整原始 A/B/C/D 四组界面、Copy All、清空配对字段，以及按明确节点集合导出新的 FBX 文件。原作者 Walter Delgado，原始头部日期 2024-10-26/About 日期 2024-11-02；原始文件逐字节归档于 upstream/WretargetTool.py.original，SHA 在 catalog.json。没有独立许可文件，不推定或新增许可。候选不等于真实 Maya 验收。

## 原算法与兼容边界

完整保留原 CopyAnim 的五个辅助组、源/目标父层约束、multMatrix/decomposeMatrix 和逐帧九通道采样。源初始姿态作为偏移，目标从自己的初始姿态出发。例如源 tx 在帧 1/2/3 为 0/2/4，目标初始 tx=10，采样结果为 10/12/14。这不是直接把源 TRS 数值复制给目标。原建议源与目标起始姿态相近仍适用。

采样整数区间 **[start_frame, end_frame)**，结束帧不采样。九通道 tx/ty/tz/rx/ry/rz/sx/sy/sz 保留：原父约束代理通常 scale=1，不传播源缩放，使用时应理解目标缩放被键为代理值的影响。目标区间内已有键会被替换；区间外键保留。采样的 Euler 旋转、关节方向、旋转顺序、枢轴和不均匀父缩放需要真实绑定实测，不宣称通用骨架求解或无翻转。

原始 UI 全部 18 个类方法、帮助/关于函数和控件布局在 native_ui.py 留存；ui.py 将业务按钮覆盖为框架调用，修复无选择、文件夹取消、方法名被控件覆盖以及字符串短名问题。Delete Place Holders 按原始生效行为仅清空八个配对文本字段，不删除场景物体。没有外部资源缺项。

## 参数

| 参数 | 默认/范围 | 含义 |
| --- | --- | --- |
| action | copy / export；默认 copy | 重定向或显式导出 |
| pairs | copy 必填，1..100 项 | 每项 source/target 为唯一完整 transform 或 joint 名称；建议长 DAG 路径 |
| start_frame / end_frame | 0 / 20，整数，绝对值≤1000000 | 正区间，长度≤10000；end 不含 |
| exports | export 必填，1..100 项 | 每项 nodes 非空完整对象列表、path 绝对 .fbx 新文件路径 |
| up_axis | y / z，默认 y | FBX 向上轴 |
| ascii | false | ASCII 而非二进制 |
| fbx_version | FBX202000 / FBX201900 / FBX201800 | 原始三版本选项 |
| bake | true | FBX 烘焙；导出区间 start..end-1，step=1 |

copy 不接受 exports，export 不接受 pairs。目标必须独立、可写、未引用/未锁定且全部九通道可键；目标之间不允许父子关系，源不能是任何目标的后代或被用作目标。实例节点因原算法 matrix[0] 限制拒绝。支持目标通道已有简单 TA/TL/TU 时间曲线；共享曲线、时间扭曲、动画层、约束或其他驱动目标拒绝，不能强制断开生产驱动。源可只读引用。FBX 插件必须由用户显式加载；预检不加载插件。

## 调用与输出

候选通过本目录 launch_candidate.py 的 load_tool()/show_ui() 加载；晋级后使用正式统一入口：

```python
maya_toolkit.execute_tool('w_retarget_tool', {
    'pairs': [{'source': '|sourceRig|source', 'target': '|targetRig|target'}],
    'start_frame': 1, 'end_frame': 25,
}, dry_run=True)
```

BaseMayaTool 的 run 返回 ToolResult。validate 和 dry_run 只读取完整批次，返回规范节点、区间、sample_count、channels、算法/缩放说明或 exports/file_effect，不创建辅助节点、不写键、不改时间/选择/autokey/插件/FBX 选项或文件。execute 重检后执行；copy 结果包含 completed_pairs、temporary_nodes，export 包含 written_files。通过 to_openai_tool/to_mcp_tool 导出完整参数描述，框架统一 UndoChunk 与结果协议已复用；生产 core 不修改。

## 场景、文件与异常影响

copy 全批写入处于一个框架 UndoChunk，成功和异常时都清理 UUID 标识且确属本次创建的辅助组/约束/逐帧矩阵节点，恢复时间、选择和 autokey。清理检测外来子节点并拒绝删除它们，不按泛化名称清扫。目标写入异常不再被原脚本静默吞掉；框架本身不自动回滚，部分已写的键可通过一次 Maya Undo 撤回。若外部脚本把外来节点挂到辅助节点上，安全清理会报错而保留该组，需用户检查，不声称清理无条件成功。

export 要求已有输出父目录，拒绝既存文件、目录、符号链接/junction、Windows 保留名称/ADS 与重复输出。临时文件使用本次 UUID，完成后移动到新目标，异常仅清理自己创建的临时文件，不运行原脚本 force=True 覆盖。恢复全部改过的七个 FBX 选项和选择；导出文件及 FBX 设置不属于场景 Undo。多项导出中后项失败时，前项成功文件仍保留，用户应在独立临时目录检查。其他 FBX 全局选项沿用用户设置，生产导出内容要人工重导入验证。

界面 Export 根据目标 namespace 去重，查找 namespace:namespaceLeaf_geo 和 namespace:Jnts_grp，输出 namespace 替换冒号为下划线的 .fbx；无 namespace 或缺组会明确失败。API 可明确指定其他节点集合，无需命名约定。GUI 不自动安装、建 Shelf、改热键、启动脚本或保存用户偏好。

## 关联工具与验证

先使用已有重定向工具确定骨架配对，或 Root Motion Bake 提取根运动，再在独立目标上使用本工具；Velocity Calculator 可测量重定向后世界位移速度。以上是输入输出相容的操作建议，组合流程尚未在生产场景验收。

普通 Python 检查归档 SHA/完整声明与矩阵引擎、参数/新文件保护；隔离 Maya 2025 检查姿态偏移/区间/九通道、父路径/已有键、整批锁预检、共享/时间扭曲、注入写入失败清理/Undo、真正 FBX 临时导出及选项恢复。独立 GUI/复杂绑定/FBX 重导入/其他版本均 not_run。具体报告在 plans/staging_run，人工步骤见候选 acceptance.md。此候选只能在用户真实 Maya 验收通过后使用预制 promotion.json 晋级，不提前更改正式注册表。
