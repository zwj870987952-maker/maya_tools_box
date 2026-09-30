# CgShake 真人验收

prepared_unverified，Qt/渐变/层GUI not_run。使用真实Maya备份场景和临时缓存目录；不安装原脚本。

```python
import runpy
candidate = runpy.run_path(r'E:\GitHub\maya_tools_box\tools_staging_pool\01_animation\cg_shake_py3\release_candidate\launch_candidate.py')
tool = candidate['load_tool']()
tool.show_ui()
```

1. 开/关/重开完整原Qt窗口/样式/图片，嵌入渐变编辑正常，Frame最低1，六amount/Overwrite/Use cache和预设菜单正常。开窗不加载插件或建文件目录。
2. 默认渐变/编辑控制点/插值/预设Points，实际权重使用原Maya valueAtPoint，检查分数playback起止和整数step的截断/归一化。API传weights与同一UI采样做对照，不当作自定义插值通过。
3. 单/多选择只操作第一transform；原正向uniform噪声、本地值/单位、零amount不打键但六TR setAttr语义正确。一次Undo恢复，dry_run比较节点/键/选择/时间/Undo无变化。
4. 在BaseAnimation及新副本层测试Overwrite与Restore，确认真实清键范围和层作用域；未限定时间/层，不依据旧active layer文字推断安全。复杂动画层、非默认单位和实际摄像机独立验收。
5. 手动加载animImportExport，再Cache/Restore/Use cache；观察默认UUID.anim/sidecar、已有文件确认、单对象导出。导入/恢复后四播放范围/时间/选择正确，文件不能靠Maya Undo删除。
6. 改目标名、UUID对应恢复；修改cache文件/sidecar或改路径应在清键前拒绝，不接管旧cache属性。没有缓存时取消Use cache或新Cache再执行。外部写失败检查文件残留/缓存属性，不猜测回滚。
7. 保存/加载/Default/重开预设、已有文件覆盖No/Yes、非法名/损坏JSON拒绝。只点击Help才开原网址，未预验证网页。
8. 节点/通道/额外动画属性锁、外部驱动/引用/歧义应拒绝；故障确认chunk关闭、状态恢复和Undo，真实使用满意后记录。

记录实际Maya版本/日期/验收人/逐项结果；问题修候选后重验。通过后建立真实记录：

```json
{"tool_id":"cg_shake_py3","passed":true,"maya_version":"实际版本","date":"实际日期","accepted_by":"验收人","candidate_sha256":"当前只读晋级预览哈希"}
```

plans/staging_run/promote_candidate.py --candidate <候选绝对路径> 预览当前哈希/目标；真实匹配记录才 --acceptance <记录> --apply。真人验收之前留待整理库。
