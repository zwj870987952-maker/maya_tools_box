# timeline_marker：时间轴颜色标记与注释候选

Robert Joosten Timeline Marker 2.0.2 完整适配；原版权 Copyright(C)2015、GPL-3.0-or-later 与 GPLv3 正文保留在包内 upstream/LICENSE。49 个原文件（含文档/动画示意、MEL安装器、userSetup）按字节归档；原Python文件用.py.original保存，不作为Python3执行。候选不运行安装器，也不修改shelf、userSetup、用户hotkeys。改动对照 timeline_marker_changes.diff。仅本地整理，没有发布或推送。

用途是给原生时间轴叠加整数帧的颜色/注释标记，右键菜单颜色选择、注释、添加/删除/清空以及Move With Time Control完整保留。不是动画书签插件，不改节点、关键帧或动画层。现有core/正式工具没有同类fileInfo标记服务；只复用BaseMayaTool/ToolResult/Undo，未修改正式core。

## API与输入

tool_id=timeline_marker，category=animation，version=2.0.2-candidate.1。action默认inspect；没有目标对象选择依赖。API不依赖GUI已安装，原命令add/remove/clear/set保留在native包并委派统一API（原版需要已打开GUI，这是明确变化）。Schema不代替validate。

| action | 参数 | 效果 |
| --- | --- | --- |
| inspect | 无 | 返回当前markers与count |
| add | frames必填，color默认[0,255,0]，comment默认空 | 批量添加，同帧覆盖颜色/注释 |
| remove | frames必填 | 删除指定帧，缺失帧忽略 |
| clear | 无 | 三列表设空，不碰其他fileInfo字段 |
| set | frames/colors/comments，默认三个空列表 | 全量替换，列表必须等长 |
| remap | old_range/new_range=[start,end] | 两个闭区间，源范围内标记映射到新范围 |
| open_ui/close_ui | 无 | 真实GUI安装/卸载本候选覆盖层与菜单 |
| hotkey | hotkey_action=add/remove/clear | 使用当前时间轴选区与候选菜单设置，不安装快捷键 |

帧是±1000000内整数、最多20000个唯一帧；颜色三个0..255整数；注释≤4096字符、无NUL；序列化整体≤4MB。未知参数、action不适用的参数、非整数/重复帧、失配数据均拒绝。API严格整数；GUI保留原timeControl范围int截断、左闭右开规则，子帧选区显示需人工核对。

remap保留原int向零截断，不是四舍五入；按源帧升序处理，映射碰撞时后面的源帧获胜，移动帧覆盖目标已有未移动标记。原逐条删除可能把稍后待移动的源标记删除后索引报错，现改为冻结完整源数据后一次计算/写入。单帧源须映射到单帧；old_range==new_range不写入。未承诺兼容其他工具私自扩展timelineMarkers结构。

## 数据/只读预检/影响

保留场景fileInfo键timelineMarkers及JSON三数组frames/colors/comments，兼容原版数据；Maya查询返回MEL转义串，完整解码引号、反斜杠、换行和Unicode。读取不写回，paint/update不保存。没有timelineMarkers键视为无标记；已有损坏JSON、数组缺项、额外字段、长度不一、多值/重复帧则拒绝数据操作，保留现场供备份后人工修复；GUI读取错误只警告，不偷偷清空原数据。

validate/dry_run检查参数、现有格式、输出总量、Undo状态与GUI/batch前提，不加载Qt/插件、不建节点、不改metadata、时间、选择、AutoKey或文件。正式执行前再次只读计算。dry返回before/after计划；inspect返回markers/count；写入返回markers/count/changed/plugin；GUI返回ui_open/action。异常为ToolResult.fail，详细错误进errors，warnings说明会话影响。

Maya2025隔离探针证实原fileInfo不入Undo，原undoChunk不能恢复。候选执行时私有加载undo_plugin.py的MPxCommand mtkTimelineMarkerData，保存精确原header值/字段缺失状态，redo写入新值，undo恢复原值或移除首次创建的字段。一次API/菜单批量修改由BaseMayaTool分组Undo；插件内部标记scene modified以便用户正常保存。撤销后场景modified标志仍可能为True。命令未成功进入Undo的modified写失败会恢复自己的metadata写入；命令成功后其他错误需用户Undo，不自动全场景回滚。

GUI/Qt布局、菜单、timeControl handler、API callback、插件加载属会话状态，不由场景Undo撤销；close_ui撤自己的菜单/回调，不删别人的action。保存并链式调用已有MEL press/release handler；卸载只在handler仍是本候选原值时恢复旧值，后来他人设置的handler保留。非字符串hook拒绝覆盖。新建/打开/Undo/Redo刷新只读显示；原版timelineMarker控件仍在时拒绝同时覆盖。插件因Undo记录持有命令而保持加载，不设置autoload、不在操作后卸载或清Undo；重启可释放，验收晋级路径切换应重启Maya以免同名命令来自旧路径被拒绝。不新增网络请求，不自动保存真实文件。

## 调用与组合

转正后示例（候选验收使用release_candidate/launch_candidate.py，不提前迁移）：

```python
import maya_toolkit
args = {"action": "add", "frames": [1, 12, 24], "color": [0, 255, 0], "comment": "contact"}
preview = maya_toolkit.execute_tool("timeline_marker", args, dry_run=True)
if preview.success:
    result = maya_toolkit.execute_tool("timeline_marker", args)
    print(result.to_dict())
```

与anim_layer_keyframe_bookmark的range书签属于不同存储模型：可先由调用者决定采样整数帧，再add相同注释用于浏览；不会自动互转。lock_to_world或keyframe_reduction操作完成后可标记检查帧；输入是调用者明确frames，不把本工具注释当曲线分析结果。上述为组合建议，尚未联合实测；本项隔离检查只验证本工具没有改变动画键。

## 实证与待验

普通Python验证全49原字节/26原类方法/13函数、Schema与lazy导入、模型碰撞/负数截断。Maya2025隔离standalone验证真实fileInfo读写与精确Undo/Redo、原格式、中文/引号/路径/换行、ma/mb临时场景保存重开、全部命令桥、dry/inspect不写、坏数据拒绝与失败Undo。回调所有权测试仅timeControl shim加真实API callback，**不是时间轴GUI通过**。未实例化Qt。

状态prepared_unverified：真实时间轴覆盖层、菜单、Qt6/Qt5 tooltip、选区拖动、缩放/高DPI、声音scrubbing、其他插件hook共存、新建/开场景与卸载/重开均待真人检查；其他Maya版本未验。完整acceptance.md与promotion.json已预制，正式库/注册表尚未改变。
