# 旋转对齐工具

id `rotation_aligner`，域 `modeling_surfacing`。原1132行完整源码/SHA归档 upstream，全部函数/矩阵算法/完全两步/单轴最小变化30度搜索/原生窗口保留 native，去模块自动开窗，窗口私有命名。完整六个有符号对齐轴、旋转XYZ限制、多对录入/移除/清空、单帧右键跳帧、自定义/时间轴/烘焙、每帧迭代右键菜单与联动保留，执行两高层入口转Base API并增加预检。GUI/生产复杂骨架/其它版本not_run。

同目录原 `Maya简化角度工具_使用说明.md` 实际描述 AngleDisplayContainer/鼠标刷新/角度标注，和本旋转对齐源码不匹配；仍按原SHA归档，不把该说明中未提供的功能当候选能力。

务必区分作用：**source 是被旋转的第一个对象，target 是只读朝向参考**。原 native 通过世界矩阵、parent delta、jointOrient/rotateAxis/rotateOrder转换旋转，只写允许且未锁源 rotate 属性。完全对齐先主轴再绕主轴对其余轴，少于两轴可写退化单轴；单轴模式根据允许轴最优投影，多个轴以原30度采样减少Euler变化。原6选择中的up对象参数实际未被算法使用；候选不伪造up向量功能，API支持2/4选择或明确 pairs，6选择拒绝。child只作退化方向fallback，不宣称主轴必定指向child。

API参数同原 settings：full_alignment=False，rotate_axes全True，source_axis/target_axis='+Y'，time_mode='timeline'，custom_start/end=1，bake_all_frames=True，per_frame_iters=5(1..100)，time_next_frame=False(仅single)。pairs 每行source/target，可加对应后代 source_child/target_child，省略pairs使用当前2/4整节点选择。源/参考可普通transform/joint，明确UUID/全路径拒绝歧义、实例、自身、重复源；源不可引用/锁node，已锁旋转轴按原跳过，剩余需至少一个可写；约束/层/非直接动画驱动拒绝。single拒绝动画连接，range允许唯一不共享、不引用且未锁的直接animCurveTA；不自动断rig/删曲线。OPM源须identity，当前/运行各帧世界方向无shear/负反射/退化，jointOrient/RA和非XYZ原支持保留。

原所谓烘焙仅改currentTime与setAttr，从未setKeyframe，执行后仅余最后姿态。候选明确修正：range 对有效源旋转轴实际 setKeyframe，各帧原迭代算法读实时曲线；bake_all_frames=True采样整数范围，False采样参考target所有原keytime并保留小数，不round。源已有范围外keys保留，但Maya自动切线可能影响相邻插值，先备份。custom端点倒置交换；all-frame端点须整数，范围至多10000，总帧迭代至多100000。单帧保持小数currentTime；成功且next_frame=True才跳+1，其它/失败恢复原时间。

validate/dry_run只读全表节点/属性/曲线/范围，不改时间采样、场景、UI、Undo/选择/AutoKey；对未来帧几何条件不承诺全时域预验，执行逐帧检查，后来异常可能已有前帧keys，Undo本次调用复查。run标准UndoChunk包含所有pairs/frames，不再原逐帧嵌套。AutoKey临时关闭恢复，选择不改。ScopedCommands只准确切源rotate写，收集原函数内部catch过的写错并令整体ToolResult失败，不静默把失败写完成。角度读写按当前单位转换为原度制算法，修复rad单位误读/写入；单位不改。

结果 data `{parameters,rows,range_writes_keys,source_is_modified}`，每行精确节点、UUID、有效axes、frames、实际channel_writes。无外部文件/配置/shelf写。示例 `tool.run(pairs=[{'source':'|jointA','target':'|reference'}],time_mode='single',full_alignment=True,dry_run=True)`，成功后同参数run；range设time_mode='custom',custom_start=1,custom_end=24。完整UI `launch_candidate.show_ui()`；只用受支持API/UI，native内部原入口不绕过scope。

复用标准Undo/结果，core未发现同一完整朝向/约束轴迭代流程，不改core。WorldSpaceTools可在本工具range后读源keys进一步世界空间处理；quaternion_tool apply仅普通XYZ静态对象，不能自动套关节本算法JO约定。组合尚无生产实测。

验证：原字节与所有函数/UI静态完整、Schema/严格类型；隔离Maya2025实际主轴/完全XYZ、原矩阵行为一致、dry/oneUndo/AutoKey/time、rad单位、真实range keys/小数参考key/逐帧方向、锁轴单轴/关节JO/旋转父/非XYZorder、全表坏后行及GUI batch拒绝。真实完整GUI/生产约束rig/长动画及跨版本not_run。原作者/发行授权未推断。
