# 模型逐帧转 BS 与 FBX

原稿无UI，直接取第一个所选模型组、整数播放范围，生成复制基模/每帧blendShape target、根joint和SmoothBindSkin，随后用户手动导出新group。候选保留完整生成/手动导出流程，并提供小面板及显式build_export。移除缺失PyMel依赖，使用cmds/API2；原文件SHA归档。

## API与数据

`PerFrameBsFbxTool`，id per_frame_bs_fbx，pipeline_io。默认inspect只读，root为精确mesh transform/group名称或UUID，省略只允许选中一个transform/group。start/end默认播放min/max；step默认1，有限正数、小数范围必须落在采样网格，1..2000帧、总顶点快照<=1000万。output_group是新简单名称，默认 `<root叶名>_FbxExpGrp`，已存在拒绝而非复用旧group。copy_materials默认True；ascii用于FBX。build_export要求output为全新绝对.fbx，目录已有，永不覆盖。build只生成可手动导出group；output不会隐式改变build行为。

```python
from maya_toolkit.tools.per_frame_bs_fbx import PerFrameBsFbxTool
tool=PerFrameBsFbxTool()
preview=tool.run(root='modelGroup',start=1,end=24,dry_run=True)
result=tool.run(action='build',root='modelGroup',start=1,end=24)
# 或 action='build_export', output='D:/temp/new-shapes.fbx'
```

输出group/joint、每source mesh UUID/base/blend_shape/skin_cluster、frames、targets/space；FBX额外outputs文件大小/路径。所有非intermediate mesh分别处理，避免对整个多模型group含混使用blendShape。mesh UV/拓扑基础复制，copy_materials复制每face原SG分配，新增导出mesh加入已有材质集合（引用材质可能记录membership reference edits），不改源mesh顶点/曲线；动画材质/visibility/customattrs不转换。output hierarchy扁平identity meshes+单rootJoint，不保留原控制rig层级。源mesh可以只读引用，但真实共享DAG mesh实例拒绝，误选多对象/组件/无mesh拒绝。

## 算法、场景与文件影响

每采样帧读取MFnMesh世界坐标（包含source deformer和父级transform运动），转换为identity输出mesh的物体坐标，blendShape origin local。每mesh每帧一个target，weight在 frame-step/frame/frame+step 为0/1/0，linear切线，因此采样帧精确再现，采样间线性插值不等于原连续模拟结果。删除临时target后shape数据仍存BS；单根joint刚性skin每顶点权重1，joint逐帧keys供FBX识别动画。创建原生BS在skin之前，避免源控制系统复制进输出。

原稿复制动画对象的局部顶点可能遗漏父级运动，改世界坐标快照；原重复已有group路径下root_joint未定义，不再reuse；原range(int...)截断小数尾帧，改网格明确验证；不用别名/MEL目标名称拼串访问weight，直接weight索引；不更改modelPanel。拓扑改变在运行中发现即拒绝并清理本操作新UUID（group、mesh、BS、skin、bindPose、curves等），不删除原对象；模拟/插件的求值副作用、失败清理极端情况待验，不承诺任意动态系统无影响。

build是场景写入，标准UndoChunk统一一次Undo，Redo恢复生成结果；正常保留有效原选区/time/AutoKey/绝对namespace。世界空间采样需currentTime逐帧求值，动态/缓存应先确保来源已正确预热，输出体积按mesh*frames*vertex增长。readonly validate只查当前拓扑和预算/路径，不跳时间、不生成骨骼/mesh、不加载FBX插件，不宣称已遍历验证全时域拓扑。

build_export使用自包含FBX helper（基于fbx_batch_exporter_v7的状态还原及独占输出，不依赖另一个待池路径），明确导出shape/skin/animation，embeds关闭，格式FBX202000/轴Y，可以ASCII。捕获并还原所用FBX全局设置、四播放范围、时间/选区/AutoKey，实际加载fbxmaya非Undo；插件可能生成日志，文件输出不能Undo。导出失败仍返回已生成BS组供检查/Undo，不声称FBX成功；Undo场景生成不会删除已输出FBX。

## 验证和复用

复用Base/ToolResult/Schema、外层Undo、API2mesh读取；世界空间几何采样不直接冒用world_transform_v4矩阵快照，不重复搬入core。输出group可交给fbx_batch_exporter_v7分段导出；不同步原source rig到UE，模型/skin/morph曲线在UE必须实测。全部代码、原件、文档、测试和注册/面板晋级预制。

隔离检查实际两mesh/源BS形变+父级位移、每帧世界顶点/脉冲target/skin、单UndoRedo和源图不变；实际ASCII FBX输出并重导入BS/skin/两mesh/顶点，已存在输出拒绝、实例/网格拒绝；GUI/长序列内存/动态模拟/引用SG/复杂拓扑切换/UE消费/跨版本not_run，prepared_unverified，集中验收见acceptance.md。
