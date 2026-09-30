# 完整第三方套件候选

原 6 文件不改写、重编码或移除通知；完整/NoUI 全部 global 签名、原 UI/业务和资源均保留。外层提供资源校验、inventory/load/invoke/open_ui、Schema/ToolResult、场景 Undo、导出路径碰撞保护与加载网关。

先读 docs/tools/anim_layer_v4_0.md 与 acceptance.md；source full 会替换大量进程 MEL 定义并重建原编辑器，这些不由场景 Undo 撤回。原界面回调不自动进入新增框架。

目前整套 prepared_unverified：普通 Python/NoUI 部分隔离检查通过，完整编辑器/原菜单业务仍待真实 GUI。请勿将此包登记为已 Maya 实测或公开再分发授权。launch_candidate.py 只打开外层网关，不自动执行原安装器。
