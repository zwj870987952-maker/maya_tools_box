# Bezier最小二乘关键帧精简候选

ID `keyframe_reduction`，animation，来源 Robert Joosten 0.0.1，MIT Copyright 2019。完整LICENSE与原Paper.js拟合来源说明保留。整仓60资源（源码、安装器、图标、原文档/图片）按字节归档，原Python2文件以.py.original存档，不误作为Python3运行源。全部原12类/68方法转换并保留在native/，包括MVector2D、Keyframe、完整FitBezier递归拟合与原Qt窗口；差异见keyframe_reduction_changes.diff。候选不执行安装器，不写shelf/userSetup。

## 原算法与边界

对全曲线在floor(first)..ceil(last)+1的半开范围按step采样，用(time,value)二维点、相邻向量角度分拆。原Bezier用chord-length参数化、least-squares控制柄（weighted）、Wu/Barsky fallback、Newton-Raphson重参数化和最大几何误差递归拆分；保留所有分支/公式。weighted=False只一次迭代，True最多四次。三种切线拆分Auto/Existing/angle threshold可同时启用。若拟合键数不小于原键数，不改该曲线并返回rate=0。

成功时保留第一键并移至floor(first)，删除其余旧键、按拟合点创建键和in/out角度/weight/weighted状态。原曲线端点为子帧时可能被移动到整数附近；最后采样可能落在原末键之后、ceil(last)+1之前，影响Infinity/区间边界。没有“保留范围外”选项，因为处理全曲线。error是采样的二维几何拟合容差，不是最终Maya切线插值的严格最大通道数值误差，也不保证子帧误差、Euler圈数、step跳变或视觉动作质量。生产曲线必须比较。

## 参数和输出

`KeyframeReductionTool.run(dry_run=False, **arguments) -> ToolResult`。

| 参数 | 默认/含义 |
| --- | --- |
| action | inspect/reduce/open_ui，默认reduce |
| curves | 明确唯一animCurve名数组；空读取选择曲线或所选对象直接输入曲线 |
| error | .1，有限正数≤1000，沿用原拟合容差 |
| step | 1，.1..100，采样步长 |
| weightedTangents | True，原加权拟合/关键帧切线 |
| tangentSplitAuto | False，原角度统计估计分拆 |
| tangentSplitExisting | False，原已有in/out角差分拆提示 |
| tangentSplitAngleThreshold | False，原角度阈值分拆 |
| tangentSplitAngleThresholdValue | 15，.01..180 |

inspect返回曲线/键数/时间列表；reduce返回results[{curve,before,after,rate}]。rate为原拟合键数算法统计，不是误差报告。原UI可按目标plug过滤，保留最大error/step、weighted、三拆分参数、选择全部曲线、Reduce/进度和选择回调。按钮统一标准API/Undo，空选择提示不再计算rate/0；PySide6/shiboken6与PySide2/shiboken2延迟至真实GUI，包内KR_icon路径不依赖XBMLANGPATH。

## 准入与安全

仅本地可写、单一输出至本地transform/joint的TL/TA/TU时间曲线，至少两键；输入为空或普通time节点。不接受driven key、时间重映射、动画层/间接图、未连接曲线、多输出共享、引用/对象或曲线锁/输出通道锁、step/stepnext切线。输入selection含不支持曲线时API全项预检失败，不先写可行项再默默跳过；UI过滤只显示可支持项。每条预计样本2..20000、总样本≤100000、曲线最多1000。复杂噪声的递归拟合仍可能耗时或失败，限额不是速度保证。

validate/dry_run只读身份/连接/键/值和样本量，不导入Qt/原算法，不改时间/选择/AutoKey/键/文件或开窗口。inspect同样只读。reduce由BaseMayaTool整个调用的Undo chunk包裹，暂关AutoKey并finally恢复；私有_removeKeys/_addKeys只能对标准运行中已验证curve UUID写入，类reduce直接调用也先桥到标准API。切键clear=True不覆盖Maya key clipboard。失败不自动回滚已删除/新增键，先Undo恢复，返回实际错误。

没有外部文件业务写入，原档案仅包内资源。UI/Qt实例/选择回调不归场景Undo；重开前关闭原窗口，close移除回调。headless mayapy不创建Qt实例。

## 修复与复用

Python2 print/unicode/long/iteritems/dict view/list、zip语义转换为Python3；完整原算法保留。Auto拆分空/常量/同角度序列原log或分母异常，增加零/等角保护返回无拆分；只变确定错误路径。删除原0.01帧后的旧键改按索引1..last，避免极近第一键的旧键残留；按原意仍保留并移动第一键。原UI空曲线平均率除零改明确提示，Qt6字体weight改setBold，图标打包路径、UI标准Undo桥及回调清理补齐。

现有正式core/工具没有同类完整Bezier least-squares拟合；只复用BaseMayaTool/ToolResult/Undo，不为统一提前下沉新算法。可接备份中已验证的烘焙输出，采样/视觉满意后再导出；与其他工具组合尚未真人验收，不把数学拟合当作Maya生产误差保障。

```python
tool.run(dry_run=True, curves=['control_translateX'], error=.1, step=1)
result = tool.run(curves=['control_translateX'], error=.1, step=1, weightedTangents=True)
```

## 验证与晋级

普通Python核对60原资源SHA、12类68方法完整性、Python3静态解析、延迟Maya导入、Schema/非法参数和临时正式布局注册/面板。Maya2025隔离mayapy三组：直线/常量20→2键并半帧曲线值保持（原1..20范围内）、Auto常量无异常/Undo、只读dry/inspect、原类标准桥、共享/step/private写保护、weighted+existing/angle拆分波形流程与无法减键的无写分支、第二拟合键注入错误后AutoKey/Undo恢复。波形测试不宣称误差品质通过；未打开真实Qt、未跨版本/制作曲线测试，prepared_unverified。acceptance.md真人确认后才按promotion.json完整代码/文档/素材/测试/注册/面板晋级。
