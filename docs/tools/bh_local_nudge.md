# bh_localNudge 局部属性微调候选

原 v1.03 工具为所选控制器的局部 translate/rotate 单轴数值做加减，提供两个滑条和12个方向按钮。完整五过程、窗口、原 MEL/ReadMe/图标均保留；去除顶层开窗，独立名称和标准回调。当前 prepared_unverified，尚未真实 GUI 验收。

## API与参数

LocalNudgeTool 继承 BaseMayaTool，tool_id=bh_local_nudge，category=animation，version=1.03.1-adapter；validate/execute 通过 run(dry_run=...) 调用，返回 ToolResult，使用现有 framework/core Undo。Schema 可导出 OpenAI/MCP 描述，晋级后可用 maya_toolkit.execute_tool。

| 参数 | 含义 |
|---|---|
| action | nudge（默认）、inventory、open_ui |
| objects | 明确 transform/joint 名称数组，空数组使用选择；拒绝歧义/缺失/重复/组件/通配符 |
| channel / axis | translate或rotate；X/Y/Z，默认translate/Y |
| direction | positive或negative，默认positive；原UI Right是负X、Left是正X |
| amount | 有限正数，None按channel默认translate=.01/rotate=1；API不限制原UI滑条范围 |
| ctrl / alt | 显式布尔，默认false。CTRL半值、ALT四分之一，两者同时为八分之一；UI读取实际按键位 |

结果含 delta 和 changes，每项 node、plug、before、expected_after、实际 after、animated。inventory 返回原件校验和完整过程目录；open_ui 返回窗口及过程来源，需要真实 GUI。

## 算法、单位和动画边界

保留原 getAttr/setAttr 数值加减、原modifier算式，不改成世界空间或沿物体旋转轴移动。父级旋转/缩放会改变世界位置变化，但修改的只是 local translateX/Y/Z。旋转也是单个 Euler 属性数值加减，不是空间矩阵旋转。使用当前 Maya 线性/角度单位；原旋转打印文字写 Degrees，但没有度↔弧度转换。

没有显式 setKeyframe，候选不自动开关 autoKey、不改变层。Maya2025隔离 autoKey关闭时，已有animCurve通道的当前值会临时改变、关键帧时间/值保持，切换时间重新按曲线计算。GUI中autoKey、时间切换、原生交互和实际层结果必须检查；不能把一次微调当作已持久写入动画键。对已有动画返回 warnings。外部约束/表达式/动画层/混合驱动被预检拒绝，先准备副本。

## 预检与场景影响

validate/dry_run仅查询对象、通道、当前值和条件，不source、开窗、写值、改变选择/时间或Undo队列。拒绝引用、节点/通道锁定、非animCurve驱动、不有限输入和结果；Undo需启用。场景影响仅所选轴属性，框架分组Undo可一次撤回全部对象；执行finally恢复仍存在的对象/组件选择。业务不修改当前时间、范围、评估、刷新、缓存或外部文件，不安装Shelf。

执行异常可能已经写入部分对象，框架不会自动回滚，需Maya Undo撤回。内部MEL写场景过程只能由标准API上下文调用，避免绕过预检和Undo。名称和控件使用mtbLN_前缀，全部五过程来源核对，原业务滑条查询改参数globals，原滑条打印仍查询自己的UI。

```python
tool.run(objects=['hand_CTRL'], channel='translate', axis='X', direction='negative', amount=.1, dry_run=True)
tool.run(objects=['hand_CTRL'], channel='rotate', axis='Z', amount=1, ctrl=True, alt=True)
```

可在无驱动控制器副本上微调姿态，明确打键后再使用动画过滤/导出；接口衔接没有验证跨工具GUI组合。不要对已有绑定/层绕过驱动保护。

## 验证与晋级

普通Python四项检查及Maya2025隔离七项通过：五过程完整source/来源/内部保护、translate/rotate与四组合modifier、多个对象/变换父级/Undo、无副作用/组件选择、已有动画与autoKey关闭、锁定/驱动/缺失/重复拒绝、失败恢复/部分写入Undo。没有创建原窗口，实际滑条/按键/autoKey/非默认单位和其他版本平台待真人。

源码差异附bh_local_nudge_changes.diff；三原资源按字节保存。ReadMe表明购买工具，未发现独立再分发许可，仅本地保留，不公开发布。Git属性保护原件/candidate字节校验。promotion.json预制完整包、说明、两测试和LocalNudgeTool注册；临时正式布局验证，不修改当前正式库。真人流程见acceptance.md，当前哈希对应的实测记录后才允许晋级，无需继续开发业务。
