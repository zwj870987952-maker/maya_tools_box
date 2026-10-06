# 定位器与父级（Locator）

创建定位器或在保留动画的流程中改变父级关系。

- 状态：prepared_unverified，等待人工 Maya 直验。
- 输入：当前 Maya 选择、通道/Graph Editor 关键帧及时间区间；固定预设由下列脚本定义。
- 输出：候选 API 返回分派状态与操作后选择，不声称原算法已成功。
- 撤销：场景操作进入 Undo Chunk；外部文件、UI、插件、偏好不由 Maya Undo 撤回。

| operation ID | 原名称 | 执行源文件（相对 Animo_v10.6.0） | 具体用途/影响 |
| --- | --- | --- | --- |
| `locator.change_selected_locators_color_b430e7ae` | Change Selected Locators Color | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Change Selected Locators Color.py` | 定位器与父级：Change Selected Locators Color。创建定位器或在保留动画的流程中改变父级关系。；DAG 节点、父级、约束或关键帧 |
| `locator.locator_on_selections_average_point_8928f808` | Locator On Selections Average_Point | `Animo_Data/Animo_Tools_Editor/tools_library/Locator/Locator On Selections Average_Point.py` | 定位器与父级：Locator On Selections Average_Point。创建定位器或在保留动画的流程中改变父级关系。；DAG 节点、父级、约束或关键帧 |
| `locator.locator_on_selections_bake_5cf617c4` | Locator On Selections BAKE | `Animo_Data/Animo_Tools_Editor/tools_library/Locator/Locator On Selections BAKE.py` | 定位器与父级：Locator On Selections BAKE。创建定位器或在保留动画的流程中改变父级关系。；DAG 节点、父级、约束或关键帧 |
| `locator.locator_on_selections_9fd7ed88` | Locator On Selections | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Locator_On_Selections.py` | 定位器与父级：Locator On Selections。创建定位器或在保留动画的流程中改变父级关系。；DAG 节点、父级、约束或关键帧 |
| `locator.locators_minus_bigger_3ade198d` | Locators - Bigger | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Locators - Bigger.py` | 定位器与父级：Locators - Bigger。创建定位器或在保留动画的流程中改变父级关系。；DAG 节点、父级、约束或关键帧 |
| `locator.locators_minus_smaller_4683ccd6` | Locators - Smaller | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Locators - Smaller.py` | 定位器与父级：Locators - Smaller。创建定位器或在保留动画的流程中改变父级关系。；DAG 节点、父级、约束或关键帧 |
| `locator.parent_selected_preserve_animation_cff11c33` | Parent Selected (Preserve Animation) | `Animo_Data/Animo_Tools_Editor/tools_library/Locator/Parent Selected (Preserve Animation).py` | 定位器与父级：Parent Selected (Preserve Animation)。创建定位器或在保留动画的流程中改变父级关系。；DAG 节点、父级、约束或关键帧 |
| `locator.world_selected_preserve_animation_e1b5ece0` | World Selected (Preserve Animation) | `Animo_Data/Animo_Tools_Editor/tools_library/Locator/World Selected (Preserve Animation).py` | 定位器与父级：World Selected (Preserve Animation)。创建定位器或在保留动画的流程中改变父级关系。；DAG 节点、父级、约束或关键帧 |

## 调用

```python
tool.run(dry_run=True, action="invoke", operation_id='locator.change_selected_locators_color_b430e7ae')
# 阅读预检结果后再执行：
# tool.run(action="invoke", operation_id='locator.change_selected_locators_color_b430e7ae')
```

所有入口的函数签名、顶层固定调用值及原索引别名见候选 `operations.json`；这些是静态证据，不表示运行兼容。
