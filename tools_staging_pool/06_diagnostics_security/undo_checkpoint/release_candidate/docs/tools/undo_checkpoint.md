# Maya多记录点与Undo恢复候选

完整保留唯一/多点创建、原深色Qt管理面板（名称/时间/状态/双击/选中恢复/最新恢复/清空/视口提示）、三个独立快捷入口、四个Shelf按钮。原6文件逐字节SHA归档，不自动加载UI；UI业务分离，静态自有MPx Marker，不再临时生成覆盖plugin脚本，不再MEL拼接用户名称，中文/引号名称纯JSON参数。

Base/ToolResult/Schema/scene_hygiene，action inspect默认、create/name/overwrite、restore/target_id/max_steps、clear、show_ui、install_shelf/shelf_name。run刻意不包通用UndoChunk：它管理原有Undo队列，restore不得在一个新chunk内Undo，create只给marker自己的唯一chunk名字mtbCheckpoint_cp_UUID，不能被外层通用框架chunk隐藏。显式调用需在其它open UndoChunk之外；嵌套时创建后发现marker不可独立可见会fail并标失效，不擅自关闭调用方chunk。dry-run不注册plugin、不加marker、不改队列、清空元数据或UI。

记录只在当前Maya进程内，不保存到scene文件，不跨重启恢复。create的no-op MPx只插Undo marker，不增加场景节点；overwrite/clear仅元数据不flush Undo、不删除native旧标记。manual Undo把已到marker标为已回退，Redo对应标记恢复Active（如果清空/overwrite旧标记则不复活UI旧记录）。队列被flush/scene切换/历史长度截断后，即使内存还记录ID，restore找不到唯一chunk会0步拒绝，绝不像原代码Undo到空队列。

read-only native printQueue临时MCommandMessage output callback捕获编号/命名chunk，未命名Python命令也计数，finally移除callback；不设置日志抑制偏好，队列输出仍可能出现在Script Editor。初测Boolean-returning filter callback导致本机Python退出bool_dealloc原生崩溃，改用返回None的output callback并核验正常退出，失败报告单独保留。格式/顺序无法识别拒绝恢复。目标steps超过max_steps（1..100000，default5000）在第一Undo前拒绝。每Undo前比较整队列与预期前缀，异步脚本/新操作改变队列停止，报实际已撤步骤不假称完成；真实plugin marker到达才成功。GUI加速suspend refresh并finally恢复原状态，batch不触viewport；原场景操作本身可能非Undoable或有文件副作用，记录点不能还原这些动作或文件IO，回退还可能执行用户原命令Undo代码。

```python
from maya_toolkit.tools.undo_checkpoint import UndoCheckpointTool
t=UndoCheckpointTool()
point=t.run(action='create',name='修改前')
# 后续可Undo场景编辑
t.run(dry_run=True,action='restore',target_id=point.data['id'])
t.run(action='restore',target_id=point.data['id'])
```

Shelf四owned docTag按钮按正式完整module调用，真实换行代码可编译、不硬编码临时sys.path；重复安装更新自身tag/不覆盖其他按钮，不自动savePrefs，不是场景Undo。独立create默认overwrite唯一，restore最新，clear仅metadata。面板全部原widget/styles/提示保留，不需QApplication新建；对已清点/队列变化须真实UI复核。native command owner路径不合拒绝，含Undo记录时不能随意unload其plugin。

2离线queue/真实Shelf command compile +3隔离Maya2025实际marker/多点tx1/2/3回退与Redo、引号名不执行MEL、dryqueue不变/max不足零步/flush旧点拒绝/foreignID/clear保队列/overwrite/Undo关闭拒绝/临时最终注册-domain-panel通过仅非GUI证据；真实MayaQt/Shelf/Refresh嵌套chunks/外部脚本队列竞争/跨版本not_run。原示例2020-2026/Python2未迁移为已支持承诺，候选目标Maya2025Python3。

参考：[MCommandMessage callback](https://help.autodesk.com/cloudhelp/2025/ENU/MAYA-API-REF/py_ref/class_open_maya_1_1_m_command_message.html)。自包含业务不修改框架/core，晋级注册与资源/知识/tests已预制；未验收仍待整理池。
