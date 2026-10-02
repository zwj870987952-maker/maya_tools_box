# UE 验收 not_run

备份UE项目启用Python Editor Script/Editor Scripting Utilities。候选根加sys.path后import无UI变化；dry_run register不加菜单。实际register两次只有一个Print Source Paths，右键点击多选SkeletalMesh/Texture/无importdata资产，Output Log保留多源/缺失/错误分类。实际相对路径回退不误报绝对路径，空选区提示，unregister删除仅自己菜单；重载/重启手动注册回调使用正式完整模块路径。Asset/uasset与外部文件均不变。UE菜单路径/section/版本兼容必须实测，不能把mock当UE验收。通过后以tool_id=ue_context_menu/current candidate_sha256/runtime_version/accepted_by/date/passed=true记录晋级依据。Maya验收不适用于此UE原生工具。
