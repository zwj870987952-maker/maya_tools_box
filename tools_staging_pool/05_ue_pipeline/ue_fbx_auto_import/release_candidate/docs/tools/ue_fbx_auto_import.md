# Maya配置生成与UE FBX动画批量导入候选

双入口完整保留：Maya PySide根路径智能Anim/Skeleton检测、可编辑两combo、FBX文本/URL拖放、Load Config、Generate Config、新编号桌面JSON；UE批量JSON读取→Skeleton检查→FbxImportUI动画设置→AssetImportTask自动导入/保存/逐文件结果。原两文件SHA归档。所有import取消自动开窗/执行，未迁入正式库。

Maya UEFbxAutoImportTool才继承Base，tool_id=ue_fbx_auto_import/category=engine_bridge/JSON Schema/ToolResult；action inspect_config默认，generate_config/config/output_dir写独占新JSON（不受Undo），detect_paths/root_path只读查Content，show_ui需真实GUI。默认桌面FBX_Configs目录仅真正generate创建；原文件永不覆盖。只检测Content中anim目录与Skeleton名称.uasset，不把Skeleton.txt当资产；/Game路径用明确Content根relative_to转换，不在字符串中截取任意/Content，不支持plugin mount自动转换。原widget/layout/drag/load流程保留，Qt6/Qt5兼容；配置三键格式完全兼容。

```python
from maya_toolkit.tools.ue_fbx_auto_import import UEFbxAutoImportTool
tool = UEFbxAutoImportTool()
tool.show_ui()
# UE Editor内独立执行（正式项目根需在UE sys.path）
from engine_toolkit.tools import ue_fbx_auto_import as ue
ue.run(action='import', config_directory=r'D:/FBX_Configs')
ue.run(dry_run=False, action='import', config_directory=r'D:/FBX_Configs', confirm_import=True)
```

UE API完全无Maya依赖，validate/execute/run返回success/tool_id/dry_run/data/errors；dry_run默认True，不创建任务/选项，不调用import/save。显式config_paths或config_directory二选一，最多1000cfg/每cfg1000FBX，JSON4MB上限；源绝对现存FBX/ASCII安全basename/重复名/配置destination重叠全批检查，源SHA保存执行前复核。Skeleton必须真实正确类型；目标/子目录须是完全全新的/Game包目录，原路径不写。每FBX放destination_content_path/<stem>/隔离多take命名冲突（明确新增层级与原不同），AssetImportTask destination_name=<stem>、replace_existing=False、replace_existing_settings=False、save_assets默认True（原行为），automated=True、FbxFactory明确legacy importer。目标在实际导入前再查，不能对抗其他编辑器进程在native importer内竞争，需单写者。

原把skeletal设置写到static_mesh_import_data并吞掉异常，候选只用动画必需设置，所有FbxImportUI mandatory参数失败在首次导入前停止；不启用update_reference_pose/import_mesh/morph/material/texture，动画长度仍EXPORTED_TIME。即使动画-only导入，UE factory可能修改共享Skeleton曲线元数据/标dirty，不能承诺既有Skeleton完全不变；请先备份项目。原生import/save没有可靠跨资产Undo，save_assets=True写UE包，False仅不主动save，仍可产生内存资产；失败/空返回停止后续，结果保留此前paths，人工清理新目标目录与审核Skeleton。源FBX/JSON不写；UE import不能在Maya执行，Maya面板只生成配置。

自包含共享纯config模块供两端用；晋级清单同时复制maya_toolkit工具UI、engine_toolkit纯UE importer/config、docs/tests，再注册Maya配置工具；真实Maya配置UI与真实UE导入均必须验收。本机仅Maya2025隔离配置API/离线mock可验，UE Editor/真实FBX/Skeleton/Interchange与FbxFactory选择/多take导入not_run。原脚本不是现有正式core的业务重复，纯文件路径与UE资产协议未下沉core。

人工验收双runtime后记录Maya版本与UE版本，promotion脚本Maya gate保持；即使Maya API测试通过，不能只测Maya窗口就批准UE端。关联vessel/普通FBX exporter输出仅候选输入，需要真实Skeleton绑定与曲线采样核对。
