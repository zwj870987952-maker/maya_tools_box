# Base OverRig 9.0 真实 Maya 验收

状态not_run；独立mayapy仅验证已记录的原功能，不证明全部GUI或生产工作流通过。

1. 使用新的Maya会话和备份动画场景。确认有权内部使用此许可软件；不安装Shelf/userSetup/热键，不修改vendor源。运行launch_candidate.py的show_ui()，检查完整主界面、Color/停靠、各折叠功能组、Noise/Tween/尾链/脊柱/Arc窗口，Script Editor无Fatal。重复窗口应先用或关闭。
2. 打开完整ENG/RUS PDF手册，对照原功能操作。API inspect(dry_run)前后场景节点/选择/当前时间/Undo/插件/选项不变，全部10资源存在；同名过程冲突应报错，不覆盖其他套件。
3. 验证定位器显示大小、归一化姿态定位器、混合约束属性清理、标准/智能/双结、前向/反向层级和Parent工具。有序选择正确，检查父子/命名空间/引用/锁，检查节点、属性与关键帧实际影响。调用API后核对环境恢复和一次Undo/Redo；原生GUI回调另行检查其原始Undo。
4. 在有GraphEditor/timeline真实选择的场景验收range bake保留外键、层烘焙、复制缩放粘贴、周期/lag/镜像/Tween/Noise。不要把无异常当作有效输出。默认rotation order radio的zxy写6需专门观察错误，原作者源不得暗改。
5. 使用备份控制链测试3+/Spline IK、脊柱、Sword/Aim、尾链重叠及Jiggle_Bone_New.mb导入；核对源动画、关联Rig集合、生成节点、scriptNode/scriptJob、插件/autoload和cached playback。分项记录Undo范围，尤其MotionTrail内部disable-Undo。
6. 停靠/关窗口/重开、重载场景后检查残留callback/scriptNode和源/结集合；不在未备份生产场景做bake source/delete knots。遇到原MEL失败保留报错/步骤，不修改许可源，外围可明确记录并修复自己的问题。

记录maya_version、Python/Qt、结果与局限。全部需用功能通过后保存用户实测JSON：passed=true、tool_id=base_overrig_v9_0、promotion预览返回的candidate_sha256、maya_version/accepted_by/date。先预览再用plans/staging_run/promote_candidate.py --candidate 此目录 --acceptance 实测记录.json --apply晋级；此前不动正式库。
