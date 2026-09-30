# Universal IK FK PRO 候选知识说明

工具 ID `ik_fk_switch`，animation，Pro版本3.0 (2021-10-06)，Monika Gelbmann。原Pro、旧版1.10源码与安装说明共3资源逐字节保留，未附独立再分发授权，私有本地整理不公开。native.py保留Pro的13全局函数和19原UI方法，完整临时控制器/约束、RP IK链、pole vector投影、腕部rotation offset、左右手臂/腿与六bend-axis的匹配算法；旧版源码完整归档，不作为候选主入口。所有适配差异在ik_fk_switch_changes.diff。

## 功能与依赖状态

完整原Pro界面包含定义控制器/side/limb、0为FK或IK、0..1或0..10、knee bend/rotation offset、Store保存更新/读取/从选择查找、match双向、单纯switch、选择/打键、逐帧与AllKeys烘焙、Store导入导出及帮助。本机Maya2025缺少pymel.core，当前只验证了标准元数据、切换与打键路径，**原匹配/临时IK链/烘焙/完整UI均未执行验收**。候选惰性加载PyMel，在缺失时返回明确失败，不安装/下载依赖。目标机器需有与Maya/Python兼容的PyMel，再执行人工验收。

API `IKFKTool.run(dry_run=False, **arguments) -> ToolResult`。`action`包括inventory、records、store、load、match、switch、key、bake、export_store、import_store、open_ui。native_callback仅原UI临时已注册ticket，不能传代码。

| 参数 | 作用 |
| --- | --- |
| fkshldr/fkellbow/fkwrist | FK上臂/前臂/腕控制器，唯一transform/joint，五个动作控制器须不同 |
| ikwrist/ikpv/switchCtrl | IK腕、真实Pole Vector控制器、开关控制器；不支持属性式pole vector |
| switchAttr/switch0isfk/switchAttrRange | 已有数值开关属性、0是否FK、范围1或10 |
| direction | to_ik为FK→IK；to_fk为IK→FK |
| rotOffset/side/limb/bendKneeAxis | 三有限偏移角、R/L、arm/leg、±X/±Y/±Z，遵循原制作rig校准 |
| record_id | 自有Store transform UUID，load或动作可据message恢复当前控制器名 |
| start/end/keys_only | API bake整数包含两端范围（默认min/max），最多10001帧；AllKeys限于此范围内源控制器key，空集合拒绝 |
| allow_reference_edits | 默认false，写引用控制器或Store message连接须本次明确true；原工具声明面向引用rig，引用编辑依然是场景修改 |
| overwrite_store/overwrite_file/file_path | 自有Store更新和绝对JSON文件覆盖分别显式允许，不删除同名外部节点 |

标准store/load输出node、record_id、fields；records返回自有Store清单，match输出方向，switch输出实际开关值，key输出方向，bake输出实际帧列表；文件操作输出路径/Store计数。

## Store与文件格式变化

Store仍为原形态的transform及原命名风格/字符串字段，增加Owner标记、结构化JSON与六个控制器message。在本地/引用控制器中均可定义元数据，按消息解析当前路径，不靠陈旧字符串；作用域身份同时包含节点UUID与引用上下文。已有自有Store更新原节点及消息，须overwrite_store；外部同名节点不接管，Maya为新自有记录分配唯一名。引用/锁定、有外部子节点/使用者或字段锁定的Store拒绝接管。原源Store未打候选标签，不默认为自有，用户应按输入重新保存。

**原.ma/.mb Store传输改为自有候选JSON**，保留界面导入/导出功能，格式不与旧场景Store文件直接互读。不会执行导入场景内代码、把Store强制unparent，或删除任意同名节点。旧场景Store文件需用户在备份中加载并用原字段重新定义候选Store；候选不自动导入旧场景。JSON仅含既有控制器的显式路径及有限参数，不执行eval。导入前检查全批字段/控制器/重复槽位/自有Store覆盖策略；当前不自动跨namespace重映射。文件覆盖默认拒绝，非覆盖写入独占创建，明确覆盖才原子替换；目录创建/写文件无法由Maya Undo恢复。JSON导入的元数据场景写入按标准Undo分组。

## 保护、影响和原算法边界

validate/dry-run只读参数/唯一控制器、引用/锁/驱动/曲线共享、依赖/范围/Store和文件，不导入原UI、建helper、切帧、改选择、关Undo或写文件。match/bake依赖缺失返回失败，不冒充通过。所需FK旋转/IK腕TR/PV平移/开关通道须可写，锁定FK平移由原部分try/snap跳过；驱动仅直接动画曲线，动画层/约束/共享外部曲线保守拒绝。生产rig里的不同方向假设、jointOrient、rotateOrder、锁定约束组合与引用操作必须复验。

原匹配会临时切开关、清零控制器、复制offset控制器、创建locator/约束/临时IK链，并删除/重打当前帧或目标区间控制器key。AllKeys烘焙会切掉目标两端之间的key再按源key重建，影响不局限于旋转；原函数按keyable通道打键。不要对长动画未经备份直接调用。

原Pro界面匹配/切换/key/Store/Bake按钮经标准API回调；根函数仅在已验证活动调用内允许写入。临时节点私有UUID前缀，不删除已有snapGrp；删除仅限当前创建helper及全部自有后代，无外部使用者，约束先detach避免误删空target。finally清理临时图/恢复时间、选择、namespace和AutoKey，Undo始终开启，失败不自动撤销局部写入，先Undo检查。Maya共享IK solver基础节点不误删。Store/场景切换标准chunk；UI原Select all是明确用户选择操作。

明确源码修复：字符串/数字is比较改==；空query key列表None规范为空数组；`  rotateY`拼写空白和multiplyer变量拼写；IK→FK最后0-is-IK开关使用实际范围而非硬编码1；原缺Store查询未定义变量改自有记录查找；eval offset改安全literal_eval；取消Bake时AutoKey变量预先初始化，UI AllKeys过滤到实际播放范围。原+Y pole分支等制作rig行为保持原实现，不未经实测改数学。JSON传输/Store管理是明确替换，原.ma/.mb进出实现完整保留在upstream供追溯。

## 示例和组合

```python
fields = dict(fkshldr='rig:upper', fkellbow='rig:lower', fkwrist='rig:wrist',
              ikwrist='rig:ikWrist', ikpv='rig:pole', switchCtrl='rig:switch', switchAttr='ikfk')
tool.run(dry_run=True, action='match', direction='to_ik', allow_reference_edits=True, **fields)
saved = tool.run(action='store', allow_reference_edits=True, **fields)
tool.run(action='load', record_id=saved.data['record_id'])
tool.run(action='export_store', file_path=r'E:\temporary\rig_store.json')
```

输入为三FK+两IK控制器/开关/rig校准参数，输出为匹配pose/key或Store元数据。可在用户已经验证的rig上衔接Bake/清理/导出，但跨工具组合未实测。仅复用现有协议/Undo，不改正式库/core/注册。

## 已验证与待验收

静态解析、完整资源/13函数19UI方法覆盖、Schema/延迟导入、临时正式布局注册/面板；Maya2025隔离验证Store只读/Undo/Redo/改名保存重载、JSON覆盖/导入更新及坏数据拒绝、0..1/10真实switch/key/Undo/共享输出拒绝、消息失败finally/Undo、引用元数据明确编辑。完整原匹配测试在缺少PyMel时明确skip；不能以测试进程成功宣称原算法/GUI已验收。补PyMel后需实际生产rig逐项真人验收，当前prepared_unverified，完整晋级清单与验收步骤已预制在待整理池。
