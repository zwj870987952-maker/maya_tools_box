# 真人验收：动画层逐关键帧命令执行器

仅使用备份/新建场景与已知无害命令，Advanced Skeleton 使用测试角色。隔离 mayapy 通过不代表窗口或 FK/IK 预设通过。

1. 从 Script Editor Python 启动候选，观察窗口、层刷新、语言/范围切换、预设和日志；无异常或闪退。

```python
from pathlib import Path
candidate = Path(r'E:\GitHub\maya_tools_box\tools_staging_pool\01_animation\anim_layer_key_runner\release_candidate')
namespace = {'__name__': 'candidate_launch', '__file__': str(candidate / 'launch_candidate.py')}
exec(compile((candidate / 'launch_candidate.py').read_text(encoding='utf-8'), str(candidate / 'launch_candidate.py'), 'exec'), namespace)
tool = namespace['load_tool']()
window = tool.show_ui()
```

2. 两个对象制作 BaseAnimation 与额外动画层，使用不同整数/子帧键点。比较 auto/BaseAnimation/具体层/All 的预检列表；显示当前层，不借其他层曲线兜底。播放范围开关改变列帧，>0.001 的时间去重符合需要。
3. Python 输入 `cmds.setKeyframe(objects, attribute='translateX', time=f)`，先预检：时间、选择、键与 Undo 队列不变；再执行，每帧调度、最后原时间/原选择恢复、一次 Undo。输入 `raise RuntimeError('fixture')` 预检应成功而不会真的 raise；语法错误应预检失败。
4. MEL 输入测试对象属性 setAttr 命令，验证每帧执行、报告与撤销；不存在的过程在 dry_run 仅列帧，实际执行清楚失败并报告逐帧错误。命令写入哪层由命令和 Maya 当前状态决定，不能只依据调度 layer 认为写入隔离。
5. 使用 API 故意让第二帧失败，分别测试默认继续与 continue_on_error=false；报告已完成帧和失败帧准确、失败不自动回滚。修改后可 Undo。空动画成功/零执行；无选择、空命令、无效层、未知参数、超过 max_frames、Undo 关闭清楚失败。
6. 临时场景分别测试重命名和删除目标：重命名后后续调度继续、选择可恢复；删除后后续帧失败，其他仍存活原选择恢复。单步 Undo 后对象存在。不要将此测试用于真实角色。
7. 在测试 Advanced Skeleton 角色上确认 asAutoSwitchFKIK 的过程确实存在，再测试少量帧，观察 FK/IK 匹配、约束、层写入和 Undo；记录版本/角色条件。未装此依赖时记录缺失，不把预检通过当成匹配通过。
8. 正式安装后的 launch_ui.mel source 仅定义启动过程；显式调用 mayaToolkitAnimLayerKeyRunnerUI 才打开 UI。候选阶段使用 Python 启动；原 archived MEL source 会自动执行，不作为此项验收入口。
9. 文件导出/写入类自定义命令若确需验收，使用临时目录并先检查覆盖；Maya Undo 不保证撤回外部影响。记录实际 Maya/Python、验收人/日期、通过与失败及复现步骤。

验收通过后运行只读晋级预览：

```powershell
python plans/staging_run/promote_candidate.py --candidate tools_staging_pool/01_animation/anim_layer_key_runner/release_candidate
```

使用输出 candidate_sha256 填验收 JSON（passed=true、tool_id=anim_layer_key_runner、candidate_sha256、maya_version、date、accepted_by），然后才使用 --apply --acceptance <文件>。晋级完整包/三份源存档/MEL 启动桥/文档/tests 并合并当前注册表供面板发现。候选更改后旧验收指纹失效。
