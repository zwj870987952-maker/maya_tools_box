# 真人验收：动画层关键帧区间书签生成器

使用新建/备份场景；清空会删除场景全部书签。Maya 2025 隔离测试不能替代本表。

1. 从 Maya Script Editor 的 Python 启动候选，确认窗口、层刷新、四色板、前缀与按钮响应；查看插件启动加载是否有异常，禁止将预检当作插件安装。

```python
from pathlib import Path
candidate = Path(r'E:\GitHub\maya_tools_box\tools_staging_pool\01_animation\anim_layer_keyframe_bookmark\release_candidate')
namespace = {'__name__': 'candidate_launch', '__file__': str(candidate / 'launch_candidate.py')}
exec(compile((candidate / 'launch_candidate.py').read_text(encoding='utf-8'), str(candidate / 'launch_candidate.py'), 'exec'), namespace)
tool = namespace['load_tool']()
window = tool.show_ui()
```

2. 两个测试对象分别制作 BaseAnimation 和自定义层的不同键点，比较 auto/BaseAnimation/指定层/All；多物体合并正确，其他层不得混入单层结果。增加 1.1、1.2、1.0005 子帧，核查区间时间与整数显示名，确认显示名重复能接受。
3. 点击检查按钮或 API dry_run，确认 keyframes/intervals/颜色/待删除节点/UUID 完整，当前时间、选择、原键、书签及 Undo 队列不变。插件未加载时 generate/clear 预检明确失败且不加载；inspect 仍可只读查询。
4. 分别生成 dual/vibrant/pastel/cyberpunk，确认时间滑块实际显示、颜色相邻区分、循环跨边界交替、priority、显示名、节点独立。生成后原选择和当前时间不变，原曲线不修改；一次 Undo 删除整批。
5. 不清空时重复生成会叠加。测试场景准备无关书签，勾选“生成前清空所有书签”：全部旧书签删除并生成新书签，一次 Undo 恢复完整旧节点/属性。单独清空按钮/API 不需选物体，一次 Undo 恢复。Maya 可能复用节点名，用 UUID 判断新旧身份。
6. 锁定某个书签或引用含书签的测试场景，尝试 clear 与 clear_existing；应整次预检失败，不删除其他书签。不清空的生成可以保留锁定/引用旧书签。此项引用书签场景本轮隔离测试尚未实测，需要真人核验。
7. 无选择、无效层、少于两键、未知色板、空前缀、未知参数、数量超限/Undo 关闭清楚失败；即使勾选清空，少于两键也保留旧书签。inspect 无键可成功返回空列表。
8. 若运行失败，检查返回的 created_bookmark_uuids/deletion_targets/errors 与实际场景；部分节点可能未配置完，使用 Undo 回原场景。插件 writeRequires 和插件加载不是场景 Undo 保证，验收时记录该影响。
9. 可在测试场景尝试生成区间后运行书签修剪器预检，观察端点输入衔接；跨工具组合不在本轮通过声明内。记录 Maya/Python 版本、验收人、日期、通过/失败及复现步骤。

验收通过后先只读预览晋级：

```powershell
python plans/staging_run/promote_candidate.py --candidate tools_staging_pool/01_animation/anim_layer_keyframe_bookmark/release_candidate
```

将输出 candidate_sha256 填入验收 JSON（passed=true、tool_id=anim_layer_keyframe_bookmark、candidate_sha256、maya_version、date、accepted_by），随后才使用 --apply --acceptance <文件> 晋级。完整代码、原档、文档/tests 和注册合并都已预制，面板由注册表发现；候选修改后旧指纹验收失效。
