# overslapper：旋转/平移延迟、过冲与风控候选

Philippe Ratté Overslapper 1.0.3，Copyright 2024 Philippe Ratté。完整9件原资源（安装器、20页手册、EULA、默认JSON、两个图标、三个源码文件）按字节归档于upstream，原Python存为.py.original。执行源码保留28个业务函数、两种QObject worker和原窗口56方法、部分导入窗口4方法；修改对照overslapper_changes.diff。安装器仅归档，不执行shelf/userScripts写入。运行源码、图标、默认设置、说明、测试都在payload内，不依赖其他staging工具或用户scripts目录。

LICENSE.txt为限制性EULA，原文包括不得未经同意再分发，以及不得逆向、复制、修改、反编译/反汇编。它不是开源许可；本次保留原许可和署名，用户本地候选整理不代表取得修改或发布授权，不上传/分享原件或候选。个人和单席位许可条件也保留；不是MIT/GPL。

用途是对有父级运动的本地transform控制器生成旋转或平移延迟。旋转使用父级/目标/上轴矩阵与24种主轴-上轴组合、六种rotateOrder计算Euler；平移使用延迟parentMatrix与当前parentInverseMatrix的局部位移。保留顺序级联、分组、1-stiffness混合、strength缩放、循环、父级影响移除、自身位移忽略、距离选项、动画层、峰谷/稳定区过冲和可动风曲线，不替换成particle、约束模拟或新的简化算法。现有正式core无等价延迟/风/过冲实现；复用BaseMayaTool/ToolResult/Undo。core自然排序会lower大小写，原排序区分大小写，因此保留原规则并以叶名排序，未下沉正式core。

## 统一接口

tool_id=overslapper，category=animation，version=1.0.3-candidate.1。统一run(dry_run=False, **kwargs)，标准Schema导出到OpenAI/MCP。框架不自动验证Schema，normalize/prepare负责实际预检；默认action=overlap。

| action | 参数与结果 |
| --- | --- |
| inspect | 只读返回tag风控、layer、选择、播放范围，无GUI创建 |
| overlap | targets空用当前选择；mode=rotation/translation；返回groups、UUID、attrs、frame_range、sample_count、written_layer/native_elapsed_seconds |
| create_wind | 创建原30点曲线与wind/wind_strength/overslapper_tag、原形状连接及候选署名属性；返回created_wind |
| set_winds | winds空用所有完整tag风控，enabled=True/False；修改wind开关并可Undo |
| select_winds | 选择显式winds或所有风控；仅此action有意改变选择 |
| open_ui/close_ui | 原生完整窗口/渐变/全部控件/部分预设导入；只能交互Maya |
| read_preset | preset_path现有JSON≤1MB；返回经过完整八组校验的preset_data |
| write_preset | 完整preset_data、preset_path现有目录JSON；默认不得覆盖，明确overwrite=True才替换；文件不受Maya Undo |

overlap完整参数如下，见Schema准确类型和上限：

| 参数组 | 规则 |
| --- | --- |
| targets/frame_range | 唯一整transform，1..500；整数start<end，默认完整整数播放范围，范围≤20000、±1000000；targets×帧数≤200000 |
| mode/order | rotation/translation；selection/name/split by name。显式targets按给定顺序，名称自然排序以叶名/namespace和数字；分组还隔离不同DAG父级，避免长路径的数字误分组 |
| axes/main_axis/up_axis | axes为x/y/z/xy/xz/yz/xyz；主轴/上轴为x+/x-/y+/y-/z+/z-，不可同一轴。只写mode的所选通道 |
| stiffness/stiffness_values/strength | stiffness 0..1，内部系数1-stiffness；可按实际groups给同形状stiffness_values，UI渐变按i/组长度取样；strength -1000..1000。0现在会得到零幅结果 |
| frame_lag/cycle | frame_lag 0..1000可小数，仅平移。循环保留原首样本替换末端采样规则，非通用循环缝合或无限循环模拟 |
| remove_parent/ignore_translation | remove_parent明确可读transform，按原矩阵算法去该父运动；ignore_translation默认True仅旋转，开启忽略自身translation |
| distance/distance_only | 正有限distance≤1000000；自动距离用组内邻居或子节点，单个无child回退默认1；distance_only需明确distance，强制同一距离 |
| animation_type | replacer：旋转先删(start+1,end)、平移删(start,end)，再逐帧写含start；additive：保留区间外键，按原规则把原通道每帧值加到新计算值；deleteall：删目标通道/指定层全部时间键再生成范围内键 |
| target_layer/new_layer/override | target_layer明确可写非Base层，或new_layer=True创建私有UUID层；两者互斥。override决定新层为override或additive，默认additive；已有层保留原类型 |
| overshoot/overshoot_first/overshoot_between/overshoot_end | 原稳定区峰谷衰减算法；first仅每组首项；between/end控制中间/末端；strength非零有限±1000，frequency整数1..100。可生成结束帧后的衰减键，预检明示此影响 |
| wind/winds/wind_strength/wind_absolute | wind开启需有启用的完整tag风控；winds省略发现所有namespace深度风控并去重，显式限定列表；wind_strength可负；wind_absolute影响平移累计风位移，旋转原来始终累计 |

动画层仅增添选择的attrs，不再把选中对象所有可动画通道加入层。setKeyframe(animLayer=目标层,noResolve=True)把原算法产出的数值写为该层原始值，cut/scale通过findCurveForPlug只编辑该层曲线；原代码受Maya当前层隐式分派，本候选明确目标。其他层/base曲线保持，选中/首选层标志恢复，新建层结束后取消选中/首选。additive本身指原数值相加，不等同于additive层；explicit layer下原读取仍是场景合成值，结果当该层原始数值，视觉可能再次叠加，需验收layer权重/父级反馈。已有层通道未指定目标层或新层直接拒绝，不猜测层。

## 预检、撤销与文件影响

validate/dry_run仅读节点、播放范围、图/层/风/文件与完整预设，不改时间、选择、AutoKey、namespace、layer标志、Undo、optionVar，不创建节点/GUI/文件。模块首次import不导入Maya/Qt；执行业务才载入QObject，GUI仅open_ui。Maya2025 mayapy可以检查算法，不具备原生窗口/渐变/按钮验收条件。

写入仅本地未锁非实例transform控制器；joint、referenced target、非零rotateAxis、constraint/非时间驱动、共享曲线、选中通道/compound锁拒绝。输入风或移除父级仅读取，允许reference作为只读输入；set_winds不能写引用/锁/已有driver的wind开关。允许普通时间曲线、unitConversion、原生animBlend层图；已有外部driver拒绝。层图拒绝未知节点，未承诺制作rig所有复杂驱动可用。

原worker/UI不可靠的手工open/closeChunk去掉，标准BaseMayaTool统一Undo；业务只在私有活跃范围执行，直接调用原native写方法会拒绝。目标节点UUID、attrs验证，fresh wind仅自有曲线/形状可加attr/接线，force连接去掉。cutKey clear=True不替换Maya键剪贴板。context finally逐项恢复时间/选择/AutoKey/namespace及原层标志，即使worker异常；失败不自动回滚已写曲线，结果fail说明一次Undo恢复。外部JSON导出不在Maya Undo范围，成功路径明确提示。

风曲线保持原overslapper_tag="wind"，原风控改名仍按tag找到，visibility不关闭风；新风名私有UUID并附mayaToolkitOverslapper，不安装其他资产。重复风原3层namespace通配改所有层扫描/去重，风强度0/负支持。wind_paths正/逆矩阵修为不同列表，避免原别名导致正路径被取负。

预设保留原八组和拼写stifness，完整/部分导入先整体类型/索引/数值/渐变校验再更新原UI；完整JSON≤1MB。新增兼容可选base_overlap.frame_lag、wind.strength以补齐原未保存这两值，旧默认依然可读；新导出往返含这两值。导出取消不写文件；已有文件需要Qt保存对话框确认或API overwrite。同目录临时JSON，独占hardlink创建（要求支持hardlink文件系统）或显式覆盖os.replace，并核对签名防预检后变化，不自动建文件夹。格式/路径/冲突错误如实返回，不运行JSON里的代码。

UI完整渐变仍需Maya gradientControlNoAttr/optionVar；原全局pratte_custom_var改私有mtkOverslapperCandidateGradient，候选窗口关闭清理私有gradient/window，既有私有名存在时拒绝覆盖。它属于UI会话设置，非scene Undo；Maya正在保存偏好时仍可能暂时包含该私有optionVar，未承诺磁盘绝无UI偏好写入。渐变、原图标、56+4方法、progress都保留；source slider文字同步现在blockSignals以避免负wind或小数frame lag被slider范围/精度覆盖。没有后台QThread发Maya命令，worker同步执行，GUI大范围仍可能短暂无响应。UI鼠标BusyCursor由桥接finally单次恢复，原error_ui不关闭别人的Undo或cursor。

其他具体修正：平移删除分支add改additive，不再误删全部键；去无关的mc.move(0,0,0)避免清零未选轴，parentMatrix采样不依赖该清零；0 strength缩放执行；单个无child默认距离；aim上轴长度使用up vector而非target vector；过冲末区int/string键查找修正、零距离最少1避免除零、end本来绝对帧不再加start_frame。其他过冲公式/峰谷/decay保留，不能承诺只在请求范围写或所有曲线形状稳定。

## 示例及关联

真实Maya候选通过launch_candidate.py取tool，转正后注册可调用：

```python
import maya_toolkit
args = dict(targets=["tail1_ctrl", "tail2_ctrl", "tail3_ctrl"],
            frame_range=[1, 48], mode="rotation", order="selection",
            axes="xyz", main_axis="x+", up_axis="y+", stiffness=0.5,
            new_layer=True, override=True)
preview = maya_toolkit.execute_tool("overslapper", args, dry_run=True)
if preview.success:
    result = maya_toolkit.execute_tool("overslapper", args)
    print(result.to_dict())
```

输入为已有父级动画/控制器与选项，输出是该控制器旋转或平移帧键和可选风/层，不创建particle/solver。适合原地延迟/尾链secondary motion；不能把每个控制器自身的任意孤立动画当主驱动而保证相同输出。Keyframe Overlap候选使用particle目标，是相近用途但不同物理/采样方法；keyframe_reduction可在验收动画、确认合并到本地普通曲线后减键，不可直接碰未显式支持的动画层图；anim_filters处理后还需重新检查循环/峰值。关联仅静态用途建议，未进行组合Maya验收。

## 验证与晋级

普通Python3组检查完整原资源hash、原函数/类方法保留、Schema/参数/懒加载、八组预设与坏输入。隔离Maya2025六组实际检查纯父平移解析结果/additive区间外保留/未选轴/zero strength/cycle/UndoRedo、六旋转顺序和单无child、三层namespace风曲线/正逆矩阵/开关Undo/rotation-translation wind/移除父级、其他层/base不变与目标层deleteall/scale/旗标恢复、第二键异常finally/Undo/constraint/shared-unchosen channel拒绝、临时JSON/dry覆盖/真实过冲可执行。原Qt QWidget从未实例化；GUI视觉/高DPI/渐变/部分导入/层混合/实际运动质量仍需acceptance.md，不能把mayapy通过当用户验收。

状态prepared_unverified，所有Maya GUI仍not_run；未改正式maya_toolkit/tools、注册表、core或knowledge。promotion.json完整镜像目标代码/9原资源/运行图标/默认JSON/说明/两份tests；预制晋级脚本检查候选hash与人类Maya验收记录后搬迁并加ALL_TOOL_CLASSES/面板。未执行apply，晋级前不需额外封装。
