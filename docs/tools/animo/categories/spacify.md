# 临时空间切换（Spacify）

建立世界、相对、摄像机、Aim、临时 IK/FK 等辅助系统，并烘焙清理。

- 状态：prepared_unverified，等待人工 Maya 直验。
- 输入：当前 Maya 选择、通道/Graph Editor 关键帧及时间区间；固定预设由下列脚本定义。
- 输出：候选 API 返回分派状态与操作后选择，不声称原算法已成功。
- 撤销：场景操作进入 Undo Chunk；外部文件、UI、插件、偏好不由 Maya Undo 撤回。

| operation ID | 原名称 | 执行源文件（相对 Animo_v10.6.0） | 具体用途/影响 |
| --- | --- | --- | --- |
| `spacify.aim_931ba549` | Aim | `Animo_Data/Animo_Space_Switcher/AimSpace.py` | 临时空间切换：Aim。建立世界、相对、摄像机、Aim、临时 IK/FK 等辅助系统，并烘焙清理。；DAG、约束、集合和关键帧 |
| `spacify.assign_camera_86a32ec8` | Assign Camera | `Animo_Data/Animo_Tools_Editor/tools_library/Spacify/Assign Camera.py` | 临时空间切换：Assign Camera。建立世界、相对、摄像机、Aim、临时 IK/FK 等辅助系统，并烘焙清理。；DAG、约束、集合和关键帧 |
| `spacify.camera_space_52217d44` | Camera Space | `Animo_Data/Animo_Tools_Editor/tools_library/Spacify/Camera Space.py` | 临时空间切换：Camera Space。建立世界、相对、摄像机、Aim、临时 IK/FK 等辅助系统，并烘焙清理。；DAG、约束、集合和关键帧 |
| `spacify.clean_and_bake_c6a393b7` | Clean and Bake | `Animo_Data/Animo_Space_Switcher/CleanAndBake.py` | 临时空间切换：Clean and Bake。建立世界、相对、摄像机、Aim、临时 IK/FK 等辅助系统，并烘焙清理。；DAG、约束、集合和关键帧 |
| `spacify.fk_chain_10942434` | FK Chain | `Animo_Data/Animo_Space_Switcher/Spacify_Quick_Actions/spacify_quick_fk_chain.py` | 临时空间切换：FK Chain。建立世界、相对、摄像机、Aim、临时 IK/FK 等辅助系统，并烘焙清理。；DAG、约束、集合和关键帧 |
| `spacify.group_0e7f8211` | Group | `Animo_Data/Animo_Space_Switcher/GroupCtrl.py` | 临时空间切换：Group。建立世界、相对、摄像机、Aim、临时 IK/FK 等辅助系统，并烘焙清理。；DAG、约束、集合和关键帧 |
| `spacify.new_pivot_2fcc26d0` | New Pivot | `Animo_Data/Animo_Space_Switcher/Spacify_Quick_Actions/spacify_quick_new_pivot.py` | 临时空间切换：New Pivot。建立世界、相对、摄像机、Aim、临时 IK/FK 等辅助系统，并烘焙清理。；DAG、约束、集合和关键帧 |
| `spacify.relative_1f867194` | Relative | `Animo_Data/Animo_Space_Switcher/RelativeSpace.py` | 临时空间切换：Relative。建立世界、相对、摄像机、Aim、临时 IK/FK 等辅助系统，并烘焙清理。；DAG、约束、集合和关键帧 |
| `spacify.temp_ik_585f585b` | Temp IK | `Animo_Data/Animo_Space_Switcher/TempIK.py` | 临时空间切换：Temp IK。建立世界、相对、摄像机、Aim、临时 IK/FK 等辅助系统，并烘焙清理。；DAG、约束、集合和关键帧 |
| `spacify.world_orient_6f5aeb74` | World Orient | `Animo_Data/Animo_Space_Switcher/WorldOrient.py` | 临时空间切换：World Orient。建立世界、相对、摄像机、Aim、临时 IK/FK 等辅助系统，并烘焙清理。；DAG、约束、集合和关键帧 |
| `spacify.world_bff19cdc` | World | `Animo_Data/Animo_Space_Switcher/WorldSpace.py` | 临时空间切换：World。建立世界、相对、摄像机、Aim、临时 IK/FK 等辅助系统，并烘焙清理。；DAG、约束、集合和关键帧 |

## 调用

```python
tool.run(dry_run=True, action="invoke", operation_id='spacify.aim_931ba549')
# 阅读预检结果后再执行：
# tool.run(action="invoke", operation_id='spacify.aim_931ba549')
```

所有入口的函数签名、顶层固定调用值及原索引别名见候选 `operations.json`；这些是静态证据，不表示运行兼容。
