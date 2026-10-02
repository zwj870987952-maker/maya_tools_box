# UE 骨骼表导出器候选

完整保留 UE Python 选中 SkeletalMesh→逐骨骼 TXT，以及 Editor C++ 右键菜单→原生 SaveFileDialog→成功消息功能。源五文件逐字节 SHA 归档 upstream/catalog.json，原导入自动导出取消。原 Python 为网格骨骼、原 C++ 为共享 Skeleton；现 C++ 有两个明确入口，网格列表默认 _BoneList.txt，共享 Skeleton 列表 _SkeletonBoneList.txt，可能包含本 mesh 没有的骨骼。保留引用骨架顺序，不含 socket，LOD/虚拟骨骼跨版本差异必须实测。

本工具在 Unreal Editor 运行，目标 engine_toolkit/tools/ue_bone_exporter，自包含，未继承 Maya 基类，未修改 Maya 注册表/面板。Python 提供 parameters_schema、validate/execute/run、结构化 success/tool_id/dry_run/data/errors。读选区会加载资产；SkeletonModifier 仅 set/get，不调用骨骼编辑、commit、save；引擎加载与缓存不等于纯内存无变化，但不修改资产内容/场景。API import 不自动运行，dry_run 默认 True，action 默认 inspect。

```python
from engine_toolkit.tools import ue_bone_exporter as t
preview = t.run(action='export', output_dir=r'D:/UE_BoneLists')
result = t.run(dry_run=False, action='export', output_dir=r'D:/UE_BoneLists')
```

output_dir 必须已经存在；空值是 UE 项目根，asset_paths 为可选 UE object path 数组，缺省 Content Browser 选区。混选非 mesh 如原版跳过；坏网格、空骨骼、同名输出、已有目标在整批写入前拒绝。独占 UTF8 无 BOM 换行 TXT；进程内失败清理自己创建的文件，不删除竞争写者的已有文件。进程中断可能留下部分文件。文件不受 UE Undo 撤销，没有覆盖功能。

C++ native/BoneListGenerator 是完整 Editor 源插件，含 uplugin/Build.cs/Public/Private，修复明确 includes、Menu owner 生命周期；保留原保存窗口/日志/消息，新增 FILEWRITE_NoReplaceExisting 和已有文件拒绝，原骨骼表菜单拆为两范围，移除已不使用 EditorStyle 依赖、补 AssetRegistry。C++ 多资产逐项窗口，取消/坏资产跳过、失败可能保留此前文件，不承诺整批事务。无骨骼或无桌面平台时不写。已存在同名插件需先人工审查备份，不能叠装。

Python 需 Python Editor Script Plugin、Editor Scripting Utilities、提供 SkeletonModifier 的 Skeleton Editing Tools（模块/插件和 UE 版本相关）；缺失时报依赖错误，可独立使用 C++。C++ 需目标 UE 的 Editor SDK 与 C++ 工具链，必须本地 UBT 编译，不能把离线文本检查称为编译成功。本机未发现 Program Files/Epic Games，UE 编辑器/UBT/真实资产检查 not_run。

晋级文件清单 promotion.json；plans/staging_run/promote_candidate.py 默认只预览，--apply 需要 passed/tool_id/candidate_sha256/runtime_version/accepted_by/date 人工验收 JSON。将来仅复制 engine_toolkit/docs/tests；UE 插件安装为单独显式动作：把 native/BoneListGenerator 复制到临时 UE 项目 Plugins/BoneListGenerator，生成项目文件/编译 Editor 后启用。包内所有路径自包含；不自动改 .uproject 或用户启动脚本。人工验收前包保留待整理池。

可组合：从 Maya FBX 导出→UE 导入 SkeletalMesh→读取 mesh bones 校对；TXT 是名称序列，不验证蒙皮/父子关系或绑定姿态，不作为自动删除/重命名依据。共享 Skeleton 名称不能冒充该 mesh 实际骨骼。

API 依据：[SkeletonModifier](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/SkeletonModifier)、[USkeletalMesh GetRefSkeleton](https://dev.epicgames.com/documentation/en-us/unreal-engine/API/Runtime/Engine/USkeletalMesh/GetRefSkeleton)、[菜单 Context](https://dev.epicgames.com/documentation/en-us/unreal-engine/API/Editor/ContentBrowser/UContentBrowserAssetContextMenuC-)、[FToolMenuOwnerScoped](https://dev.epicgames.com/documentation/en-us/unreal-engine/API/Developer/ToolMenus/FToolMenuOwnerScoped)、[SaveStringToFile](https://dev.epicgames.com/documentation/en-us/unreal-engine/API/Runtime/Core/FFileHelper/SaveStringToFile)。仅依据文档补适配，目标 UE 编译/运行仍待验。
