# KS SaveTimer 1.3 完整中英文候选

39原始文件SHA归档，完整中英文timerWidget/GUI/config/tracker/history/stat/about、Maya/Nuke/Desktop lib与runApp、README/EULA PDF保留。六兼容源自固定官方MIT六模块自包含，Qt5/6 facade/Signal/Property/shiboken、Python3/配置bool(False)与idle扣减不负数、Qt6旧QDesktopWidget/font enum确定兼容修复；旧six多metaclass QObject单例改显式单实例factory，功能与共享signal保留。Base/Schema/ToolResult默认inspect/validate纯，无Qt/回调/定时/配置写入；API show/close/start/pause/reset/set_time/read_history/set_option完整，未来layout/注册挂面板预制。

实际用途是保存间隔提醒/计时/idle detection/阈值颜色/flash/reset/save动画/选项/文件版本工时历史，不自动保存scene。一次host(maya/nuke/desktop)+language(zh/en)+data_root固定，不能热切或混foreign旧模块；独立现有目录中仅ksSaveTimer_config.ini和KSSaveTimer_timeTrackHistory.json写入，不用HOME、包内默认、旧KS_TIMETRACKER环境变量。既有数据严格全量校验；INI无插值/重复未知项/限定bool/颜色/时间；JSON32MiB/host/计时/version结构严格校验。覆盖和删除历史通过native保存都先exact backup再atomic；失败传播，外部写不可Maya Undo。旧版本按basename归档，跨项目相同basename可能归在同项，原行为保留且在直验中重点核对，不声称自动去冲突。

实际Maya宿主用自有MSceneMessage kAfterNew/Open/Save IDs；Nuke保留addOnScriptLoad/Close/Save并精确记录同callable用于remove；desktop只有明确watch_file才QFileSystemWatcher，不监听自有state目录，修复splitext原tuple不能endswith与signal参数。关闭只移本会话listener/timer/animations/dialog/widget；reopen重建单例避免旧widget信号closure，不杀foreign scriptJob或覆盖全局hook。Maya嵌入statusLine用独立MTB rootLayout，创建时MQt pointer记录/foreign同名替代保护，恢复setParent；Nuke statusbar唯一时可嵌入，自有widget移除不改原statusbar。完整旧runApp源作为兼容参考保留，框架session入口负责生命周期，主线程/真实host Qt要求不静默退desktop。

Maya scene是读取当前文件名和保存后通知，预检不创建回调/写scene，不需要scene Undo。本工具可与保存/版本管理工具手动衔接，不证明静态import即组合成功。离线typed数据/精确备份/foreign写拒绝、隔离Maya文件名与dry无Qt/listener、独立Qt中英文完整timer/options/history/about/保存signal计时持久化/关闭watcher/reopen；实际Maya GUI statusLine/真实save callback及Nuke GUI/原复杂历史/跨版本not_run。
