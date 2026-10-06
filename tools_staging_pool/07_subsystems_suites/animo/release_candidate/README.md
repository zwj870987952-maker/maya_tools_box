# Animo V10.6.0 待人工检验候选

状态：`prepared_unverified`。已完成本机整理、统一协议封装及离线检查，**没有进行真实 Maya 检验，也没有转正**。

- [功能目录：55 类、553 个入口](../../../../docs/tools/animo/INDEX.md)
- [统一 API 与影响说明](../../../../docs/tools/animo.md)
- [代码分析](../../../../docs/tools/animo_code_review.md)
- [人工检验步骤](acceptance.md) / [553 项逐项记录](acceptance.json)
- [离线验证证据](verification.json) / [两处本机生命周期调整](patches.json)
- [OpenAI Schema](schemas/openai_tool.json) / [MCP Schema](schemas/mcp_tool.json)

## 在 Maya 中打开候选面板

在 Maya 2022–2026 的 Script Editor **Python** 页执行：

```python
import runpy
candidate = runpy.run_path(
    r"E:/GitHub/maya_tools_box/tools_staging_pool/07_subsystems_suites/animo/release_candidate/launch_candidate.py",
    run_name="animo_candidate_loader",
)
tool = candidate["load_tool"]()
tool.show_ui()
```

首先使用“安装运行副本”，再使用“打开原生工具栏”或选择入口执行。安装仅复制到 Maya 用户全局 `scripts/Animo_Data`，不调用原覆盖安装器、不创建 Shelf、不改启动文件。**已有 `Animo_Data` 时会拒绝安装；先自行备份并移开旧目录，再安装候选。** 未执行该按钮前不会向 Maya 安装供应方代码。本次整理没有点击安装或启动原工具。

候选面板可搜索入口、查看描述与路径、执行 Dry-Run、运行选定入口。预检只检查固定入口、版本、运行代码完整性、显式节点及 Undo 状态；原生工具需要的 Rig、层、摄像机、选帧条件仍需在具体 UI/脚本中检查。API 返回分派成功不能替代观察实际结果。

## API 示例

```python
print(tool.run(action="inspect").to_dict())
print(tool.run(action="catalog", query="镜像", limit=20).to_dict())
print(tool.run(dry_run=True, action="install_runtime").to_dict())

# 安装后检查入口；只读预检，不打开原工具：
print(tool.run(dry_run=True, action="invoke", operation_id="suite.tweenify").to_dict())
# 手动执行时取消下一行注释：
# print(tool.run(action="invoke", operation_id="suite.tweenify").to_dict())
```

默认 `load_tool()` 不注册。若要在本次 Maya 会话中用项目 API 调用，可显式执行 `tool = candidate["load_tool"](register_for_session=True)`，之后通过 `maya_toolkit.execute_tool("animo", {...}, dry_run=True)` 预检。此操作不会修改正式注册文件；统一面板已打开时需刷新/重新打开。人工检验通过前仍从本候选启动器加载。

## 文件与可复现流程

`maya_toolkit/tools/animo/` 是候选适配器；`native/Animo_Data/` 保留全套本机资源。上游 `../upstream/` 不改动，候选只调整启动配置自动调用与窗口清理范围，不重写算法。

在项目根目录，用 Python 3.12 运行：

```text
python scripts/prepare_animo_staging.py
python scripts/verify_animo_staging.py
python scripts/sync_obsidian_knowledge.py
```

构建器拒绝覆盖已有不同内容的候选源码。验证器不覆盖已有人工验收记录。上游包、原始/候选供应方源码及素材通过项目 `.gitignore` 保留在本机；适配器、入口索引、Schema 和说明可随项目管理。源码可读但许可受限，不计入原有开源工具数量；本次没有上传、分发或提交供应方文件。
