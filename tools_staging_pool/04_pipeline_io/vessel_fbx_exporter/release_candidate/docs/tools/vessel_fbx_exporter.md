# 舰船选择集自动 FBX 导出

原脚本完整SHA归档，无原UI，导入即依次烘焙All_joints、清空Reset_Trans动画并重置、导入全场references、选择_FBXExport集/移除namespace、输入关键词导出、rename root。候选保留全部业务阶段/原TRS默认值/原FBX选项/可选结果引用函数，但整套流程只在当前场景的独立临时副本里做；调用者dirty/untitled场景、references、keys、namespace、Undo保持。新增简易预检/选项/目录/关键词面板，import不再执行场景写入。

## 标准协议

`VesselFbxExporterTool` / vessel_fbx_exporter / pipeline_io / BaseMayaTool、ToolResult、Schema。默认action=inspect只读集合/实际成员/引用文件/范围/输出预览；process才导出私有snapshot.ma、启动matching mayapy。output_dir为绝对目录可不存在（执行时创建），省略使用已保存源目录FBXExport，untitled必须明确给目录。keyword默认scene stem（无路径时untitled），原AAA替换；集合名去除_FBXExport并替换AAA，namespace冒号转换下划线，安全文件名全表检查，existing/同批collisions拒绝，不覆盖。

start/end默认min/max，范围有限且跨度<=100000。bake_joints/reset_transforms/import_references/remove_namespaces/rename_root默认True，reference_results/save_prepared_scene默认False（原结果引用是注释关闭），ascii/embedded_textures原默认True。reset_values九个有限TRS数，默认[0,0,0,-90,0,0,1,1,1]，按Maya当前UI单位，不是freeze transform。timeout10..3600默认300。结果outputs文件/bytes、prepared_scene可选、新副本events、caller_scene_preserved。

原备用bake_animation_for_export_sets函数通过bake_export_sets选项保留，默认False与原注释调用相符，显式True对导出集合成员做原生simulation烘焙，仍只修改副本；不假称此额外分支已生产实测。

```python
from maya_toolkit.tools.vessel_fbx_exporter import VesselFbxExporterTool
tool=VesselFbxExporterTool()
preview=tool.run(output_dir='D:/temp/ship',keyword='ship',dry_run=True)
result=tool.run(action='process',output_dir='D:/temp/ship',keyword='ship',save_prepared_scene=True)
```

## 私有场景业务与影响

1. exportAll复制当前全部场景含references、未保存修改到独有临时MA，不rename/save原文件。child使用原workspace解析相对资产路径，scene scriptNodes关闭、私有MAYA_APP_DIR存插件日志；全场reference必须已loaded/源可读，不能猜未加载资产可安全导入。
2. 仅副本原生importReference全场引用，包括顶层/嵌套，直至无reference；保留原整场处理范围，非只导出集。与原顺序不同，先导入再bake/reset，避免改referenced成员生成后被import丢弃的编辑；明确记录为候选行为变更。
3. All_joints标记集（字面包含，不假定全部成员是joint）原bakeResults simulation/sample1/preserveOutsideKeys/minimizeRotation等flags；Reset_Trans标记集把成员全部动画keys（包括非TRS custom attrs）cutKey，再TRS设预设值，首帧setKeyframe原可keyable attrs。这是原脚本破坏性行为，保留且预览写明，仅作用副本。锁或非animCurve驱动Reset TRS前置拒绝；不绕锁和断连接。
4. _FBXExport集合/成员namespace mergeRoot，会搬该namespace中其他副本节点、可能自动改重名；不改调用者namespace。绑定真实set UUID跟随名称变化，嵌套sets有界展开，组件/非transform成员或循环拒绝。原集empty跳过，全部empty则拒绝无意义流水线。
5. 原生FBX选中成员及子层级：smoothing/smoothMesh/shape/skin/cameras/includeChildren、animation、ASCII、embedded textures、inputConnections=False、axisY、FBX202000；原invalid file-version -v语法修正；所改FBX设值finally逐项还原，无Push/Pop落盘。所有输出经自有临时结果→xb独占目标，不覆盖已有file。每导出后原root按已有root_NNN序号重命名一次，发生在副本，因此首份/后份root名称可能不同，保留原时序并待UE实测。
6. reference_results可显式启用，仅副本引用导出FBX/选结果namespace；save_prepared_scene另存 `<keyword>_prepared.ma`，以查看原bake/reset/import/namespace/root结果，正确ASCII且不覆盖。原reference_exported_fbx语义保留，不把新引用写入调用者。

外部FBX/目录/可选prepared MA/插件日志非Maya Undo；GUI是同步等待一child，超时终止可能保留已完成输出/自有临时，失败不回滚外部file，需查结果目录。工作进程无Maya用户界面，原动态模拟、插件求值、脚本依赖GUI或私有外部写入未保证隔离；scriptNodes禁用不等同文件系统沙箱。调用者exportAll及source graph serialization的插件副作用需实际生产样例验收，不承诺第三方插件完全无外部影响。

## 复用与验证

核心读取set/范围/锁复用cmds，采用框架标准API；自包含FBX helper取自fbx_batch_exporter_v7、独占MA保存取自replace_references同语义，不依赖其他待池路径。输出可以交给UE导入，但UE材质/根骨骼名字/坐标轴必须真人验证。

隔离Maya2025完整dirty场景native exportAll→真正child、原source引用/动画/选区/time/AutoKey/Undo全保持；副本引用导入、namespace去除、root_001、baked1/2/3和reset/custom全部cut/首帧keys，真实FBX再导入模型、新MA读取，已有输出/坏后行锁/无集拒绝。GUI/嵌套reference/动态simulation/全部原FBXflags/UE/跨版本not_run，prepared_unverified，acceptance.md复验后才晋级。
