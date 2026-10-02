# UE 资产引用检查器候选

原资产选择→AssetRegistry direct hard/soft package referencers→忽略大小写_zoo正则→完整880x460深色Tk结果表/统计/异常优先/双滚动/右键定位/关闭保留，原单文件SHA归档，不自动main。纯UE模块，无Maya继承/注册；validate/execute/run和Schema、结构化success/data/errors。inspect默认只读、pattern默认_zoo可配置、locate exact package_name、show_ui打开结果、close_ui移除自己窗口和Slate callback。dry_run不打开/关闭UI、不改变Content Browser选区，不保存资产或写外部文件。

查询在UE主线程，不启动worker或强制扫描。AssetRegistry正在加载时拒绝判定，get_referencers异常或None记unknown并overall success=False，保留其他结果，不把失败当无引用。空列表才是确认零directrefs；按package去重，两个同名资产路径独立。pattern是路径文本匹配，correct意味着至少一个directreferencer符合约定，不等于UE资产技术正确、无循环、场景已加载或资产可以安全删除；不递归，不包含management/searchable-name。unsaved编辑可能未进入on-disk registry。

```python
from engine_toolkit.tools import ue_reference_checker as t
result = t.run(pattern='_zoo')
t.show_ui(pattern='_zoo')
t.run(dry_run=False, action='locate', package_name='/Game/Props/Hero')
t.run(dry_run=False, action='close_ui')
```

UI沿用原全部widget/交互，改为UE Slate tick在同一个主线程pump Tk update，不使用Tk.mainloop堵塞UE，不从其他线程quit/destroy Tk；根窗口关闭下一tick卸载，显式close立即卸载并清队列；不改变其它应用窗口。每tick任务至多100，逐任务异常记录，单例重开UI替换旧Tk root。定位使用ARFilter exact包→object path strings，修复原sync_browser_to_objects传Object而不是Array[str]。locate会加载资产与更改浏览器选区，非场景或文件写入；不宣称GUI体验已通过。Tk/Tcl在目标UE Python可能缺失，需要本地环境验证，代码不会安装依赖。

所有UI/API资源在engine_toolkit/tools/ue_reference_checker，自包含docs/tests/promotion。只预览晋级，真实UE验收后runtime_version/current SHA/人名日期才允许apply；无Maya面板伪入口。引用结果可指导人工检查/定位，不能作为自动杀毒、删除或修复依据。离线3mock/临时最终布局通过不等于UE结果/窗口/Slate实际验证。

参考：[AssetRegistry](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/AssetRegistry?application_version=5.5)、[EditorAssetLibrary sync_browser_to_objects](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/EditorAssetLibrary?application_version=5.5)。
