# cvWrap / weightDriver / mGear 完整套件候选

`prepared_unverified`。原包全部 532 文件、363 Python 模块、4,614 函数/类定义、80 UI、绑定/rig 模板和全部图片留存；catalog逐文件记录原字节SHA，upstream归档原Python为`.py.original`。native保留完整业务，候选可整体晋级，不依赖池外原目录。真实GUI、编译插件和生产rig验收均not_run。

实际范围包含cvWrap创建/选项/局部rebind/权重paint/绑定导入导出，weightDriver 3.6完整MEL RBF编辑器和AE模板，以及mGear 4.0.9 Shifter classic/EPIC组件、Simple Rig、Rigbits/RBF/SDK、Skinning、Animbits、CFXbits、Crank、Anim Picker、Synoptic、Flex及Utilities。所有上游模块、UI和菜单保留；适配器不把数千个上游函数重写为统一协议。原包没有cvwrap、weightDriver、mgear_solvers编译二进制或C++源，本机Maya2025缺PyMel，不能凭离线解析证明这些算法实际工作。提供匹配Maya版本的插件与PyMel后，在备份场景执行完整验收。

候选继承BaseMayaTool，category=`modeling_surfacing`，提供Schema/ToolResult/只读validate/dry_run及Undo。默认`status`只读返回依赖、版本及范围，绝不加载插件、修改sys.path或建立UI。输入按action严格检查，未知或不适用参数拒绝。

|action|输入与输出|影响|
|---|---|---|
|status|无需参数，返回真实插件/PyMel状态|只读|
|load_plugin|plugin为cvwrap/weightDriver/mgear_solvers，path为匹配名称的现有绝对.mll路径|显式加载当前会话，不安装、不改autoload；插件加载不能由Undo卸载|
|create_wrap|objects省略用当前有序选择，至少两个几何对象；name=cvWrap#，radius=.1（0..100），new_bind_mesh=False，可选path现有绑定文件|保留原cvWrap name/radius/newBindMesh/binding调用；返回真实插件结果|
|rebind|wrap明确cvWrap节点、objects明确驱动mesh/组件、faces明确目标mesh面，radius=.1|只读转换得到vertices/faces，再真实cvWrap rb调用|
|import_binding|wrap与path现有绝对文件|真实插件im，绑定格式/拓扑由原生插件解析|
|export_binding|wrap与path不存在的绝对目标，父目录已存在|原生ex先写私有临时文件，再xb独占写目标；外部文件不受Undo|
|paint_wrap|wrap|启动原生权重paint上下文，UI状态需人工恢复|
|cvwrap_options / cvwrap_rebind_ui|无需参数|完整原cvWrap选项与rebind界面，提交经候选校验|
|weightdriver_editor|无需参数|显式source完整三个weightDriver MEL，开启原编辑器|
|rbf_manager|无需参数|原mGear完整RBF Manager，需weightDriver与PyMel|
|mgear_menu|无需参数|显式调用完整原菜单加载器，需mgear_solvers与PyMel；已有mGear菜单拒绝替换|

节点必须唯一、无通配符/代码字符，目标引用、节点锁、真实DAG实例拒绝。操作后恢复原选择；Scene写入使用框架Undo，但原生插件是否完整Undo必须实测。原完整编辑器/菜单中的后续按钮由上游管理，不能宣称全部操作自动进入适配器Undo、预检或覆盖保护；Flex替换、rig构建/清理、skin/模板/SDK文件操作须使用备份场景和全新临时输出，并核对上游确认框。适配器导出不可覆盖，RBF/weightNode preset导出改独占写入；其余上游导出保持原协议，需人工确认目标。

Py3转换仅两个原Py2 cvwrap文件。QtWidgets兼容PySide6/PySide2；QInputDialog取实际value并处理取消。SDK的旧reload补标准importlib。gSkin原pickle读取改限512MiB的基本数据Unpickler，禁止任意全局对象执行，根必须dict；基本dict/list/string/number/set数据兼容，自定义类旧文件拒绝，需可信环境转换JSON。原Python字节完整保留，不能直接执行不可信旧pickle。

标准mgear/cvwrap命名空间为上游字符串回调契约，显式activation只在当前进程加入native和icons路径；已有其他来源模块拒绝，使用新Maya会话。用户目录不安装userSetup/.mod，不写环境配置，不自动defer菜单。原startup所有菜单函数完整保留，只去import时print/deferred调用。显式加载cvwrap或执行绑定时安装其AE模板；真实Qt/AE/菜单待验收。29个原菜单SVG未提供，补了清楚标识的本地两字母SVG，原图像逐字节保留；不能把这些占位图算上游素材。

```python
tool = load_tool()  # 候选launch_candidate.py
print(tool.run(action='status').to_dict())
print(tool.run(action='create_wrap', objects=['surface','driver'], dry_run=True).to_dict())
# 插件未加载时上述预检明确失败；不能凭空模拟cvWrap变形结果。
```

launcher提供统一入口和show_ui。晋级清单完整镜像代码/资源/知识/测试及注册面板，真实验收通过才使用promotion。与core复用Base/Undo协议，不迁第三方底层到core；cvWrap/RBF与普通skin weight转移是不同任务，不声明已验证组合。可人工按建rig→cvWrap/RBF→动画检查顺序验收，跨工具组合尚未实测。

原anim_picker MIT、Qt/six头与Ingo Clemens MEL MIT通知保留；不推断整个混合包的公开发布授权。4组离线检查证明字节/定义完整、80 UI和29 SVG可解析、Schema与命名空间防冲突、独占路径和安全pickle；2组隔离Maya2025证明只读依赖预检保持场景/选择/时间/Undo/插件/sys.path，以及完整4个MEL可source。编译插件缺失是真实失败记录，不用mock冒充完整套件通过。
