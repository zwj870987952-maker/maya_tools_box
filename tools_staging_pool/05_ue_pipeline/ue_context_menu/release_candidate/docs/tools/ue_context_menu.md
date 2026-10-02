# UE 资产源路径菜单候选

完整保留原 Content Browser 右键 Print Source Paths 与逐资产多路径 Output Log。单文件 SHA 精确归档；import 不注册菜单、不打印日志。修复原 asset.has_editor_property 的不可靠调用，改 try get_editor_property；逐方法读取错误不吞掉为成功，get_all_filenames→extract_filenames→get_first_filename→source_data raw 四回退保持。raw_relative 原相对路径明确标记，不按 cwd 拼成错误绝对路径；此工具不判断源文件存在，不修复导入元数据。

UE原生 package engine_toolkit.tools.ue_context_menu 无Maya依赖；parameters_schema/validate/execute/run 提供结构化结果。action 默认 inspect（读选区）；print_source_paths 输出日志；register_menu/unregister_menu 更改该 owner 的临时菜单、不改资产/文件、不受Undo管理。dry_run=True只检查，不注册、不注销、不日志。空选区返回空rows，打印时提示；超过10000拒绝。show_ui显式注册菜单；重复注册先注销自己的 owner，不动其他菜单。

```python
from engine_toolkit.tools import ue_context_menu as t
t.run(action='inspect')
t.run(dry_run=False, action='register_menu')
t.run(dry_run=False, action='print_source_paths')
t.run(dry_run=False, action='unregister_menu')
```

菜单路径改为通用 ContentBrowser.AssetContextMenu 的自有 EngineToolkitSourcePaths section，避免原把 AssetActions section误当菜单名；标签/靠前插入保留；callback使用完整正式模块名，不依赖原临时路径。ToolMenuOwner + unregister_owner_by_name 在关闭或热重载时需显式注销；不自动改UE启动脚本。右键操作读取执行时Content Browser全选区，不保证仅菜单上下文资产。UE版本菜单布局仍待实测。需要Python Editor Script/Editor Scripting Utilities/ToolMenus；无UE安装，真实菜单/多类型import_data检查 not_run。

纯查询结果可供骨骼导出、源文件复制预检，不能把未解析/缺元数据当做资产无源。extract_filenames可多源；raw仅原字串。target/package/docs/tests晋级由promotion.json与临时promote_candidate.py负责，不改Maya注册表，--apply必须UE runtime_version与当前SHA人工验收。

参考：[AssetImportData](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/AssetImportData?application_version=5.1)、[ToolMenuEntry](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/ToolMenuEntry)。离线mock/临时布局通过不等于UE直验。
