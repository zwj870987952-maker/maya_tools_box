# Anim Layer v4.0 过程签名目录

从完整原始文件声明生成；静态标签不覆盖调用链，不表示 Maya 验证或最终效果。
API 先 inventory 查选定版本/过程，再用 arguments 的同名键调用；原文件行号与返回类型保留在 catalog.json。

## full

| 过程 | parameters | 返回 | 原文件行 | 直接文本中出现的影响 |
| --- | --- | --- | --- | --- |
| `create_and_select_anim_layer` | `int rotation_mod` | `string` | 1 | 属性/连接写入 |
| `extract_anim_on_base_layer_selected_object` | `无` | `int` | 9 | 选择 |
| `extract_part_to_over_layer` | `float side_frames` | `string` | 63 | 动画写入、选择 |
| `selectLayer` | `string layer` | `void` | 111 | 未标记；仍须检查依赖过程 |
| `select_few_Layers` | `string[] layers` | `void` | 120 | 未标记；仍须检查依赖过程 |
| `select_object_in_selected_layers` | `无` | `void` | 129 | 未标记；仍须检查依赖过程 |
| `select_best_layer` | `无` | `string[]` | 135 | 未标记；仍须检查依赖过程 |
| `animLayerMerge_toAdditive` | `string[] layers, float[] timerange` | `string` | 148 | 删除、动画写入、属性/连接写入、选择 |
| `extract_animation_to_additive_layer` | `无` | `string[]` | 198 | 动画写入、选择 |
| `anim_layer_fast_merge` | `无` | `void` | 263 | 删除、选择 |
| `getLayerDisplayType` | `无` | `string` | 273 | 未标记；仍须检查依赖过程 |
| `get_anim_time_range_from_anim_layer` | `string anim_layer_name` | `float[]` | 289 | 未标记；仍须检查依赖过程 |
| `get_anim_time_range_from_multiply_anim_layers` | `string[] anim_layers_name` | `float[]` | 309 | 未标记；仍须检查依赖过程 |
| `create_add_anim_layer_from_objects_and_set_framerange_from_multiply_anim_layers` | `string[] objects, int mod` | `string` | 333 | 动画写入、选择 |
| `create_add_anim_layer_from_timerange` | `string[] objects, int mod` | `string` | 353 | 动画写入 |
| `create_anim_layer_from_channelbox_attrib` | `int mode` | `string[]` | 361 | 属性/连接写入 |
| `extract_smart_anim_on_base_layer_selected_object` | `int fidelity, float tolerance` | `void` | 381 | 选择 |
| `anim_layer_smart_fast_merge` | `int fidelity, float tolerance` | `void` | 411 | 删除、选择 |
| `execute_smart_fast_merge` | `int fidelity, float tolerance` | `void` | 421 | 选择 |
| `execute_fast_merge` | `无` | `void` | 430 | 选择 |
| `execute_smart_fast_selected_merge` | `int fidelity, float tolerance` | `void` | 439 | 选择 |
| `execute_fast_selected_merge` | `无` | `void` | 448 | 选择 |
| `extract_to_additive_layer` | `无` | `void` | 457 | 未标记；仍须检查依赖过程 |
| `anim_layer_util_menue` | `无` | `void` | 463 | 动画写入、UI/设置/回调、选择 |
| `get_min_max_from_selected` | `无` | `float[]` | 518 | 未标记；仍须检查依赖过程 |
| `get_time_range_from_selected_keys_or_timeslider` | `无` | `float[]` | 529 | 未标记；仍须检查依赖过程 |
| `disable_viewport` | `无` | `void` | 544 | 运行状态 |
| `enable_viewport` | `无` | `void` | 559 | 运行状态 |
| `bake_simulation_timerange_on_over_layer` | `float[] timerange` | `string` | 574 | 动画写入、运行状态、选择 |
| `bake_smart_simulation_playback_range` | `int fidelity, float tolerance` | `void` | 601 | 动画写入、运行状态、选择 |
| `bake_simulation_playback_range` | `无` | `void` | 629 | 动画写入、运行状态、选择 |
| `euler_filter_on_selected` | `无` | `void` | 653 | 动画写入、选择 |
| `select_skip_no_exist` | `string[] objs` | `string[]` | 671 | 选择 |
| `getSelectedAnimLayer` | `string toolName` | `string[]` | 731 | UI/设置/回调 |
| `deselectAnimLayers` | `string toolName, string[] layers` | `void` | 738 | UI/设置/回调 |
| `isAffectedLayer` | `string layer, string[] affectedLayers, int recursive` | `int` | 794 | 未标记；仍须检查依赖过程 |
| `getAffectedLayers` | `string[] selected` | `string[]` | 830 | 未标记；仍须检查依赖过程 |
| `buildAnimLayerArrayRecursive` | `string layer, string[] layerArray` | `void` | 845 | 未标记；仍须检查依赖过程 |
| `buildAnimLayerArray` | `无` | `string[]` | 861 | 未标记；仍须检查依赖过程 |
| `animLayerWarnNonEmptyAccChange` | `string[] layers` | `void` | 875 | 未标记；仍须检查依赖过程 |
| `openFloatingAnimLayerEditor` | `无` | `void` | 902 | UI/设置/回调 |
| `updateAddButtons` | `无` | `void` | 914 | 未标记；仍须检查依赖过程 |
| `createAnimLayerEditor` | `string parentLayout, string toolName` | `void` | 927 | UI/设置/回调、运行状态 |
| `layerEditorBuildAnimLayerMenu` | `string parent, string toolName` | `void` | 1311 | UI/设置/回调、选择 |
| `layerModeSubMenu` | `string layerModeMenu, string toolName` | `void` | 1581 | UI/设置/回调 |
| `layerRotationAccSubMenu` | `string layerAccumulationMenu, string toolName` | `void` | 1614 | 属性/连接写入、UI/设置/回调 |
| `layerScaleAccSubMenu` | `string layerAccumulationMenu, string toolName` | `void` | 1641 | 属性/连接写入、UI/设置/回调 |
| `onAnimLayersAnimationChanged` | `string toolName` | `void` | 1869 | 属性/连接写入、运行状态 |
| `onAnimLayersBaseLockChanged` | `string toolName` | `void` | 1885 | 属性/连接写入、UI/设置/回调 |
| `onAnimLayersLockChanged` | `string toolName` | `void` | 1907 | 属性/连接写入、UI/设置/回调、运行状态 |
| `updateEditorFeedbackAnimLayers` | `string toolName` | `void` | 1930 | UI/设置/回调 |
| `animLayerEditorDoNothingSJ` | `无` | `void` | 2022 | 未标记；仍须检查依赖过程 |
| `animLayerEditorUpdateWeightSJ` | `string pTool, string pWeightAttribute` | `void` | 2027 | 未标记；仍须检查依赖过程 |
| `setPreferredForAllLayers` | `int preferred` | `void` | 2037 | 未标记；仍须检查依赖过程 |
| `setSelectedForAllLayers` | `int selected` | `void` | 2046 | 未标记；仍须检查依赖过程 |
| `setSelectedLayerRecursive` | `string layer, int selected, int skipRoot` | `void` | 2055 | UI/设置/回调 |
| `animLayerMuteCallBack` | `string item, int buttonState` | `void` | 2125 | UI/设置/回调、运行状态 |
| `animLayerGhostCallBack` | `string animLayerEditor, string item, int buttonState` | `void` | 2147 | 属性/连接写入、UI/设置/回调、运行状态 |
| `animLayerGhostColorChanged` | `string layer` | `void` | 2182 | 运行状态 |
| `animLayerGhostRightCallBack` | `string item, int buttonState` | `void` | 2189 | UI/设置/回调 |
| `animLayerSoloCallBack` | `string item, int buttonState` | `void` | 2200 | UI/设置/回调 |
| `animLayerLockCallBack` | `string item, int buttonState` | `void` | 2233 | 未标记；仍须检查依赖过程 |
| `animLayerDragAndDropCallback` | `string[] dropItems, string[] oldParents, int[] oldIndexes, string newParent, int[] newIndex, string newItemPrev, string newItemNext` | `void` | 2241 | 未标记；仍须检查依赖过程 |
| `layerEditorMoveAnimItem` | `string toolName, int up` | `void` | 2282 | UI/设置/回调 |
| `animLayerEditLabelCallback` | `string item, string newLabel` | `string` | 2318 | 运行状态、选择 |
| `animLayerExpandCollapseCallback` | `string item, int expand` | `void` | 2352 | UI/设置/回调 |
| `updateAnimLayerEditor` | `string toolName` | `void` | 2372 | UI/设置/回调 |
| `rebuildAnimLayerEditor` | `string toolName` | `void` | 2381 | UI/设置/回调 |
| `animLayerEditorOnSelect` | `string item, int itemSelected` | `int` | 2459 | UI/设置/回调、选择 |
| `layerInitialiseParameterDefaults` | `无` | `void` | 2550 | UI/设置/回调 |
| `layerEditorBuildAnimOptionMenu` | `string parentMenu` | `void` | 2622 | UI/设置/回调 |
| `layerEditorBuildAnimShowMenu` | `string parentMenu` | `void` | 2665 | UI/设置/回调 |
| `layerEditorBuildAnimHelpMenu` | `string parentMenu` | `void` | 2718 | UI/设置/回调 |
| `layerEditorBuildPopupMenu` | `string toolName, string parentMenu, string item` | `int` | 2727 | UI/设置/回调 |
| `layerEditorAnimLayersPopup` | `string[] layers, string toolName, string parentMenu, int outline` | `void` | 2808 | 属性/连接写入、UI/设置/回调、选择 |
| `layerEditorCreateAnimLayer` | `int addSelection, int createOverrideLayer` | `string` | 3017 | 属性/连接写入、UI/设置/回调 |
| `layerEditorDeleteAnimLayer` | `string[] layers` | `void` | 3079 | 删除 |
| `animLayersExport` | `string[] layers, int branch` | `void` | 3097 | 选择 |
| `animLayersSaveExportClbc` | `string file, string type` | `void` | 3135 | 文件命令 |
| `deleteEmptyAnimLayers` | `无` | `void` | 3167 | 未标记；仍须检查依赖过程 |
| `packageAnimLayerObjects` | `无` | `void` | 3211 | 未标记；仍须检查依赖过程 |
| `layerEditorAddObjectsAnimLayer` | `string[] objects, string[] layers, int showOptions` | `void` | 3219 | 未标记；仍须检查依赖过程 |
| `layerEditorExtractObjectsSingleAnimLayer` | `string[] objects, string layer` | `string` | 3230 | 选择 |
| `layerEditorExtractObjectsAnimLayer` | `string[] objects, string[] layers` | `void` | 3334 | 未标记；仍须检查依赖过程 |
| `layerEditorMergeAnimLayer` | `string[] layers, int pOptions` | `void` | 3343 | 未标记；仍须检查依赖过程 |
| `layerEditorRemoveObjectsAnimLayer` | `string[] objects, string[] layers` | `void` | 3352 | 未标记；仍须检查依赖过程 |
| `layerEditorCopyAnimLayer` | `string[] layers` | `void` | 3378 | 未标记；仍须检查依赖过程 |
| `layerEditorCopyAnimLayerNoAnim` | `string[] layers` | `void` | 3391 | 未标记；仍须检查依赖过程 |
| `layerEditorSelectObjectAnimLayer` | `string[] layers` | `void` | 3405 | 选择 |
| `layerEditorZeroKeyAnimLayer` | `string[] layers` | `void` | 3433 | 未标记；仍须检查依赖过程 |
| `layerEditorZeroWeightKeyAnimLayer` | `string[] layers` | `void` | 3438 | 未标记；仍须检查依赖过程 |
| `layerEditorFullWeightKeyAnimLayer` | `string[] layers` | `void` | 3444 | 未标记；仍须检查依赖过程 |
| `layerEditorWeightAnimLayerNoForcedRefresh` | `string[] layers, float value` | `void` | 3450 | 未标记；仍须检查依赖过程 |
| `layerEditorWeightAnimLayer` | `string[] layers, float value` | `void` | 3463 | 运行状态 |
| `layerEditorKeyWeightAnimLayer` | `string[] layers` | `void` | 3473 | 动画写入 |
| `layerEditorExclusiveSoloAnimLayer` | `string[] layers` | `void` | 3485 | 未标记；仍须检查依赖过程 |
| `getSelectedRenderItems` | `string toolName, string specified, int type` | `string[]` | 3525 | UI/设置/回调 |
| `buildRenderLayerArray` | `无` | `string[]` | 3554 | 未标记；仍须检查依赖过程 |
| `buildLayerContMapIdent` | `string layer, string map` | `string` | 3572 | 未标记；仍须检查依赖过程 |
| `parseLayerContMapIdent` | `string ident` | `string[]` | 3581 | 未标记；仍须检查依赖过程 |
| `renderLayerEditorValidateSelection` | `string toolName, int deselectNonCurrent` | `void` | 3598 | UI/设置/回调 |
| `blendModeOptions_AttrToUI` | `int attrVal` | `string` | 3648 | 未标记；仍须检查依赖过程 |
| `blendModeOptions_UIToAttr` | `string ui` | `int` | 3682 | 未标记；仍须检查依赖过程 |
| `isNodeConnectedToContMap` | `string obj, string map, string attr` | `int` | 3710 | 未标记；仍须检查依赖过程 |
| `alterNodeContMapConnection` | `string obj, string map, string attr, int connect` | `void` | 3729 | 属性/连接写入 |
| `alterContMapConnectionsForParentsOfShape` | `string shape, string map, int connect` | `void` | 3751 | 未标记；仍须检查依赖过程 |
| `displayLabelRenderLayer` | `int showNamespace, string layer` | `string` | 3787 | 未标记；仍须检查依赖过程 |
| `hookShaderOverride` | `string layer, string type, string shader` | `void` | 3817 | 属性/连接写入 |
| `getUnassociatedContMaps` | `string layer` | `string[]` | 3846 | 未标记；仍须检查依赖过程 |
| `layerEditorRenderLayerManagerChange` | `string toolName` | `void` | 3859 | 选择 |
| `renderLayerEditorItemOnRename` | `string oldName, string newName` | `string` | 3891 | 未标记；仍须检查依赖过程 |
| `renderLayerEditorOnSelectionChanged` | `string toolName` | `void` | 3927 | UI/设置/回调 |
| `layerEditorRenderLayerOnDragDrop` | `string toolName, string[] dropItems, string[] oldParents, int[] oldIndexes, string newParent, int[] newIndexes, string newItemPrev, string newItemNext` | `void` | 3988 | 属性/连接写入、UI/设置/回调 |
| `renderLayerEditorRenderable` | `string toolName, string layer, string state` | `void` | 4030 | 属性/连接写入 |
| `renderLayerEditorRecycleChange` | `string toolName, string layer, string state` | `void` | 4042 | 属性/连接写入 |
| `renderLayerEditorSettingsOverride` | `string toolName, string layer, string state` | `void` | 4062 | UI/设置/回调 |
| `layerEditorMoveRenderItem` | `string toolName, int up` | `void` | 4081 | 属性/连接写入 |
| `layerBlendModeChanged` | `string toolName` | `void` | 4110 | 属性/连接写入 |
| `renderLayerEditorShowLayersMenu` | `string toolName, string menu` | `void` | 4125 | 属性/连接写入、UI/设置/回调 |
| `renderLayerEditorShowContributionMenu` | `string toolName, string menu` | `void` | 4168 | UI/设置/回调 |
| `renderLayerEditorShowOptionsMenu` | `string menu` | `void` | 4217 | UI/设置/回调 |
| `layerEditorCreateRenderLayer` | `int contents` | `void` | 4244 | 属性/连接写入、UI/设置/回调 |
| `renderLayerEditorCopyLayer` | `string toolName, string inLayer` | `void` | 4270 | UI/设置/回调 |
| `setRenderLayerCopyLayerMode` | `string parent` | `void` | 4302 | UI/设置/回调、选择 |
| `resetRenderLayerCopyLayerMode` | `string parent` | `void` | 4320 | UI/设置/回调、选择 |
| `renderLayerEditorCopyLayerOptions` | `string toolName` | `void` | 4331 | UI/设置/回调、选择 |
| `renderLayerEditorDeleteLayer` | `string toolName, string inLayer` | `void` | 4391 | 删除、属性/连接写入 |
| `renderLayerEditorSelectObjects` | `string toolName, string layer` | `void` | 4436 | 属性/连接写入、选择 |
| `renderLayerEditorRemoveObjects` | `string toolName, string inLayer` | `void` | 4455 | 属性/连接写入 |
| `renderLayerEditorEmptyLayer` | `string toolName, string inLayer` | `void` | 4474 | 属性/连接写入 |
| `renderLayerEditorAddObjects` | `string toolName, string inLayer` | `void` | 4491 | 属性/连接写入 |
| `renderLayerEditorDeleteUnused` | `string toolName` | `void` | 4513 | 属性/连接写入 |
| `renderLayerEditorLayerAttributes` | `string layer` | `void` | 4534 | 选择 |
| `renderLayerEditorMembership` | `string toolName, string layer` | `void` | 4554 | 未标记；仍须检查依赖过程 |
| `renderLayerEditorAlterObjectsInContMap` | `string toolName, string layer, string inMap, int addObjects` | `void` | 4565 | 未标记；仍须检查依赖过程 |
| `renderLayerEditorSelectObjectsInContMap` | `string toolName, string inMap` | `void` | 4611 | 选择 |
| `renderLayerEditorEmptyContMap` | `string map` | `void` | 4630 | 属性/连接写入 |
| `renderLayerEditorAssocContMap` | `string toolName, string[] layers, string map` | `void` | 4649 | 属性/连接写入 |
| `renderLayerEditorCreateContMap` | `string toolName, string inLayer, int withSelected` | `void` | 4666 | 未标记；仍须检查依赖过程 |
| `renderLayerEditorCopyContMap` | `string toolName, string inMap, string inLayer` | `void` | 4684 | 属性/连接写入 |
| `renderLayerEditorDeleteContMap` | `string toolName, string map` | `void` | 4711 | 删除 |
| `renderLayerEditorDeleteUnusedContMaps` | `string toolName` | `void` | 4746 | 未标记；仍须检查依赖过程 |
| `renderLayerEditorContMapMembership` | `string toolName, string map` | `void` | 4764 | 未标记；仍须检查依赖过程 |
| `renderLayerEditorContMapAttributes` | `string toolName, string map` | `void` | 4776 | 选择 |
| `renderLayerEditorCreateAndAssignPass` | `string layer, string map, string uiName, string presetPath` | `void` | 4796 | 属性/连接写入 |
| `updateEditorFeedbackRenderLayer` | `string toolName, string layer` | `void` | 4832 | UI/设置/回调 |
| `updateEditorRenderLayer` | `string toolName` | `void` | 4905 | UI/设置/回调 |
| `getSortedPassContributionMapList` | `string layer` | `string[]` | 5014 | 未标记；仍须检查依赖过程 |
| `renderLayerEditorFloatingWindow` | `无` | `void` | 5027 | UI/设置/回调 |
| `createRenderLayerEditor` | `string parentLayout, string toolName` | `void` | 5044 | UI/设置/回调 |
| `layerEditorBuildRenderLayerMenu` | `string parent, string toolName` | `void` | 5179 | UI/设置/回调 |
| `layerEditorBuildRenderContributionMenu` | `string parent, string toolName` | `void` | 5250 | UI/设置/回调 |
| `layerEditorBuildRenderOptionMenu` | `string parent, string toolName` | `void` | 5324 | UI/设置/回调 |
| `renderLayerEditorBuildPopupMenu` | `string toolName, string parentMenu, string item` | `int` | 5367 | 属性/连接写入、UI/设置/回调 |
| `setLayerToMenuItems` | `string parent, string layers` | `void` | 5614 | UI/设置/回调 |
| `layerEditorBuildDisplayLayerMenu` | `string parent` | `void` | 5723 | UI/设置/回调 |
| `layerEditorBuildDisplayOptionMenu` | `string parent` | `void` | 5822 | UI/设置/回调 |
| `getLayerSelection` | `string type` | `string[]` | 6125 | 选择 |
| `layerEditorNewScene` | `无` | `void` | 6273 | 未标记；仍须检查依赖过程 |
| `layerEditorOpenScene` | `无` | `void` | 6286 | 未标记；仍须检查依赖过程 |
| `layerEditorDisplayLayerChange` | `无` | `void` | 6301 | 未标记；仍须检查依赖过程 |
| `layerEditorDisplayLayerManagerChange` | `无` | `void` | 6313 | 选择 |
| `layerEditorLayerButtonSelect` | `int modifiers, string layerButton` | `void` | 6335 | 选择 |
| `layerEditorQuickEditWindowSave` | `string[] layerArray` | `void` | 6503 | 属性/连接写入、UI/设置/回调、选择 |
| `updateLayerEditorColorType` | `string objectColorType, string colorPalette, string rgbSlider` | `void` | 6679 | 选择 |
| `createLayerEditorQuickEditWindow` | `string[] layerArray` | `void` | 6686 | UI/设置/回调、选择 |
| `layerEditorLayerButtonRename` | `string oldName, string newName` | `void` | 6905 | UI/设置/回调 |
| `getDisplayLayerVisibility` | `string layer` | `int` | 6940 | 未标记；仍须检查依赖过程 |
| `getDisplayLayerHideOnPlayback` | `string layer` | `int` | 6962 | 未标记；仍须检查依赖过程 |
| `setDisplayLayerVisibility` | `string layer, int layerVisibility` | `void` | 6968 | 属性/连接写入 |
| `setDisplayLayerHideOnPlayback` | `string layer, int layerHideOnPlayback` | `void` | 6976 | 属性/连接写入 |
| `layerEditorLayerButtonVisibilityChange` | `string layer` | `void` | 6984 | 未标记；仍须检查依赖过程 |
| `layerEditorLayerButtonHidePlaybackChange` | `string layer` | `void` | 7000 | 未标记；仍须检查依赖过程 |
| `layerEditorLayerButtonTypeChange` | `string layer` | `void` | 7016 | 属性/连接写入 |
| `layerEditorLayerButtonDrag` | `string dragControl, int x, int y, int mods` | `string[]` | 7040 | 未标记；仍须检查依赖过程 |
| `layerEditorLayerButtonDrop` | `string dragControl, string dropControl, string[] messages, int x, int y, int dragType` | `void` | 7067 | 未标记；仍须检查依赖过程 |
| `layerEditorShowEditMenu` | `string menu` | `void` | 7120 | 属性/连接写入、UI/设置/回调 |
| `layerEditorShowOptionsMenu` | `string menu` | `void` | 7234 | UI/设置/回调 |
| `layerEditorShowPopupMenu` | `string menu, string layerButton` | `void` | 7264 | 删除、属性/连接写入、UI/设置/回调 |
| `layerEditorCreateLayer` | `int contents` | `void` | 7375 | UI/设置/回调、选择 |
| `layerEditorDeleteLayer` | `string inLayer` | `void` | 7440 | 删除、属性/连接写入 |
| `layerEditorEditLayer` | `string layer` | `void` | 7497 | UI/设置/回调 |
| `layerEditorSelectObjects` | `string layer` | `void` | 7524 | 属性/连接写入、选择 |
| `layerEditorAddObjects` | `string inLayer` | `void` | 7571 | 属性/连接写入 |
| `layerEditorRemoveObjects` | `string inLayer` | `void` | 7610 | 属性/连接写入 |
| `layerEditorEmpty` | `string inLayer` | `void` | 7640 | 属性/连接写入 |
| `layerEditorSelectUnused` | `无` | `void` | 7682 | 属性/连接写入、选择 |
| `layerEditorRemoveFromLayer` | `无` | `void` | 7753 | 属性/连接写入 |
| `layerEditorLayerAttributes` | `string layer` | `void` | 7789 | 选择 |
| `layerEditorMembership` | `string layer` | `void` | 7818 | 未标记；仍须检查依赖过程 |
| `layerEditorDisplayTypeChange` | `无` | `void` | 7851 | 未标记；仍须检查依赖过程 |
| `layerEditorMoveDisplayLayer` | `int up` | `void` | 7884 | 属性/连接写入 |
| `displayLabel` | `int showNamespace, string layer` | `string` | 7915 | 未标记；仍须检查依赖过程 |
| `updateLayersByType` | `string type` | `void` | 7935 | 删除、UI/设置/回调、选择 |
| `updateLayerOrderByType` | `string type` | `void` | 8087 | 属性/连接写入 |
| `updateLayerEditor` | `无` | `void` | 8163 | 未标记；仍须检查依赖过程 |
| `layerEditorVisibilityStateChange` | `int newState, string layout` | `int` | 8176 | 未标记；仍须检查依赖过程 |

## no_ui

| 过程 | parameters | 返回 | 原文件行 | 直接文本中出现的影响 |
| --- | --- | --- | --- | --- |
| `create_and_select_anim_layer` | `int rotation_mod` | `string` | 1 | 属性/连接写入 |
| `extract_anim_on_base_layer_selected_object` | `无` | `int` | 9 | 选择 |
| `extract_part_to_over_layer` | `float side_frames` | `string` | 63 | 动画写入、选择 |
| `selectLayer` | `string layer` | `void` | 111 | 未标记；仍须检查依赖过程 |
| `select_few_Layers` | `string[] layers` | `void` | 120 | 未标记；仍须检查依赖过程 |
| `select_object_in_selected_layers` | `无` | `void` | 129 | 未标记；仍须检查依赖过程 |
| `select_best_layer` | `无` | `string[]` | 135 | 未标记；仍须检查依赖过程 |
| `animLayerMerge_toAdditive` | `string[] layers, float[] timerange` | `string` | 148 | 删除、动画写入、属性/连接写入、选择 |
| `extract_animation_to_additive_layer` | `无` | `string[]` | 198 | 动画写入、选择 |
| `anim_layer_fast_merge` | `无` | `void` | 263 | 删除、选择 |
| `getLayerDisplayType` | `无` | `string` | 273 | 未标记；仍须检查依赖过程 |
| `get_anim_time_range_from_anim_layer` | `string anim_layer_name` | `float[]` | 289 | 未标记；仍须检查依赖过程 |
| `get_anim_time_range_from_multiply_anim_layers` | `string[] anim_layers_name` | `float[]` | 309 | 未标记；仍须检查依赖过程 |
| `create_add_anim_layer_from_objects_and_set_framerange_from_multiply_anim_layers` | `string[] objects, int mod` | `string` | 333 | 动画写入、选择 |
| `create_add_anim_layer_from_timerange` | `string[] objects, int mod` | `string` | 353 | 动画写入 |
| `create_anim_layer_from_channelbox_attrib` | `int mode` | `string[]` | 361 | 属性/连接写入 |
| `extract_smart_anim_on_base_layer_selected_object` | `int fidelity, float tolerance` | `void` | 381 | 选择 |
| `anim_layer_smart_fast_merge` | `int fidelity, float tolerance` | `void` | 411 | 删除、选择 |
| `execute_smart_fast_merge` | `int fidelity, float tolerance` | `void` | 421 | 选择 |
| `execute_fast_merge` | `无` | `void` | 430 | 选择 |
| `execute_smart_fast_selected_merge` | `int fidelity, float tolerance` | `void` | 439 | 选择 |
| `execute_fast_selected_merge` | `无` | `void` | 448 | 选择 |
| `extract_to_additive_layer` | `无` | `void` | 457 | 未标记；仍须检查依赖过程 |
| `anim_layer_util_menue` | `无` | `void` | 463 | 动画写入、UI/设置/回调、选择 |
| `get_min_max_from_selected` | `无` | `float[]` | 518 | 未标记；仍须检查依赖过程 |
| `get_time_range_from_selected_keys_or_timeslider` | `无` | `float[]` | 529 | 未标记；仍须检查依赖过程 |
| `disable_viewport` | `无` | `void` | 544 | 运行状态 |
| `enable_viewport` | `无` | `void` | 559 | 运行状态 |
| `bake_simulation_timerange_on_over_layer` | `float[] timerange` | `string` | 574 | 动画写入、运行状态、选择 |
| `bake_smart_simulation_playback_range` | `int fidelity, float tolerance` | `void` | 601 | 动画写入、运行状态、选择 |
| `bake_simulation_playback_range` | `无` | `void` | 629 | 动画写入、运行状态、选择 |
| `euler_filter_on_selected` | `无` | `void` | 653 | 动画写入、选择 |
| `select_skip_no_exist` | `string[] objs` | `string[]` | 671 | 选择 |

