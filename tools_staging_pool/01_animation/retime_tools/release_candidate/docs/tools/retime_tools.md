# eblabs Retime Tools 动画重定时候选

用途：用控制器 `timeWarp` 动画驱动目标 animCurve 的 `input`，支持启用、禁用、重置、反向、连接、断开、烘焙、洗牌和子帧清理。完整原 Qt 界面和 38 个旧 MEL 过程均保留，原始 28 文件包括压缩包、图片、空 Plugin.py、Qt 辅助库与安装脚本按字节归档。原始源码未执行安装；晋级包不依赖待整理池外部路径。

作者：Python/套件 eblabs，原界面标注“帝都儿汉化”；历史 MEL 注明 Eric Bates 2011，版本 2018-05-28。原官网指向 https://eblabs.com/shop/retime-tools/。没有随包独立再分发许可；个人本地整理不代表获得再分发许可。QTS 与顶层 LicenseManager 的版本模块/UXFramework 不全，原试用参数、许可代码不改不模拟；主 RetimeTools.py 未导入这些模块，实际主界面只使用 Qt。空 Plugin.py 不视为提供了一个 Maya 插件。

## API 与输入输出

`maya_toolkit.execute_tool('retime_tools', arguments, dry_run=True)` 调用标准 BaseMayaTool 协议。候选使用 launch_candidate.py 的 load_tool()，晋级后注册 RetimeToolsTool 并由现有面板发现。`validate`/dry_run 只读；不创建 Qt widget，不加载 MEL，不安装 Shelf，不写文件。所有 API 场景写入一个 UndoChunk，失败允许 Undo，不自动回滚；time/selection/namespace/autokey 用 finally 恢复。选中操作在界面由用户主动触发。剪贴板 copyKey/cutKey/pasteKey 与原算法一样会改变 Maya key clipboard，场景 Undo 不等于恢复剪贴板。

| action | 必要参数/行为 | 输出/影响 |
| --- | --- | --- |
| inspect | 无参数 | 只读控制器列表 |
| create | name 可选 | 原完整多形状控制器、timeWarp/offline/store/state 与动画范围线性关键帧 |
| connect | controller，nodes 或 curves；省略时当前选择 | 原列表深度 2 的关联 animCurveT，替换普通 time.outTime，拒绝其他 warp/驱动 |
| disconnect | controller，可给已连接 curves 子集 | 断开 warp 并显式恢复唯一 time.outTime，避免曲线冻结 |
| state | controller，state 为 Enable/Disable/Reset/Invert/Disconnect/Delete | 原启停离线槽、反向采样、删除逻辑；删除先恢复时间输入，拒绝外部 DAG 子项/消费者 |
| bake | controller | 原 bakeResults，sampleBy=1/simulation=True；原 preserveOutsideKeys=False，范围外关键帧可能丢失 |
| shuffle | controller，clean 可选 | 完整原复制/粘贴/切线/替换/Infinity 算法，用修正的逆查找移动关键帧；断开 warp，可同时清理子帧 |
| clean_subframes | controller 或 nodes/curves 或当前选择 | 保留完整原先插入整数帧再剪切子帧算法；负帧 round 以 floor(t+0.5) 修正 |
| rename | controller，name | 重命名所选控制器 |
| update_legacy | 明确旧 controller | 完整原添加 state/移除 shuffleData，不自动升级整个场景 |
| import_curve | file，name 可选 | 原一列值/两列帧值或 JSON frame:value 语义，完整控制器创建后应用关键帧并记录路径元数据 |
| export_curve | controller，file，overwrite 默认 False | .json 或 .txt/.ascii，写现有目录；临时文件+无覆盖硬链接或明确覆盖原子替换；不可 Maya Undo |
| open_ui/close_ui | 交互 Maya | 完整原 Qt 界面，私有 objectName；写回调转统一 API |
| open_legacy_ui | 交互 Maya、备份场景 | 完整历史 MEL UI，过程/UI/全局变量私有化；独立人工验收 |

返回 ToolResult.data 含 controller、curves、file、warnings；数据只描述实际 API 作用范围。curves 子集仅用于 connect/disconnect/clean_subframes，烘焙/洗牌/状态按整个控制器处理。所有 API 拒绝引用/锁定节点、其他时间驱动、共享到其他目标的 warp 动画曲线，以及不可编辑的目标输出；不支持动画层/约束输出重连。shuffle/Invert 要求有界且采样严格单调，平坦或非单调 warp 无唯一逆，使用 bake 后验收；这明确收窄了原代码容易零除/多解覆盖的输入范围。

## 算法演进与原始边界

完整原 32 类 211 方法保存在 native.py；五个业务类全体方法另提取 engine.py，不是演示替代。原 UI 的导入/导出菜单本来是禁用打印占位，仍保留这个事实，实际文件功能由明确 API 提供。原 Utilities 全部方法保留可追溯，但不走其缺失 ebLabs_createTimeWarpController MEL 全局依赖/忽略传入参数/取消文件对话框报错路径。

RetimeLookup 原源码两个 lerp 时间端点都写 min_index，邻接方向也不稳定。候选 API 在完整原分段/采样数据上逐相邻样本求逆、去重，得到 time=0/负帧及正确局部 warp 斜率；原全部辅助方法仍保留。ShuffleKeys 的原 `if not rt` 改为 `is None`，paste 使用 merge 避免插入时移动已粘贴时间，Infinity 直接读写原 curve 属性（源 query 会返回 None），临时曲线异常 finally 清理，替换失败不会被打印后当成功。原 Invert 包含末帧。原 bake 输出查询错误地每轮查询整个曲线列表，改为每条 output，仍保留完整原烘焙算法。

历史 MEL 套件保留完整旧算法，包括 calculator、velocityTimeWarp、迭代连接、字符集处理、旧 shuffle/bake、子帧清理与进度 UI。私有化并修复缺失 animscratch Python 连接桥，除此保留其原场景行为。**历史 MEL 回调不是 Python 安全 API：其旧的 force 连接、场景遍历、关键帧/播放设置及 Undo 行为须分别在备份场景验收，不作为无人值守场景写入入口。** 静态定义编译通过只能证明能加载，不证明每个按钮正常。

## 可组合与验证

输入是已有时间输入 animCurve 的 Maya 场景；输出是重定时连接、重排或烘焙的动画。可在动画清理/降帧工具之前先烘焙并检查断开连接；这只是潜在流程，不代表与正式工具联测通过。沿用框架 BaseMayaTool/Undo/ToolResult，不修改 core；原专有控制器形状和查找算法不适合未经多工具验收下沉。

离线 Python 测试核对全套 SHA256/211 方法/Schema/严格输入/ASCII/JSON/零负帧查找；隔离 Maya2025 五组检查覆盖完整控制器、连接、启停与 Undo、洗牌与临时清理、删除恢复时间、目标锁与外部子项拒绝、文件 IO、烘焙、Qt 类导入（不创建 QWidget）、38 MEL 定义编译。真实 GUI、生产 rig、引用/动画层、加权切线、非线性曲线、反向速度、跨 Maya 版本尚未验收。隔离通过不等于真人 Maya 验收。

## 完整原方法与 MEL 过程目录

* `Window`: `__init__`, `display`
* `RetimeStates`: `get_state_for_string`, `get_state_for_int`, `get_string_for_int`
* `Document`: `__init__`, `setup_signals`, `add_user_menu_items`, `import_retime`, `export_retime`, `update_old_retime_curves`
* `LayoutWidget`: `__init__`, `set_data`, `get_data`, `do_layout`, `update`, `on_selection_change`, `on_set_data`
* `ActionsWidget`: `__init__`, `do_layout`, `set_valid`, `set_valid_item`, `action_clean_subframes`, `action_bake`, `action_shuffle`, `on_data_change`, `create_new_retime_controller`
* `ConnectionsWidget`: `__init__`, `do_layout`, `on_click_item`, `on_click_remove_objects`, `on_click_add_objects`, `on_data_change`, `on_set_data`, `update`, `set_valid`, `set_valid_item`
* `ControlersWidget`: `__init__`, `do_layout`, `on_item_selection_change`, `clear_items`, `update`, `on_clicked_select`, `on_selection_change`
* `ControllersWidgetItem`: `__init__`, `do_layout`, `split_namespace`, `on_rename_curve`, `on_select_clicked`, `on_state_change`, `on_set_data`, `update_comboBox`
* `CoreFunctions`: `get_retime_curves_in_scene`, `object_exists`, `getAttrFromObject`, `isStringListInString`, `getConnectedNodes`, `getCurvesFromNodes`, `get_all_related_curves_for_object`, `getActiveTimewarp`, `getSelected`, `addCurvesToTimewarp`, `getCurvesAttachedToRetime`, `getAllConnectionsToRetime`, `getAttributeFromCurve`, `get_hierarchical_connection_info_from_retime`, `print_curve_points`, `get_controller_shape_node`, `create_new_retime_controller`, `create_new_retime_controller_exec`, `set_retime_controller_state`, `reset_retime`, `invert_retime`, `completely_disconnect_retime`, `disconnect_curve`, `delete_retime`, `select_maya_nodes`, `get_retime_controller_status`, `bake_retime_controller`, `get_plugs_for_anim_curves`, `cleanSubframeKeys`, `find_old_retime_curves`, `update_old_retime_curves`, `update_old_retime_curve`
* `ShuffleKeys`: `process`
* `RetimeLookup`: `__init__`, `getDirection`, `drange`, `getKeyTimes`, `getSections`, `create_value_time_lookup`, `get_nearest_pair_index`, `float_lerp`, `slope`, `clamp`, `get_slope_between_pairs`, `getSingleKeyTimeLookup`
* `Color`: `__init__`, `get_rgba`, `set_rgba`, `r`, `g`, `b`, `a`, `r_int`, `g_int`, `b_int`, `a_int`, `multiply_hsva`, `lighten_hsva`, `get_average_intensity`, `get_int_rgba`, `get_int_rgba_string`, `lerp`, `float_to_int`, `float_rgba_to_hsva`, `float_hsva_to_rgba`
* `Utilities`: `ebLabs_retimeTools_createRetimefromAscii`, `ebLabs_retimeTools_createRetimefromJson`, `loadDataFromFile`
* `QTHelpers`: `populateComboBox`, `get_key_modifiers`, `getStringFromUser`, `getYesNoFromUser`, `get_files_from_user`, `get_folder_from_user`, `get_main_window`
* `MessageQueryDialog`: `__init__`, `do_layout`, `on_click_okay`, `on_click_cancel`, `closeEvent`
* `BoolQueryDialog`: `__init__`, `do_layout`, `on_click_okay`, `on_click_cancel`, `closeEvent`
* `VBoxLayout`: `__init__`
* `GridWidget`: `__init__`
* `GridLayout`: `__init__`
* `StackedLayout`: `__init__`
* `ListWidget`: `__init__`
* `ColoredButton`: `__init__`, `updateButtonColors`
* `ColoredComboBox`: `__init__`, `wheelEvent`, `on_click`, `setCommand`, `updateButtonColors`
* `CollapsableWidget`: `__init__`, `set_expand_state`, `get_expand_state`, `set_section_label`, `add_widget`, `update_UI_state_change`, `on_click`
* `ScrollableLayoutWidget`: `__init__`, `add_widget`
* `DictTree`: `__init__`, `mouseReleaseEvent`, `on_click`, `get_top_parents`, `get_end_children`, `new_item`, `fill_item`, `set_dict_data`
* `ConfirmButton`: `__init__`, `get_data`, `set_data`, `get_kwarg_template`, `on_click_main_button`, `on_click_okay_button`, `set_checked_state`, `get_checked_state`, `set_expand_state`, `run_command`, `set_valid`, `get_expand_state`, `update_UI_state_change`
* `SimpleDataHandler`: `__init__`, `get_template_data`, `get_data_key`, `get_all_data`, `set_data_key`, `update_data`, `modify_data`, `on_data_change`, `on_pallete_change`, `on_redraw_pre`, `on_redraw`
* `EditableLabelWidget`: `__init__`, `modify_data`, `on_redraw`, `on_edit_action`, `on_edit_finished_action`, `on_edit_cancelled_action`, `set_editible`, `toggle_editor`, `get_template_data`
* `EditableLabel`: `__init__`, `on_redraw`, `get_template_data`
* `EditableTextField`: `__init__`, `get_template_data`, `on_redraw`, `eventFilter`, `editNote`, `setDisplayText`, `editing_finished`, `cancelEdit`
* `Utils`: `doubleClickable`

历史 MEL：`ebLabs_timeWarp`, `ebLabs_tw_ebLabs_connectToTimeWarpControllerPython`, `ebLabs_tw_calculator`, `ebLabs_tw_isNumber`, `ebLabs_tw_doCalculate`, `ebLabs_tw_enableMayaUI`, `ebLabs_tw_velocityTimeWarp`, `ebLabs_createTimeWarpController`, `ebLabs_tw_updateTimeWarpControllerList`, `ebLabs_refreshTimeWarpConnectionList`, `ebLabs_tw_expand`, `ebLabs_tw_updateList`, `ebLabs_disconnectToTimeWarpController`, `ebLabs_getObjectsFromConnections`, `ebLabs_connectToTimeWarpControllerIterations`, `ebLabs_connectToTimeWarpController`, `ebLabs_storeConnections`, `ebLabs_retrieveConnections`, `ebLabs_getAnimCurvesForObject`, `ebLabs_timeWarpShuffleKeys`, `ebLabs_timeWarpBake`, `ebLabs_tw_getCurveFromAttr`, `ebLabs_tw_getAttributeFromCurve`, `ebLabs_tw_selectAll`, `ebLabs_tw_selectNone`, `ebLabs_tw_cleanSubFrameKeys`, `ebLabs_tw_setTimeWarpModeStatus`, `ebLabs_tw_getTimeWarpModeStatus`, `ebLabs_tw_disable`, `ebLabs_tw_enable`, `ebLabs_tw_invert`, `ebLabs_tw_completelyDisconnect`, `ebLabs_tw_getTimeWarpFromList`, `ebLabs_tw_setTimeWarpFromList`, `ebLabs_tw_selObjFromList`, `ebLabs_tw_reset`, `ebLabs_tw_deleteBoringKeys`, `ebLabs_updateProgress`
