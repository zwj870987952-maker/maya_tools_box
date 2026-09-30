# 可晋级候选包

此包镜像未来正式目录，尚未转正。原始入口/说明完整归档于运行包 upstream，业务算法/原生 UI/框架适配拆开，资源不依赖待整理池临时路径。launch_candidate.py 仅供本阶段加载候选，不写正式注册表。

真人测试按 acceptance.md，详细输入、范围与影响见 docs/tools/anim_layer_bookmark_trimmer.md。promotion.json 列出全部未来目标，晋级脚本预览只读；须用对应包指纹的真人验收记录才能申请写入正式库。

两个 tests 分别服务普通 Python 离线检查与专用 mayapy 隔离检查。后者会创建新场景，必须经 plans/staging_run/run_mayapy_check.py 启动，不能在生产 Maya 会话运行。
