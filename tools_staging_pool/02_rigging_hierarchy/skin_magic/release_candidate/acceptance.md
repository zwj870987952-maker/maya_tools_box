# SkinMagic 4.0 真实 Maya 验收

先打开备份场景；PyMel 必须与目标 Maya/Python 版本兼容。当前只在隔离 Maya 2025 下验证原生批量权重及 XML/JSON，完整 GUI 和 PyMel 引擎未运行。原包无独立许可；本包仅本地整理，晋级不代表可以发布。

1. 通过 `launch_candidate.py` 的 `show_ui()` 呼出，依次切中文/英文/日文，检查4套原布局、全部按钮/滑条/列表及图标；关闭/重开后 scriptJobs 不重复，原选择优先级恢复，Script Editor 无 Fatal/Traceback。缺 PyMel 应返回明确错误，不能以此算验收通过。
2. 小网格绑定两个骨骼，选顶点启用 Weight，逐项验证七个固定权重、自定义值、增减、复制/粘贴、平滑、prune、normalize、影响数检查、范围增减、连通/ring/wave选择、添加/移除骨骼、选加权骨骼/顶点。Undo 一次恢复操作前权重。原 GUI 导出两位精度保留，批量完整精度另测。
3. 对称绑定网格，测试X/Y/Z方向、正反方向、整网格/部分顶点镜像、多个目标 transfer、A/B swap/merge、fine/fast closest vertex copy；检查未选顶点保持、源权重/源图未污染，单步Undo，Bind Pose后的连接骨架影响符合预期。
4. 颜色代理：打开/关闭/切选择、重开UI、失败清理，恢复原显示设置；场景里预置无关 `_colorProxy`、`annotation*`、`weightMeshMetal` 等，确认冲突被拒绝或新建着色器，不删除/修改无关对象。Weight map 的网格排列、标签与颜色逐骨骼一致，失败检查自有临时节点。
5. 外部临时目录导出/导入安全 `.VertexWeight`、`.BoneList` 和XML；取消对话框不报异常；同名输出拒绝覆盖；旧pickle与恶意文件明确拒绝；目标换名按索引匹配，错误影响/顶点数拒绝；XML导入单Undo恢复旧权重，无holderBone残留，内部 XML 不写场景目录。
6. LoD：加载源/目标和删除→接收骨骼，增删/刷新映射，保存加载，分别原网格减少/新目标/批量。对删除源、删除骨骼及共享skin必须查看 dry-run 范围后在备份场景执行；确认无误才认可。自动全场景材质删除已禁用。
7. `tool.run(action='show_gore')` 补充窗口：加载源、添加/删除/清目标，测试绑定复制、默认保留源与显式删除源、目标清历史；比较实际权重并Undo。原包不含Spring算法/界面，应使用独立SpringMagic，不能把缺失功能算作通过。
8. Rename：替换大小写、前后缀/插入、数字/字母模板、选择与层级范围；全场景模式确认节点数，对重复名字、namespace、根节点和层级改名验收。Misc逐项：关节缩放、用户属性清理、只选unknown删除、网格清理、Bind Skin+、非skin历史。备份验证删除影响。
9. Deformer→BS 时间段、已有skin源/目标、BS源/目标Wrap转移、保留目标或复制源skin；检查源 BS 各权重恢复、无关同名 alias 目标被保护、Wrap临时Base仅删除本次新建者，Undo恢复完整历史。测试多模型/constraint/animation layer/version支持；不支持情况明确记录。
10. `validate`/`run(dry_run=True)` 不改选择、时间、Undo队列、节点、权重或文件；错误时不要继续叠加操作，检查Script Editor和Undo本次。shelf仅在点击时创建并能重启后呼出候选；用户偏好和外部文件不属于MayaUndo。

每项记录 Maya/Python/PyMel、场景样例、实际结果与遗漏。全部满意后才运行预制晋级脚本/清单；真实验收暴露的缺陷先在本候选修复，不提前迁入正式库。不运行 Obsidian 同步。
