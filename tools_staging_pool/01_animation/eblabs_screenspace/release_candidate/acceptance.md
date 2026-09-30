# EB Labs ScreenSpace 人工验收

仅私人备份场景，版权Eric Bates/EB Labs，原资源/许可管理归档不改，不公开发布。候选完整native MEL，无需原Hub安装器或缺失的PackageData版本壳。

1. `runpy.run_path(r'E:\GitHub\maya_tools_box\tools_staging_pool\01_animation\eblabs_screenspace\release_candidate\launch_candidate.py')['load_tool']()` 取得tool，`tool.run(action='open_ui')` 检查完整双页窗口、camera/rig列表、朝向、Create/Delete/Smart/Full Bake、quick Undo/redo、刷新/帮助和重复开关。不要拖入原ScreenSpace.py installer；不应自动建shelf、改prefs/namespace或隐藏Maya窗口。
2. perspective camera及translation键目标，create前dry_run对比节点/键/buffer/剪贴板/选择/时间无变化。歧义/锁/引用目标/外部驱动/无translation键/重复live record拒绝；有旋转键时orientation开关生效，无旋转键原降级需要检查提示和返回值。
3. 移屏幕控制器XY、编辑zDepth/planeAdjust/controlRadius，看world目标与实际透视画面的对应。检查静态和移动/旋转camera、镜头/nearClip、源pivot、非零世界位置、父级scale、非均匀scale/jointOrient、物体跨相机前后/近相机/零距离；零距离应失败并可Undo。评估原按键时间采样是否足够，检查步间/接地/漂移。
4. 在不同备份各做Smart/Full Bake，比较TR关键帧/稀疏-密集时序/plateau/Euler/首尾/rotation，尤其zDepth-only的新键、旧曲线层与其他属性。回烘会替换/扩充原目标TR键且改变Maya动画clipboard/buffer，不算无损时序编辑。没有GUI或真实投影检查不能仅凭隔离数值批准。
5. 清理默认放弃屏幕编辑，删除本rig并保护空原控制器，允许保留必要blend/动画buffer/来源record。人为插外部子节点/连接/驱动要拒绝。改名rig/control/target/camera、另存重开再回烘/清理应依UUID正确识别，不影响场景已有同后缀原EB工具。
6. create、Smart/Full Bake、cleanup各直接Undo/redo一次，验证节点/连接/键及时间/选择/namespace。Undo前别额外切帧或改场景，否则先撤销的是该新动作；失败立即Undo检查原备份。Script Editor不得有Error/Fatal Traceback。

2项离线/6项隔离Maya2025和临时注册通过，不等于以上真人验收。记录验收人/日期/版本/备份rig/camera与具体结果；真实通过后按plans/staging_run/promote_candidate.py当前hash人工记录规则晋级，本轮不会apply。
