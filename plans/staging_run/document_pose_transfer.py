"""Document the complete original locator workflow and concrete Maya acceptance boundaries."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
RC=ROOT/'tools_staging_pool/01_animation/pose_transfer_remote/release_candidate'
(RC/'docs/tools/pose_transfer_remote.md').write_text('''# Pose Transfer Remote：ROOT平移姿态迁移候选

状态prepared_unverified；真实GUI、生产rig/pivot/非均匀scale/shear/引用编辑尚未人工验收。原PoseTransfer.py和Readme.txt全部字节归档，9个原类方法与完整1..5步/自动手动/清理界面保留；catalog.json含原文件与native SHA256，完整AST差异可追溯。原文件没有独立license或作者声明，仅本地个人整理，不发布。

## 原业务与实际边界

原方法__init__、get_selected_root、get_all_controllers、is_controller、manual_select_and_create_locators、create_locators_and_record_pose、move_locators_to_new_root_position、apply_pose_from_locators、cleanup_locators全部完整保留。以locator复制每个控制器当前world matrix，计算ROOT新旧world position差，给每locator平移同一delta，再把locator的完整world matrix写回原控制器。只迁移ROOT平移，旋转/scale的root差异不纳入offset；不生成动画/键，不做joint/skin转换。

Readme描述“不同坐标空间跨模型还原”，实际源码按original_controller名字写回同一组控制器，没有模型间重命名映射、旋转空间变换或比例匹配。候选保留实际行为，不把它包装成自动跨模型重定向；locator属性手改成其他controller会被拒绝，防止逃逸写入范围。用户需要跨模型时另用已验收映射工具，不把本候选静态依赖当组合验收。

## 架构与复用

maya_toolkit/tools/pose_transfer_remote中有tool/runtime/native/ui_bridge/catalog/upstream；正式知识/测试候选与promotion.json齐备。继承BaseMayaTool，复用框架run/validate/ToolResult/UndoChunk与Schema导出；现有core的DAG/Undo能力和世界matrix通用逻辑已比对，本轮不改生产core，不为统一而重写原方法。

network marker记录session id/version、ROOT UUID、controller/locator/shape UUID、原控制器path、完整捕获标记、上一ROOT world position。每次API都从scene重读，删除/Undo/Redo、保存重开和rename不依赖旧Python实例；同场景最多一套local候选session，多marker/坏数据明确拒绝。辅助节点均私有前缀+session id+UUID，不按pose_loc_*通配删；源UI与原版窗口私有名隔离，关闭UI不删scene helpers。

## API 参数、输出与预检

tool_id=pose_transfer_remote；action默认inspect，只读当前session/选择；detect只读发现controller；capture建立/替换locator姿态；shift按当前ROOT差移helpers；apply把记录matrix写回控制器；cleanup清助手/marker；open_ui/close_ui管理原UI。

root在detect/capture时要求一个完整transform，不接受joint/shape/组件/实例/歧义短名。controllers可明确有序列表，1..1000唯一名称；省略时通过ROOT下transform的原命名/override/curve/surface特征与ROOT自己发现。control_set可明确给objectSet；省略时检查ROOT namespace内ControlSet，只接受ROOT本身及其descendants，跳过外部set member，不盲取别的rig。明确手选controllers可包含ROOT树外对象，这是用户明确范围。最终按DAG父先子后排序，避免父最后写破坏子world pose。

shift/apply默认使用scene内ROOT/controllers UUID，root可选提供用于核对capture身份，不允许另一个ROOT替换。controllers/control_set只影响新capture/detect；其他操作由已有会话决定。apply写T/R/S/shear完整world matrix，所有这些通道必须可写，已有animation/constraint/layer/driver或锁拒绝，不忽略scale锁装作成功。allow_reference_edits默认false；明确true/GUI复选允许控制器引用matrix edits，仍拒绝锁/driver；文件保存时这些引用编辑会留场景。capture可只读引用transform，helpers/metadata是新local节点。

所有world matrix有限且绝对值<=1e12，捕获ROOT position严格3有限数字。validate/dry_run只读，不造locator/marker/UI、不改选择/time/AutoKey/namespace/Undo队列。ToolResult.data含root/controllers/locators/session_id或inspect session；detect只给发现列表，不自动选中。未知参数/类型/预算/损坏marker/被锁或驱动metadata拒绝。

```python
import runpy
tool=runpy.run_path(r'E:/GitHub/maya_tools_box/tools_staging_pool/01_animation/pose_transfer_remote/release_candidate/launch_candidate.py')['load_tool']()
tool.run(action='open_ui')
tool.run(action='capture',root='rig:ROOT_ctrl',controllers=['rig:ROOT_ctrl','rig:hand_ctrl'],dry_run=True)
tool.run(action='capture',root='rig:ROOT_ctrl',controllers=['rig:ROOT_ctrl','rig:hand_ctrl'])
# 用户在备份场景把ROOT平移到目标位置后：
tool.run(action='shift')
tool.run(action='apply')
tool.run(action='cleanup')
```

## 行为修复与安全影响

完整原matrix/locator/translation业务保留。修重复shift累加同一offset：每次成功shift更新marker内上一ROOT位置，未再动ROOT重复调用delta为0；若用户手动调locator，保留该修正并再加新的delta。shift的marker更新和locator变化同一Undo chunk，Undo后下次读取的是恢复的数据。

capture重做先只清自有helpers，再用原逻辑重建；helper新建后立刻加入tracking，出错时在finally保存partial capture，不标complete，shift/apply拒绝直到recapture/cleanup或Undo。marker创建skipSelect，scope终于恢复原selection/time/AutoKey/absolute namespace/relativeNames；不借新marker作为原选择。场景失败不会自动回滚，框架一次Undo恢复已有写入。

识别命名只检查leaf，属性/shape用full path，避免父名误判和deep namespace/同名歧义；辅助名不拼原DAG带|字符串。apply先检查UUID/锁/driver并核对locator.original_controller仍是记录的原path或同UUID现path；rename后同步path继续原矩阵流程。控制器被删后仍可cleanup剩余helpers，缺helper也可清理可识别部分；需要完整捕获时缺失节点拒绝。

删除仅session UUID归属的locator/shape，外部child（包括额外shape）或外部输出导致拒绝；不因相同名称删除别人的节点。metadata被锁/驱动或marker接外部consumer时cleanup拒绝。用户不要手改metadata UUID，助手归属不是对恶意伪造scene数据的沙盒。清理不删除ROOT/controllers，不删除外部曲线/文件；创建会话/pose helpers留scene直到清理或Undo。

UI完整按钮与布局经SessionButtons桥接同一标准API，window高550以容纳原全部按钮，加默认关闭的引用编辑复选。手选弹窗实际使用当前选择（模态期间无法继续改scene选择），先在scene选好controllers再确认；重新开窗可shift/apply已有session，capture前重新选择ROOT。新GUI未在mayapy构造，真人仍须核验布局/弹窗/滚动或不同DPI。

## 文件与组合

原流程和API不写外部文件，无shelf/userSetup/用户配置或插件安装；scene保存由用户明确操作，Maya会保存network/locator属性。一次Undo/Redo覆盖scene matrices/helper/metadata，不承诺恢复用户另外做的场景保存。输出controller的world pose可作为其他已验收keying/retarget工具输入，先通过锁/driver预检；没有自动动作串联或跨模型/动画转换证据。

## 证据与晋级

普通Python2组验证9原方法、两资源hash、懒Maya import与Schema。Maya2025隔离5组：detect set范围/dry/Undo零改动/private原方法guard；capture→ROOT平移→shift重复delta0→apply且子world pose/rotation正确、Undo/Redo、ma保存重开/cleanup Undo恢复后shift；外部child/locked scale/被改目标属性拒绝；第二helper xform注入失败partial flag/finally/Undo；UUID rename后apply、控制器被删后的cleanup。没有构造原UI，未用真实生产rig或引用编辑资产，rotation/scale/pivot复杂情况待真人验证。

候选镜像完整目标路径，promotion.json预制ALL_TOOL_CLASSES注册与面板；临时正式布局检查payload import/Schema，不改真实production。按acceptance.md实际满意后才晋级，本轮不apply、不改core/长期规范/Obsidian生成结果。
''',encoding='utf-8')
(RC/'acceptance.md').write_text('''# Pose Transfer 真人Maya验收（未运行）

在备份rig/临时场景使用launch_candidate.py load_tool/open_ui，不执行原文件自动入口。

1. 原1..5自动/手动/记录/移动/应用/清理按钮全部可见，窗口不盖掉原版，默认Allow reference edits关闭；重开候选可读取scene session，Script Editor无致命错误。
2. 一个ROOT与层级控制器，部分含同leaf不同namespace，capture dry_run不造节点/改选择/AutoKey/时间/ns/Undo；detect仅ROOT范围，namespace ControlSet有别rig成员时不能混入。
3. capture，用户ROOT仅平移，再shift/apply；检查所有world位置/旋转/scale/shear与locator，父先子后；重复shift不漂移，再动ROOT后按新delta移动，一次Undo/Redo包括metadata。
4. ROOT rotation/scale改变不作相应姿态空间变换，不能宣称跨模型自动retarget；生产pivot/nonuniform scale/shear/rotateOrder/OPM用备份场景核验全matrix效果。已有动画/driver/constraint/层/锁应拒绝apply。
5. 手选controllers包含ROOT外对象时仅该明确范围参与；先在scene选好再点手动确认；root修改/rename、controller rename、scene.ma/.mb保存重开/Undo后能重读UUID，不按旧名字写错对象。
6. cleanup只删session helpers/marker，目标控制器不变，Undo/Redo恢复助手和session；外部child/shape/output拒绝，控制器已删、部分helper缺失仍可清剩余owned helper。marker被锁/接consumer时拒绝。
7. 第二helper或apply中途错误：partial capture不能shift/apply，context finally恢复，Undo可恢复；recapture只换原owned helper，不删同名用户locator。坏metadata/重复marker明确拒绝。
8. 引用控制器capture只读允许；默认apply拒绝。只有在备份引用场景显式勾选允许edit，再核对实际ref edits/全matrix和保存影响，锁/driver仍必须拒绝。

记录Maya/Python版本、rig/pivot/scale/ref条件、各按钮/scene结果与错误。5组隔离检查不是上述真人验收，满意后才按promotion.json晋级；无独立license仅本地不发布。
''',encoding='utf-8')
print('Pose Transfer full knowledge and acceptance written')
