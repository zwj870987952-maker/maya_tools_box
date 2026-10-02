# UE 人工验收（not_run）

1. 使用备份 UE 项目和空临时输出目录。启用 Python Editor Script/Editor Scripting Utilities/Skeleton Editing Tools；把候选根加入 sys.path，import engine_toolkit.tools.ue_bone_exporter，确认没有写文件或骨骼提交。
2. 两个实际 SkeletalMesh 共用 Skeleton 且 mesh 骨骼不同，含中文骨名/不同文件夹同名 mesh。run(action='export') 确认全表可读、没有文件/资产 dirty；执行 dry_run=False 核对 UTF8、网格骨名/顺序、非网格跳过；同名、已有文件、空选区、禁用依赖全表拒绝；资产和磁盘 uasset 哈希不变。
3. 将候选 native/BoneListGenerator 安装到备份 C++ UE 项目 Plugins（原插件若存在先备份审查，不覆盖），生成项目文件，通过目标引擎 UBT 编译。启用插件，SkeletalMesh 右键出现网格/共享 Skeleton 两个入口，逐项保存对话框、取消、成功消息与失败日志正常。对比共享 Skeleton 额外骨骼差异；已有目标即使对话框确认也不覆盖。
4. 卸载/重启/热重载检查菜单不重复且注销完整。Windows保存路径/中文/扩展名/无骨骼/只读目录/多资产 partial outputs检查。Python/C++ 实测均通过后记录版本、工具 ID、promotion 预览 SHA、操作者/日期，不用离线 mock 或静态 C++ 代替 UE 验收。
5. 用户验收 JSON 必含 passed=true/tool_id=ue_bone_exporter/candidate_sha256/runtime_version/accepted_by/date；晋级脚本只布置项目内最终路径，插件安装仍是 UE 原生操作。Maya验收对此纯UE工具不适用（不声称通过）。
