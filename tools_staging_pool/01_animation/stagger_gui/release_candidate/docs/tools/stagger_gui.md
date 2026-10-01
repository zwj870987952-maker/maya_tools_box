# Stagger 1.1.0 候选

tool_id: stagger_gui；animation；真实 Maya GUI not_run。作者 Animation Creation，2022 animationcreation.com；原包12文件（两个Python、八SVG、Demo GIF、三页安装PDF）全部原字节归档。未提供独立许可，不宣称可分发。PDF只读提取核对：正确原入口是 import stagger.ui; stagger.ui.win()，原代码头部 stagger.ui() 示例与空 __init__.py 不匹配，正式候选已提供独立框架入口。没有安装Shelf或改用户脚本目录。

此工具对已有动画曲线制造逐帧 stagger，**并非多个物体依次延迟动画**。保留原算法：在 start/end 插入键以保持边界，查询区间值并和曲线首键值比较；变化曲线每隔2帧交替取 f+amount 与 f+2 的评估值，写到 start+1 起的连续整数帧；奇数区间追加 end-0.5 样本；end-1 插入 ease 边界。原区间其他键不会被删除，常量曲线仍插入起止键。保留首次键值而非区间首值的原判定语义。范围外原键值保留，边界插值/加权切线在生产曲线另需实测。

参数 objects（省略用当前所选整节点；允许 transform/joint 或明确 animCurve）、必需整数 start/end（至少四个含端点帧，差值>=3）、amount 原Slider范围2.2..4默认3.1。负帧支持。输出 ToolResult.data.results 每曲线 samples/written_times，gui_acceptance=not_run。复用正式 BaseMayaTool/UndoChunkContext，不改变core；独立API不读取UI字段。

validate/dry_run 不插键、不变选择/键选择/时间、不加载原UI、不写文件；只处理明确对象的时间曲线，避免原 keyframe 无对象参数可能受全局键选择影响。拒绝引用/锁定对象或通道、驱动键/时间warp、共享至范围外的曲线、animBlend/pairBlend/unitConversion 连接；这些复杂图可先在备份场景烘焙为独立曲线后验收。直接显式曲线意味着允许处理它的目标，但所有目标仍需可写，复杂连接仍拒绝。

执行前整批预检，所有键写入在一个 Undo组；异常报告已完成曲线，需Undo恢复部分写入，不自动声称回滚。算法只改键，不需要改时间/对象选择或文件。图标/原UI字段/高度随slider变化/start-end读取时间滑块/进度布局完整保留，控件命名私有以避免 sf/ef/fl/form/pb 冲突；计算回调统一run，finally隐藏进度并恢复窗口高度。Maya批处理明确不打开UI。原GIF/PDF只作说明资源，不冒充本次实测。

```python
tool.run(dry_run=True, objects=['ctrlA'], start=1, end=48, amount=3.1)
tool.run(objects=['ctrlA'], start=1, end=48, amount=3.1)
```

可潜在衔接 bake→stagger→曲线调整；和stagger_offset用途不同（后者依选择次序移时间），组合未实测。完整代码/资源/docs/tests与注册面板迁移已在promotion.json，真实验收前仅预览，不迁正式库。
