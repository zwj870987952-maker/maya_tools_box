# animFilters 动画曲线过滤器

- tool_id：`anim_filters`；category：`animation`；version：`1.1.0`。
- 状态：完整待整理候选，真实 Maya GUI 未验收；科学滤波因本机 mayapy 缺 SciPy 未验证，不能视为整项检查通过。
- 来源：Michal Mach 的 animFilters 1.0（2018）；上游源码声明 GNU GPL v2 或后续版本。完整上游源码、UI、图标、readme 和 GPL v2 正文随包保留；本候选的派生算法与 UI 适配沿用该声明。

## 用途和前提

保留 Adaptive 关键帧精简、Butterworth 低通、Median 中值三种过滤，Graph Editor 选键输入、实时 Preview、滑条刷新、Cancel、Apply、关闭时恢复和 Auto Buffer Curves。适用于非引用、可编辑、有单一目标连接的 animCurveTA/TL/TU。不是 Euler Filter，也不操作任意单位输入的驱动关键帧曲线。

代码面向 Python 3（候选加载入口使用 pathlib/importlib）；旧 Maya Python 2 环境尚未适配或验证。Adaptive 仅依赖 Maya/framework 和标准库；Butterworth/Median 需要与目标 mayapy Python/NumPy ABI 匹配的 SciPy。UI 在运行时选择 PySide6 或 PySide2，必须在真实 Maya GUI 中复验。没有将一个 Python 解释器的科学计算包强行塞进另一个 Maya 解释器，也没有自动安装依赖。

## 参数

继承 `BaseMayaTool.run(dry_run=False, **kwargs)`；转正后统一入口为 `maya_toolkit.execute_tool("anim_filters", arguments, dry_run)`。当前候选直接加载类，见 acceptance.md。

| 参数 | 类型 | 默认/条件 | 含义 |
| --- | --- | --- | --- |
| mode | string | adaptive | adaptive、butterworth、median |
| anim_curves | array[string] | 省略时所选 Graph Editor 键所属曲线 | 显式非空，去重，需唯一名称 |
| time_range | array[integer] | 省略时所选键全局起止帧取 int | 含端点，start < end；显式曲线必须显式提供范围 |
| tolerance | number | 0.25 | Adaptive 累计线性偏差阈值；UI 为 Threshold × Multiplier |
| window_size | integer | 35，范围 1..10001 | Median 偶数窗口按原算法加 1；过大窗口仍保留上游零填充并警告 |
| sample_frequency | number | 30 | Butterworth 采样频率，必须 > 0 |
| cutoff | number | 7 | 必须 > 0；Butterworth 时必须 < sample_frequency/2 |
| order | integer | 5，范围 1..32 | Butterworth 阶数；高阶数可能有数值限制 |
| max_samples | integer | 100000，范围 2..2000000 | 全部曲线整数采样和滤波样本的总量上限 |

## 预检和输出

validate/dry_run 检查参数、未知字段、曲线类型/唯一性、引用和锁定、单目标连接、Undo 是否开启、区间、样本上限、科学依赖与有限数值。预检读取并计算过滤结果，但不写曲线、不动选择、不操作关键帧剪贴板、不打开 UI、不改 Undo 开关、不写配置。

预检 data：mode、anim_curves、time_range、input_sample_count、output_sample_count。执行成功 data：mode、anim_curves、time_range、processed_samples；每条曲线为按时间排序的 `{time, value}` 列表，全部是可 JSON 序列化的普通数值。写入失败返回 errors，`partial_changes_possible=True`，应撤销并检查场景。

警告说明 Median 零填充、短段 Gustafsson 边界处理。缺 SciPy、Nyquist 违规、空选择、引用/锁、采样过多等明确失败，不将失败包装成成功。

## 影响与恢复

过滤读取每一整数帧的曲线求值，删除 `(start+0.001, end-0.001)` 内的旧键，用自动切线写入过滤样本；区间外的键不删除。端点可能被过滤结果覆盖，不承诺数值保持原样。Median 按上游仅处理 start..end-1，最后一帧原键保留。Weighted/手工切线在处理区间内不保留，这是原过滤写入的效果，不是精确原样修复工具。

由基类 run 提供单次 Undo，写入改为 Maya 命令而非未接入撤销缓存的直接 API。发生异常时不会自动回滚部分修改。

实时预览每次使用唯一 Undo Chunk；刷新先撤销自己的上次预览，再从原曲线重新计算。Cancel/关闭也仅在该预览仍位于 Undo 栈顶时撤销它；检测到其他场景编辑时拒绝自动撤销，避免误撤销无关操作。可先手动撤销插入的操作再 Cancel，或 Apply 保留当前结果；关闭在无法安全 Cancel 时会被拒绝并报告。Apply 接受当前预览，不再重复写入，用户仍能用 Undo 撤销这次过滤。Undo 全程保持开启。

Auto Buffer Curves 的绘图需用户在 Graph Editor 中启用显示 buffer curves。UI 的 buffer 选项写入原 QSettings 命名空间（MayaAnimFilters/animFilters），不受 Maya Undo 管理；业务 API 不写外部文件或设置。Ctrl+Z、外部编辑、删除曲线和关闭窗口的复杂交互仍须 GUI 验收。

## 算法保留和明确修复

- Adaptive 保留累计误差 criterion；改成显式堆栈避免 Python 递归深度限制，并修复零阈值/完全线性段递归到单点的缺陷。
- Butterworth 保留上游每 30 帧参考的时间采样及线性插值，不根据场景帧率默默换算；因此 sample_frequency 不是自动从场景获得的物理 Hz。
- 修复 NumPy linspace 的 float 样本数，按原式取整数；当长度恰好等于 padlen 时使用 gust，不再进入会失败的 padding 分支。
- 拒绝 cutoff >= Nyquist，代替上游把它夹到恰好 Nyquist 后仍调用无效归一化截止频率。
- 不用 live preview 关闭全局 Undo；移除依赖关键帧剪贴板恢复的方式，避免覆盖用户 clipboard。
- 用原 `.ui` 保留控件和默认值，替换旧 long()/distutils.strtobool 等启动兼容点，支持 PySide6/2 的 UI 适配路径，但尚未验证所有 Maya 版本。

上述数值边界参考 [SciPy butter](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.butter.html) 和 [SciPy filtfilt](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.filtfilt.html)；这里不据文档推定本机科学滤波已经通过。

## 示例与组合

转正后示例：

```python
import maya_toolkit
args = {"mode": "adaptive", "anim_curves": ["cube_translateX"], "time_range": [1, 60], "tolerance": 0.25}
preview = maya_toolkit.execute_tool("anim_filters", args, dry_run=True)
if preview.success:
    result = maya_toolkit.execute_tool("anim_filters", args)
    print(result.to_dict())
```

输出 anim_curves 与 time_range 可供后续动画工具定位处理范围。尚无经用户实测的工具组合；不能将与框架的静态依赖当成已验证组合关系。

## 离线证据和待测项

2026-09-30：隔离 Python 测试 10 项通过，1 项科学滤波数值测试因 SciPy 缺失跳过；Maya2025 mayapy 的 5 项场景/预览/端点对照测试通过，1 项依赖检查失败（无 SciPy），1 项 Qt widget 测试跳过。一次单独在 standalone 中创建 Qt widgets 的尝试以 3221226505 退出，证据保存，不视为 GUI 可用性结论，也未冒充通过。

科学模式须在配置兼容 SciPy 的目标 Maya 复测；原算法端点覆盖行为已经在隔离 translateX/rotateX 曲线上对照，而不是凭注释猜测。完整 GUI、切线复杂场景、不同帧率/角度单位、不同 Maya/Python/Qt 版本都待验收。状态与原始输出见本轮 manifest 及报告。
