# bh_waveIt 真人验收

prepared_unverified；GUI not_run。使用真实 Maya 备份场景，关闭原工具，不复制至 scripts/Shelf。

```python
import runpy
candidate = runpy.run_path(r'E:\GitHub\maya_tools_box\tools_staging_pool\01_animation\bh_wave_it\release_candidate\launch_candidate.py')
tool = candidate['load_tool']()
tool.show_ui()
```

1. 窗口开/关/重开、compact/advanced、全部滑条/四预设/六轴/Channel Box/Interactive 无致命报错；原大小和默认值正确。
2. 创建有序 transform/joint 链，默认旋转 X，四 S/C、frequency/phase/amplitude、首对象 offset 与原 6.28/rad_to_deg 公式一致。显式数组交换顺序检查首对象和数值；不能凭名字排序假定选择顺序。
3. 开多个旋转/位移轴、选择数值自定义属性，实际 local 覆盖一致；检查线性/角度非默认单位与整数/bool/enum 强制转换。波浪数值也写位移/custom，不改单位换算。
4. Interactive 关闭时 Size/Frequency/Offset 拖动不写，打开时写；四预设始终写；Rotate Base Offset 独立滑条仅首对象启用旋转轴变为负offset。真实 Channel Box 选中属性正确传入，缺失/锁定属性拒绝。
5. dry_run 比较通道、选择、时间、节点、Undo 队列无变化；普通一次调用 Undo 撤回所有通道。Interactive 连续回调每次归组，实际拖动的 Undo 数量记录，不声称整段拖动原子撤销。
6. 已有动画曲线分别 autoKey 关闭/开启，键帧/非键帧/切时间检查实际值与持久键，原工具不显式打键。引用/锁/组件/歧义短名/外部驱动/缺失属性拒绝，不绕过生产 rig 保护。
7. 失败可能部分写入，检查 ToolResult/Script Editor、时间/组件选择/内部guard及 Undo；实际制作场景和其他版本独立验收。

记录实际 Maya 版本、日期、验收人和逐项结果，问题修候选后重验。通过才建立真实记录：

```json
{"tool_id":"bh_wave_it","passed":true,"maya_version":"实际版本","date":"实际日期","accepted_by":"验收人","candidate_sha256":"当前只读晋级预览哈希"}
```

用 plans/staging_run/promote_candidate.py --candidate <候选绝对路径> 先预览当前哈希和目标。真人记录匹配才能 --acceptance <记录> --apply 完整迁移/注册；验收前不迁正式库。
