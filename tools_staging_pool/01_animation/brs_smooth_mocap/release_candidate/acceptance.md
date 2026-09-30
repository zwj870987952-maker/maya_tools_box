# BRS Smooth Mocap 真人验收

prepared_unverified，GUI/制作动捕not_run。使用真实 Maya 临时骨骼和动捕副本；不执行原入口或 scripts 目录文件。

```python
import runpy
candidate = runpy.run_path(r'E:\GitHub\maya_tools_box\tools_staging_pool\01_animation\brs_smooth_mocap\release_candidate\launch_candidate.py')
tool = candidate['load_tool']()
tool.show_ui()
```

1. 开/关/重开参数窗口不写场景，Root Selected/strength/annotation/dense/timeline、Mocap确认Yes/No和所选键按钮正常；不会打开/关闭别的BRS工具或下载代码。
2. Graph Editor 至少三个键，默认smooth_keys一次三点平均，首末所选键不改。部分/不连续选键、全范围显式曲线、同曲线未选键、非均匀时间间隔验证；Undo和原键选择恢复正确。
3. root单joint/多joint层级，静态和一时间键后代被跳过；strength=1/2/3/较大值分别0/1/2等轮数，观察实际动画和完整回烘密度，不按次数推断输出仍稀疏。
4. Annotation/dense/timeline选项与round边界、范围外键、breakdown、切线和filterCurve效果，选含小数帧/大角度旋转的副本。检查成功后自己的临时locator/约束清理、joint存活、blend载体保留和一次Undo。
5. 制作骨架jointOrient、脚部接触、root motion、旋转跨180/360、线性/角度单位、动画层/复杂blend独立确认视觉质量；自动通过不代表动捕降噪满意。
6. dry_run比较节点/键/选择/时间/Undo/视口/键选择无变化；引用/锁/外部驱动/约束/time warp拒绝。失败可能已有helper/曲线变化，检查状态并Undo，不继续保存生产文件。
7. 与另一个BRS候选窗口/辅助对象共存，私有后端Owner/命名独立，不接管或删除其他对象。晋级不需要安装BRSLocTransfer.py到scripts。

记录实际版本、日期、验收人、逐项结果和制作资产质量；问题修候选后重验。通过后记录真实当前哈希：

```json
{"tool_id":"brs_smooth_mocap","passed":true,"maya_version":"实际版本","date":"实际日期","accepted_by":"验收人","candidate_sha256":"当前只读晋级预览哈希"}
```

plans/staging_run/promote_candidate.py --candidate <候选绝对路径> 先预览完整文件/当前哈希；真实记录匹配才 --acceptance <记录> --apply，验收之前不迁正式库。
