# AssetIt 1.2 完整原套件候选

`asset_it_v1_2`，`pipeline_io`。完整978文件约159MB：18个Python源码、225个函数、293份MayaASCII（290个图库资产及3个创建模板scene）、354张PNG、309份JSON、HDR EXR/TX与启动JPG。保留原资产浏览、标签/子标签、搜索/收藏、元数据、导入/参考/放置/替换/拖拽、缩放、重命名/删除、单资产与场景/文件多资产创建、Arnold缩略图/相机、主题/尺寸/偏好等全部原代码/UI与资源。目录 `bundle/AssetIt` 可按原安装方式执行，含Qt.py；旧Drag安装器逐字节归档为 `.py.original`，候选从不执行它的move/rmtree/shelf写入。

原 `AssetIt_License.txt` 保留完整；其范围为个人非商业、不可转让，明确限制修改、第三方分发。候选未修改18源码或推断更宽许可，单独写适配层。本地整理/复制不表示允许商用或向第三方发布；晋级前仍需用户核对自己的使用授权。原suite代码与资源逐文件SHA记录catalog，原Preferences保留原作者路径，不悄悄改写归档。该候选不是去license或把套件宣布为开源。

## 标准适配API

- `action=inventory` 默认只读，不导入任何nativeQt/Arnold/PyMel模块。`library` 为绝对目录，默认包内AssetIt_LIBRARY。输出assets（relative/bytes/thumbnail/metadata）、count、library、license_path、native_code_modified=False。这是完整模型清单，不预加载全部模型。
- `action=metadata` 指定相对 `.ma` `asset`，必须严格在library内，拒绝绝对/..路径与逃逸symlink；读取同名有限JSON，返回asset/relative/metadata/thumbnail。缺可选metadata显示None，不伪造说明。
- `action=import_asset` 需上述asset及简单、未存在namespace，`scale=1`正有限。调用 native file import，禁止执行script nodes、禁止与原namespace/材质网络自动合并，用独占新namespace和group控制统一缩放，返回完整DAG group路径/created/created_uuids/namespace/scale与metadata。保留输入选择、时间和AutoKey/current namespace；不设置placement/渲染/偏好/贴图路径，不删除原scene对象。原生file import不支持外层Undo，adapter显式加载自己独占MPxCommand来记录本次所有新节点UUID，Undo删除这批节点、保留占用的空namespace，Redo从MDagModifier恢复节点而不重读文件。Maya2025中删除并重建namespace会导致恢复节点虽被ls列出却不能按名称查询，因此不承诺Undo清namespace；下一次导入使用新的namespace。手工删除保留的namespace后Redo明确拒绝。内部记录临时关闭但保留原Undo队列；dry不注册command。资产requires可能原生自动加载插件（本检查实际加载Arnold），插件加载及新增系统属性本身不保证Undo。异常只清本次UUID节点，不泛按namespace/名称删原scene。这是单独公共API；原复杂放置/拖拽/替换仍由完整nativeUI保留，不把它们假装成此入口已验算法。
- `action=install` 显式复制完整原版到新的target_dir（名称须AssetIt，父目录已存在），默认原Maya用户目录/version/scripts/AssetIt；已有目录/已import套件拒绝，不备份替换、不跑原拖拽安装器、不装shelf。复制仅新目标；原code/resources保持字节。运行时安装副本UserLibPath配置指向安装副本模型库，避免原作者C路径或原包内资源被原UI编辑；自定义library不得是本候选包，用户自行备份。复制与UserLibPath配置不由scene Undo撤回；失败可能留新目标部分副本，核对后由用户处理，candidate不自动递归删除任何旧库。
- `action=launch_native` 必须真实交互Maya，原version/scripts安装路径匹配，所有原PythonSHA匹配，UserLibPath存在，PySide2/shiboken2/PyMel/mtoa可发现且不存在固定thumbnail cleanup节点冲突；另一个同名包已加载拒绝。调用原AssetIt_UI.showUI，完整原UI/所有原算法都保留，不新造QApplication、不改原软件或移除授权。缺依赖返回真实失败并保留原库；不假装已有Qt条件就经过GUI验收。
- Adapter `show_ui` 提供inventory/启动预检/新复制安装/完整原窗口按钮，所有动作显式。模块import只准备class，不写用户目录、不装shelf、不读改真实偏好、不动scene。

所有参数实现严格类型/字段/scope检查，Schema仅描述不代替validate。dry_run 不复制、不导入、不创建namespace/group、不改UserLibPath，也不打开原GUI。复用BaseMayaTool/ToolResult/Undo；无正式core改动。与 `export_sets_to_fbx` / `abc_batch_exporter` 可衔接import输出group或created模型，但生产组合未验；此工具是模型资产库，不能替代骨骼/动画FBX导出。

```python
from maya_toolkit.tools.asset_it_v1_2 import AssetItTool
t=AssetItTool()
entry=t.run(action='inventory').data['assets'][0]['relative']
args=dict(action='import_asset',asset=entry,namespace='assetExample',scale=1)
if t.run(dry_run=True,**args).success:
    result=t.run(**args)
    print(result.data['group'])
```

## 原完整UI的真实影响

原代码不改，因此原高级回调没有被全部改造成此adapter的validate/Undo事务。原Delete直接rmtree资产文件夹，Rename/收藏/主题/元数据写文件不可sceneUndo；原OpenFile可替换scene；原batch/render/新增缩略图会改scene/renderSetup/optionVar/工具模式/固定名称helper；原showUI和关闭job会按固定名称清thumbnail节点。原import/template场景可能依赖作者贴图路径、Arnold或PyMel。启动前拒绝当前固定名冲突只是入口防错，并不等于所有未来native按钮都具有独占资源和可撤销保证。必须在备份库/备份scene手工验收这些完整功能。此限制随套件授权/原环境保留，不以离线解析或成功导入一个模型冒充完整legacy验收。

## 验证与晋级

包内978文件SHA、18源码解析、225函数与290图库模型metadata/thumbnail清单、目标布局注册、隔离Maya API/临时安装检查见manifest。原PyMel当前未安装，完整nativeUI依赖与生产渲染/拖拽/放置/替换/高级文件操作/跨版本 not_run，prepared_unverified。candidate完整native实现和所有素材已备齐，并非只有launcher。promotion镜像完整目标目录+文档+tests+注册，原GUI真实满意且授权条件确认前不晋级。工具GUI可能有新缺陷，集中验收发现后以允许的适配或合规版本解决，不擅改受限制原软件。
