# 真人 Maya 验收：动画层书签修剪与曲线优化器

在备份或新建测试场景里执行，不使用生产动画。Maya 2025 mayapy 检查不代表本表已通过。

1. 在 Script Editor 的 Python 中执行 candidate 启动器，确认窗口打开无 Fatal Traceback，书签列表/动画层刷新正常。启动器使用独立包名，重新执行会重新加载候选。

```python
from pathlib import Path
candidate = Path(r'E:\GitHub\maya_tools_box\tools_staging_pool\01_animation\anim_layer_bookmark_trimmer\release_candidate')
namespace = {'__name__': 'candidate_launch', '__file__': str(candidate / 'launch_candidate.py')}
exec(compile((candidate / 'launch_candidate.py').read_text(encoding='utf-8-sig'), str(candidate / 'launch_candidate.py'), 'exec'), namespace)
tool = namespace['load_tool']()
window = tool.show_ui()
```

2. 给两个测试控制器创建基础层、额外动画层、位移/旋转/缩放/customFloat/visibility 键。创建 1~5 和 8~12 的两个书签，并保留书签外与中间空隙的键。核查自动层、指定层、两个对象、仅一层，以及 Channel Box 高亮优先；未选的层和离散通道不得改变。
3. 分别按修剪预检与优化预检，比较对象选择、关键帧值/时间、Undo 队列；确认均不改场景。API 在插件未加载时应失败而不加载；只有明确启动 UI 或手动 loadPlugin 才准备插件。
4. 测试 all/playback/selected：all 修剪整条曲线；局部范围选择相交的完整书签，修剪覆盖首尾范围及中间空隙。鼠标框选优先；光标不在任何书签时原逻辑使用最近书签。确认报告与实际目标一致。
5. 缺少端点时测试修剪补键勾选/不勾选；不补键可能删除完范围内全部键。优化应插入端点并保持该层曲线求值。分别尝试六种模式、strength/bias 的 0/0.5/1、ease_bounds 开关；逐次 Undo 回原场景后再测试下一模式。
6. 检查端点值、外部关键帧值、单次 Undo。专门观察范围外插值和 weightedTangents 影响，并确认动画效果可接受；端点保持本层曲线值，不保证混合后的世界姿态。重复执行可能继续改变动画。
7. 锁定或引用目标、锁曲线/动画层、空选择、无曲线、无书签、重叠/退化优化书签、未知参数均应清楚失败。测试出现异常时检查是否有部分修改，使用 Undo；不得把失败当作通过。
8. 关闭/重开窗口，检查控件、滑杆、日志、书签/层刷新和 Script Editor。记录实际 Maya/Python 版本、验收人、日期、通过/失败、复现步骤。

验收后先运行只读晋级预览：

```powershell
python plans/staging_run/promote_candidate.py --candidate tools_staging_pool/01_animation/anim_layer_bookmark_trimmer/release_candidate
```

用该预览输出的 `candidate_sha256` 填写验收 JSON：passed=true、tool_id=anim_layer_bookmark_trimmer、candidate_sha256、maya_version、date、accepted_by。仅验收通过后带 `--apply --acceptance <验收文件>` 晋级。此步骤复制完整运行包/原始存档/文档/测试并合并当前注册表，面板由注册表发现；任何修改都会令旧指纹验收失效。
