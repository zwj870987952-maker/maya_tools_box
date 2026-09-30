# 可晋级候选包

完整运行代码、Schema、原生 UI、MEL 启动桥、源文件存档、说明、tests 与晋级资料齐备；当前仍在待整理池，未注册进正式库。资源不依赖待整理池临时路径。

launch_candidate.py 在真实 Maya 用于加载候选。先读 acceptance.md 和 docs/tools/anim_layer_key_runner.md，再用备份场景验收。预检只查询调度帧，不能判断任意脚本的副作用；正常进程权限执行的命令由用户输入决定。

tests/test_anim_layer_key_runner_maya.py 会创建新 scene，必须通过 plans/staging_run/run_mayapy_check.py 使用隔离 mayapy，不在生产 Maya 会话执行。原存档 MEL 会 source 后自动执行，只留作溯源；标准入口为候选 Python 启动或转正后的 launch_ui.mel 显式过程。
