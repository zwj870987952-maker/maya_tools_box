# Malcolm341 全49工具真实Maya验收 not_run

1. 备份场景、prefs与userSetup，使用独占临时输出目录；load候选show_ui完整49按钮/内置图标、右键菜单/双击，重复开关仅自有Shelf，同名foreign拒绝，不source原版，不自动写prefs/windowPrefs/安装userSetup。
2. 逐行docs原49标签测试完整原子窗/slider/按钮响应、选择结果、建模/UV/材质/HUD/Shelf/导出；不是打开Shelf就整套通过。pivot单mesh顶点非空平均中心/锁/reference/多mesh/坏最后对象/dry零修改/一次Undo与Redo。原其他广范围清理/层/历史变化在备份场景验证Undo-Redo，部分全局状态如实记录不能Undo。
3. 临时ma/obj/fbx显式路径：导出只新文件、重复拒绝旧bytes保持、导入不执行MA scriptNodes、原插件autoload影响记录；OBJ/FBX/UV snapshot已存在路径拒绝。逐测native子窗口内有变量拼接的output、文件parent缺失/取消、Unicode与带引号路径，避免共用路径竞争。
4. userSetup fopen a/w和uvGrab删除前同目录独占备份存在且SHA一致；原file未写之前backup失败应拒绝。偏好/HUD/脚本job/延迟函数关闭清理按原功能确认，备份偏好手动恢复，不以scene Undo撤回文件。close只在已保存场景测试（原早Maya硬退出保留必须了解影响）；不自动删除windowPrefs、不执行安装说明中的系统路径删除。
5. 全体源license文字/资源/hash及无前缀helper冲突，Maya2017/2018旧版本及Maya2025逐测。candidate_sha256/maya_version/accepted_by/date/passed=true之后执行预制晋级；正式库当前未改。
