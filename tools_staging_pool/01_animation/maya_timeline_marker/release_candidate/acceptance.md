# Timeline Marker 真人验收

prepared_unverified；只在备份或新测试场景中验收。49原资源/26方法/13函数已保留，mayapy不代表GUI验收。

1. 重启真实Maya，先停止原版Timeline Marker。在Python Script Editor执行：

```python
import runpy
tool = runpy.run_path(r"E:\GitHub\maya_tools_box\tools_staging_pool\01_animation\maya_timeline_marker\release_candidate\launch_candidate.py")["load_tool"]()
print(tool.run(action="open_ui").to_dict())
```

2. 确认原生时间轴右键菜单包含颜色、注释、Add/Delete Selected/Delete All、Move With Time Control。设RGB与中文注释，对单帧/多帧添加；悬停tooltip正确，滚动缩放/高DPI和短播放范围没有报错或闪退。刚开界面/新建/打开场景/绘制不应新增空metadata或变更场景标记。
3. 对已有帧改色/注释，删选区、清空；每次一次Undo恢复全部标记，Redo也恢复，覆盖层立即刷新。动画键、选对象、时间及AutoKey保持；scene modified标志允许仍为True。
4. 开Move With Time Control拖动/压缩范围，验证1..3→2..4碰撞仍保留原a/b/c；压到单帧后源末帧获胜、目标旧标记被覆盖；负帧向零截断。关闭该选项时标记不跟随。单帧扩范围不移动；明确观察子帧选区截断。
5. 保存为临时ma/mb并重开，中文、双引号、反斜杠、换行数据正确。打开旧原版场景能读同一timelineMarkers字段；加载过程不写。损坏字段使用备份场景测试，操作应拒绝且不自动清空；恢复备份后继续。
6. 使用tool.run(action="hotkey", hotkey_action="add"/"remove"/"clear")验证当前选区与菜单设置；不产生用户hotkey安装。Script Editor没有Fatal Traceback。
7. 核对已有timeline press/release MEL handler继续执行，声音拖动正常；close_ui恢复原handler并删自己的菜单/回调，不影响其他插件。若其他插件在候选打开后改handler，关闭本候选须保留后来handler。关闭后再打开无重复菜单或浮动callback。
8. 核对inspect/dry_run不写场景、不加载插件，插件正式首次写入才加载；每次Undo正常。不要强制卸载存在Undo记录的插件，也不要让候选/转正路径同名插件在同一会话混用；晋级后重启。

记录真实Maya/Python/Qt版本、步骤结果与Script Editor错误；失败回候选修复。通过且用户确认后，才按promotion.json及plans/staging_run/promote_candidate.py预制映射晋级，注册ALL_TOOL_CLASSES并让统一面板列出animation领域。当前仅做晋级预览，未apply。
