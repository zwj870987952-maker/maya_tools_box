"""Knowledge and truthful manual acceptance for original full Root Motion workflow."""
from prepare_root_motion_bake import RC,PKG
import json

DOC='''# Root Motion 约束烘焙与偏移动画层

tool_id：`root_motion_bake`，category：animation。原始单文件标题“约束烘焙工具”，作者头部标注 Assistant，无随附独立许可，按用户本地个人候选整理。全部 13 类方法和原界面完整保留，原始字节在 upstream/root_motion_original.py.original；去除 import 时顶层启动 UI，窗口名私有化。

用途：把质心的选定平移/旋转轴约束到 Root，以逐帧烘焙得到 Root 动画；有大环时创建新的偏移动画层，在起止帧保持原定义的相对位移与旋转。**原“相对”算法是世界位置和世界 Euler 分量相减/相加，不是矩阵相对变换，不处理父物体旋转/缩放带来的真正局部偏移。** 保留此数学语义，生产 rig 和大角度旋转必须实测。

## 参数与输出

继承 BaseMayaTool，`validate(**kwargs)`/`execute(**kwargs)`/`run(dry_run=True, **kwargs)` 返回 ToolResult。`show_ui()` 可由晋级后的原主面板呼出；注册/文件搬迁预制在 promotion.json，不提前改正式库。

| 参数 | 默认/行为 |
| --- | --- |
| action | inspect；可选 discover/bake/open_ui/close_ui |
| groups | 可选 root/center/可空ring 列表，1..100；省略时明确的自动识别组 |
| translate_axes | ['z']，x/y/z 唯一列表；只是约束轴 |
| rotate_axes | []；x/y/z 唯一列表；至少一个约束轴 |
| maintain_offset | True，起帧创建约束时保持偏移 |
| snapshot_center | True；先逐帧采样所有质心的世界姿态到独立临时定位器，再执行原约束流程，避免质心为Root子节点产生循环；False沿用独立源的直接约束，仅适合不依赖Root的源 |
| start/end | 可选成对有限数值；两者同时给出就作为实际范围 |
| time_range | timeline=播放min/max；animation=完整动画范围；selected=真实时间滑块框选并按排他的末端减1；explicit必须给start/end；0<长度<=10000 |

返回 data.groups（root/center/ring/baked_attributes）、range、layers（实际新增层名）、warnings；discover/inspect 返回 groups/ambiguous，只读扫描完整命名空间和短叶名。同名多个候选不采用首匹配，禁止RootX_M误作Root，手动参数可消除歧义。

dry_run 不创建定位器/层/约束、不改选择/time/autokey/namespace、不打开UI、不写文件。全批 root 先完成预检，拒绝引用/锁定Root、共享外部动画输出、输入的引用/锁定动画曲线及其他非animCurveT驱动/动画层/约束。组Root不可重复或祖先交叠；ring不可位于Root下；约束轴必须keyable，有ring时所有T/R必须keyable。质心和ring是只读输入，可以来自引用，未创建引用编辑。

## 完整原流程与行为修正

原全部 create_constraint、bake_animation、get_relative_transform、set_relative_transform、process_single_group 与GUI方法可逐项追溯。质心快照在修改任何Root前完成；Point/OrientConstraint的skip/maintainOffset与原算法相同。烘焙保留原 bakeResults 全部选项，sampleBy=1/oversamplingRate=1/minimizeRotation=True/shape=False。**原烘焙作用于Root全部keyable属性，不只所选约束轴；preserveOutsideKeys=False可能改变范围外关键帧。** baked_attributes 是预检实际范围，不声称处理只限于所选轴。

源代码直接删除同名offsetLayer，候选使用唯一UUID层名且拒绝删除非本次创建的临时节点；新增层包含原 addSelectedObjects 的完整Root通道。隔离实测发现源两个xform调用写被动画驱动的Root后，末帧偏移在setKeyframe前重新求值丢失。候选在无输入连接的临时parentOnly副本上执行**完整原世界/Euler相对算法**，让Maya计算相同parent/pivot/rotateOrder的局部值，再明确在新animLayer写六个T/R关键帧；起止其他通道仍依源流程打键。不把偏移层删掉或跳过来让测试通过。

原UI框选选项实际取animationStart/End，候选桥读取真实高亮范围，未框选时报错。保留原界面控件，API与GUI整批用同一预检、同一UndoChunk；ring可空，修正原手动UI强制三个对象但业务允许无ring的不一致。源GUI扫描/执行/范围方法原定义保留并别名记录，安全回调桥替换调用。

所有创建的constraint/定位器/副本按UUID追踪，成功/失败finally清理，仅删除本次临时对象；有外部DAG后代时拒绝递归删除，保留供Undo。失败不自动回滚已写烘焙或层，一次Undo恢复；即使清理失败仍释放会话并尝试恢复状态。调用恢复选择、时间、namespace、autokey及原层selected/preferred/lock/mute/solo；新层不强占用户原层。没有文件写入，不需要外部程序或插件。

## 示例与组合

```python
args={'action':'bake','groups':[{'root':'rig:root','center':'rig:RootX_M','ring':'rig:main'}], 'translate_axes':['z'],'rotate_axes':[], 'start':1,'end':24,'maintain_offset':False}
preview=maya_toolkit.execute_tool('root_motion_bake',args,dry_run=True)
if preview.success:
    result=maya_toolkit.execute_tool('root_motion_bake',args)
```

沿用core的Undo/框架ToolResult；当前core没有与本完整质心抽取/偏移层业务等价的正式工具，不修改core。输出Root可接入动画检查或明确烘焙后的重定时/降帧流程；现有 retime_tools/keyframe_reduction 是候选潜在关联，不代表生产rig上已组合通过。重复处理已有层输入会被预检拒绝，应先备份并明确整理已有层后再验收。

## 验证范围

普通Python核对原字节/native SHA/13方法、无顶层启动、Schema及严格参数。Maya2025隔离六组覆盖原完整平移/旋转约束、已有动画Root、真实bake及Undo/Redo、完整新增偏移层末帧位置、保留原同名层和层flag、下级质心快照、全批预检不产生首组半成品、注入bake失败清理/time恢复、深namespace歧义与范围、batch拒绝UI。真实原cmds界面未打开；生产引用、层叠rig、所有旋转序/pivot/JO/RA/scale剪切、框选交互仍待人工检查。prepared_unverified，不迁入正式库。
'''

ACCEPT='''# Root Motion 真人 Maya 验收（not_run）

仅在备份动画场景，原始脚本不要直接import以免自动呼出未经适配的UI。

```python
import runpy
tool=runpy.run_path(r"E:/GitHub/maya_tools_box/tools_staging_pool/01_animation/root_motion_bake/release_candidate/launch_candidate.py")['load_tool']()
tool.show_ui()
```

1. 原窗口/三个字段/选择与重新扫描按钮/六轴/保持偏移/时间范围/执行/成功对话框响应，Script Editor无致命错误；重复呼出不冲掉其他工具窗口。
2. Root、RootX_M、main三对象完整流程；不同轴与maintain_offset逐帧检查Root烘焙和新增offsetLayer起末帧。检查所有Root keyable属性及范围外关键帧影响，不能只看所选z轴。
3. center位于Root下时默认快照不会出现循环警告；独立质心用snapshot_center=False对照原直接约束语义；输入中心有pivot/所有RO/JO/RA/非均匀scale时逐项检查世界姿态。
4. 无ring只执行约束与烘焙，API/手动UI均可；有ring保持原世界位置/Euler差值语义，验证大角度旋转、层权重和插值，不能当成严格相对matrix。
5. 已有同名root_offsetLayer必须保留；新增层唯一；层flag/选择/time/autokey/namespace恢复；一次Undo/Redo恢复整个批次，.ma保存重开后动画/层可恢复。
6. 相似名字、多层namespace、重复Root/祖先交叠、多个自动候选、非法/锁定/引用Root、非animCurve驱动与已有层Root：明确拒绝而不半处理批次；只读引用输入不应创建引用编辑。
7. 高亮时间滑块与timeline/animation/explicit分别核对实际烘焙范围；没框选时报错。分数起止帧与sampleBy=1的末端行为在实际场景确认。
8. 故障或中断后检查临时约束/定位器/副本清理，已有对象不被删；失败已写动画按提示Undo。不覆盖任何文件，不运行Obsidian同步。

逐项记录Maya版本/结果，未通过修候选。真人通过后生成含tool_id/candidate_sha256/passed/maya_version/accepted_by/date的验收文件，先用plans/staging_run/promote_candidate.py --candidate 本目录预览清单，再按验收晋级；本轮不执行apply。
'''


def main():
    cat=json.loads((PKG/'catalog.json').read_text(encoding='utf-8'))
    (RC/'docs/tools/root_motion_bake.md').write_text(DOC+'\n原13方法：'+', '.join('`'+n+'`' for n in cat['methods'])+'\n',encoding='utf-8')
    (RC/'acceptance.md').write_text(ACCEPT,encoding='utf-8')
    print('Wrote complete workflow knowledge and acceptance')


if __name__=='__main__':
    main()
