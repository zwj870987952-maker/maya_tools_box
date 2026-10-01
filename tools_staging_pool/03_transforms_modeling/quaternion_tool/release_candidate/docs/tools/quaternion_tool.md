# Maya 四元数工具

id `quaternion_tool`，域 `modeling_surfacing`，完整原单文件/SHA 归档 upstream。所有原 Quaternion 类/算子/方法、完整创建/向量/欧拉/应用/帮助窗口留 native；受支持的 QuaternionCandidateUI 所有按钮通过 Base API 返回 ToolResult，新增应用预检。导入不启动窗口，候选留待整理池。真实 GUI 与生产复杂变换/跨版本 not_run。

完整原数学约定保留，不替换乘法或 RotateDirection 方向：xyzw 分量，XYZ Euler，角度制，原 qX*qY*qZ 和 inverse*direction*q。Maya2025 实际 MEulerRotation/MQuaternion 和向量几何检查一致。FromTo 和轴角复制输入 MVector，避免 normalize 改调用者向量；点积/acos 输入浮点边界钳制，原 Slerp 最短路径/接近线性/参数 clamp01 保留。原小于1e-5 的零模/零方向返回 identity 也保留；zero raw from_components 仍零分量，Euler/方向规范化按原 identity fallback，不宣传为合法非零姿态。

十一 action：from_euler(euler3)、from_axis_angle(axis3,angle)、from_components(quaternion4)、from_to(from_direction3,to_direction3)、rotate_vector(quaternion4,vector3)、to_euler(quaternion4)、slerp(quaternion4,second4,t)、multiply(quaternion4,second4)、inverse(quaternion4)、normalize(quaternion4)、apply(quaternion4,objects)。未填值来自 Schema 默认，默认 action from_euler；所有数字必须有限、非 bool、绝对值不超过1e12，vector长度严格，action外参数拒绝；Slerp t 原样钳至0..1，不当外插。apply objects 省略为当前选择，仅整节点 transform，拒绝歧义/重复别名/组件/joint/实例、锁/引用/动画驱动、非 XYZ rotateOrder、非零 rotateAxis 或非 identity offsetParentMatrix，避免把固定 XYZ Euler 静默应用到不同约定。

输出 data `{quaternion,euler_degrees,convention}`；rotate_vector 加 rotated_vector；apply 加 targets 的全路径/UUID。validate/dry_run 计算结果及全表目标检查，不改场景/选区/时间/Undo/AutoKey。纯数学 action 不写场景；apply 继承 UndoChunk，临时禁 AutoKey/恢复，不主动建 keys。按原 cmds.rotate(absolute=True) 应用，显式 `deg` 数值后缀修复场景当前 angle unit=rad 时原输入角度被误解释的问题，保持用户 currentUnit 不变。仅作用于目标旋转，不做骨骼 orient/几何变形/镜像算法，不写外部文件。

示例：`q=tool.run(action='from_axis_angle',axis=[0,0,1],angle=90).data['quaternion']; tool.run(action='apply',quaternion=q,objects=['|ctrl'],dry_run=True)`，预检成功后同参数 run。异常写错误可能部分目标已改，基类不会自动回滚，Undo 本次调用复查。完整 UI `launch_candidate.show_ui()`；包 show_ui 提供兼容显式入口。native 原类保存完整数学与布局，场景写入口使用受支持 UI/API，不绕过校验。

core 无相同完整数学工具/UI，复用框架 Undo/ToolResult，不改 core。结果 quaternion 可用于工具自身 apply；mirror_tool 使用原 Euler 公式且输入不同，不能不经转换直接把 q 当 mirror 参数。WorldSpaceTools 可读/烘焙应用后的变换，受驱动目标要先在备份静态对象上操作，不自动删驱动。组合未生产验证。

验证：2离线检查 SHA/全部定义与UI/Schema/类型边界，3隔离 Maya2025：十一纯计算无场景变化、真实 API XYZ quaternion 与90度向量、FromTo同向/反向、逆乘积identity/normalize/Slerp短路半角/零fallback、MVector输入不变；真实原 cmds.rotate 姿态一致、dry/单Undo/AutoKey、rad场景显式角度姿态不变、全表锁/旋转顺序/key驱动/别名/组件/实例拒绝。GUI/非XYZ生产转换/其它版本 not_run；原作者/公开发行授权未推断。
