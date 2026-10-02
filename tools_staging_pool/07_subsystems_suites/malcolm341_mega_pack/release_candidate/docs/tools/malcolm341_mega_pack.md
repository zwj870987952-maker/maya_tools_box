# Malcolm341 Mega Pack（完整待验候选）

来源为用户提供20230114付费MEL shelf及安装说明；49按钮、119原始回调位（含空菜单分隔项）、全部建模/UV/材质/导入导出/测量/偏好/HUD/Shelf功能与源许可文字完整保存。个人已提供资源整理，不推定公开再分发许可。未下载商业资源，图标使用原Maya内置图标。upstream精确原bytes+SHA；运行包不依赖待整理池路径。

所有原button/mi/双击与尺寸/颜色/注释在自有Shelf完整保留，只替换为固定id分派包装；native完整代码置于commands.json，SHA可核。原m341_命名统一MTB_m341_，隔离窗口、optionVar与脚本名，未将第三方算法未经实测改为core。部分原无前缀helper如killScriptJob保留，勿在同Maya会话混用原版与候选；实际兼容需测试。默认inspect列全部工具，不自动source/安装Shelf/写prefs/导出/创建节点。show_ui只创建MTB_Malcolm341_Candidate，不保存所有Shelf；同名foreign拒绝，close_ui仅删自有Shelf，不广泛关闭native子窗口或kill scriptJobs。

```python
from maya_toolkit.tools.malcolm341_mega_pack import Malcolm341MegaPackTool
t=Malcolm341MegaPackTool()
t.run() # native inventory
t.show_ui() # 真实Maya49按钮、右键菜单、双击
t.run(action='run_button',button_id='button_018',event='primary',confirm_native=True,dry_run=True)
t.run(action='run_button',button_id='button_018',event='primary',confirm_native=True)
```

Schema/validate/ToolResult只接收固定button/event，拒绝用户代码/eval字符串。scene写入UndoChunk；当前selection或显式selection全表解析/不存在/含wildcard/锁/reference拒绝；pivot进一步非空单个poly mesh/components及pivot轴锁预检，原native平均顶点中心算法保留，多mesh原只改首项的含糊行为改拒绝。dry不设选择、不编译MEL/安装UI/改场景/创建文件。实际batch仅已检的pivot主操作允许，其余native需真实GUI。部分原功能主动读取全场景、切换工具/单位/颜色管理、操作layers等，不能将selection参数误解为限制其原始处理范围。

原临时导入导出6/7改显式file_path（绝对ma/obj/fbx，与模式匹配）：输出已有parent/新文件、不再固定C盘temp覆盖；UI选文件取消不执行；导入已存在文件，MA不执行scriptNodes。file导出/FBXExport/uvSnapshot实际路径在native执行前拒绝已存在文件，原nativeforce标志不能绕过guard。直接API模式输出只预制source中完整原算法，path字符串经过MEL转义，不是任意命令注入。由于其余原窗口内部为原菜单程序，子窗口后续动作仍按原代码运行；已经对明确file exports/FBX/uvSnapshot/userSetup写入和uvGrab删除加guard，但不宣称覆盖未知插件、shell或延迟写入。

原Shelf/HUD userSetup功能保留，fopen a/w及uvGrab删除在原处备份同目录新.mtb_backup_UUID文件，精确bytes/SHA核验，128MiB上限；backup失败不继续写，已有文件导出拒绝覆盖。备份与文件写入、MEL proc定义、optionVar、插件autoload、HUD/scriptJob、prefs/save所有shelf/窗口状态/退出Maya不由scene Undo撤回。close/sPref/HUD/Shelf按钮的原广范围动作须显式confirm_native与UI默认取消确认；不要在未保存正式场景执行close，使用备份prefs/临时目录验收。子窗口内部原confirm/按钮保留，未假称所有原UI动作均完全可回滚。文件检查与第三方write之间存在竞争窗口，验收使用独占临时路径。

可组合：先用inspect找到按钮与事件，再准备选择/备份、dry预检，确认原功能影响后run；建模/UV输出可接既有几何工具，材质copy/paste原全局clipboard依赖同session；原file exporter产物可接外部DCC。但未真实验证任何跨工具组合，不等于依赖import即可自动组合。晋级完整code/native/resources/docs/tests及ALL_TOOL_CLASSES注册已准备，真实GUI满意后按promotion执行。

离线检查为只读inventory/坏参数/防覆盖/exact备份；隔离Maya检查MEL完整Shelf声明编译（未调用建Shelf）、guard临时文件、polyCube顶点pivot/dry/一次Undo/锁与多mesh拒绝。全49按钮/原子窗口、右键与双击/延迟scriptJob/导出插件/真实GUI/跨版本 not_run；这些检查不代表整套实际Maya验收。

| button_id | 原标签 | 可调用event |
| --- | --- | --- |
| button_001 | Help | primary |
| button_002 | tbExp | primary |
| button_003 | uvEdge | primary |
| button_004 | normR | primary, menu_002 |
| button_005 | obj | primary |
| button_006 | export | primary, menu_002, menu_003, menu_004, menu_005 |
| button_007 | import | primary, menu_002, menu_003, menu_004, menu_005 |
| button_008 | Xray | primary, menu_002 |
| button_009 | wire | primary, menu_002 |
| button_010 | imgRef | primary |
| button_011 | DEG | primary, menu_002 |
| button_012 | sPlugin | primary |
| button_013 | close | primary, menu_002 |
| button_014 | sPref | primary, menu_002 |
| button_015 | shelf | primary |
| button_016 | HUD | primary |
| button_017 | DM | primary |
| button_018 | pivot | primary, menu_002 |
| button_019 | reBuild | primary, menu_002 |
| button_020 | faceY | primary, menu_002 |
| button_021 | stSurf | primary, menu_002 |
| button_022 | stCent | primary, menu_002 |
| button_023 | vSnap | primary |
| button_024 | weldTC | primary, menu_002 |
| button_025 | weldTT | primary, menu_002 |
| button_026 | CPAS | primary |
| button_027 | lattice | primary, menu_002 |
| button_028 | miror | primary |
| button_029 | cmbine | primary, menu_002 |
| button_030 | extract | primary, menu_002 |
| button_031 | dupeF | primary, menu_002 |
| button_032 | dotPat | primary |
| button_033 | Half | primary, menu_002 |
| button_034 | findGB | primary, menu_002, menu_003 |
| button_035 | Name | primary |
| button_036 | copy | primary, double, menu_002 |
| button_037 | paste | primary, menu_002 |
| button_038 | replace | primary, menu_002 |
| button_039 | default | primary |
| button_040 | matID | primary, menu_002 |
| button_041 | graph | primary, menu_002 |
| button_042 | checker | primary |
| button_043 | uvGrab | primary, menu_001, menu_002, menu_003, menu_004, menu_005 |
| button_044 | Udim | primary, double |
| button_045 | LMap | primary |
| button_046 | unwrap | primary |
| button_047 | gridUV | primary, menu_002 |
| button_048 | recUV | primary, menu_002 |
| button_049 | uvMap | primary |
