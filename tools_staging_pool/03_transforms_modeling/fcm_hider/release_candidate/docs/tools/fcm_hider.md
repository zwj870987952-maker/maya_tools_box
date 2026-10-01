# FCM Hider Beta 2.0 完整候选

`prepared_unverified`；真实GUI/生产rig未验收。Francisco Cerchiara Montero原57文件、54个图标、完整58函数定义（含重复mirror函数与嵌套helper）逐字节SHA归档。shelf文本内1309行原Py2业务转换为私有native.py，完整身体/额外集合、对象/shape/面隐藏、edit、选择mask/颜色/grow/shrink/template line、镜像、检查循环、联系/帮助及原紧凑窗口保留。原安装器不执行，候选不向用户scripts/icons/shelf写文件，所有图片使用包内路径。

`FcmHiderTool`，category=`modeling_surfacing`；Base/ToolResult/Schema/read-only preflight/Undo。system默认mtbFCM，为mtbFCM开头的简单根namespace；每系统有9个成员集合、All_Sets_Hider聚合集合、FCM_Hider_Settings。候选所有系统节点标记owner，已有异源同名节点拒绝，不接管原root/引用的FCM系统。inspect默认只读，initialize显式建立完整系统；open_ui按原行为初始化后打开完整窗口，场景初始化受Undo，GUI本身不能Undo。

|action|参数/行为|
|---|---|
|inspect / initialize / open_ui|system，返回明确scope或初始化/UI结果|
|add|set默认Head_Hider，objects省略用当前选择，shape_mode=False存原对象；True按原shape/face分组；原行为添加即隐藏|
|remove / clear|set，remove的objects指定要移除成员，clear只清空成员并显示，不删除场景物体|
|hide / show / toggle|set，真实transform/shape visibility及mesh面隐藏|
|hide_all / show_all|完整9组，All按钮原WIP改接已有完整全部显示函数|
|clear_body / clear_extra|分别清空6身体／3Extra集合，并按原逻辑显示成员|
|cleanup|显示／清空成员，删除确切拥有的10 sets+settings，源对象保留|
|mirror|右Arm/Leg→左Arm/Leg，mirror_tolerance默认.0001，有限(0,1]；全表预检后追加匹配成员|
|unlock_visible / unlock_meshes|仅Hider成员与shape以及完全由该scope覆盖的displayLayer；不会全场景解锁|
|lock_selection|objects／当前选择，原overrideDisplayType=1；拒绝pickWalk会影响的未选child|
|show_faces|仅集合面成员恢复hidden face/polyHole，拒绝原全scene defaultHideFaceDataSet|
|export_sets / import_sets|现有父目录下绝对.json path；9组mtbFCM-1纯数据；导出独占新文件，不能Undo|

输入唯一、明确，无代码字符/通配符。允许mesh face range在预检中实际展开，再校验现有拓扑索引，不支持其它组件。引用、node锁、display属性锁/驱动、真DAG实例、旧set中的失效成员拒绝。已有系统set和settings所有者／类型逐一核对；settings内foreign child或输出连接外部消费者拒绝清理，UI“Remove All”同样预检。成员限制geometry/control/face，不接受任意嵌套外部set。

所有实际写命令通过允许UUID保护，不靠后缀猜删除。空sets(None)不退化为全场景ls／hide，面隐藏只处理真实列表，删除原为规避hide缺陷而修改“最后一面”的fallback，避免改未选面。原namespace remove/add非幂等与clear查询短名缺陷修正。两处r_→r_的错误left pattern修为l_；控制器镜像完整原命名约定，必须唯一，找不到时全表拒绝。原reflectionSetMode并不计算真实对称face，候选按mesh局部X反射顶点、唯一距离容差匹配、相同顶点集合的face拓扑映射；非对称／多解拒绝，不改global reflection mode。历史／skin／世界变换不会被这项镜像重写，角色左右轴必须人工确认。

原Save/Load输出Python并exec整文件，改为严格JSON，禁止导入旧.py；需在可信原环境人工转换成数据。全部成员在导入前解析、核对锁/引用/实例/拓扑，旧集合和新集合都进入scope。导入是替换9组membership，成员按原clear行为显示后恢复新membership，visibility state不等价恢复之前的隐藏状态，需再点击hide。数据包含Maya成员名称，不跨scene自动猜改名/namespace。外部文件不可由Maya Undo撤回。

原字符串UI回调改私有callable；只编译已随包提供的固定回调或明确固定窗口focus命令，不向__main__注入函数，不允许API传代码。场景写入标准Undo；UI的selection mask/displayColor、循环progress与窗口状态保留原影响，需人工恢复，不能声明Undo会恢复全部GUI设置。每次执行finally恢复AutoKey/namespace及场景操作前选择；明确“Select Set”/grow等选择辅助按钮保留其新选择。父transform显示会影响其子层级的最终可见性，是原对象显示语义。

```python
tool = load_tool()  # 候选launch_candidate.py
print(tool.run(action='initialize').to_dict())
p = dict(action='add', set='Head_Hider', objects=['character_control'])
print(tool.run(dry_run=True, **p).to_dict())
print(tool.run(**p).to_dict())
tool.show_ui()  # 全原紧凑窗口，真实Maya GUI
```

原Help_1/Help_2_On/Help_2_Off图片未提供，完整文字帮助代替，不声称补齐原插图。contact/教程按钮仍保留作者联系方式；无额外联网/系统进程。原包没有许可授予文档，不推断公开发布权。复用现有Base/Undo；core显示工具与此九集合/面及scene metadata协议不同，不改core、不声明组合已验证。晋级清单已包含全部源码/归档/图标/文档/测试/注册面板，真实验收后才晋级。

2离线检查证明原字节、函数与Schema完整、安全纯JSON/no source exec、独占路径。4组隔离Maya2025证明真实sets/membership/visibility/dry与Undo、命名镜像/JSON往返与覆盖拒绝、真实mesh face隐藏而无关对象不变、scope unlock与Undo、foreign collision/child/锁/GUI batch拒绝。真实镜像面拓扑、所有原UI/selection mask/生产rig和跨版本仍待验收。
