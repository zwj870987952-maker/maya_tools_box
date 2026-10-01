"""Write the complete source-indexed candidate knowledge and acceptance documents."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RC = ROOT / 'tools_staging_pool/01_animation/physics_tools/release_candidate'
inventory = json.loads((ROOT / 'plans/staging_run/physics_tools_source_inventory.json').read_text(encoding='utf-8'))
knowledge = '''# Physics Tools 1.8：完整 MEL 动态与动画套件候选

状态：prepared_unverified。Maya2025 隔离 mayapy 检查不等于真人 GUI/生产绑定/运动品质验收；本候选留在 tools_staging_pool，禁止直接执行原始文件的自动入口。

## 来源与完整性

原文件 PhysicsTools_v1.8.mel，307004 bytes / 7314 行，署名 IURI MONTEIRO，Version 12/10/22，modified by k31。未附独立许可；只作本地个人整理，不推定再分发或修改授权。upstream 原文件字节归档，catalog.json 保存 SHA256；physics_tools_changes.diff 显示全部适配。原 109 个无参数 global proc 的完整主体和 319 行主 UI 保留，五段内嵌 Python 保留完整函数算法，非删减重写。

保留粒子质心/goal 平移、六主轴/上向量旋转、Jiggle 平面/毛发 follicle、多个控制器烘焙、局部空间、代理球/立方体、匹配/约束、临时 pivot、轨迹/ghost、播放速度、键偏移、Euler 过滤、曲线循环和每 1/2/5 帧噪声流程。跟踪/Rivet/Ghost/editor 等 Maya runtime command 或外部资产仍须在实际交互 Maya 中核验。主 UI 的外部网址/教程按钮会按原行为打开浏览器；API 不自动调用这些过程。

## 目标结构与复用

maya_toolkit/tools/physics_tools/{tool.py,runtime.py,native.mel,catalog.json,upstream/}；正式文档 docs/tools/physics_tools.md；目标 tests/test_physics_tools.py；附隔离 mayapy 测试。BaseMayaTool 的 run/ToolResult/UndoChunk/Schema 协议复用现有 framework/core，不改生产 core。原套件的 particle、Jiggle 与 MEL editor 流程依赖 Maya 自身，不能拿其他工具的关键帧平滑当等价替换。共享数学/文件能力仅记录为后续组合边界，本轮不迁入 core。

## API 参数与输出

tool_id=physics_tools；action：inspect 默认，只读状态与过程目录；invoke 执行一个原过程；open_ui/close_ui 管理候选原生 UI；cleanup_session 清理本候选所有助手、烘焙层/曲线、会话 marker 与登记缓存。procedure 是 catalog 的 109 项枚举。targets 是明确有序选择，省略沿用选择；依赖会话的无目标过程省略时检查会话原目标。源在前、目标在后；单控制器 setup 严格一个 transform；实例/joint/未允许引用/锁/已有外部 driver、约束或 layer 拒绝，普通独立 time animCurve 允许。RemoveConstraints 是显式例外，只删除所选目标的可写现有约束，并拒绝共享目的端。

frame_range 是闭区间整数，省略 playback min/max；端点 ±1000000、跨度 ≤10000、样本预算 ≤100000。原展开式多目标操作仍有有限容量，超限拒绝，不默默截断。overlap 0..10 默认2；weight/softness/damping 0..1 默认0.5/0.1/0.4；jiggle_weight 0..0.9 默认0.7。GUI 仍从原 floatSliderGrp 读值。attributes 可指定噪声通道，默认选中对象共同 keyable TR 通道；原 Channel Box UI 对应改为明确参数范围。allow_reference_edits 默认false；GUI 新增复选框，显式允许时可能留下键/约束/临时 lock 的引用编辑，需备份场景核对。

cache_directory 是 CacheMe 必须提供的已有父目录，GUI 点缓存按钮会让用户选目录；不会自动改项目规则。ToolResult.data 返回 procedure、targets、frame_range、会话 namespace、owned_nodes、cache_files 或 deleted_nodes。失败包含实际 errors 和已生成缓存路径；外部文件不可 Maya Undo。inspect/validate/dry_run 不编译 MEL、不造助手/会话、不加载 GUI、不改选择/场景/文件/Undo 队列。

```python
# 真人 Maya Script Editor；绝对路径仅启动候选，运行包内部不依赖 staging 路径。
import runpy
tool = runpy.run_path(r'E:/GitHub/maya_tools_box/tools_staging_pool/01_animation/physics_tools/release_candidate/launch_candidate.py')['load_tool']()
tool.run(action='open_ui')
tool.run(action='invoke', procedure='PhysicsMagicButton', targets=['myControl'], frame_range=[1,24], dry_run=True)
tool.run(action='invoke', procedure='PhysicsMagicButton', targets=['myControl'], frame_range=[1,24])
tool.run(action='invoke', procedure='BakeinfoController', frame_range=[1,24])
# cleanup_session 也删除本会话烘焙层/曲线，保留结果时不要调用它。
```

## 场景影响、保护与已改变行为

正式写入由框架单次 Undo 分组，失败不会自动回滚，明确一次 Undo 恢复已写场景。private mtkPTC_ MEL globals/UI 与 mtkPhysics_<UUID> 助手 namespace 隔离原版。首次场景操作创建 network JSON marker，记录自有 UUID/原目标/缓存；原全场景 *Physics*、*particle*、*nucleus*、hairSystem* 的删除由当前 namespace 和 UUID 守卫约束；外部子节点或非目标输出导致拒绝（Maya 默认 shading membership 例外）。其他副作用仍由完整原 MEL 产生，私有命名空间不是场景写入沙盒；未知 runtime command 需要人工验收。

真实隔离检查发现删除 legacy particle graph 会连带删除目标控制器；候选先删除自有约束，临时保护原目标，再按 DAG 根和其余节点逐个删除，finally 恢复 lock。避免同时删除 particle/set/curve 引发 Maya bulk-delete 卡住，已检查控制器存活与 Undo。不批量删除全场景 diskCache；仅删除 marker 登记的 .mcj，目录 owner.json/session_id 与父路径校验一致才操作。没有场景会话时 cleanup_session 不创建 marker。

去掉原顶层 print/自动开窗；原 Connection Editor/Goal UI 的镜像调用取消，保留实际 particle/goal/连接业务。所有过程须进入统一 API scope，直接调 private Native_* 拒绝；回调 wrapper 再入同 scope，不重复开 Undo。助手名由目标 leaf+UUID 构成，支持命名空间目标；修正绝对 DAG 与 namespace/layer 名，避免 relativeNames 丢失助手前缀。多选择数组越界前先判断 size；空 PhysicsSets 已被 Maya 自动移除时不再访问；原重复点击判断/流程顺序大体保留。

doJiggle 改为对应原生 jiggle+diskCache 节点和原默认参数，避开 Autodesk helper 自动改 workspace 文件规则/隐藏缓存路径。createHair、follicle 和原烘焙仍完整保留；有些 Maya 版本的节点命名/runtime command 可能不同，未知失败如实返回，不能据定义编译宣称通过。

finally 逐项尝试恢复时间、AutoKey、playback 范围/速度、refresh suspend、绝对 namespace/relativeNames、原层 selected/preferred、原选择。明确 PlayEveryframe/PlayNormalframe 保留速度效果，ParticleOptions/LocalspaceLoccontrolerselect/SProxies*/RotWorkflowSelect 等保留原目的选择。原 selectMode/工具上下文/editor/ghost/browser 状态属于交互 Maya 会话，不由场景 Undo 承诺恢复。GUI UI_only 原过程未在 mayapy 强行执行。

五段内嵌 Python 保留全函数，执行在私有 dict 内，以命令代理检查写入范围，不污染 Maya __main__。循环曲线保留首末键算法。噪声保留 random 与原采样步长，显式通道端点写键、新建自有 layer，不隐式向别人选中的 layer 增通道；恢复进程 random 状态。随机运动无固定种子，未承诺跨次相同；新层合成/前后键仍需真人核对。

## 文件、副作用与组合边界

CacheMe 在显式目录创建唯一 mtk_physics_<session> 子目录、owner.json 和 UUID.mcj。Maya diskCache 全局命令运行时临时禁用可写的其他 enabled cache，finally 恢复；他人 enable 被锁/驱动或引用则拒绝。不会删其他缓存，不安装资产、不写用户 shelf/userSetup、不改项目规则、不装依赖。已写/已删缓存不由 Undo/Redo 恢复；cleanup 保留空自有目录及 owner.json 供追溯，文件清理失败报告实际错误。Maya可能在场景保存时记录 marker/cache 节点，执行前先保存备份。

输入是控制器/选区/时间范围，输出是预览助手、动力学连接和烘焙层或曲线。可先用已验收空间匹配/控制器定位工具准备干净 transform，再执行预览→烘焙；烘焙后可由曲线过滤/减键工具进一步处理，但必须分别验证 layer 与 driver 兼容。UI/editor 工具和缓存文件不构成可自动 Undo 的组合事务。所有关联仅是候选组合建议，未把静态依赖当作实测。

## 已有证据与仍需验收

普通 Python 检查全部 109 private wrapper/native、原资源/hash、归属保护入口、Schema/懒 import；Maya2025 隔离六组：109 过程定义编译/guard/dry/inspect；locator/namespace/清理/UndoRedo；粒子 goal 预览→烘焙→Undo、完整清理→Undo 且目标保留；原内嵌曲线循环/噪声；真实 jiggle/diskCache/.mcj 创建删除与注入失败后上下文恢复；外部 child/driver/lock 拒绝。所有测试使用新场景、临时 preferences/cache；未构造主窗口，也未使用生产 rig。

临时正式布局另检验全部 payload import、注册/面板条目、Schema，不写真实生产目录。真人须按 acceptance.md 验证主 UI、所有分组按钮/slider、源选择顺序、advanced six-axis、Jiggle+hair 全流水线、各多选择容量、localspace/proxy/pivot/track/ghost/Euler/浏览器与 production rig/layer 品质。当前没有 Maya GUI acceptance，其他 Maya/Python 版本尤其 Maya2022 Python3.7 未通过；候选使用 Python3.9+ 的 API，首选本机 Maya2025。

晋级只能在真人满意后调用 plans/staging_run/promote_candidate.py，promotion.json 已准备完整目标文件与 ALL_TOOL_CLASSES/面板注册；本轮只 preview 和临时布局。许可限制也必须先处理，不能发布 upstream 或改稿。

## 原过程完整索引

以下顺序/行号来自原文件；每项完整主体在 native.mel，对应参数语义以原过程/主 UI 为准。存在表中不表示该项已动态实测。

| 原过程 | 原行号 | 主体行数 | 条件/依赖 |
| --- | --- | --- | --- |
'''
for row in inventory['procedures']:
    flags = []
    if row['embedded_python']:
        flags.append('完整内嵌 Python')
    if row['cache']:
        flags.append('自有缓存适配')
    if row['uses_ui']:
        flags.append('GUI依赖待验')
    flags.extend(row['external_calls'])
    knowledge += '| `{}` | {} | {} | {} |\n'.format(row['name'], row['line'], row['lines'], ', '.join(flags) or '按原流程选择/助手状态')
(RC / 'docs/tools/physics_tools.md').write_text(knowledge, encoding='utf-8')
(RC / 'acceptance.md').write_text('''# Physics Tools：真人 Maya 验收（尚未运行）

只在备份新场景、临时目录执行候选 launch_candidate.py，不 source 原文件。首选 Maya2025；保留现有原版窗口时检查私有窗口共存。先记录场景、当前工具/选择模式、时间/AutoKey/namespace/layer/editor；不要把以下步骤当作通过记录。

1. `load_tool()` 后 inspect/dry_run；核对 scene/文件/Undo 无变化，再 open_ui，完整分页/scroll/sliders 无致命 Traceback，默认 Allow reference edits 关闭。close_ui 只关候选窗口。
2. 一条平移有键的普通控制器，在1..24帧 PhysicsMagicButton 预览，调原 overlap/weight，再 BakeinfoController。控制器不能消失、他人 Physics/particle/nucleus/hair 节点不变，检查烘焙新层/结果和一次 Undo/Redo。隔离环境已修旧粒子删除连带控制器的危险，仍需实际 rig 复核。
3. 在另一新场景直接 preview→cleanup_session，核对目标存活、锁状态恢复、助手消失，Undo 恢复全部预览。cleanup 也删除本会话已烘焙层/曲线，想保留结果时不要执行它。
4. advanced 六主轴/正负/上向量、Aim locator/up locator、各刷新 slider→rotation bake；检查 rotateOrder、越轴和运动品质，不以定义编译代替。
5. SetupPhysics 与 SetupRotationsPhysics：Jiggle平面、follicle/createHair 原命名、softness/damping/weight 实时与烘焙；在已存在hairSystem1/nucleus1的备份场景核对原节点不被删。
6. CacheMe 只选临时父目录，确认仅新 owner 子目录有 .mcj；其他缓存 enable/文件不变；缓存开/关/RedoMe/BakePhysics 与 cleanup。文件不能 Undo，Redo也不自动重建被删文件。
7. 多目标平移10、旋转30、TR20、Localspace11的实际原容量和顺序，超限/空选择安全拒绝；相同leaf不同namespace、深层父级、局部空间/localspace bake/删除。
8. proxy球/方/locator、武器/手工作流、匹配/约束/pivot，源前目标后；对象层级及自有命名正确，重复点击不删他人助手，RemoveConstraints不会删共享外部约束。
9. track 01/02/03 与 Rivet/ghost/editor/Graph Editor/Euler/key-offset/播放速度，缺命令/资产时记录原错误，不宣称通过；浏览器按钮可单独选择验收。
10. 曲线循环比较前后键；1/2/5帧噪声在timeline选区/全范围、指定通道、新layer，对比端点/层合成和未选通道，Undo/Redo。
11. 锁/驱动/层/实例/joint/引用默认拒绝。需要引用编辑时显式复选，仅在备份引用场景检查产生的 edits。选区节点被重命名/删除、外部child接入助手/外部输出时拒绝cleanup，保留原对象。
12. 中途故障检查finally时间/选择/AutoKey/refresh/namespace/layer flag；显式选择工具与速度按钮允许留下原效果。selectMode/工具/editor/ghost属于会话状态，按记录手动恢复。

记录实际Maya/Python版本、每组成功/失败、Script Editor错误与运动观感；全部满意后才按promotion.json晋级。主GUI及完整hair/advanced/runtime-command/生产rig尚未验收。未附独立许可证，只本地个人候选，不发布。
''', encoding='utf-8')
print(json.dumps({'documented_procedures': len(inventory['procedures'])}))
