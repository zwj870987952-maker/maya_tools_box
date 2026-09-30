# Anim Layer v4.0 整理检查点（尚未形成完整候选）

当前 manifest 为 working，不计入已完成单元。下轮继续整体套件适配，不能只包装菜单并丢弃其他功能。

## 已核对的源文件

单元 `tools_staging_pool/01_animation/anim_layer_v4_0/anim_layer_v4_0/` 共 6 文件：完整 layerEditor.mel、NoUI MEL、NoUI 拖放安装器、帮助 JPG、readme、License。无根 README，入口为完整 layerEditor.mel。全部运行资源最终须原样带入候选；安装器仅作为归档，不自动改用户脚本目录或 Shelf。

License.txt 是 Barnev Pavel 的自定义商业许可文本，列明商业使用、再分发与修改限制。原 MEL 还包含 Autodesk 2021 的版权/许可头。按第三方套件准备外层适配，保留原内容/通知，不修改或抽取重写原算法、不推送/发布。候选文档须明确许可，不把它标为普通开源。

`audit_mel_suite.py` 全文件词法扫描完成，并生成 `anim_layer_v4_0_source_audit.json`。此扫描不 source、不执行源代码，只用于声明/顶层动作检查，真实 MEL 语法仍以 Maya 为准。

- 完整文件 276424 字节，216 个过程声明（197 global）；存在重复 getLayerDisplayType（一个 global、一个 local）。顶层会条件 source createMayaRenderPassTab.mel、设置渲染编辑器全局变量、末尾直接 createLayerEditor/updateLayerEditor。
- NoUI 文件 23592 字节、33 个 global 过程，仅定义过程，无顶层执行。名称包括图层创建、按 Channel Box 创建、提取到基础/叠加/覆盖层、快速/智能合并、烘焙、Euler filter、时间区间查询、选层/选对象、viewport 开关与工具菜单。
- “NoUI”仍有需要 Channel Box/AnimLayerTab/时间滑块的过程，也依赖 Maya 内置 layerEditor 的 getAffectedLayers、layerEditorSelectObjectAnimLayer 等；不能因文件名推定全部支持 mayapy。
- 全版定义/覆盖大量 Maya 原生 animation/render/display layerEditor 过程，source 会改变进程 MEL 全局定义与 UI。这些加载影响不能由场景 Undo 撤回。
- NoUI 安装器顶层创建 Shelf 按钮，InstallLocationPath 取 whatIs 的路径；不能执行它作为离线验证入口。
- 全版含非 UTF-8 字节。审计用 latin-1 保留 ASCII 语法字节位置，未认定真实本地化编码；NoUI 为 UTF-8。候选应复制原始 bytes，不能因为解析方便转码。

## 后续工作

1. 完整原样资源镜像，查看帮助图并保留许可；静态声明目录可作为 API 签名信息，不依赖待整理池路径。
2. 管理完整/NoUI 的明确加载；preflight 只验证参数/资源/环境，不 source MEL。全版要求真实 GUI，避免在 standalone 触发 UI/全局覆盖；NoUI 在隔离 mayapy 单独 source 检查，失败如实记录。
3. 保留完整 UI 和业务过程可用性；准备类型受限的 MEL 调用/Schema、过程签名/影响说明、框架结果/Undo、面板注册与晋级资料。字符串参数需按 MEL 字面量转义；原函数内部拼接 eval 仍属于原算法影响。
4. 记录合并/抽取可能删除层、烘焙会修改键、全版渲染层导出会写文件，使用备份/临时目录验收；原 UI 回调不能假称全都走新增框架的预检。
5. 逐项验收各菜单、控制器/选层/时间范围、跨版本、Undo、失败恢复和加载全局影响；不能把单个 readonly 过程通过当作整套通过。

最近额度实际读取：5 小时 used=5%、resetsAt=1790773406；周 used=42%、resetsAt=1791163488；4 张卡仍可用，未兑换。此前窗口自然刷新，未采集完整 0~100% 工作窗口，不据此给出固定周额度轮数估计。heartbeat 保持暂停，定时续跑/手机推送仍未实测。
