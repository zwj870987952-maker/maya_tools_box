# Joint Optimal Pro 4.1 真实 Maya 验收

状态not_run。隔离mayapy通过不等于真实Maya GUI或生产绑定通过。

1. 用新的Maya会话与备份骨骼/网格/曲线场景；确认自身许可使用条件。运行launch_candidate.py的show_ui()打开原完整主界面及镜像选项窗口，核对三页功能/停靠/折叠/关闭重开与Script Editor；不拖放原installer、不运行system find、不改vendor。
2. inspect/dry_run前后核对scene节点、选择、时间、Undo、options不变；六个资源/SHA齐全。确认本机Unicode loader通过，其他版本或OverRig同名过程明确拒绝；不要在同会话手工重定义过程。
3. 按PDF检查普通joint、顶点中心、选择位置、内嵌joint、非线性链增删、曲线链增删、三点T/-T/L/V/圆心创建。检查输入顺序、退化输入和重复短名/namespace，创建数量与实际世界位置正确；API whole创建调用后环境恢复、一次Undo/Redo。
4. 备份场景检查parent/true-parent/unparent、正反层级、对齐/平滑/分布、最短骨骼路径选取；原行为可扩展scope，逐项记录连接对象/父子/关键帧影响，带skin移动模式场景单独复验，避免无备份生产rig。
5. 检查冻结rotate/jointOrient、Orient→Rotate、自动/手动各axis/up朝向、镜像及命名/namespace工具。对照实际jointOrient/rotate/child worldMatrix、名称与原动画，不只看有无报错；原catchQuiet可能只完成部分步骤。
6. 验证indexed颜色/radius/Handle、RGB模式拒绝、锁/引用/驱动radius、多父DAG实例和limit相等拒绝；native UI的显示/镜像/高亮偏好单独记录，scene Undo不包含这些runtime设置。

记录Maya/Python版本、结果和局限。真正用户验收后填写JSON：passed=true、tool_id=joint_optimal_pro_v4_1、candidate_sha256=promotion预览精确指纹、maya_version/accepted_by/date。用plans/staging_run/promote_candidate.py --candidate 此目录 --acceptance 实测.json --apply晋级。此前不迁正式库，不改注册/面板，不运行Obsidian同步。
