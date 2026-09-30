# IK/FK Pro 真人验收

当前not_run；本机Maya2025缺少PyMel，原匹配/烘焙/GUI没有通过运行验证，标准Store/切换/key检查不能替代。

1. 在具备兼容pymel.core的Maya备份场景中执行下方启动；确认完整Pro的Setup/Help/Match/Bake、Store和所有参数字段，无Error/Fatal Traceback。记录实际PyMel/Maya/Python版本。
2. 真实引用rig的左右arm/leg分别设置三个FK、IK腕/PV/开关，校准六bend-axis与rotation offset；检查0-is-FK/IK、range1/10，双向match的腕姿势/PV/肘膝弯向、旋转顺序、jointOrient、FK锁平移；对比原完整源码行为。默认引用编辑拒绝，明确允许后才进行。
3. 三个Store控制阶段保存/加载/从选中找Store、改名/namespace/保存重载、同名外部节点/自有Store覆盖与保护。原.ma/.mb传输改JSON，旧记录需从备份里的字段重新定义，不自动加载旧场景文件。
4. 验证纯switch、select、key、逐帧Bake、AllKeys（范围内/无源keys/取消）。在备份Graph Editor检查目标区间删改key与源key保持；非整数源keys、多个控制器所有keyable属性、AutoKey开关均复验。
5. 操作前放一个外部snapGrp同名节点，确认未删除；检查临时helper清理/外部后代输出保护/共享solver保留。逐步Undo/Redo，失败先Undo检查局部结果，时间/选择/namespace/AutoKey/Undo保持。
6. Store导出临时绝对JSON，默认重复写拒绝，明确覆盖后允许，导入自有冲突需明确更新；恶意/错类型offset应拒绝，不执行eval/场景文件导入。JSON文件与目录不归MayaUndo。
7. 记录场景、版本、参数、现象/错误/满意度；环境缺失和原算法问题如实记下。真人通过前不转正、不执行promotion apply、不公开版权资源。

```python
import runpy
tool = runpy.run_path(r'E:\GitHub\maya_tools_box\tools_staging_pool\01_animation\ik_fk_switch\release_candidate\launch_candidate.py')['load_tool']()
tool.show_ui()
```
