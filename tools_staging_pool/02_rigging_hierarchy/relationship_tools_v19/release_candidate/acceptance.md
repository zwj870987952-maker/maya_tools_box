# Relationship Tools v19 真实 Maya 验收

not_run；隔离Maya2025不等于完整真实GUI/生产rig验收。

1. 备份场景中通过launch_candidate.py show_ui()打开完整原主界面，所有折叠、TR/Bake/Step/World Coords/Layer、One/More/Align按钮与JSON按钮可用，Script Editor无Fatal；无自动开窗/共享temp文件。
2. dry_run前后scene/选择/时间/Undo/cache/文件不变。Mark子对象后选父，移动父→One Step子对象按相对关系匹配；Mark Foot为静态世界位置，Mark Ani记录指定[start,end)及Step端点。检查message源改名/namespace/重复短名、位置与真实键，一次Undo/Redo。
3. 备份含范围外键、scale/custom/禁用TR、子帧的场景执行More/Align。Bake+step只加选定TR采样键，原未采样/外部键保留；key-only无键时no-op，单帧Align不强制新键。真实timeline选择end不含、playback fallback、GUI成功advance一帧、失败不advance。
4. Copy World→源改名→勾World Coords→One/More，验证真实世界pos/rot、父子层级排序和收敛失败报告，时间/选择/evaluation/refresh原状态恢复。jointOrient、负缩放、旋转边界、已有动画层和复杂constraint等逐项记录保守拒绝或实测结果，勿将简单样例推广为任意rig兼容。
5. Layer仅选定TR进新override层，基础动画与其他属性不变，原preferred/selected恢复、一次Undo。Mark替换和Delete Marks只删除本候选ownership：放入外来同后缀物体、同名物体、owned下外来子对象/外部驱动应拒绝不误删。旧未owned标记需人工review，不能自动迁用。
6. 临时目录Export新JSON/Import回会话，检查UUID/数据/禁止覆盖/NaN/无效UUID/文件链接拒绝；scene Undo不删除外部JSON、不恢复Python复制缓存。记录Maya/Python版本和每项结果。

真正验收后保存passed=true、tool_id=relationship_tools_v19、candidate_sha256=最新promotion预览指纹、maya_version/accepted_by/date，使用plans/staging_run/promote_candidate.py --candidate 此目录 --acceptance 实测.json --apply晋级。此前不迁正式库/注册/Obsidian。
