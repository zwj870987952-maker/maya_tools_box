# TB Anim Tools Maya 人工验收（not_run）

1. 在备用 Maya 用户配置下备份 prefs/modules/hotkeys，使用空备份场景；不可在生产配置首次启用。
2. 加载 `launch_candidate.py` 的 `load_tool()`，调用默认 inspect 和 install_files 的 dry_run，确认节点、关键帧、selection、optionVars、用户文件不变。
3. `tool.show_ui()` 检查圆角/拖动/Escape、路径选择和三个独立按钮，检查 Qt6 Script Editor。选择临时新目录安装完整文件，四个 GIF 和全部源码资源可找到；原有目录再次安装应失败且原件不变。
4. 在测试用户配置创建/选择 modules 目录，确认备份后只注册新 tbAnimTools.mod；已有同名模块必须报错，tbUpdateType=2，用户 userSetup 不被覆盖。退出恢复备份时检查文件操作不可 Undo。
5. 明确确认影响后在当前尚未载入 TB 的 Maya 启动原版套件；模块/路径必须匹配。等延迟任务完成，检查菜单、热键/运行时命令、工具选项、脚本回调、插件加载和 Script Editor；接口成功只表示启动请求。已加载冲突模块应提示重启。
6. 再启动备用 Maya 确认 userSetup/启动回调正常、自动网络更新没有触发；依次按四个帮助 GIF 检查播放切换、平滑拖时间轴、向前/后跳帧，再按上游菜单检查其余可用工具、撤销和场景影响。付费 proApps 若缺许可应正常提示，禁止绕过。
7. 若任何窗口、版本插件或工具失败，记录 Maya/Qt、依赖和 traceback，修复候选后复验；当前不能转正。全部满足后使用 promotion.json 预制动作和 promote_candidate.py preview/apply；正式库此前不改变。
