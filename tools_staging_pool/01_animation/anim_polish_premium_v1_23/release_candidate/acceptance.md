# AnimPolish 完整候选验收

prepared_unverified；真实 GUI `not_run`，其他 Maya/Python 版本待测。原 DOCX 声称 Maya 2015+，本候选 Python3 适配不据此宣称所有旧版本兼容。用可写备份 rig 和临时缓存根目录，不对正式资产直接实验。

1. 在 Maya Script Editor Python 执行候选启动器：

```python
import runpy
candidate = runpy.run_path(r'E:\GitHub\maya_tools_box\tools_staging_pool\01_animation\anim_polish_premium_v1_23\release_candidate\launch_candidate.py')
tool = candidate['load_tool']()
tool.show_ui()
```

2. 入口打开无业务副作用，inventory 列出 160 函数、19 素材；选一个 mesh 做 dry-run，不创建节点/文件/目录，不更改 keys、选择、Evaluation。分别打开不停靠/停靠原完整界面，检查无重复按钮、折叠栏、工具提示和 stock Maya 图标；可以同时保留原 animPolish 安装，核对没有覆盖其模块。
3. Sculpt 全流程：开始并改变 vertices，标准/单帧/P2P 应用，检查 XYZ clusters、0-1-0 keys、两个不同帧 P2P 的插值；Sculpt From Zero 四模式、level 增加、P2P Zero/Hold、编辑/应用编辑、中止、Channel Box 选择删除/整 level 删除；确认原 mesh 可见性和材质，Undo 回到预期。排序返回 deferred 后等界面 idle，改选另一个对象也不能误排其属性；删除原对象再同名重建不能误操作新对象。
4. Wrap To Mesh（多被驱动、driver 最后）、To World 和单 mesh face 提取。Deform/Flood Verts 为空及部分 vertices，平滑次数与隐藏数据选项；核对原输入顺序和真实动画驱动。
5. Subdue 切 DG/off，完整测试顶点/整 mesh、Resample Rate=1/3/4、Smooth Map；检查新 `maya_toolkit_data/anim_polish/subdue_cache/<uuid>` 的 .xml/.mcx 及 cache 节点连接、原曲线清理和输出。Undo 应恢复场景，但文件仍保留；不得覆盖当前项目缓存。parallel/serial 时预检拒绝且不自动切模式。执行中异常时检查 viewport，原 UI 入口可用 Fix Viewport。
6. Grow/Shrink 和 Iron：whole/partial Deform Verts、Flood Verts、smooth 次数、Hide Data，确认权重可绘和范围外不受预期之外影响。Sticky Mod：单 vertex、多 vertex、单 curve point，检查 softMod、rivet、offset、falloff、sphere/LRA/color/scale、显示层，以及增减 mesh、断旋转、对世界和朝向对象操作。
7. Utilities：颜色所有 preset/random/blinn/lambert、颜色打印、层级 mesh 平滑预览、camera cycle（含 skip ortho）、quick bake/rivet bake/plane bake，核对 playback 时间范围，错误/中断后 Evaluation/刷新/选择顺序/时间恢复。原 callback 不走框架 finally，失败时单独确认状态。
8. Settings Save/Load/Default 只写 JSON；重新打开 UI 恢复已知控件。Copy All/Keyable → 多目标 Paste，测试字符串引号/换行、标量、向量、锁定/连接/缺失属性、Undo 与跳过报告。不要执行 upstream 的旧 user_copyPasteAttrs.py；候选不自动迁移旧 Python 用户设置。
9. 缓存只用独立临时目录。显式加载 AbcExport/AbcImport；几何导出 New Version：没有版本及已有至少一个版本两分支均实际生成 geometry.abc，时间使用 animation start/end；导出相机生成 cameras.ma。已有文件再次导出应拒绝且字节保持原样，UI Yes 也不能覆盖。测试 import range checkbox、_ABC_CTRL、Attach To Anim/Imported、换到另一个根目录的版本、Delete From Scene；对比 topology/namespace/ref/lock 限制。场景 Undo 不删除文件。
10. Script Editor 无致命错误，真实绑定动画满意后才验收。standalone 不代替窗口、paint、完整 cache 和 idle 回调。检查 `promotion.json` 预览当前 SHA，填写 tool_id、passed=true、candidate_sha256、maya_version、date、accepted_by 的验收 JSON，再运行 `plans/staging_run/promote_candidate.py --candidate <本候选> --apply --acceptance <验收文件>`。晋级资料覆盖代码、原资源、说明、测试与 ALL_TOOL_CLASSES/面板；验收前只预览。

本候选包含原件归档和独立运行副本，差异随知识说明保存，未赋予公开再分发许可。
