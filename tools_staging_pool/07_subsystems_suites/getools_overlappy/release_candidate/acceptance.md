# 真实Maya整套验收 not_run

1. 备份场景与动画，打开完整候选窗，7模块中文布局/全部slider/menu/相对图标/关闭重开/独立正式原GETools窗口互不关闭；启动不自动改全局CachedPlayback/HelpPopup，不下载资源/安装Shelf，原候选包/原脚本bytes不改。
2. COM create/activate/加权targets（同权两点应中点）/不同权重/投影x-y-z/缓存bake；borrowed COM删除拒绝、foreign MTB_ovlpGroup拒绝，不因名称碰撞删用户节点，锁/reference/不存在目标/坏最后对象预检拒绝。dry nodes/选择/dirty/Undo/文件无变化。真实原projection命令和引用rig需实测。
3. 使用非reference简单动画测试point/aim/combo/nucleus/particle参数/非零aim-upoffset、setup/当前bake/层输出/循环边界/删除setup；20/30/60 FPS结果需各自检查。确认bake才替换keys/layers；出错后选择/currentTime/range/refresh恢复，Undo/Redo关键帧与节点/层恢复与solver缓存差异实记。不在正式rig上试原删除全部层/骨骼/实验功能。
4. 完整Tools locator/bake/Animation/Timeline、Rigging blendshape/curve/skin、MotionTrail/Experimental、Shelf原菜单逐项检查：源filename与正式完整import可用、不会依赖池路径。文件IO/导出/Shelf偏好不可由scene Undo回滚，手动保存/备份再测，原广范围功能结果实记，不笼统宣布全部实测。
5. 预设literal读取不exec、不污染File.globals，非法/malformed拒绝；userAppDir/MTB_GETools_PRESETS手动创建，default只首次save，新filename另存，不覆盖旧文件；dry不mkdir。Reload/Quit默认Cancel，只在保存完备份后测试显式确认；验证跨Maya版本。candidate_sha256/maya_version/accepted_by/date/passed=true后执行预制晋级。
