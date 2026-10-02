# 蓝图工具盒真实Maya验收 not_run

1. 已打开真实Maya中show_ui，全中文45节点/颜色/搜索/右键分类/拖动/端口连线类型/平移缩放/Delete/属性面板/选中上游子图/次数/状态/print/关闭重开，与原版窗隔离。离屏Qt不替代此步骤。
2. 检查重复id/坏最后节点/未知type/参数/端口/双来源/环/必连/strict bool/非有限值在首次场景写前拒绝。dry nodes/选择/currentTime/dirty/Undo队列/文件一致；未来写入输出deferred如实显示，不谎称全图静态预知。一次Undo/Redo整个执行图；异常后当前已完成输出和可Undo部分准确记录。
3. 备份场景逐测全部Maya节点：attr/锁/reference/connected/重命名碰撞/祖孙混批/组/删/4约束；关系遍历/materials/skin/blend/deformer/时间/range/channelBox；非空1:1copy→paste/key。重点父级旋转/缩放/负scale/shear/jointOrient/不同rotateOrder：世界样本使用xform转目标parent space，部分世界轴粘贴时local XYZ耦合打键与锁预检，不将普通带父fixture通过当成全生产rig验证。
4. 两原示例、draft JSON save/load/坏图加载不清空旧图、新名保存/重复名拒绝/显式overwrite精确SHA备份/无路径CopyFrame唯一temp文件；输出前parent须存在，dry不mkdir。FBX插件加载/选择与3项Bake flag恢复/新输出/overwrite明确备份/范围/失败恢复；MA import/reference不执行scriptNodes但插件仍需可信。复杂文件/引用不能假称Undo完全恢复。
5. Qt5/6、Maya2020+原目标与本Maya2025 GUI逐验；文档原规划的尚无节点不认为已实现。candidate_sha256/maya_version/accepted_by/date/passed=true后用promotion一次晋级。
