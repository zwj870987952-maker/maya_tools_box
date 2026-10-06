# 姿态与动画镜像（Mirror）

建立默认姿势/镜像设置，按当前姿势或关键帧区间镜像。

- 状态：prepared_unverified，等待人工 Maya 直验。
- 输入：当前 Maya 选择、通道/Graph Editor 关键帧及时间区间；固定预设由下列脚本定义。
- 输出：候选 API 返回分派状态与操作后选择，不声称原算法已成功。
- 撤销：场景操作进入 Undo Chunk；外部文件、UI、插件、偏好不由 Maya Undo 撤回。

| operation ID | 原名称 | 执行源文件（相对 Animo_v10.6.0） | 具体用途/影响 |
| --- | --- | --- | --- |
| `mirror.fix_mirror_settings_3b4f0fd2` | Fix Mirror Settings | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Fix Mirror Settings.py` | 姿态与动画镜像：Fix Mirror Settings。建立默认姿势/镜像设置，按当前姿势或关键帧区间镜像。；变换、关键帧和镜像配置文件 |
| `mirror.mirror_all_keys_b8f2d3f1` | Mirror All Keys | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Mirror All Keys.py` | 姿态与动画镜像：Mirror All Keys。建立默认姿势/镜像设置，按当前姿势或关键帧区间镜像。；变换、关键帧和镜像配置文件 |
| `mirror.mirror_pose_minus_animation_f93fbda2` | Mirror Pose-Animation | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Mirror Pose-Animation.py` | 姿态与动画镜像：Mirror Pose-Animation。建立默认姿势/镜像设置，按当前姿势或关键帧区间镜像。；变换、关键帧和镜像配置文件 |
| `mirror.snapshot_default_rig_eda8c0b4` | Snapshot Default Rig | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Snapshot Default Rig.py` | 姿态与动画镜像：Snapshot Default Rig。建立默认姿势/镜像设置，按当前姿势或关键帧区间镜像。；变换、关键帧和镜像配置文件 |

## 调用

```python
tool.run(dry_run=True, action="invoke", operation_id='mirror.fix_mirror_settings_3b4f0fd2')
# 阅读预检结果后再执行：
# tool.run(action="invoke", operation_id='mirror.fix_mirror_settings_3b4f0fd2')
```

所有入口的函数签名、顶层固定调用值及原索引别名见候选 `operations.json`；这些是静态证据，不表示运行兼容。
