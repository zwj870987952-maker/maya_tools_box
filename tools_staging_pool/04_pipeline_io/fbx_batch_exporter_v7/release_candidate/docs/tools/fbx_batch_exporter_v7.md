# 分组分段 FBX 导出 V7

原两脚本（V7主窗及配套预设）完整SHA归档；保留完整native form布局、两列表/计数/增删、时间滑条高亮范围、prefix、所有FBX复选框/轴/版本、导出、配置管理、关闭SSC、层级烘焙及by ZWJ水印。模块导入不再创建窗口。类 `FbxBatchExporterV7Tool`，tool_id fbx_batch_exporter_v7，类别pipeline_io，BaseMayaTool/ToolResult/Schema/UndoChunk遵循正式协议。

## 参数与结果

默认 action=inspect，jobs为1..1000条 `{objects:[精确transform/joint名或UUID],start:有限帧,end:有限帧,filename:可选安全.fbx名称}`。output_dir显式已有绝对目录，可省略使用当前已保存场景目录；untitled必须给目录。prefix为安全文件名前缀；所有路径、坏后行、范围、对象、文件名一次性预检，不按原稿min(列表长度)静默忽略多余条目。支持小数帧和高亮end-exclusive→包含结束帧的转换。默认文件名按首组对象的namespace/范围或leaf/index生成；DAG路径字符规范化，已有文件和本批重复名追加序号，保留prefix。最终使用独占xb写入，前置规划后目标被其他进程占用仍拒绝；已完成输出不会随后行错误撤销。

options包括 export_animation/input_connections/ascii/smoothing_groups/smooth_mesh/referenced_assets/triangulate/skins/cameras/embedded_textures 布尔值，up_axis=Y/Z，file_version为原UI列出的FBX202000/201900/201800/201600/201400/201300/201200/201100/201000/200900。按原默认保存，精确含义由原生FBX插件定义：embedded_textures是嵌入贴图，原标签“包括子对象”错误已修正；层级选择始终选group roots和子层级。input_connections=True可能导出其他连接网络，请审查数据范围。旧格式可选不等于本机插件确已支持，插件拒绝则返回失败。

```python
from maya_toolkit.tools.fbx_batch_exporter_v7 import FbxBatchExporterV7Tool
tool=FbxBatchExporterV7Tool()
args=dict(jobs=[{'objects':['model'],'start':1,'end':24}],output_dir='D:/temp/export',prefix='shot',options={'ascii':True,'embedded_textures':False})
preview=tool.run(dry_run=True,**args)
result=tool.run(action='export',**args)
```

export返回tasks/options/count和outputs，每个output含objects/start/end/output/bytes。inspect/dry不加载FBX插件、不设导出全局选项、不改选区/时间/播放区间/Undo、不创建文件。实际export加载fbxmaya（插件加载不是Undo），原生选择导出到同目录自有临时子目录，再独占复制目标。FBX导出和JSON写入不能Maya Undo；临时目录正常退出清理，但中断可能残留。

## 设置、烘焙与SSC

`save_settings`要求settings_path指向已有目录中的全新JSON和configuration={version:1,jobs,prefix,options}，只读schema验证后独占写，不自动覆盖共享fbx_exporter_settings.json。`load_settings`有限2MiB、UTF8/BOMJSON，完整校验返回configuration，不修改scene/UI；UI通过文件选择加载后填控件。兼容两原配套预设objects/time_ranges与复选框键名，缺export_animation用原默认True，数量不匹配/非法类型/NaN拒绝。untitled配置管理不再os.path.join(None,..)异常。

`bake`要求objects/start/end，选中transform/joint及后代，原生bakeResults simulation/sampleBy=1/shape=True/preserveOutsideKeys等V7完整flag保留，逐帧烘焙是明确场景写入。全表拒绝引用节点/锁节点/锁keyable属性，恢复有效选区/时间/AutoKey，一组Undo。复杂动画层、控制器、自定义插件或约束求值须人工验收，不承诺原生bake可保全所有业务关系。`disable_ssc`要求明确joint列表，全表拒绝引用/锁/driven SSC，设segmentScaleCompensate=False，一次Undo，可能改变骨架scale继承。

实际export捕获每项被改的FBX命令值、动画property、当前时间/选区/AutoKey和四个播放范围，finally恢复；不调用会落盘的FBXPushSettings/FBXPopSettings（本机Push尝试写设置文件失败），也不ResetExport覆盖未使用设置。恢复期间关闭Undo记录但保持原队列；实际文件export不成为可撤销文件写入。原稿只保存animationStart/End再误覆盖min/max，改四值独立恢复；prefix碰撞丢失、未加载插件、MEL路径引用和异常后状态未恢复均修正。

## 复用和验收

与abc_batch_exporter使用相同文件输出可组合约定，但FBX属性和SSC/bake属于具体业务不下沉core。可从world_transform_v4场景动画产生jobs，导出到UE导入工具；只为接口关系，未声明真实UE生产组合验证。注册/面板及全部代码/原件/docs/tests晋级清单预制，验收前不改正式库。

离线原件SHA/schema/legacy配置、坏范围/名字；隔离Maya2025真实ASCII FBX导出并导入回读模型/动画，碰撞序号保prefix、FBX及四播放范围/Undo队列恢复，真实SSC/约束对象烘焙一次Undo，配置新文件及已有JSON不覆盖、坏后行不写。GUI/highlight/所有flag和旧格式/embedded resources/生产动画层及跨Maya与UE尚未验收，prepared_unverified。详细步骤见acceptance.md。
