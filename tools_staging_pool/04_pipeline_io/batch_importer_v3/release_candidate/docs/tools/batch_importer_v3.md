# 批量导入与引用 V3 候选

`batch_importer_v3` / `pipeline_io`，原单文件及by ZWJ水印逐字节保留；未提供再分发授权，不推断许可。完整原Qt主窗口、文件/递归文件夹按钮、References/Import/Delete列表项/Del Ref、逐行namespace名称与1..9999次数框、列表多选、水印保留。导入时不构造QApplication；Qt6/Qt5 lazy条件适配并把Python2 long指针转int，真实两绑定版本尚未GUI验收。文件夹取消不再直接索引空值；namespace框可编辑以解决冲突。

## API与预检

- `action=inspect` 默认只读，需要非空 `items:[{path,count=1,namespace?}]`。支持绝对存在 .ma/.mb/.fbx/.obj/.abc，只读文件SHA；按行和count生成namespace base/base1/base2。默认base为完整stem的ASCII安全标识（不再把多点文件截到首段），用户可指定简单标识。所有路径/类型/count/字段、全部计划名及当前已有namespace冲突先整批拒绝，合计<=10000实例。dry不读文件为scene、不注册command、不加载translators、不改selection/time/AutoKey/namespace/Undo队列。
- `action=import` Maya原生file import；禁止scriptNodes、namespace clash自动合并、共享材质网络合并。执行才加载fbxmaya/objExport/AbcImport等需要的native translator。单独MPxCommand记录本次新DAG/DG UUID，以MDagModifier支持所有新节点一次Undo/Redo，Redo不重读源文件。保留空namespace保证Maya2025 API恢复名字可被查询；每次新导入选新namespace，手工删除保留namespace后Redo拒绝。
- `action=reference` 原生文件reference，禁scriptNodes；每份新引用记录独占RN UUID/文件SHA/namespace。Undo仅删除这些RN的整份引用，Redo需原路径存在且SHA不变，并重新读取原文件；RN/引用节点UUID可能改变，重新inspect，而不是使用旧结果身份。插件自动加载和namespace本身非全量sceneUndo保证；FBX/OBJ/ABC reference可用性取决实际translator/Maya版本，未实测支持不能标已通过。
- `action=remove_reference` 指定 `objects`（整体引用成员或shape）或精确 `reference_nodes`，否则当前选择。每个对象必须referenced；同一RN去重。预检返回整份reference的节点/源路径/namespace/load状态；删除单个选中mesh会移除同一RN的所有对象，不是只删选择。只接受顶层、无reference edit、源文件可读且简单namespace的reference；nested/编辑过/缺源等拒绝，不冒充可以完整恢复复杂referencing图。删除的Undo会从未改SHA的源文件重建引用、恢复原RN名称及loaded状态和可恢复选择；UUID可能变化。Redo再删本次重建RN，绝不按filename泛删所有重复引用。
- `items`与删除scope互斥，unknown keys/空项/非bool整数边界等均实际检查。引用删除不是清理namespace或删除外部文件。Maya默认锁住RN元数据，本API使用原生file removeReference操作，不因标准元数据锁误拒绝，也不手动解锁它。原用RuntimeError悄悄跳过多项错误，候选报告具体失败和全表边界；异常仍可能部分native操作，框架不会自动rollback，需检查scene及一次Undo支持范围。

## 输出和影响

inspect data.tasks/count；remove dry data.references/whole_file_reference_removal=True。import/reference data.imports、created_uuids/namespaces/mode；删除 data.references/removed=True。所有均ToolResult。导入新增scene节点与native插件；不覆盖/保存源文件、不写用户preferences/shelf；保持有效原selection、current time、AutoKey/current namespace。删除时原选中的引用节点不存在，所以selection保留仍活的原节点；Undo恢复按原名称可重新找到的选择。Maya文件解析仍可加载requires插件，复杂renderer节点及外部texture路径依赖不能靠scriptNodes禁用解决。

内部关闭子命令Undo记录而保留现有队列，由自己的独占command管理lifetime；command路径不同的其它候选占用同名命令时明确拒绝，dry没有plugin副作用。普通import failure仅清本次UUID，不泛删旧scene；reference failure清自己已成功创建RN；删除native失败可能部分已移除reference，具体错误记录，生产复杂情况待集中复验。

```python
from maya_toolkit.tools.batch_importer_v3 import BatchImporterV3Tool
t=BatchImporterV3Tool()
args=dict(action='import',items=[dict(path=r'E:\\temp\\asset.ma',count=2,namespace='assetA')])
if t.run(dry_run=True,**args).success:
    print(t.run(**args).to_dict())
```

组合候选：`asset_it_v1_2`查询完整图库相对路径，取其library/relative拼成此API绝对path；`abc_batch_exporter`生成ABC后此工具导入；`replace_references`处理不同源替换（待自身验收），此工具只创建/删精确scope。不改正式core/FBX工具；现有Base/ToolResult/Undo框架复用。原UI只可Qt交互启动，所有scene业务同Base/API。

真实GUI/递归目录控件/五translator全部import及reference形式/复杂nested或编辑reference/跨版本 not_run；Maya2025隔离场景和目标布局结果见manifest，prepared_unverified。候选完整业务/UI/Schema/知识/测试/promotion齐备，人工满意前留在池内。
