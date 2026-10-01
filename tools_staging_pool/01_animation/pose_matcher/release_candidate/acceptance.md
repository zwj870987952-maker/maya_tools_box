# Pose Matcher 真人Maya验收（未运行）

在备份场景和已有临时文件目录使用launch_candidate.py load_tool/open_ui；不要runpy原自动入口。保存原pose/geometry与场景副本，所有文件写入不可Undo。

1. inspect与align/merge/split dry_run：选择/时间/AutoKey/refresh/namespace/Undo/文件不变；正常/缺map、缺joint、同名leaf、零长度骨/锁/引用/driver/无UV/实例/组件/超预算均合理返回。
2. 原Skeleton Settings、file、两列表、默认6组、手指30组、增删/同步/auto-detect、deep namespace、Browse/load/save、scroll/窗口关闭共存检查，无致命Script Editor错误。Save Map对已有文件询问整组覆盖；Align不再自动保存。
3. 单骨/多支链、六旋转order、JO/RA/父旋转、twist、同父多个映射、MetaHuman/DAZ真实rest pose，检查方向/父处理顺序和肌肤外观，一次Undo/Redo。源joint与JO/bindPose/权重不变；目标写joint已有键/driver/ref/scale/shear时预检拒绝。
4. 两个世界transform不同的cube/多边形（包含硬边和UV seams），overlaps indices符合十进制round首匹配语义；merge的OBJ+Info与新mesh形状/normal/UV/face数量匹配，源mesh/材质/skin保持。
5. 对合并mesh只改位置/法线，再split；两mesh原face/UV恢复、法线/位置随当前合并模型，分别新建Lambert。用.ma和.mb保存重开比对；Undo/Redo删除恢复新增mesh/material，已写OBJ/JSON保持。
6. 顶点/face重排或改拓扑、旧无证明MergeInfo、坏/过大JSON、错误map_v/face索引均应拒绝且不造输出。UV编辑不会传播到split，原各部分UV恢复，这不是UV/skin/history/material往返器。
7. 文件整组无覆盖/显式覆盖/Cancel、原输入JSON不得覆盖、同父temporary cleanup、中途取消/磁盘写失败与已发布部分文件fail.data；出错scene一次Undo恢复且selection/time/AutoKey/ns/refresh恢复。
8. 不覆盖他人progressWindow，关闭自己的窗口不关闭原版；重载/未来晋级更换plugin路径前重启Maya，保留Undo时不要手卸mesh命令plugin。

记录Maya/Python/NumPy版本、真实rig/shape条件、每组结果及Script Editor报错；隔离4组通过不代表这些真人步骤已过。完整候选需用户满意后按promotion.json晋级，许可未附独立声明仅本地不发布。
