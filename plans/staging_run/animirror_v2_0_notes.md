# AniMirror v2.0 审计与完成记录

最终候选已包含完整 API、原窗口回调、UUID 所有权、专项说明、两个测试、晋级清单和真人验收步骤；当前最终证据为 animirror_v2_0_mayapy.json（14 项真实隔离检查）和 manifest 指纹匹配，仍是 GUI not_run。下方“工作中”内容保留早期检查点过程，不代表最终缺项。早期 UI-query shim 报告只作探索历史；probe_animirror_suite.py 现仅编译检查，实际镜像检查使用候选标准 API，不绕过内部保护。

最终保留 X/Y/Z 参数语义，不再推断平面。所有三轴、旋转、累计烘焙、Undo、错误恢复、组件选择、重命名替身、外部消费/后代、场景保存重载已在 Maya2025 隔离场景检查通过。实际 GUI/复杂中心/真实绑定/其他版本仍待人工。

实节点排查修正：MEL 全局数组用 typed 返回过程读取；重建 globals 依赖场景记录；捕获前显式逐节点记录 UUID，避免不完整 baseline 覆盖其他镜像所有权；floatMath 默认工具列表连接按真实 defaultRenderUtilityList 类型判断。删除先记录 UUID、脱离目标下本候选约束再删 helper，避免 Maya 连带删除空目标。完整原过程和窗口保留，删除保护及四按钮走标准 Undo API。当前对象源码/upstream Git 属性为 -text，保持原资源字节与哈希跨检出一致。

## 以下为早期工作中审计历史

当前仅完成完整原资源归档、嵌入命令提取、私有 MEL 名称及参数契约。没有完整 ToolResult 类/GUI 回调保护/删除保护/晋级资料，candidate_complete=false，不能记入已完成数量或转正。

原文件只有一个安装 MEL 和两页 PDF，MEL 顶层 create_shelf_Animall 会改 Shelf；从唯一 -command 字符串解码实际 9 过程，不 source 原安装器。embedded_original.mel 保存完整解码业务原文；runtime.mel 将所有过程改 global proc 并加 mtbAV2_ 前缀，私有全局变量/UI 名也加前缀，保留 Maya 原生 gPlayBackSlider。去除顶层开窗和状态重置，之后由明确入口调用。原两个文件按字节保留。

已修正 mirror_animation 内 withBake 的计数顺序：原先 fast_bake 清空全局状态后 ind 又加一，之后镜像产生数组空项；候选先计数再 bake/reset。原业务算法、mirrorJoint/makeIdentity/floatMath/约束和原窗口布局都仍在 runtime.mel，详细 diff 单独存档。

9 原过程：aniMirror_menu、globals_variables、change_options_mirror、mirror_animation、transform_connect_operator、rotate_connect_operator、delete_all_created、fast_bake、define_frames_range。隔离编译探针检查全部 whatIs 来源，初始化 globals 后节点集合未变、不创建窗口，gui_acceptance=false；探针放在 plans 中，runner 的通用 fingerprint 不代表候选整体。探针输出另列 runtime.mel 的实际 SHA256，待完整 candidate/tests 检查覆盖所有运行文件。

PDF 两页内容提取和页面图片均已查看。原说明支持 Maya2016–2022 Mac/Windows，中心→参考→目标选择，Interactive Mirror/Undo/Bake/Mirror with Bake 与开关均需保留；这不构成 Maya2025 的正式 GUI 通过。原指南平面按钮 XZ/YX/ZY 与源码 mirrorXY/mirrorYZ/mirrorXZ 一一对应，API 用真实平面 XY/YZ/XZ，文档明确按钮映射，不默默重写算法。rotation 默认 Y/Z 反转。原说明对 skeleton/AdvancedSkeleton 的支持尚须真人副本实测。

待做：完整 BaseMayaTool/ToolResult 适配、无副作用 validate/dry_run、标准 UI 回调、动作 inventory/open_ui/mirror/mirror_bake/bake/clear、时段选择/指定与参数回填。保留原镜像完整算法，不能只写直接 tx/ry 数值取反。独立 batch 无 UI 时明确拒绝依赖 UI 的流程，不把编译通过当镜像实测。

必须防护：原 delete_all_created 按全局名字删除 joint/floatMath，会误删重命名后的同名替身；须按 UUID 校验和删除，仅清理本候选创建节点。回调需纳入 Undo，异常也恢复 refresh/currentTime/selection。原 fast_bake 暂停刷新、删静态曲线/filterCurve，bake 集合为累积 mirrorObject，须如实记录范围和影响。mirror 后的目标约束是否随辅助 joint 清理干净需实节点检查。重新 source/reset 不能遗失现有会话节点；运行时来源和私有 globals 需验证。

原资源未发现独立再分发许可，只保留本地来源及 PDF 联系信息，不公开发布。API/界面/说明/测试/晋级注册和验收说明全部完成后，才能将本项标 prepared_unverified 或 prepared_verified_offline。

补充实节点探针：Maya2025 默认未加载 floatMath，原脚本会创建 unknown1 并报 unknown1.floatB；本机 Autodesk lookdevKit.mll 存在，隔离显式加载后 floatMath 可用。候选 validate 应只读检查节点类型/插件，不能自动加载；用户加载方式必须写入依赖/验收。

实际 XAxisTransRadio=true 时，mirrorJoint 虽使用 mirrorXY，后续 floatMath 却反转 pointConstraint 的 X，实测目标为 (-sourceX, sourceY, sourceZ)。此前探针把 mirrorJoint 的 XY 误推为最终位移平面而断言失败；修正为验证原实际 X 反转行为。当前 contracts.py 的 plane 语义仍待修正，不能用尚未正确的映射交付。优先把接口改为原 translation_axis X/Y/Z，并列出镜像 joint 与最终位移的耦合；对旋转和中心非零变换继续观察，不能只根据按钮文字作几何承诺。

保存检查点前已将契约改为 translation_axis X/Y/Z（默认 X），移除 plane 推断。最终探针通过：目标1帧(-3,2,1)→5帧(-5,2,1)，清理后全部候选 joint/floatMath/constraint 消失。只替换原 UI 查询为固定值并显式加载插件，执行的是原真实 Maya 业务算法；GUI 与其他轴/旋转/中心变换/烘焙尚未通过。
