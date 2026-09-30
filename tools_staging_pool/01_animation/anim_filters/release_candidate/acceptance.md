# anim_filters 用户验收与晋级

候选齐备，尚未 GUI 实测；本机 SciPy 缺失和 standalone Qt 创建失败已记录。只在备份或临时场景执行，保留另存的原曲线用于对照。

## 在真实 Maya 启动候选

```python
import os
candidate = r"E:\GitHub\maya_tools_box\tools_staging_pool\01_animation\anim_filters\release_candidate"
entry = os.path.join(candidate, "launch_candidate.py")
scope = {"__file__": entry, "__name__": "candidate_loader"}
with open(entry, "rb") as stream:
    exec(compile(stream.read(), entry, "exec"), scope)
tool = scope["load_tool"]()
tool.show_ui()
```

此入口面向 Python 3，不提前注册正式工具。若修改候选后重载，先安全 Cancel/关闭旧窗口；不要在尚有 live preview 时重新加载。

在目标 Maya Script Editor 先检查 `import numpy, scipy`。如果缺包，记录 Maya 内 Python、NumPy 版本与错误，配置匹配该解释器的科学包后复验；不得把系统 Python 的 site-packages 直接加入 Maya。原 readme 中的 cp27 wheels 是历史说明，不作为现代 Maya 的安装推荐。

## 验收表

| 项目 | 操作和预期 | 结果 |
| --- | --- | --- |
| UI/资源 | 三标签、全部滑条/输入框、Preview/Cancel/Apply/Reset、图标和 Buffer checkbox 可用 | 待填 |
| dry_run | 显式曲线范围和所选 Graph Editor 键两种输入；键/切线/选择/Undo 栈保持不变 | 待填 |
| Adaptive | 对线性、非线性、长段、负帧和 tolerance=0 过滤；与原数学结果核对 | 待填 |
| Butterworth | SciPy 可用后测默认、短段、长度恰好 padlen、截止非法；输出有限值，失败不改场景 | 待填 |
| Median | 奇偶窗口、超长窗口、端点；核对上游零填充效果与警告 | 待填 |
| Preview/滑条 | 预览后反复调参数，始终基于原曲线而非叠加过滤；Undo 全程开启 | 待填 |
| Cancel/关闭 | 恢复原键/切线及适用的 buffer；不要丢失原始曲线 | 待填 |
| Apply/Undo | 接受预览后关闭不恢复；一次 Undo 恢复原曲线 | 待填 |
| 外部编辑保护 | 预览后修改其他对象，Cancel/关闭拒绝撤销无关编辑；先 Undo 外部编辑再 Cancel 可恢复 | 待填 |
| 场景边界 | 多曲线、角度/线性曲线、引用/锁定/异常连接、超量采样；拒绝条件不写场景 | 待填 |
| 时间与角度单位 | 记录不同场景帧率和角度单位；确认上游 30 帧采样约定及端点行为可接受 | 待填 |

记录 Maya/Python/Qt/SciPy/NumPy 版本、日期、验收人、场景和 Script Editor 报错。科学模式或 GUI 任一失败，不把整个工具标为已验收。

## 晋级

默认预检不写正式库：

```text
python plans/staging_run/promote_candidate.py --candidate tools_staging_pool/01_animation/anim_filters/release_candidate
```

实测通过后按输出指纹填写真实验收 JSON：

```json
{"tool_id":"anim_filters","passed":true,"maya_version":"实际版本","accepted_by":"实际验收人","date":"实际日期","candidate_sha256":"当前预检指纹"}
```

再运行同一命令，加 `--acceptance <实际记录路径> --apply`。脚本会安放 runtime、全部上游资源/许可证、知识文档与测试，并合并当前正式注册表。验收前不运行 apply。已有目标或指纹变化时拒绝覆盖。晋级文件修改不能由 Maya Undo 撤销。

晋级后重启 Maya，验证统一面板条目和正式 execute_tool 的 dry_run/执行/Undo，再记录正式复验。原始工具与候选保留追溯。
