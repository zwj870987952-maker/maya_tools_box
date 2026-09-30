# bh_localNudge 真人验收

当前prepared_unverified / GUI not_run。在实际Maya备份场景运行，关闭原工具窗口，不安装Shelf、不复制原脚本至scripts。

```python
import runpy
candidate = runpy.run_path(r'E:\GitHub\maya_tools_box\tools_staging_pool\01_animation\bh_local_nudge\release_candidate\launch_candidate.py')
tool = candidate['load_tool']()
tool.show_ui()
```

1. 窗口开/关/重开，两个滑条、打印和12个按钮无异常；默认位移.01、旋转1，检查原范围/布局和Script Editor。
2. 无驱动transform、joint与多个控制器，dry_run比较属性、节点、选择/时间、Undo队列，应无写入。
3. Up/Down为±Y，Right负X、Left正X，Forward/Back为±Z；旋转±X/Y/Z正确。父级旋转/缩放副本中修改local属性，勿按世界向量推断。
4. 普通、CTRL、ALT、CTRL+ALT分别使用全值、半值、四分之一、八分之一；验证实际键位，不把API显式ctrl/alt测试当原生按键通过。
5. 一次Maya Undo撤回所有对象的微调；组件选择在显式objects调用后恢复。失败可能已部分写入，需观察后Undo，不自动回滚。
6. 已有关键帧，分别autoKey关闭/开启，在键帧和非键帧微调、切换时间，检查值/曲线/是否打键。原算法不显式打键；只有当前值变化不代表动画已保存。测试线性/角度非默认单位，原Degrees文字不是单位换算。
7. 引用、节点/通道锁定、外部约束/表达式/层/混合驱动、歧义/重复/缺失对象应拒绝；不在生产rig绕过保护。
8. 记录实际Maya版本、日期、验收人和逐项结果，确认真实GUI与动画操作满意；发现问题修候选再验收。

实际通过后建立记录，占位字段不能用作实测证据：

```json
{"tool_id":"bh_local_nudge","passed":true,"maya_version":"实际版本","date":"实际日期","accepted_by":"验收人","candidate_sha256":"当前只读晋级预览哈希"}
```

先运行plans/staging_run/promote_candidate.py --candidate <候选绝对路径>预览；真实记录匹配后才能 --acceptance <记录> --apply，复制完整代码/资源/说明/测试并合并注册。真实验收前不迁入正式库。
