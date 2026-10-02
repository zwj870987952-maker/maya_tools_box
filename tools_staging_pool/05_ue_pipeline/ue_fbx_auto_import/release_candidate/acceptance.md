# 双运行时验收 not_run

1. 备份Maya scene和UE项目/共享Skeleton，空临时目录。Maya窗口打开/根Content检测anim与uasset/两combo/URL拖放/加载旧JSON/Generate独占编号JSON；中文/Content大小写/坏最后FBX/非/Game/重名/外Content路径应拒绝。dry_run与detect/load不写文件，不改当前dirty场景/Undo。
2. UE启用Python Editor Script/EditorScriptingUtilities以及目标引擎legacy FBX importer，使用实际动画FBX和正确Skeleton、完全全新/Game目标。inspect/dry-run无tasks/asset writes；confirm_import=False拒绝实际导入。真实导入每FBX独立stem子目录，检查AnimationSequence绑定Skeleton/帧段/曲线/多take，无mesh/material/texture意外资产；save True磁盘新包/False内存区别；原FBX/JSON和既有其他包保持、共享Skeleton变化如实审查。
3. 坏最后配置/缺Skeleton/目标已有/配置destination重叠首次import前拒绝；某FBX损坏或native空返回必须失败且保留之前成功outputs信息。不用UE Undo期待回滚保存；清理只能操作已确认新目标目录，不覆盖正式动画。Maya真实GUI与UE真实导入均not_run，mock/mayapy不替代。两端满意才记录current candidate_sha256/tool_id/maya_version/runtime_version/accepted_by/date/passed=true晋级；目标清单与Maya注册预制，UE无需Maya继承。
