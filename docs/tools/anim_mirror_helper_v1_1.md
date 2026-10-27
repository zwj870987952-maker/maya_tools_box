# Anim Mirror Helper v1.1 候选知识说明

tool_id: `anim_mirror_helper_v1_1`；类别 Animation；适配版本 `1.1.1-adapter`。
作者 Pavel Barnev；本地来源 `Anim_Mirror_Helper_v1_1_studio_lic`。目录名 v1.1，原始窗口标题仍写 v1.0，适配不修改标题或原算法。

用途是把一组控制器的运动记录到镜像系统中，再连接另一侧控制器，以偏移时间重算步行、跑步等循环动画。它不是通用骨架自动识别器，也不实时求值镜像；原指南要求更改源动画后点击重算。原文件的速度及性能宣称没有作为本项目实测结论。

## 来源与完整性

候选内 `upstream/` 保留 MEL、原安装器、Studio License、BMP 图标、英俄两份 PDF 共六个文件，字节校验在 `catalog.json`。不执行拖放安装器；它会向当前 shelf 添加按钮。显式加载仅 source 完整 MEL，然后配置包内图标路径，不转换原 MEL 的旧编码。签名目录涵盖全部 90 个 global proc，原算法及原 UI 回调不做改写；混淆名称仍可通过 `invoke` 调用。

`License.txt` 是作者自定义商业协议，限制修改与再分发。本候选为现有本地副本的外部适配，不赋予公开发布、转载或重许可权。原许可随完整素材保留。

## 前提及原始行为

需要交互式 Maya、可写的测试绑定、已打开 Undo，以及正确的控制器选择顺序。核心系统使用 locator、group、joint、blindDataTemplate、约束、属性与视口 buttonManip。系统生成 `mirror_system` 与 `mirror_system_gr`，前者具有 `Offset`、`Cycled`、`calculate` 等属性；内部以 `base_group_for_mirror` 和 `base_group_not_mirror` 的相对坐标传递运动。

通常先让角色处于对称姿势，选一侧全部待镜像控制器，创建系统；设置侧名称后连接另一侧，Offset 通常取半周期。已有动画可借临时动画层建立对称姿势，连接完成后删除临时层；此步骤由用户控制，适配器不自动删层。缩放镜像需要手动 scaleConstraint。前后腿同侧传递可修改镜像基组 scale 为正值；前移步行需让系统总组随主控制器移动。添加遗漏控制器后，仍须连接对应另一侧。

自动连接包含属性连接及设关键帧，不仅是 transform；`select_pairs` 也可能设关键帧，不能当只读检索。匹配基于原名称替换规则，复杂 namespace、异向轴、多个同名候选和引用绑定需实测。

## 参数与常用调用

统一入口是 `AnimMirrorHelperTool().run(dry_run=True/False, **kwargs)`；转正注册后可调用 `maya_toolkit.execute_tool`。`action` 默认 inventory；`procedure` 默认空；`arguments` 默认 `{}`；`force_reload` 默认 false，且仅显式执行加载时生效。多余参数及错误类型在 validate 中拒绝。invoke 的 procedure 必须是 catalog 过程，arguments 的键必须与原参数名完全一致；全部签名另见 `anim_mirror_helper_v1_1_procedures.md`。

| Action | arguments | 选择及影响 |
| --- | --- | --- |
| inventory | `{}` | 返回原过程签名、资源哈希及常用映射；无需 Maya，无 source |
| load | `{}` | 显式加载 MEL 与图标全局变量，不创建系统或安装 shelf |
| open_ui | `{}` | 打开完整原始窗口；原按钮继续执行原 MEL |
| create_system | `mirror_axis: x/y/z, offset: float, cycled: 0/1` | 选源控制器；创建系统、属性与视口操作器 |
| add_items | `{}` | 选新增控制器，最后选已有系统 locator |
| auto_connect | `side_from: string, side_to: string, rig_type: Symmetric/SymmetricRotate/AdvSkel` | 只选一个系统 locator；生成约束、关键帧与同名属性连接；AdvSkel 为原隐藏分支，待单独验收 |
| attach_pairs | `type: parent/orient/point, offset: 0` | 依次选镜像对象/目标控制器，多个有序对；创建 locator 和约束。原 across 过程忽略 offset，适配仅接受 0 |
| select_pairs | `side_from: string, side_to: string` | 选镜像对象；查另一侧、改变选择，原过程可能设键 |
| connect_attributes | `{}` | 有序镜像对象/控制器对；强制连接同名用户属性 |
| copy_rotation | `{}` | 选一个对象；写原 MEL 旋转剪贴板全局变量 |
| paste_rotation | `{}` | 选目标对象；使用原旋转剪贴板，先 copy |
| mirror_rotation / zero_rotation | `{}` | 对选中对象调用原 UI 的 object space rotate 180/0 0 0 |
| calculate | `{}` | 只选一个系统 locator；重算错帧动画 |
| bake_selected | `{}` | 选目标控制器；原 UI 四段流程：暂停、bake、Euler 处理、恢复；使用 animationStartTime/animationEndTime，不是 playback min/max |
| delete_system | `{}` | 只选一个系统 locator；删除原连接系统，先确认烘焙结果 |
| invoke | 原过程的同名参数 | 专家入口，保留全部内部辅助过程；选择、域、依赖与影响须查原代码，常用 action 的选择保护不覆盖 arbitrary invoke |

string、int、float、string[]、vector[] 由类型序列化，禁用非有限数字和字符串控制字符；vector[] 是 `[[x,y,z], ...]`，平均坐标过程拒绝空数组。外层参数不会被拼成任意 MEL 语句；原内部 `eval`、`command` 字符串仍按原语义执行，不能将专家入口视为受限脚本沙箱。

```python
# 在验收启动器 load_tool() 获取候选实例后
tool.run(action='create_system', dry_run=True,
         arguments={'mirror_axis':'x','offset':12.0,'cycled':1})
tool.run(action='create_system',
         arguments={'mirror_axis':'x','offset':12.0,'cycled':1})
# 创建后只选生成的系统 locator；确保测试绑定侧名确为 _L/_R
tool.run(action='auto_connect', dry_run=True,
         arguments={'side_from':'_L','side_to':'_R','rig_type':'Symmetric'})
tool.run(action='auto_connect',
         arguments={'side_from':'_L','side_to':'_R','rig_type':'Symmetric'})
tool.run(action='calculate')
```

`validate` 与 dry_run 仅校验目录、参数和场景查询，不 source、不配置全局图标、不动选择、不设键、不建约束。常用写入 action 拒绝选中引用/锁定节点，要求整个 transform；attach/connect 要求偶数对象；add 要求系统最后；calculate/delete/auto 要求唯一且连接原系统的 locator。复杂原内部目标不能静态穷尽，此预检不能证明系统最终匹配正确。

## 输出、撤销与状态

返回 ToolResult，包含命令/参数预检数据、source 路径、源是否重新加载、原过程返回值、错误与运行状态恢复错误。成功表示 MEL 返回，不表示所有镜像效果正确；原 catch/catchQuiet 可吞掉单项错误，必须看 Script Editor 和场景。调用异常会返回失败，已发生的场景变动不会自动回滚。

框架 run 将场景写入包进 UndoChunk。适配执行 finally 恢复 Evaluation、refresh suspend 和交互 Maya 的 timeSlider 可见性；恢复失败也返回失败。原 UI、MEL 全局过程定义、图标全局变量、旋转剪贴板和 move tool context 不由场景 Undo 撤销。原始 UI 与视口按钮直接调用原 MEL，不经过适配的 validate 或 finally，原快捷按钮报错后仍需检查 Maya 状态。

本接口不写用户外部文件、不自动安装 shelf，也不覆盖文件；打开指南由 showHelp 调用系统查看器。保存场景、改棚架或外部导出由用户另行操作，不由场景 Undo 撤回。

## 实测边界与组合

隔离 Maya 2025 已加载全部 90 个过程，并核对 whatIs 来源与图标路径；离线静态/资源/契约测试及 standalone 的 vector[]、单位换算、dry-run 无 source、运行状态恢复通过。这不能替代真实 GUI、绑定连接、循环/非循环偏移、scale、视口按钮和烘焙测试；状态 prepared_unverified。

可先用现有 animation layer 工具准备姿势和源动画，再配置镜像系统，重算并烘焙后用 anim_filters 检查曲线。但这些工具的跨工具顺序尚未实际验证，不宣称组合已可生产使用。不得将其他工具的全场景删书签、删层或曲线过滤直接套到镜像系统。

本轮新增外部适配、目录契约和预检，保持原业务代码/资源不变；无可安全下沉 core 的新算法，复用现有 BaseMayaTool/ToolResult/UndoChunk。真实 GUI 暴露缺陷后只修对应候选，再重新验收晋级。
