# TheKeyMachine 真实Maya验收 not_run

1. 新会话选择备份场景和已有独立data_root，完整原toolbar与selection sets/customGraph/Qt菜单所有png/svg正确；原186资源完整、inspect/dry不写prefs/启动job/timer。首次显式show新数据namespace，已有prefs/connect只literal，不自动执行配置代码；中文/英文切换不改源文件。
2. 原按钮/slider/右键完整检查：smart keys/inbetween/tangent/time move/reset/mirror/pose/animation insert/opposite/worldspace frame/range/link/locators/pivot/tracer/followCamera/depth/gimbal/selectionSet/shelf/hotkey runtime catalog、customGraph/blend/offset/micro。复杂rig、namespace、父变换和锁轴/reference检查；原native接口失败不能登记通过。
3. pose/anim/镜像异常/reset默认/selection-set/pivot JSON先backup再覆盖，坏key/非有限/重复key不接受；删除移自有.mtb_deleted，只自有root/明确Save Dialog路径；外部file不能scene Undo。单业务一次UndoRedo、选择/时间恢复，选择类保留输出选择。
4. 重复show/reload/close不叠线程，timer全部Qt主线程；close撤自有job/UI/commands/callback，长期offset/micro正确结束Undo，不清外来UI/job/短名对象、不删除用户安装/数据/userSetup/Maya.env。runtimecommand前缀，已有用户同名原命令不动，不自动热键绑定；foreign冲突明确报告。
5. 记录所有未通过source catalog分支、Maya版本、candidate_sha256、accepted_by/date/passed=true后再promotion；隔离Qt/mayapy/离线不能冒充真实Maya直验。
