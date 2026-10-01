# Stagger Maya 验收

1. 备份动画场景，runpy.run_path(<本包绝对路径/launch_candidate.py>)['load_tool']().show_ui()。检查八SVG、Start/End按钮、Slider 2.2..4与图形高度、Stagger按钮、进度与反复关闭打开，无sf/ef/form与其他UI冲突。timeline框选右端应减1，无框选按当前帧按钮写对应字段。
2. 对非线性曲线分别用偶数/奇数/最小四帧/负帧范围，amount2.2/3.1/4，原包独立备份对照；确认真实stagger采样、end-0.5奇数分支、end-1 ease，不误当多物体时间延迟。常量曲线只插边界、原密集内部其他键保留。
3. dry_run节点/键/时间/对象选择/键选择/Undo栈应不变。预先在无关对象选键，显式objects操作只改变指定曲线。一次Undo/Redo整组恢复；范围外键和值以及加权切线、旋转Euler生产动画另行比较。
4. 引用/锁定通道、共享曲线外部目标、animBlend/层、时间warp应明确拒绝，不能部分先改好曲线。注入异常后进度隐藏、高度恢复，部分动画需Undo。零动画和end<=start/不足范围提示。
5. 隔离mayapy参考算法仅固定原UI读取，真实动画命令全部Maya执行；不等于原UI或SVG实测。记录目标Maya版本/结果后才按promotion清单晋级；原安装PDF/GIF仅来源资料。
