# RdM Tools v2 真实 Maya 验收

not_run。隔离mayapy不替代完整PyMel/Qt GUI或生产绑定实测。

1. 使用备份场景、新Maya会话，准备原功能所需PyMel；确认原EULA/使用条件。候选launch_candidate.py show_ui()打开完整主窗口，查看全部功能页、控件图标、滑条、停靠/关闭重开，无Fatal。不运行run_RdMTools/install，不写用户scripts。
2. inspect/dry前后核对选择、时间、Undo、scene/偏好不变；164资产与全部签名存在。Qt5/Qt6、随包UI/资源定位、Python3回调import/reload均正常。明确记录未随包提供的RdMTools Legacy、旧独立Picker资源/开发模板，不把这些缺项标为通过。
3. 对11种控制器、颜色/轴/Root/Auto/Offset、文本/滑条/Picker及属性显隐/重命名/约束/match做真实按钮检查。检查worldMatrix、创建/父子/短名冲突、namespace/重复叶名、锁/驱动/引用/多父DAG、API环境恢复及一次Undo/Redo；GUI回调另核对其原范围。
4. 按原PDF/docx，在新的备份场景顺序执行Spine/Head/Arms/Legs/Hands定位器→joint→rig、FK/IKFK切换、FootRoll/部位改进、AutoComplete连接/skin、Twist/Ribbon/Quadruped。原固定命名/connected/hairSystem/示例删除范围须逐项检查，不能用无异常证明绑定正确；PyMel缺少就记录真实缺依赖，勿伪造替代。
5. 验证面部extra joints/controllers、嘴/眉、edge/face/NURBS、skin bind/mirror/move/key cleanup和各blend/constraint功能。检查原动画/输入网格/外部节点、权重与Script Editor，使用备份/临时模型。AddRemoveJoints原语法修正的实际influence增加单独验证。
6. CurveToJson在临时目录导出全场景曲线，核对原CV数据结构、多次不积累、现存文件拒绝且无场景改动；可选UItoPY准备pyside2uic后用明确输入.ui/新.py检查。文件不会由Undo删除。SkinWeightMaps原GUI导入导出只用临时目录。

记录Maya/Python/Qt/PyMel与具体通过/缺依赖/失败范围。用户真实验收通过后保存passed=true、tool_id=rdm_tools_v2、candidate_sha256=最新promotion预览指纹、maya_version/accepted_by/date，用plans/staging_run/promote_candidate.py --candidate 此目录 --acceptance 实测.json --apply晋级。此前不迁正式库/改注册/同步Obsidian。
