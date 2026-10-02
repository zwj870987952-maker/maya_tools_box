# Smart Assistant 真实Maya验收 not_run

1. show_ui仅controls不修改prefs/注册hooks；enable/disable重复启停，Qt5/6 QObject强引用filter单实例，拖拽支持文件/序列、其他后缀/其他窗口不吞事件；整批多files不忽略第二项。场景dirty open要求先保存，namespace取消不建ref，已有namespace拒绝，open仅1file默认取消且不可Undo。FBX/OBJ/ABC插件与引用复杂源使用备份场景。
2. export/read/apply/restore原5optionVars实际类型、坏最后key不先改首项、重复key拒绝、新绝对JSON不覆盖不mkdir，多个apply恢复所有初始值/不存在key。仅optionVar不是scene currentUnit切换，确认真实偏好UI刷新语义；没有自动SavePreferences/重写config/userSetup。
3. Python fileDialog2 caller未提供dir用当前scene目录、明确dir尊重、args/kwargs与返回完整、不重复嵌套、restore还原原callable；foreign后来wrapper需先恢复它，候选不强覆盖；原MEL命令参数/返回保持原生，未假称MEL路径已劫持。
4. 同prefix/padding连续数字图片至少2frame、gap/multiple groups拒绝，sequence camera+正确imagePlane shape+frame expression/frameExtension/独立viewport实际显示、原selection保持/单UndoRedo。open_view=False可纯scene调用；窗口不可由scene Undo撤回，图片为外部用户输入，不写素材。
5. fullGUI关闭/重开/会话hooks独立管理、disable恢复；并行其他工具的global patch/Drop过滤器交互与Maya跨版本实记。candidate_sha256/maya_version/accepted_by/date/passed=true后执行promotion；此前不迁正式。
