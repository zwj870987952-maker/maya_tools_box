# KS SaveTimer 真实GUI验收 not_run

1. 新Maya会话选独立state目录，中英文各新会话，完整浮动/嵌statusLine计时、pause/mute/reset/idle/颜色阈值/flash/保存动画/Options/History/About。它只提醒保存，不能记成自动保存功能。
2. 保存临时scene触发自有kAfterSave，打开/新建归零，分钟/idle扣减不负，unsaved不写history。同目录v001/v002文件与不同项目同basename核对原历史汇总行为，不满意时在candidate修复后再验收。
3. 配置/历史只写独立state两个文件；已有每次先精确backup，坏末项不覆盖；旧HOME/KS_TIMETRACKER/原包与测试scene不变。native历史删除确认后备份，数据保存不可Maya Undo。
4. close/X/remove只停止own timer/animation/MSceneMessage/QFileSystemWatcher；reopen不叠监听，foreign scriptJob/callback/statusLine保留。真实Maya save events/Qt嵌入、Nuke唯一statusBar/save callbacks、desktop指定watch_file的新版本/原file替换需实测。中英文/跨版本每项记录accepted_by/date/maya_version/candidate_sha256/passed=true才promotion。
