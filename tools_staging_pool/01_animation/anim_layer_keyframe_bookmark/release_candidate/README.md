# 可晋级候选包

完整的层查询、四色板、原生 UI、generate/clear/inspect API、Schema、源文件归档、说明/tests 与晋级清单均在包内；尚未进入正式库或正式注册表。

通过 launch_candidate.py 在真实 Maya 加载候选，按 acceptance.md 使用备份场景验收；详细行为见 docs/tools/anim_layer_keyframe_bookmark.md。clear 和 clear_existing 会删除场景全部书签；API 默认 false，原 UI 默认勾选保持不变。

隔离 Maya tests 会创建新 scene，只经 plans/staging_run/run_mayapy_check.py 运行。预检不加载插件、不修改插件保存要求，启动 UI 会明确加载插件。生成时 writeRequires 属于无法由场景 Undo 保证恢复的插件设置。
