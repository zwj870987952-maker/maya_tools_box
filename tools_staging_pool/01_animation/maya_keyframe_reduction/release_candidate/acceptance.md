# 真人Maya验收：Keyframe Reduction

状态not_run；当前只有Python3/离线和隔离mayapy算法检查，不等于生产动画质量通过。仅备份曲线，完整MIT许可/作者说明保留。

1. launch_candidate.py load_tool().show_ui()打开原Qt窗口，Maya2025 PySide6及用户其他Maya版本按实际PySide环境核验。检查包内图标、选中对象/曲线时的plug过滤、选择全部、error/step/weighted与三拆分字段、Reduce和进度，没有Fatal/Error。
2. 明确选择本地TL/TA/TU已烘焙曲线，直线/常量/弯曲波形/旋转分别试参数。比较减键率和原键/子帧视觉/曲线值；error不是最终Maya间帧最大值误差保证，不能只看减键率。
3. 整条曲线处理，检查floor(first)/末端采样移动子帧边界、Infinity和范围外运动影响。step跳变/驱动键/时间重映射/多输出/引用/锁/动画层应拒绝，不自动接管图。
4. weighted=False/True、Auto常量、Existing切线角差、angle threshold分别比较。极近第一键的旧键应清除，零error拒绝，大采样量拒绝；高噪声递归性能要记录。
5. 一次Undo恢复完整旧曲线与切线，AutoKey/时间/选择保持；错误后先Undo，不自动局部回滚。打开/关闭/重开窗口后选择回调正常且无残留；文件/shelf/userSetup不写入。
6. 记录版本、曲线fixture、效果/采样误差/截图/报错与是否满意；只有用户确认才执行预制promotion.json晋级，正式库在验收前不改。
