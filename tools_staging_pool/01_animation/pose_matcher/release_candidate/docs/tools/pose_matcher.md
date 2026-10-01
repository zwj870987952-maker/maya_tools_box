# Pose Matcher：骨架方向对齐和网格合并/拆分候选

状态 prepared_unverified；原界面、MetaHuman/DAZ生产骨架、skin影响和真实模型运动/表面品质尚未人工验收。全部候选留待整理库。55原函数及完整原生 cmds UI保留，upstream/PoseMatcher.py.original是49691bytes原文件字节归档，catalog.json记原文件与完整native AST改稿SHA256，全改动diff在同目录。原文件没有作者/独立license声明，仅本地个人整理，不发布。

## 功能与完整性

骨架部分保留基础名匹配、namespace/prefix检测、默认6组手臂及30组手指映射、映射表增删/同步/自动识别、JSON新旧格式、方向/LRA、jointOrient/rotateAxis/rotateOrder矩阵与twist父级跳过、同父只处理一次的完整原算法。只写目标父joint.rotate，不改jointOrient、bindPose/权重、source骨架或层级；旋转可能改变蒙皮外观，不是bindPose修复或动画重定向。

网格部分保留MFnMesh数组读取、NumPy十进制round/intersect1d重合识别、顶点合并映射、UV平移、法线拼接、face-corner映射、OBJ与MergeInfo以及拆分重建的完整流程。交集只给每组重复坐标的第一匹配对，不是merge-by-distance，也不焊每个输入内部的重复点。源几何只读，新网格为世界坐标/identity transform，无蒙皮/动画/history迁移，创建独立Lambert/SG，不复用原材质。

maya_toolkit/tools/pose_matcher内有tool/runtime/native/ui_bridge/progress/mesh_command/mesh_plugin/catalog/upstream；docs/tools/pose_matcher.md、tests/test_pose_matcher.py和隔离mayapy测试均镜像正式目标目录。复用BaseMayaTool/ToolResult/Undo核心协议，不改生产core。现有几何/字符串能力与原方向算法不是无验收可替换关系；可记录组合，不提前下沉公用实现。

## API 与参数

tool_id=pose_matcher，action默认inspect。inspect返回选择与条件；align调用原矩阵对齐；detect在两个root内匹配唯一相同leaf名；load_map只读JSON；save_map明确写JSON；overlaps只返回两网格重合indices，不改选择；merge写OBJ+MergeInfo并造一网格；split读MergeInfo，写Part1/Part2 OBJ并造两网格；open_ui/close_ui管理私有原窗口。

source_root/target_root要求各为一个独立joint根，两棵树不得重叠。joint_map是source leaf→target leaf的非空字典，最大5000项，不含path/namespace；也可map_path载入dict或旧[{mh_joint,daz_joint}]。重复leaf/缺骨/root没有父/零长度方向、目标写joint被锁/引用/已有rotate键或driver、实例、目标链scale!=1或shear!=0拒绝。原twist跳过后的真正写父也必须在目标root内。按映射顺序执行，原同父只处理一次；根本身不能作为映射目标child。目标已skin时先备份测试，不宣称安全调整bind/rest pose。

meshes明确有序transform列表，省略沿用选择；merge/overlaps恰好2个，split恰好1个。每transform恰有1个nonintermediate polygon shape，不支持实例/组件/无完整UV的模型。decimals是0..8整数，默认3；坐标round后交集识别，非距离阈值。总顶点<=200000、face corners<=600000、UV/normal数组<=600000，有限/非负合法整数索引；每面至少3corner、连续face id。原逐行NumPy叠加在大模型仍可能慢，界面可取消，未承诺性能。

output_path是明确已有父目录中的输出；merge须.obj，副文件为同stem_MergeInfo.json；split把suffix去除作前缀，再加_Part1.obj/_Part2.obj；save_map按完整路径。map_path是只读map或拆分Info输入，最大64MB；输出不能覆盖输入。overwrite默认false，任一文件已存在整组拒绝；true明确允许替换，GUI对整组再展示Replace/Cancel。

validate/dry_run只读，不开GUI/创建shape/plugin/文件/改变选择、AutoKey、Undo或namespace。Maya mesh读取会触发必要的outMesh求值，不写拓扑。ToolResult.data返回映射/原parents、overlap indices、created_meshes与written_files；失败包含真实errors和已经写出的文件。失败不自动回滚场景，单次Undo恢复；文件不能Undo，批次文件只保证逐文件发布，部分失败可能已有输出。

```python
import runpy
tool = runpy.run_path(r'E:/GitHub/maya_tools_box/tools_staging_pool/01_animation/pose_matcher/release_candidate/launch_candidate.py')['load_tool']()
tool.run(action='open_ui')
tool.run(action='align', source_root='source:root', target_root='target:root', joint_map={'upperarm_l':'l_upperarm'}, dry_run=True)
# 明确已有临时父目录，不使用生产资产路径验收：
tool.run(action='merge', meshes=['meshA','meshB'], output_path=r'E:/Temp/merged.obj')
tool.run(action='split', meshes=['<returned created_meshes name>'], map_path=r'E:/Temp/merged_MergeInfo.json', output_path=r'E:/Temp/restored.obj')
```

## 行为修复与撤销

骨架修复零向量/acos浮点越界、缺DAZ joint先访问parent、根无父、重复basename歧义、Euler.reorderIt返回值依赖（使用被重新排序的Euler本体）；原矩阵/JO/RA/parent delta算法保留。原align内部异常被warning吞掉现返回errors/processed_parents，由ToolResult报告部分失败。完整debug aimConstraint helper保留但不作为公开API使用，主算法不调用它；用户不应调用native内部写函数。

网格原getVertexNormals数组却用face-vertex normal IDs索引，会破坏硬边/越界；改getNormals与getNormalIds配对。修第二模型face id偏移错误（face-corner行数→实际face数）；ProcessUV先复制输入，碰到tile bounds重叠时第二组沿U平移到第一组最大U边界，修误用V上界及相同U起点漏平移；拆分仍恢复原各自UV坐标，不传播用户在合并mesh上的UV编辑。

MergeInfo新增candidate_format=2与merged_faces拓扑证明。拆分仅接受候选生成的版本2，核对当前face id/vert ids顺序完全一致，再按face-corner取当前法线、按map_v取当前顶点，分别恢复原各部分UV/face拓扑。允许合并模型改位置/法线；变拓扑、重排vertex/face、旧无normal/topology证明的MergeInfo明确拒绝，不猜索引。原SplitMeshes完整主体仍可追溯，但实际GUI/API走校验后的完整拆分流水线。

原MFnMesh直接造scene节点不能靠普通UndoChunk保证回滚；新private MPxCommand在MFnMeshData中按原点/face/UV/normal算法造geometry，再用MDagModifier创建transform/mesh、附cachedInMesh和Undo/Redo；仅实际造mesh时加载，不autoload，不在还有Undo时卸载。command/data支持ma保存重开，实际检查过geometry和撤销。名字加清洗前缀+UUID，Lambert/SG自动新建，不覆盖现有node；plugin是命令而非自定义节点，保存scene不需要插件节点类型。迁入正式路径或重载候选时需重启Maya避免同名命令来自另一copy。

finally逐项恢复selection/time/AutoKey/refresh/absolute namespace/relativeNames；输出mesh不自动留为当前选择。进度仅持有自建progressWindow，取消抛错、finally关闭，不返回半个数组并发布。源UI完整布局/private名称保留，按钮桥接API；映射删除改按两表共同row index，sync finally清flag，reset接受Maya回调参数，namespace检测去掉DAG路径前缀。对齐不再自动保存映射，使用原Save Map明确保存；拆分另选输出前缀，不静默写到输入JSON旁边。

## 文件与组合边界

输出先写同父目录唯一临时文件夹，再原子hardlink禁止覆盖、或显式overwrite核对先前内容SHA256再os.replace。只有自有TemporaryDirectory清理；OBJ/JSON没有Maya Undo，部分发布结果在fail.data.written_files列出。无自动建父目录、没有export/import scene或用户设置/shelf/userSetup安装。原JSON map兼容旧列表和新dict，错误/空值/重复行严格拒绝，不默默吞错。

骨架对齐输入是source/target映射与当前pose，输出是target父旋转，可接用户已验收的pose/retarget流程，但对含动画驱动joint拒绝；不把方向对齐当动画transfer。网格merge输出新geometry与Info，可接仅改位置/法线且保拓扑的雕刻操作，再split恢复两个网格。Info与OBJ要一起保管；UV编辑/重拓扑/顶点重排、skin绑定或原材质重建不在此往返契约内。组合关系仅候选建议，未真人实测。

## 验证证据与晋级

普通Python2组检查55全函数/原bytes hash、Schema与惰性Maya import。Maya2025隔离4组：dry/inspect/overlaps不改变场景/文件/Undo；原向量角度与UV复制/平移；六rotateOrder真实joint对齐+Undo、锁拒绝；普通/旧map读写与覆盖拒绝、before-publication故障finally；硬边cube合并→ma保存/重开→拆分顶点/UV/拓扑/face normals匹配、真实Undo/Redo、源文件保持及after-geometry故障Undo。没有构造UI、使用生产资产、证明任意骨架JO/RA/twist或复杂拓扑可用。

临时正式布局检查完整payload、tool registration/面板/Schema，不改变真实maya_toolkit。按acceptance.md真人验证成功且满意后，再用promotion.json与promote_candidate.py；本轮不apply、不转正、不Obsidian同步。

API依据：[Autodesk MeshData](https://help.autodesk.com/cloudhelp/2024/ENU/MAYA-API-REF/cpp_ref/class_m_fn_mesh_data.html)说明数据块承载geometry；[官方polyPrimitiveCmd示例](https://help.autodesk.com/cloudhelp/2024/ENU/MAYA-API-REF/cpp_ref/poly_primitive_cmd_2poly_primitive_cmd_8cpp-example.html)说明mesh的inMesh与cachedInMesh输入。候选实现与Undo证据来自本机Maya2025隔离检查，不把示例当验收。

## 原函数完整索引

| 函数 | 原起止行 | 说明 |
| --- | --- | --- |
| `get_base_name` | 12..14 | 完整主体在native.py/upstream，适配见diff；存在不等于实测 |
| `apply_global_rotation_to_vector` | 16..19 | 完整主体在native.py/upstream，适配见diff；存在不等于实测 |
| `getlocalRotation` | 21..22 | 完整主体在native.py/upstream，适配见diff；存在不等于实测 |
| `calculate_angle_3d` | 24..32 | 完整主体在native.py/upstream，适配见diff；存在不等于实测 |
| `get_joint_lra` | 34..60 | 完整主体在native.py/upstream，适配见diff；存在不等于实测 |
| `get_joint_global_lra` | 62..91 | 完整主体在native.py/upstream，适配见diff；存在不等于实测 |
| `findClose0or180` | 93..99 | 完整主体在native.py/upstream，适配见diff；存在不等于实测 |
| `getAimUpVector` | 101..114 | 完整主体在native.py/upstream，适配见diff；存在不等于实测 |
| `rotate_joint_to_direction` | 116..125 | 完整主体在native.py/upstream，适配见diff；存在不等于实测 |
| `normalize_vector` | 133..137 | 完整主体在native.py/upstream，适配见diff；存在不等于实测 |
| `get_joint_position` | 139..142 | 完整主体在native.py/upstream，适配见diff；存在不等于实测 |
| `getGlobalRot` | 144..148 | 完整主体在native.py/upstream，适配见diff；存在不等于实测 |
| `getJointOrient` | 150..158 | 完整主体在native.py/upstream，适配见diff；存在不等于实测 |
| `getRotateAxisRot` | 160..170 | 完整主体在native.py/upstream，适配见diff；存在不等于实测 |
| `getRotOrder` | 172..174 | 完整主体在native.py/upstream，适配见diff；存在不等于实测 |
| `getAnimRotate` | 176..185 | 完整主体在native.py/upstream，适配见diff；存在不等于实测 |
| `getInherentRotWithoutParent` | 187..196 | 完整主体在native.py/upstream，适配见diff；存在不等于实测 |
| `get_parent_delta_global_rot` | 198..203 | 完整主体在native.py/upstream，适配见diff；存在不等于实测 |
| `getNeedRot` | 205..207 | 完整主体在native.py/upstream，适配见diff；存在不等于实测 |
| `align_parent_to_vector` | 209..247 | 完整主体在native.py/upstream，适配见diff；存在不等于实测 |
| `find_joint_by_base_name` | 249..258 | 完整主体在native.py/upstream，适配见diff；存在不等于实测 |
| `get_joint_direction` | 260..278 | 完整主体在native.py/upstream，适配见diff；存在不等于实测 |
| `resetTwist` | 280..292 | 完整主体在native.py/upstream，适配见diff；存在不等于实测 |
| `align_skeleton` | 294..355 | 完整主体在native.py/upstream，适配见diff；存在不等于实测 |
| `save_joint_map` | 357..365 | 完整主体在native.py/upstream，适配见diff；存在不等于实测 |
| `load_joint_map` | 367..390 | 完整主体在native.py/upstream，适配见diff；存在不等于实测 |
| `auto_detect_namespace` | 392..411 | 完整主体在native.py/upstream，适配见diff；存在不等于实测 |
| `sync_selections` | 414..444 | 完整主体在native.py/upstream，适配见diff；存在不等于实测 |
| `auto_detect_ns_cmd` | 446..463 | 完整主体在native.py/upstream，适配见diff；存在不等于实测 |
| `load_map_cmd` | 465..480 | 完整主体在native.py/upstream，适配见diff；存在不等于实测 |
| `save_map_cmd` | 482..503 | 完整主体在native.py/upstream，适配见diff；存在不等于实测 |
| `reset_table` | 505..524 | 完整主体在native.py/upstream，适配见diff；存在不等于实测 |
| `add_selected_cmd` | 526..542 | 完整主体在native.py/upstream，适配见diff；存在不等于实测 |
| `remove_selected_cmd` | 544..583 | 完整主体在native.py/upstream，适配见diff；存在不等于实测 |
| `add_finger_mapping` | 585..597 | 完整主体在native.py/upstream，适配见diff；存在不等于实测 |
| `auto_detect_cmd` | 599..648 | 完整主体在native.py/upstream，适配见diff；存在不等于实测 |
| `execute_alignment_cmd` | 650..692 | 完整主体在native.py/upstream，适配见diff；存在不等于实测 |
| `get_mesh_arrays_fast` | 702..741 | 完整主体在native.py/upstream，适配见diff；存在不等于实测 |
| `get_selected_meshes_numpy` | 747..773 | 完整主体在native.py/upstream，适配见diff；存在不等于实测 |
| `find_overlaps` | 779..800 | 完整主体在native.py/upstream，适配见diff；存在不等于实测 |
| `select_vertices` | 806..811 | 完整主体在native.py/upstream，适配见diff；存在不等于实测 |
| `detect_and_select_overlaps` | 817..823 | 完整主体在native.py/upstream，适配见diff；存在不等于实测 |
| `writeWithColor` | 829..858 | 完整主体在native.py/upstream，适配见diff；存在不等于实测 |
| `ProcessVertices` | 860..888 | 完整主体在native.py/upstream，适配见diff；存在不等于实测 |
| `is_overlap` | 890..904 | 完整主体在native.py/upstream，适配见diff；存在不等于实测 |
| `ProcessUV` | 906..915 | 完整主体在native.py/upstream，适配见diff；存在不等于实测 |
| `ProcessVN` | 917..918 | 完整主体在native.py/upstream，适配见diff；存在不等于实测 |
| `ProcessFaces` | 920..947 | 完整主体在native.py/upstream，适配见diff；存在不等于实测 |
| `MergeMeshes` | 949..969 | 完整主体在native.py/upstream，适配见diff；存在不等于实测 |
| `SplitMeshes` | 971..995 | 完整主体在native.py/upstream，适配见diff；存在不等于实测 |
| `assign_lambert_to_mesh` | 997..1004 | 完整主体在native.py/upstream，适配见diff；存在不等于实测 |
| `build_mesh_from_numpy` | 1006..1048 | 完整主体在native.py/upstream，适配见diff；存在不等于实测 |
| `MergeMeshes_cmd` | 1055..1074 | 完整主体在native.py/upstream，适配见diff；存在不等于实测 |
| `SplitMeshes_cmd` | 1079..1088 | 完整主体在native.py/upstream，适配见diff；存在不等于实测 |
| `create_alignment_ui` | 1092..1248 | 完整主体在native.py/upstream，适配见diff；存在不等于实测 |
