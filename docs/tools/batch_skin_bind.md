# 批量绑骨头 / 生成代理

工具ID：batch_skin_bind。两份用户原型完整归档于upstream，文件SHA与完整三函数/三UI方法目录在catalog.json，无独立许可文件。用途是明确的一骨骼一模型绑定，或按源transform生成joint/locator/cube代理，并可将刚性模型的transform动画烘焙到新骨骼后转为蒙皮。

## 旧行为与修复

“批量绑骨头.py”连续两次读取同一pm.selected()，没有独立捕获骨骼与模型，不能可靠表达顺序配对。候选通过显式pairs及两次UI独立捕获解决，Maya cmds.skinCluster(toSelectedBones=True)每项仅指定一个影响骨骼，不再依赖PyMel或全局当前选择。

“生成代理.py”三种代理创建函数及原始UI全部保留在engine/native_ui，通过外围API调用。原名冲突后skinning分支重构基础joint名，会误找既存对象；候选使用actual source→created joint映射。joint烘焙后移除本次创建的parentConstraint，再在起始帧清除源动画并创建skinCluster，避免约束继续跟随已清动画的源。Bake区间包括两端，源模型固定于起始姿态，最终运动由独立烘焙骨骼驱动。

原代理不传递缩放，parentConstraint无offset，保留其平移/旋转跟随语义。选中source默认不再扩展所有子transform。skinning仅支持独立、未绑定的单polygon mesh，unit静态scale、零shear及无动画/驱动祖先；复杂绑定、缩放动画和层级双重变换不声称自动解决。原始注释明确模型间不能有父子关系，批量蒙皮预检因此拒绝这些输入。

## 参数与输入

| 参数 | 默认/条件 | 含义 |
| --- | --- | --- |
| action | proxies / bind；默认proxies | 新代理或绑定已有骨骼 |
| objects | proxies可选，1..1000唯一transform | 省略时当前完整选择，不扩展孩子；普通代理可读取锁/引用源 |
| proxy_type | joint / locator / cube；默认joint | 完整原三种代理 |
| skinning | false | 仅joint模式，烘焙并给源模型蒙皮 |
| allow_source_key_removal | false | skinning必须明确true：删除源transform全部动画键，包括区间外、自定义属性/visibility键 |
| start_frame / end_frame | skinning可选，默认playback min/max | 必须一起传；有限帧，含结束帧，长度≤10000 |
| pairs | bind必填，1..1000 | 每项joint为已有唯一joint，mesh为可写未绑定单polygon transform |

bind只接受action/pairs。不支持给既有skinCluster加影响、不复制权重、不覆盖既有蒙皮。一个骨骼可以绑定多个独立模型，一个模型不能重复。引用/锁骨骼或模型写目标、锁形状、实例、多个有效shape、共享/锁/时间扭曲源曲线、驱动/层源通道、带动画祖先或非unit缩放的skinning源拒绝。整个批次在执行前先检查；普通代理的锁/引用源只用于查询及作为约束驱动。

## API与结构化输出

候选launch_candidate.py的load_tool()/show_ui()可直接加载；真实验收转正后统一入口示例：

```python
maya_toolkit.execute_tool('batch_skin_bind', {
    'action': 'bind', 'pairs': [{'joint': 'joint1', 'mesh': 'body'}],
}, dry_run=True)
maya_toolkit.execute_tool('batch_skin_bind', {
    'objects': ['body'], 'proxy_type': 'joint', 'skinning': True,
    'allow_source_key_removal': True, 'start_frame': 1, 'end_frame': 24,
}, dry_run=True)
```

BaseMayaTool.run返回ToolResult；validate/dry_run只读整批输入、节点/网格/skin历史、动画曲线、父层和删除影响，无节点/键/选择/时间/Undo/文件修改。Schema通过OpenAI/MCP导出。execute返回规范plan：bind含bindings的joint/mesh/skin_cluster；proxies含mappings的source/proxy/proxy_uuid、created的joints/locators/cubes/constraints/sets/skin_clusters和proxy_constraints_retained。skinning预览还有每源curve/key_count及全部键删除范围。

原ISS_joint/GOS_joint和ISS_cube/GOS_cube选择集命名保留，定位器原型也用cube后缀。冲突由Maya创建新后缀名，不合并或改写既有选择集；结果返回实际名。没有临时待整理池路径依赖，没有素材缺项。复用core.get_mesh_shape/get_skin_cluster与框架Undo/结果协议，不修改正式core。

## 影响与撤销

bind新增skinCluster/bind pose和连接。普通代理新增代理/无offset约束及源/代理选择集；不会删除原动画。skinning新增joint/bake keys/skinCluster/sets，删除本次代理约束和源全部动画键；不清理其他场景约束、节点或选择集。source→proxy映射使用实际对象，禁止按猜测名称删除。

一次框架UndoChunk覆盖整个批次，恢复调用者选择/时间/autokey/namespace。框架异常不自动回滚，执行中若部分操作失败，应检查并Undo一次撤回；没有虚构“原子成功”。外部文件、用户偏好、插件、Shelf与安装均不写入。

GUI保留原Joint/Locator/Cube和Create，Skinning文字明确包含bake/remove source animation，再增加绑定已有骨骼入口：独立捕获有序骨骼与模型、检查相等非空数量后Bind pairs。无选择、类型不符、既有蒙皮或父子输入提示而不强制修改。

## 关联与验证

可为后续Weights Copy准备新skinCluster，但本工具的一骨骼刚性权重不替代正式weights_copy的重叠顶点权重复制。新joint动画可供W Retarget或速度测量分析；这些跨工具顺序建议仍待生产场景组合验证。

普通Python检查两份完整源SHA、三函数/三UI方法、Schema和显式源动画删除约束。隔离Maya2025检查：真实两对绑定各仅一影响且顶点weight=1，Undo/Redo；三代理名称冲突/姿态/原集合保留/约束跟随/Undo；skinning含末帧烘焙、实际后缀骨骼、删除本次约束和原键、帧末网格顶点world运动等于原动画、Undo恢复完整场景/键；整批已有skin/层级/动画scale拒绝。独立GUI、生产动画/模拟/不同Maya版本仍not_run，prepared_unverified，人工步骤见acceptance.md。未验收不迁正式库。
