# TB Anim Tools 安装与启动候选

本单元原始内容只有 Tom Bailey 的安装器和四个帮助 GIF，主工具从 GitHub 的 main 分支下载。候选保留全部原件，补齐完整上游 ZIP（286 个目录/文件条目，2,759,177 bytes），固定提交 `eb8ede026c61f3cf5e38bafbc709d3bbed4d90c1`，SHA256 `290cc3ff67d81347037b3b6d011547b76bd2bdf158e5c27c93c3f74b2a2758d9`。来源为 https://github.com/tb-animator/tbAnimTools/commit/eb8ede026c61f3cf5e38bafbc709d3bbed4d90c1 。套件全部 Python、插件脚本、Icons、appData、proApps、样式和许可证在 ZIP 内；没有删减功能、模拟套件 API 或解锁付费扩展。

## 入口与参数

`TBAnimToolsTool.run(dry_run=False, action='inspect', destination=..., module_dir=..., acknowledge_external_effects=False)` 返回 ToolResult；tool_id=`tb_anim_tools`。默认 `inspect` 仅检查包内 ZIP 哈希、安全路径、完整资源和逐文件哈希，不读取用户安装、不联网、不导入上游。`install_files` 要求 Windows 下明确绝对新目录，父目录已存在；现有目录即使空也拒绝覆盖。逐文件完整校验后临时同级目录解包，Windows rename 发布，失败只清除自己的临时目录。生成独立 `.maya-toolkit-tb-install.json`，保留 upstream appData/tbVersion.json 原件。

`register_module` 要求由本候选产生且所有源资源哈希一致的安装，明确确认外部影响，目标 module_dir 已存在（默认 Maya userAppDir/modules），以独占新建写入 `tbAnimTools.mod`，设置持久 optionVar `tbUpdateType=2` 禁用自动上游更新。仅注册，不导入套件；不改用户 userSetup、不覆盖已有模块或热键文件。自定义 module_dir 需自行配置 MAYA_MODULE_PATH。

`launch_native` 仅真实交互 Maya，必须先在默认 modules 目录注册本候选的精确模块文件；拒绝已加载的 TB/apps 同名模块，拒绝非本目录解析出来的 installer，需要重启清除冲突。显式启动完整原版 `tbtoolsInstaller.installer().install()`，上游继续设置 sys.path、调用原版 module_startup，并安排延迟菜单/工具载入。返回仅说明请求了原版启动，不能证明延迟任务或每项套件工具通过验收。没有自动化测试执行此启动。

输入 `destination` 不能是相对路径、包含点段、换行、引号或 junction/symlink/reparse 路径。ZIP 拒绝越界、绝对路径、反斜杠、Windows 设备名/ADS/尾点空格、大小写重复、文件目录冲突、链接、特殊/加密成员以及体积/膨胀超限。安装是文件操作，继承框架 UndoChunk 不会使文件写入可撤销。API 的 validate/dry_run 完全只读，不能为了测试去创建 modules。

## UI 与兼容

旧安装器全部 11 个类方法、样式、圆角绘制、拖动/Escape、路径选择工作流保留并记录在 catalog.json。候选修复 Python 3.12 distutils、缺失 PyMel、Qt6 导入、默认父窗口过早求值、错误 FocusReason 窗口标志、QColor 与 globalPosition；构造只允许真实 Maya。原 Install 自动下载/启用改为三步显式按钮；不再关闭安装界面或直接启用套件。createVersionFile 改为确认独立精确提交收据，不写当前时间冒充上游版本。GUI、旧 Qt、不同 Maya 版本仍 not_run。

上游完整套件仍原样提供，其内部插件、可选 proApps 和 Maya 版本依赖由真实验收确认。候选安装器不要求 PyMel；这不是整个第三方套件不存在外部依赖的承诺。禁止在 mayapy 中创建窗口或运行套件原版启动，不能以离线安装通过宣称全套动画功能通过。

## 影响与恢复

安装/模块文件、optionVars、Python imports/sys.path、原版延迟启动、运行时命令/菜单/插件/热键的影响不受 Maya Undo 保护，也不承诺失败原子回滚。激活前备份 Maya 用户目录。卸载先退出 Maya，核实模块属于本候选再手工移走模块文件和候选新安装目录，按备份恢复偏好和 `tbUpdateType` 原值；不提供一键删除用户目录。注册原子创建避免覆盖，但后续原版 Windows module_maker 可能重写同名自有模块；后续启动后资源/模块发生变化可能无法再次通过初始哈希预检，使用完整备份恢复或新目录安装，不能强行跳过预检。

## 来源与组合

原始安装器头为 LGPL v3-or-later，固定上游仓库 LICENSE 内容为 GPL v3。原件、版权和全部 LICENSE 均随包保留；不重新给第三方组件指定许可证，分发时须逐组件核对。ui.py 显著标注 2026-10-01 修改和原作者，原 notices 在 upstream/tbAnimToolsInstaller.py.original。本候选仅作为可独立晋级的安装/启动适配器注册面板；第三方套件自身菜单/热键仍由原版负责。与 core 无重复业务算法，不往 core 下沉第三方实现，不承诺与其他动画工具经过组合验收。

晋级清单含完整 ZIP、帮助、来源/哈希、UI、Schema、文档与 tests；通过真实 Maya 后运行计划目录的晋级脚本。当前全部留在待整理池。
