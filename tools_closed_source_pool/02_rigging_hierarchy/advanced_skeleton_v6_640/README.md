# AdvancedSkeleton 6.640 本机备用副本

2026-10-15 从本机 `E:/TOOLS/adv_rig/AdvancedSkeleton.6.640/` 完整复制，逐文件 SHA-256 比对一致：585个文件，446143890字节（包含隐藏文件）。未修改原版 MEL。完整清单见 `installation_manifest.json`。

`vendor/` 已排除 Git。其 EULA、安装脚本、原生资源一并保留；不上传、不重新分发。旧 `advanced_skeleton_v5_74` 保留为历史资料，不作为新动画 API 的默认运行来源。

用户后续指定：**ADV 调用默认寻找本机最新安装**。因此此副本只作本地备用；共享发现器 `maya_toolkit.core.advanced_skeleton` 优先选择外部安装版本，API 可用 `source_path` 明确指定来源。没有安装时，需要安装 ADV 或提供搜索位置；Git 克隆本身不包含运行内核。
