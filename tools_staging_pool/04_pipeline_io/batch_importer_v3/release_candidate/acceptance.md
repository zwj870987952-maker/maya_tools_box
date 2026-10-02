# 真实 Maya 验收（not_run）

1. 完整Qt窗口无自动模块开窗：添加文件、递归文件夹/取消、次数/可编辑namespace、multi-select Delete列表、水印，全部控件响应正常。
2. 专门备份scene里逐个 .ma/.mb/.fbx/.obj/.abc 重复导入/引用；核对模型材质/动画/translators、有效namespace与count/原选择/time/AutoKey/currentnamespace。实际各格式reference支持需单独记录，未验证不得宣称通过。
3. 坏后行文件、空列表、NS冲突、同stem不同文件夹、9999多实例超过10000前拒绝。import一次Undo所有新DAG/DG，保留空NS；Redo不读源文件。引用Redo需源文件仍存在且SHA相同，RN UUID可变化。
4. 同源引用2份，在第1份选多个对象/shape后Del Ref，preview明确删整份文件；第2份保持。Undo重新读取源恢复无edit的引用、loaded状态/RN名字/元数据锁和选择，Redo删除重建同份。测试unloaded精确RN、编辑引用/nested/缺源拒绝，不删除非引用选择。默认RN元数据锁不误判为不可file-remove。
5. 使用真正复杂rig/reference/外部材质/引用edit生产备份，记录已声明拒绝范围是否满意；观察错误与partial失败。文件导入/引用会加载插件，插件状态/空namespace非sceneUndo，候选不对真实文件保存或删除。
6. Script Editor无fatal/控件可用且行为满意，记录版本后按promotion晋级并再验正式面板。
