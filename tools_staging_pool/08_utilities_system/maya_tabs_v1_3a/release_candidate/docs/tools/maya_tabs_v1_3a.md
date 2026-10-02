# Maya Tabs 1.3a 完整候选

27原文件精确SHA归档，完整混淆源算法（AST排版，未拆掉业务分支）/Tab/Toolbar/tooltip动画/active选项/autosave-on-switch/clear/delete/open-folder/session JSON/PNG viewport thumbnails/完整cmds主题编辑器与19主题/icon/logo/安装图/原INI样例。原PyMel versions唯一用途改cmds.about版本查询；Qt5/6 facade/shiboken/QAction/python3 imagebuffer/size兼容。Base/Schema/API/read-write settings/session/theme/主题UI与未来注册面板预制，默认inspect/validate无native/Qt、授权读取或scene/file写入。

保留原chkSrl/guiSerial/install授权逻辑和2014-2023版本allowlist，无序列号生成/跳过授权/把新Maya版本视为原授权兼容。显式独立state目录可放用户已有合法serial.cfg/mayatabs_51x56.config；修复原undefined m2mSerialFile等别名，仅显式启动读取，原许可判定仍由原函数处理。缺授权或不在原版本列表时show明确未创建toolbar，保留vendor activation UI而不能登记成功。独立Qt preview只构造无scene demo，不执行install/license gate，不属于有授权生产可用证据。

原HOME固定路径改自包含resources、独立state中的Maya-Tabs.ini；新目录创建8个空tab，不自动导入原INI用户场景/缩略图。JSON32MiB/256tabs/strictbool/完整style/hexRGB/size/base64PNG/引用索引/duplicatekey全量预检后写；scene fname仅绝对ma/mb。每次已有设置/会话/主题覆盖先精确backup再atomic，包内资源只读，原重复settings overwrite移除。native open和QtFileDialog私有代理仅明确Save路径/自有配置写入，不全球patch；原授权文件只用户原激活成功才写自己的state且先backup。剪贴板改Qt clipboard，不shell拼echo。

原slot打开/clear强制file新建可能在当前slot缺失时丢未保存scene，cmds私有proxy补全modified确认Save/Discard/Cancel；取消不open/new，所有现存scene保存前精确磁盘backup，后续save/scene切换不可Maya Undo。原autosave指切换前保存该slot，不是定时autosave。clear/delete/session/theme只真实用户按钮执行，原SceneOpened/Saved/New回调用owned IDs和generation保护Qt deferred，close停止own timer/tooltip/toolbar与native窗口，foreign同名/指针变拒绝删，不注册startup/loadPlugin或改Maya.env。生产API干净模块不依赖旧staging路径。

原API2 viewport pointer路径需跨版本真实验收；修复buffer原少4通道尺寸并保留像素copy。完整offline19themes/session备份/坏末项不覆盖、独立Qt8→9tab/PNG/close后deferred不执行/future布局；真实Maya授权/版本/UI主题编辑/场景SaveDiscardCancel/viewport/真实callbacks not_run，prepared_unverified。生产scene切换只临时备份scene验收，静态依赖不证明组合已通过。
