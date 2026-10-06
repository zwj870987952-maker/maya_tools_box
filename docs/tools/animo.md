# Animo V10.6.0 候选工具说明

工具 ID：`animo`。类型：第三方动画套件适配器。状态：`prepared_unverified`，仅入待整理库，真实 Maya 直验等待用户完成。继承 `BaseMayaTool`，默认没有正式注册或统一面板挂载。

候选包含 **55 类、553 个固定入口**：540 个库脚本（573 条显示记录去重）及 13 个完整套件入口。入口数含不同预设和 UI，不等于 553 种独立算法。逐项路径、功能、输入输出和操作影响见 [功能目录](animo/INDEX.md)，可检索结构位于 [operations.json](../../tools_staging_pool/07_subsystems_suites/animo/release_candidate/maya_toolkit/tools/animo/operations.json)。描述来自分类阅读和静态源码证据，具体参数/语义仍需 Maya 观察确认。

## 用途与适用条件

用于动画滑块、关键帧/切线/时间操作、镜像、临时空间/轴心、烘焙、姿态与动画传递、轨迹/路径、选择集和预览输出。支持范围按上游标注限定 Maya 2022–2026 GUI，PySide2/PySide6；当前已验证版本列表为空。调用业务入口需要先安装本候选运行副本和配置合适的 Maya 选择/选帧/时间区间，原生 UI 决定剩余选项。

候选复用项目 `UndoChunkContext`、Maya 主窗口与深色主题；原算法/资源随仓库同步，供应方算法仍保留原有结构，未迁移到 `core`。本次发布依据见 [作者授权确认](../../tools_staging_pool/07_subsystems_suites/animo/AUTHOR_PERMISSION.md)。静态比较与重点算法见 [代码审查](animo_code_review.md)。

## 启动与统一 API

```python
import runpy
candidate = runpy.run_path(
    r"E:/GitHub/maya_tools_box/tools_staging_pool/07_subsystems_suites/animo/release_candidate/launch_candidate.py",
    run_name="animo_candidate_loader",
)
tool = candidate["load_tool"]()
tool.show_ui()
print(tool.run(action="catalog", query="镜像", limit=20).to_dict())
```

| 参数 | 类型/默认值 | 范围与作用 |
| --- | --- | --- |
| `action` | string / `inspect` | `inspect`、`catalog`、`show_ui`、`install_runtime`、`invoke`、`launch_toolbar` |
| `operation_id` | string / 省略 | `invoke` 必需；553 个白名单 ID，拒绝任意代码或脚本路径 |
| `objects` | array[string] / 省略 | 仅 `invoke`，1–4096 个有序唯一节点名；拒绝组件/属性与歧义节点，省略时保持当前选择 |
| `query` | string / 空串 | `catalog` 搜索名称、ID、中文用途 |
| `operation_category` | string / 空串 | `catalog` 按原英文分类筛选 |
| `offset` | integer / 0 | 检索分页起点，非负 |
| `limit` | integer / 50 | 检索分页大小，1–200 |
| `dry_run` | bool / False | 继承的 `run()` 参数，仅执行只读预检 |

未知参数拒绝。检索参数用于 `catalog`；其他动作不会用它们改变原工具设置。API 保留原入口固定预设，未将原函数的所有参数转换成新的统一算法接口；新增入口应重新解析白名单及 Schema 并检验。

```python
# 在 Maya GUI 中安装前检查；正式安装仍需显式执行：
result = tool.run(dry_run=True, action="install_runtime")
print(result.to_dict())
# tool.run(action="install_runtime")

# 安装后预检选中的入口；替换为实际 Rig 节点路径：
result = tool.run(dry_run=True, action="invoke",
                  operation_id="suite.tweenify", objects=["|rig|ctrl"])
print(result.to_dict())
# tool.run(action="invoke", operation_id="suite.tweenify", objects=["|rig|ctrl"])
```

`tool.to_openai_tool()` / `tool.to_mcp_tool()` 导出真实框架 Schema，文件见 [OpenAI](../../tools_staging_pool/07_subsystems_suites/animo/release_candidate/schemas/openai_tool.json) / [MCP](../../tools_staging_pool/07_subsystems_suites/animo/release_candidate/schemas/mcp_tool.json)。如需会话调度，显式 `load_tool(register_for_session=True)` 后可调用 `maya_toolkit.execute_tool("animo", arguments, dry_run=True)`；未通过人工检验不持久注册到正式工具。

## 输出、操作影响与预检边界

统一返回 `ToolResult`，包含 `success`、`message`、`data`、`warnings`、`errors`、`tool_id`、`dry_run`、`execution_time`。检索返回完整入口元数据和分页总数；分派返回 `state=dispatched_unverified`、`native_business_success=None`、`maya_verified=False` 及选择变化。原生脚本可能提示取消、静默返回或延迟创建 UI，所以分派成功不表示算法或文件输出成功。

预检不 import 原工具、不修改选择/场景、不写文件。Maya 动作查询 GUI/版本/脚本目录，检查运行候选标记及全部 Python 哈希、显式节点唯一性、Undo 和短模块冲突；**未检查原生 Rig、约束、动画层、摄像机或关键帧等业务条件**。离线 `inspect`/`catalog` 无需 Maya。

场景写入使用继承的 Undo Chunk；嵌套原生 Undo、滑块预览与释放回调仍需实测。UI 延迟回调不在初始分派的 Chunk 内。安装复制、输出文件、插件、模块路径、Qt timer 和偏好设置不由 Maya Undo 撤回；失败不会自动回滚全部副作用。显式 `objects` 在执行时改选择并保留原工具最终选择。

安装在用户全局 `scripts/Animo_Data` 新建候选副本，逐文件校验素材，已有目录拒绝覆盖。主启动器取消两处导入时自动配置调用，窗口清理限定 Animo 前缀；原生 UI 主动配置仍能改变偏好/启动项。调整记录见 [patches.json](../../tools_staging_pool/07_subsystems_suites/animo/release_candidate/patches.json)。

常见错误：`MAYA_REQUIRED` / `GUI_REQUIRED`、`MAYA_VERSION_UNVERIFIED`、`RUNTIME_EXISTS` / `RUNTIME_MISSING`、`RUNTIME_CODE_MISMATCH`、`MODULE_COLLISION`、`AMBIGUOUS_OR_MISSING_OBJECT`、`UNKNOWN_OPERATION`、`UNDO_DISABLED`、`NATIVE_ABORTED`。错误存于 `ToolResult.errors`，未自动卸载其他模块、覆盖旧文件或重试场景写入。

## 检验与关联工具

[离线证据](../../tools_staging_pool/07_subsystems_suites/animo/release_candidate/verification.json) 记录源码 AST、完整资源哈希、两处差异、索引/Schema 及 20 项适配器边界测试。**尚未运行真实 Maya、供应方算法或 Qt 界面，未测量性能。** 按 [人工验收](../../tools_staging_pool/07_subsystems_suites/animo/release_candidate/acceptance.md) 检查 UI、按钮/滑块、选择/操作、Undo 和 Script Editor。

功能与 `animbot_copy`、`the_key_machine`、`fd_multi_space`、`brs_loc_transfer`、`copy_animation` 有概念重叠；正式 `euler_winding` 可用于旋转曲线问题的独立处理。上述关联均未做实际组合检验，不构成已验证流程。后续应从已通过的入口记录中提炼组合的输入、输出、层/约束和单位条件。

## 来源与演进记录

2026-10-05：从用户指定官方包整理 V10.6.0；原始 ZIP 与解压目录完整保留；创建自有候选适配器、55 类索引、Schema 和检验清单，仅调整两处本机启动管理行为。包内许可限制修改/分发，供应方内容通过 `.gitignore` 排除、仅存本机，未发布或迁移为项目自有算法。

2026-10-06：用户明确确认已取得原作者授权、允许全套公开上传；收录授权确认记录，同步原始 ZIP、源码、资源与候选副本。原始 ZIP 字节不变，解压目录旧许可 PDF 已由用户删除。修正预检自动安装与未验证成功标记，继续保持待人工检验、显式会话注册和新目录安装保护；新增两项回归测试。通过 `.gitattributes` 保持供应方文件字节，避免换行转换破坏运行哈希。
