# CgShake 1.5 候选

`cg_shake_py3` / `animation` / `CgShakeTool`。prepared_unverified；真实 Qt/渐变/动画层 GUI not_run。完整原十四方法对应原生界面/样式/Help/渐变/六amount/Cache/Restore/Overwrite/Use cache/预设，七原文件含四图片按字节归档。未附独立license，仅本地私有准备。沿用现有 core.ui_base 的 PySide2/PySide6 与 Maya主窗口获取，去掉 six 和旧 PySide 自动回退、默认参数中的导入时主窗口包装；框架复用 BaseMayaTool/ToolResult/UndoChunk。

原工具实际仅处理第一个选中对象，虽旧按钮写 object(s)；候选明确提示first selected。没有新建动画层或自动选择层，不保证旧“active layer”文案意味着只删一个层。原类会尝试载入animImportExport并直接listdir缺失presets目录；候选开窗不加载插件或建目录，缺目录按空列表，文件动作才写入。原样式漏掉vignetteFrame扩展名修为实际PNG。

## 参数与调用

候选加载见 acceptance.md。真实验收晋级后可 `maya_toolkit.execute_tool('cg_shake_py3', arguments, dry_run)`；当前未注册正式库。

| 参数 | 默认/范围 | 用途 |
|---|---|---|
| action | inventory | inventory/open_ui/apply/cache/restore/clear/save_preset/load_preset |
| object | 空 | 明确transform/joint，空读取第一个选择；其他对象不处理 |
| start/end | null | apply取playback min/max，也可传有限数值 |
| step | 1，整数1..99 | 原Frame步长，拒绝0 |
| amounts | tx/ty/tz/rx/ry/rz各5 | 完整六项0..99.99，沿原spin box范围 |
| falloff_samples | [] | apply必须每个采样帧一个有限权重；GUI从原生gradient取值，不重写插值 |
| seed | null | null保留全局random，整数使用独立随机源便于复现 |
| overwrite | false | apply先全范围cutKey；clear必须true |
| use_cache | false | apply先验证并restore本候选cache，再加扰动 |
| file_path | 空 | 文件动作绝对.anim/.cgsk路径；cache空时用用户数据目录/UUID.anim，restore空读自身记录 |
| overwrite_file | false | .anim/sidecar/.cgsk覆盖必须显式true；GUI已有文件询问 |
| preset | {} | save_preset原Frame/TX/TY/TZ/RX/RY/RZ/Points完整字段 |

所有参数自行严格验证；Schema不代替预检。对象组件/通配符/歧义/引用/锁定拒绝。apply会setAttr全部六TR，所以amount=0的通道也必须可写；普通animCurve/animBlend可接受，其他直接外部驱动拒绝，复杂层/间接驱动待真人。清键动作额外检查动画属性锁定。amount全部0时原空at可能给额外属性打键，候选明确拒绝。

## 原扰动与渐变

保留两个循环：先完整采样原六TR，再逐帧加扰动/写键。帧序列为 `range(int(start), int(end+1.0), step)`，保留原小数截断；GUI渐变归一化为 `(frame-start)/(end+1-start)`，末整数帧不必达到1。API显式falloff_samples避免在headless伪造gradient或改变原Maya插值；caller需按frames顺序提供权重。

每帧按 tx/ty/tz/rx/ry/rz 顺序六次 `uniform(0, amount)`，包括amount0；值为原采样值+weight*随机值。它不是以0为中心的对称噪声，权重为负时符号也会改变。全部六TR setAttr，只有非零amount通道 setKeyframe；保留原本地数值/当前Maya单位。原生默认渐变asString为 `0,1,3,1,0,3`，UI直接求值；预设保留原Points三元组格式，不用自制线性曲线替换。

Overwrite先cutKey(object,clear=True)，Use cache随后restore，最后取baseline。这些清键未限定时间范围/参数没有显式动画层限制，可能影响对象其他动画键；界面警告已写明，必须在副本实测层作用域。所有场景动作现在一个标准UndoChunk，修复原overwrite/cache恢复在chunk外、错误可漏关chunk的问题。

## 缓存与预设文件

cache/restore预检只查询animImportExport是否已加载，未加载需用户在Plugin Manager手动操作，开窗/普通apply不自动加载。cache保留原.anim导出options与精度/层级/shape行为，但只选择本次单目标，避免原将多选择导入到一个目标；生成UUID文件名替代所有对象共享tempCache.anim。文件导出可能改Maya动画clipboard，不保证被Undo恢复。

cache在私有 `mtbCGShakeCache` 字符串属性和 `.anim.json` sidecar 保存Owner、目标UUID、绝对路径、SHA256；restore在清键之前校验完整记录/文件/sidecar和插件。改名可按UUID记录恢复，换目标/路径/内容/外部同名属性拒绝。不会自动采用原任意 `cache` 属性或旧共享缓存，需用Cache重新生成。没有缓存时Use cache失败，若确实要直接apply可取消Use cache，不猜测继续。

导出先写自己唯一临时.anim，再替换目标；JSON同样用临时文件后替换。文件/目录写入、覆盖和sidecar不属于场景Undo；若文件完成但场景属性写失败，文件可能仍留下，应检查并重新Cache。Undo可能撤销cache属性，但不会删除已生成文件。无插件安装、脚本安装或自动网络请求；原Help仅点击时打开原网址，未抓取网页内容。

UI默认用户 `Maya app dir/maya_toolkit/cgshake/cache` 与 `presets`，包images只读。save_preset拒绝路径穿越名称，文件已有需确认；API只接受显式绝对.cgsk路径。load校验Frame/六amount/Points，兼容原字段，缺失或损坏返回失败；不凭部分字段覆盖UI。

## 状态、输出与验证

validate/dry_run不建GUI、载插件、建目录、写键或文件，只返回对象/frames/文件动作与校验计划。finally恢复时间、存活组件选择及四播放范围，并关闭内部guard；导入原combine时间范围的临时变化不遗留。异常不自动回滚部分键，查看ToolResult后Undo；文件另行检查。

inventory返回原方法/资源/变动审计；open_ui返回window。apply返回目标、samples(frame/falloff/六values)、keyed_channels；cache返回cache_record；restore/clear返回目标/路径或cleared；preset加载返回原数据。输出只是隔离执行信息，不证明复杂动画层或所有曲线操作满意。

可在副本已有动画→必要时Cache→apply原渐变→检查曲线/画面→Restore做对照；外部文件必须保留sidecar及原目标UUID。不推荐把未验收layer/缓存结果直接接生产导出。

普通Python3项通过：七来源SHA/原十四方法/四图片/无导入主窗口或自动插件，严格参数/Points，文件只读计划/Schema/无Maya inventory。Maya2025隔离6项通过：正向随机及六次调用顺序/首对象/Undo、小数范围和0amount、dry_run/锁/GUI拒绝、clear/preset覆盖、真正animImportExport导出导入及SHA变更拒绝、故障恢复和Undo。插件仅在隔离测试显式载入，文件仅写临时目录。

原Qt窗口/渐变鼠标编辑/嵌入Maya控件、Presets交互、层作用域/Use cache完整GUI、非默认单位/其他Maya版本仍需真人验收。完整资源/两测试/知识/注册/晋级已预制；验收当前哈希通过后才迁正式库。
