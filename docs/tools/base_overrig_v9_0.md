# Base OverRig 9.0

用途：原始 OverRig 动画方法套件，将已有动画转换为便于编辑的附加定位器、结、层级、IK、重叠与物理系统。原作者 Barnev Pavel；完整分发包有10个文件，包括368204字节 MEL、安装脚本、ENG/RUS PDF手册、热键说明、两张图标和 Jiggle_Bone_New.mb。所有字节及 License.txt 保留，catalog.json记录逐文件SHA。许可规定不得修改原代码/再分发，商业用途需购买；本次只建立自用外围适配，不运行安装脚本、不购买、不发布。

## 完整功能与入口

原始 MEL 包含308个声明、307个独立过程，一个内部过程重复声明保留。完整主界面、各子窗口及原始业务代码在 vendor 中，没有用简化模拟替换。外围 API 开放57个原始公共过程，内部 BOver9_0_* 与通用 find 仅由原引擎使用，不接受任意 MEL 代码。下列功能族均保留：

- 标准/智能/双全局/双局部/定向/枢轴/跨父结，前向/反向层级、parent in/out/swap、对象及组件快照。
- 全范围、选区保留外键、智能及动画层烘焙，Bake source/delete knots、约束混合通道清理。
- 三对象或多对象FK→IK、独立/依赖Spline IK、脊柱重计算、Aim/Sword/总枢轴、物理Jiggle Bone、尾链重叠。
- 动画键滞后/周期偏移/振荡/反向镜像、开始结束键、选区键、拷贝缩放粘贴、Tween/Noise及GraphEditor infinity。
- 归一化姿态定位器、定位器/joint显示大小、源/结集合选择、约束源查询、快速MotionTrail、Arc Polish及完整子窗口。

运行候选 launch_candidate.py 的 load_tool() 取得工具；show_ui() 显式打开完整原始界面。无需Shelf/userSetup/热键安装。适配启动时将原 `$path_to_JGLBN` 指向完整候选 vendor/misc，晋级后自动随正式路径，不引用外部待整理池路径。原引擎所有 MEL 名称/全局变量与窗口名称未改；已加载其他版本或不同来源的同名过程时拒绝覆盖，需新的 Maya 会话。

## 统一参数与结果

| 参数 | 默认/条件 | 含义 |
| --- | --- | --- |
| action | inspect / call；默认inspect | 资源和过程说明，或调用明确公共过程 |
| procedure | call必填，Schema枚举57过程 | 必须为完整原始过程名 |
| arguments | []，数量须与原签名一致 | 位置参数，严格int/有限float/string及数组；正尺寸/比例/周期 |
| objects | 可选，有序唯一完整节点列表≤1000 | 省略时读取当前选择；建议明确输入，输入顺序有业务意义 |
| rotate_order | 0，0..5 | 每次API调用设置原结旋转顺序全局值 |

inspect 不接受其他场景参数，返回全文件/SHA、57公共完整签名、直接影响标记、声明数/重复名、许可及not_run验收状态；其 validate/dry_run 不source脚本、不创建窗口、不注册回调、不改全局变量/选择/时间/选项或文件。call预检完整资源与同名过程、参数、输入/形状锁引用及实例、明确对象数组和必要有序输入数量；源/结集合烘焙删除要求明确scope包含两套集合所有成员。API对引用/锁输入保守拒绝；原生UI仍按作者原始逻辑运行，其输入条件需单独实测。

调用示例（正式晋级后）：

```python
maya_toolkit.execute_tool('base_overrig_v9_0', {'action': 'inspect'}, dry_run=True)
maya_toolkit.execute_tool('base_overrig_v9_0', {
    'action': 'call', 'procedure': 'scale_selected_lock_or_joint',
    'arguments': [1.5], 'objects': ['locator1'],
}, dry_run=True)
```

通过BaseMayaTool.run返回ToolResult，通过框架导出OpenAI/MCP Schema。call结果包括 procedure、arguments、objects、signature、native_result、created_node_uuids、native_result_selection 和Undo限制。原void返回None不表示创建了有效结或烘焙成功；需核对输出/Script Editor。参数/资源失败在预检返回failure，真实执行失败返回原错误，不能把原catch吞错变成所有业务均验收成功。

## 影响、状态与撤销

统一call调用原版过程，使用框架UndoChunk；记录原MEL嵌套开关，在异常时补关本次未关闭的内部chunk，不关闭未知外部chunk。恢复调用者时间、选择、namespace、autokey、线性单位、evaluation mode、refresh suspend、选择顺序偏好、八个原有optionVar和插件autoload状态；真实交互模式还恢复cache preference/timeSlider显示。中点时间和集合/约束对象选择过程保留其明确目的的时间/选择输出。native globals/复制键缓存保留供原多步工作流使用。

许可限制下原算法不修改、不自动回滚。原native catch可能静默拒绝部分操作，出现错误需检查备份场景并尝试一次Undo。MotionTrail内部含disable-Undo；scriptJob、scriptNode、插件加载、界面/preferences及全局变量不由普通scene Undo保证。原脚本可扩大范围到父子、连接对象、OverRig集合、关键帧和blendParent/blendOrient/blendPoint/blendAim/MaxHandle混合属性；预检只覆盖已明确输入，不声称所有内部影响都可静态证明。普通API不是沙箱。

原始完整UI启动及其回调有作者定义的runtime/preferences/layer选择影响，与外围API的恢复策略不同。主窗口会设置trackSelectionOrder与animLayerSelectionKey；Arc工具可设置matrixNodes autoload，其他功能可加载lookdevKit、建立选取回调/场景scriptNodes、读取候选MB模型。原始“zxy”默认radio写6（Maya rotateOrder常用0..5），该可疑源行为保留且待GUI复验，不暗中修补许可源代码。

没有运行Drag_and_Drop_to_install.mel，没有写userSetup、热键、Shelf或用户工具目录。API无外部导出/覆盖操作；物理功能会向场景导入候选MB，对场景产生节点/namespace/scriptNode影响，真实备份场景中验收。原始许可与手册不修改。

## 可组合与验证

可在已有烘焙动画后建立OverRig附加结构，再使用动画曲线整理工具或速度测量检查输出。Weights Copy处理的是蒙皮权重，不能替代该套件的动画层级/约束变换。具体跨工具组合尚未实测，尤其共享公共MEL名字的套件需先检查source冲突。

普通Python检查10原资源字节SHA与57签名/Schema/参数防注入。隔离Maya2025加载全部307过程无场景或窗口副作用，并检查真实原定位器缩放与Undo/Redo、真实归一化姿态定位器与Undo、混合约束属性清理/外部对象与userNote保留/Undo、只读预检与锁拒绝。批处理缺少timeline/GraphEditor时拒绝复杂交互过程，未伪造这些内置UI。全套窗口、生产绑定、IK/烘焙/物理/重叠/FBX等后续输出、其他版本均not_run。保留prepared_unverified，见候选acceptance.md完成真实验收后再晋级。
