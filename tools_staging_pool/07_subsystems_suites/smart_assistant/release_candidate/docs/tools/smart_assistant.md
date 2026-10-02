# Maya Smart Assistant 完整待验候选

用户17原文件精确SHA归档；完整偏好JSON保存/应用、拖拽ma/mb/fbx/obj/abc打开/导入/引用选择、图片序列相机+独立modelPanel、Python fileDialog2当前场景目录功能与控制UI全部准备。原path_utils空文件缺is_image_sequence_folder、QtWidgets.QObject错误/弱生命周期、Qt6导入缺失、namespace取消变root引用、optionVar全部用stringValue、launch默默覆盖偏好/全局命令等确定问题已改。native模块路径完整，默认inspect/show_ui不注册监听或patch，不生成config、不写package路径；需要明确enable或UI按钮，关闭控件后仍可用disable显式撤所有自有hooks+恢复本会话optionVars。没有启动安装/userSetup自动写入。

API遵循Base/Schema/ToolResult，actions原三feature及capture/read/save/apply/restore prefs、open/import/reference、sequence、monitor/patch独立启停。GUI/mainwindow/QApplication/主线程检查；Qt6/Qt5真实filter使用QtCore.QObject、application强引用、仅Maya窗口子树支持文件Drop/DragEnter/Move，未支持后缀和其他窗口不拦截；stop只移除自有filter。fileDialog2只补caller未明确startingDirectory/dir时的当前scene目录，保存原函数且不重复叠加；foreign后装wrapper时拒绝覆盖，先恢复foreign wrapper再disable。原MEL global proc fileDialog2不能保持内建签名/返回值，不继续破坏内建MEL命令；MEL直调保持原生行为，Python调用默认路径功能完整。

```python
from maya_toolkit.tools.smart_assistant import SmartAssistantTool
t=SmartAssistantTool()
t.show_ui() # controls; hooks opt in
t.run(action='enable')
t.run(action='save_prefs',path=r'C:/temp/new_prefs.json')
t.run(action='apply_prefs',preferences={'gridDivisions':8},dry_run=True)
t.run(action='apply_prefs',preferences={'gridDivisions':8})
t.run(action='restore_prefs')
t.run(action='import_file',paths=[r'C:/temp/source.ma'],dry_run=True)
t.run(action='create_sequence_camera',path=r'C:/temp/sequence',open_view=True)
t.run(action='disable')
```

偏好只原五key：workingUnitLinear/Time string，gridSize/Spacing正有限数，gridDivisions正整数数值且保留原float/int存储（实际Maya2025为float），未知key/strict bool/类型错误/重复JSON key/超过1MiB拒绝。保存已有parent的新绝对JSON，不覆盖/不mkdir；read/dry只查文件/scene。apply全部数据先检，typed optionVar；记录每key第一次状态，后续apply不同key也保留，失败恢复本次，restore准确恢复不存在key或原类型。不主动SavePreferences，不假称改scene currentUnit/grid生效：原设计存optionVar，需用户选项UI刷新后实际核验。

file操作全1–64paths先检存在/后缀/绝对/重复，坏最后文件不前项import；reference明确namespace、不碰撞，多文件suffix分配，namespace取消不运行。import/reference existing新scene对象UndoChunk，但真实reference/file插件Undo支持须验收；open一次1file/confirm_replace_scene=True/dirty scene须先保存，force=False，不自动丢未存场景；open整体不能Undo。MA执行scriptNodes=False，FBX/OBJ/Alembic插件按真实Maya运行方式，不声称此参数封闭所有插件或reference副作用。

序列要求唯一同prefix/padding/扩展名、至少2连续数字帧，最大10000；避免原不明确目录多组和字符串顺序。预检纯查文件，不建nodes/view；执行完整camera+imagePlane/正确shape attrs/隐藏camera/只当前相机显示/可选modelPanel，复用本次新imagePlane的原生frameExtension驱动，只有未连接才创建frame expression并返回frame_driver，不覆盖外来连接。scene单Undo并保持原selection，view属非sceneUI只由用户关闭，Undo不撤viewport窗口/外部图片；timeline按源图片帧号（如0008-0010需时间8-10），不自动修改playback或当前时间。图片不复制，folder/first_image属于用户外部输入路径，不是遗漏候选素材；Maya低于原兼容target/缺图片时实记，不能用UI打开就推定显示/帧序列正常。

隔离检查为typed optionVar/dry/restore、真正camera/imagePlane/选择/一次UndoRedo/frameExtension、坏最后file/dirty open拒绝/真实MA import与open的临时fixture、Python wrapper尊重caller dir/传参返回/重复不叠加/foreign拒绝/restore；单独Qt离屏QObject/QDropEvent测试只自有子树受支持文件/其他对象与后缀不吞/停止强引用filter。真实用户文件Drop/filter重复长期生命周期、实际Python对话框与MEL原生、UI/sequence显示/插件/production reference/跨版本均not_run。全部code/UI/资源/测试/文档及注册promotion预制，用户真实Maya满意前留待整理池；不改正式core/registry。
