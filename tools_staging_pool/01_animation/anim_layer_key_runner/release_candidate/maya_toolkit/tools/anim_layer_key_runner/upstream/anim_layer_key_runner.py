# -*- coding: utf-8 -*-
"""
Anim Layer Keyframe Command Runner (动画层逐关键帧命令执行器)
============================================================
智能检索当前选中的物体/控制器在指定动画层（或当前高亮激活层）上的专属关键帧，
并在每个关键帧处批量跳转并执行自定义 MEL 或 Python 命令。

典型应用场景：
- Advanced Skeleton: 在动画层的所有关键帧处批量执行 `asAutoSwitchFKIK` 进行无缝切换匹配；
- 姿态烘焙/匹配: 仅针对动画层上打 key 的姿态逐帧触发对齐或吸附脚本；
- 批量处理: 仅针对动画层关键帧进行属性清洗、打标记或特定通道更新。

支持特性：
- 智能识别动画层：自动检测当前在 Maya 动画层面板中高亮的层、BaseAnimation 或全部层合并；
- 关键帧高精度检索：去重、时间排序，支持浮点数子帧容差判定；
- 范围筛选：支持仅限播放时间范围 (Playback Range) 或全局关键帧；
- 双引擎执行：无缝执行 MEL 命令/过程或 Python 表达式/函数；
- 安全与撤销：内置原子级 Maya UndoChunk (Ctrl+Z 一键撤销整个批量执行操作)；
- 独立交互式 UI 界面 + 无界面直接调用 API。
"""

from __future__ import absolute_import, division, print_function

import sys
import maya.cmds as cmds
import maya.mel as mel

# 预置常用命令
PRESET_COMMANDS = [
    {
        "name": "asAutoSwitchFKIK (Advanced Skeleton FK/IK自动匹配切换)",
        "cmd": "asAutoSwitchFKIK",
        "lang": "mel",
    },
    {
        "name": "setKeyframe (在当前选区打关键帧)",
        "cmd": "setKeyframe",
        "lang": "mel",
    },
    {
        "name": "delete -attribute (清除多余关键帧属性)",
        "cmd": "",
        "lang": "mel",
    },
]


# ==============================================================================
# 动画层与关键帧检索核心逻辑
# ==============================================================================

def get_scene_anim_layers():
    """获取当前场景中所有的动画层列表（按层级堆叠顺序）"""
    layers = cmds.ls(type="animLayer") or []
    valid_layers = [l for l in layers if cmds.objExists(l)]
    if "BaseAnimation" in valid_layers:
        valid_layers.remove("BaseAnimation")
        valid_layers.insert(0, "BaseAnimation")
    return valid_layers


def get_active_anim_layer():
    """
    自动检测当前在 Maya 动画层面板中激活/选中的层。
    优先从 UI 树形控件查询；若未打开面板则从 animLayer 节点属性查询。
    若未选中则默认回退至 'BaseAnimation'。
    """
    # 1. 从动画层编辑器界面查询
    if cmds.treeView("AnimLayerTabanimLayerEditor", exists=True):
        ui_selected = cmds.treeView("AnimLayerTabanimLayerEditor", query=True, selectItem=True) or []
        if ui_selected and cmds.objExists(ui_selected[0]):
            return ui_selected[0]

    # 2. 从节点属性查询
    layers = cmds.ls(type="animLayer") or []
    selected = [l for l in layers if cmds.animLayer(l, query=True, selected=True)]
    custom_selected = [l for l in selected if l != "BaseAnimation"]
    if custom_selected:
        return custom_selected[0]
    if "BaseAnimation" in selected:
        return "BaseAnimation"
    return "BaseAnimation"


def _filter_curves_by_objects(curves, objects):
    """通过历史依赖下游连接，筛选出驱动目标 objects 的动画曲线"""
    obj_set = set(objects)
    matched = []
    for curve in curves:
        future_history = cmds.listHistory(curve, future=True) or []
        if any(o in obj_set for o in future_history):
            matched.append(curve)
    return matched


def get_layer_curves_for_objects(objects, layer_name):
    """
    获取指定对象在特定动画层上关联的所有动画曲线。
    结合了 `findCurveForPlug` 与下游历史拓扑双重校验，保证 100% 捕获。
    """
    if not objects or not layer_name:
        return []

    collected_curves = set()

    # 方式 A：通过 animLayer -findCurveForPlug 针对可动画属性查询
    for obj in objects:
        anim_plugs = cmds.listAnimatable(obj) or []
        for plug in anim_plugs:
            try:
                curves = cmds.animLayer(layer_name, query=True, findCurveForPlug=plug) or []
                for c in curves:
                    if c and cmds.objExists(c):
                        collected_curves.add(c)
            except Exception:
                pass

    # 方式 B：若层本身有曲线，辅以下游拓扑匹配补漏
    try:
        layer_all_curves = cmds.animLayer(layer_name, query=True, animCurves=True) or []
        if layer_all_curves:
            matched = _filter_curves_by_objects(layer_all_curves, objects)
            for m in matched:
                collected_curves.add(m)
    except Exception:
        pass

    return list(collected_curves)


def get_keyframes_from_layer(objects, layer="auto", only_in_playback=True):
    """
    检索指定对象在特定动画层上的所有关键帧时间戳（去重升序排列）。

    参数:
        objects (list[str]): 目标对象/控制器名称列表。
        layer (str): 目标层名称。
            - "auto": 自动检测当前高亮的动画层。
            - "BaseAnimation": 基础层。
            - "All": 所有动画层及基础层的关键帧合集。
            - 具体层名 (如 "Layer_Arm"): 仅该层关键帧。
        only_in_playback (bool): 是否仅限制在播放范围 (Time Slider) 内。

    返回:
        tuple[list[float], str]: (关键帧列表, 实际解析出的动画层名称)
    """
    if not objects:
        return [], ""

    if isinstance(objects, (str, bytes)):
        objects = [objects]

    # 解析目标层
    if not layer or layer == "auto":
        target_layer = get_active_anim_layer()
    else:
        target_layer = layer

    # 确定时间范围参数
    time_arg = None
    if only_in_playback:
        min_t = cmds.playbackOptions(query=True, minTime=True)
        max_t = cmds.playbackOptions(query=True, maxTime=True)
        time_arg = (min_t, max_t)

    all_keyframes = set()

    def _query_keys_from_curves(curves):
        if not curves:
            return []
        kwargs = {"query": True, "timeChange": True}
        if time_arg is not None:
            kwargs["time"] = time_arg
        return cmds.keyframe(curves, **kwargs) or []

    # 场景一：全部层合并
    if target_layer == "All":
        # 1. Base 关键帧
        kwargs = {"query": True, "timeChange": True}
        if time_arg is not None:
            kwargs["time"] = time_arg
        base_keys = cmds.keyframe(objects, **kwargs) or []
        for k in base_keys:
            all_keyframes.add(round(float(k), 4))

        # 2. 各自定义层关键帧
        for l in get_scene_anim_layers():
            if l == "BaseAnimation":
                continue
            curves = get_layer_curves_for_objects(objects, l)
            for k in _query_keys_from_curves(curves):
                all_keyframes.add(round(float(k), 4))

    # 场景二：BaseAnimation 基础层
    elif target_layer == "BaseAnimation":
        curves = get_layer_curves_for_objects(objects, "BaseAnimation")
        if curves:
            keys = _query_keys_from_curves(curves)
        else:
            kwargs = {"query": True, "timeChange": True}
            if time_arg is not None:
                kwargs["time"] = time_arg
            keys = cmds.keyframe(objects, **kwargs) or []
        for k in keys:
            all_keyframes.add(round(float(k), 4))

    # 场景三：特定自定义层
    else:
        if not cmds.objExists(target_layer) or cmds.nodeType(target_layer) != "animLayer":
            cmds.warning(u"指定的动画层不存在: {}".format(target_layer))
            return [], target_layer

        curves = get_layer_curves_for_objects(objects, target_layer)
        for k in _query_keys_from_curves(curves):
            all_keyframes.add(round(float(k), 4))

    # 排序与去重
    sorted_keys = sorted(list(all_keyframes))
    unique_keys = []
    for k in sorted_keys:
        if not unique_keys or abs(k - unique_keys[-1]) > 0.001:
            unique_keys.append(k)

    return unique_keys, target_layer


# ==============================================================================
# 批量执行入口与调度
# ==============================================================================

def run_command_on_keyframes(
    objects=None,
    command="asAutoSwitchFKIK",
    layer="auto",
    language="mel",
    only_in_playback=True,
    dry_run=False,
):
    """
    在指定动画层的每个关键帧上逐帧执行指定命令。

    参数:
        objects (list[str]|None): 目标对象列表。若为 None 则使用当前选中的对象。
        command (str): 要执行的 MEL 或 Python 命令。
        layer (str): 目标动画层。'auto', 'BaseAnimation', 'All', 或指定层名。
        language (str): 'mel' 或 'python'。
        only_in_playback (bool): 是否仅限制在播放范围。
        dry_run (bool): 预检模式。为 True 时不执行命令，仅返回解析到的关键帧列表。

    返回:
        dict: 执行结果概报。包含 success, layer, frames, count, message 等。
    """
    if objects is None:
        objects = cmds.ls(selection=True) or []

    if not objects:
        msg = u"执行终止：请先选中需要处理的控制器或物体！"
        cmds.warning(msg)
        return {"success": False, "message": msg, "frames": [], "count": 0}

    command = (command or "").strip()
    if not command and not dry_run:
        msg = u"执行终止：命令内容为空！请输入有效的 MEL 或 Python 命令。"
        cmds.warning(msg)
        return {"success": False, "message": msg, "frames": [], "count": 0}

    # 获取关键帧
    frames, resolved_layer = get_keyframes_from_layer(
        objects=objects,
        layer=layer,
        only_in_playback=only_in_playback,
    )

    if not frames:
        msg = u"未在动画层 [{}] 上检测到选中物体的有效关键帧。".format(resolved_layer)
        cmds.warning(msg)
        return {
            "success": True,
            "layer": resolved_layer,
            "frames": [],
            "count": 0,
            "message": msg,
        }

    if dry_run:
        msg = u"[预检就绪] 动画层 [{}] 共包含 {} 个关键帧: {}".format(
            resolved_layer, len(frames), frames
        )
        print(msg)
        return {
            "success": True,
            "layer": resolved_layer,
            "frames": frames,
            "count": len(frames),
            "message": msg,
        }

    # 记录原始帧
    original_frame = cmds.currentTime(query=True)

    # 开启安全撤销块
    cmds.undoInfo(openChunk=True, chunkName="AnimLayerKeyRunner")
    success_count = 0
    errors = []

    try:
        print(u"// ===================================================")
        print(u"// 开始在动画层 [{}] 执行批量命令...".format(resolved_layer))
        print(u"// 待处理关键帧总数: {}".format(len(frames)))
        print(u"// 执行语言: {}, 命令: {}".format(language.upper(), command))
        print(u"// ===================================================")

        for f in frames:
            cmds.currentTime(f, edit=True)
            cmds.select(objects, replace=True)

            try:
                if language.lower() == "python":
                    exec(command, globals(), locals())
                else:
                    mel.eval(command)
                success_count += 1
            except Exception as err:
                err_msg = u"帧 {} 执行出错: {}".format(f, err)
                errors.append(err_msg)
                cmds.warning(err_msg)

    finally:
        # 关闭撤销块
        cmds.undoInfo(closeChunk=True)
        # 恢复选择
        if cmds.objExists(objects[0]):
            cmds.select(objects, replace=True)

    summary_msg = u"执行完成！已在动画层 [{}] 的 {}/{} 个关键帧上成功执行。".format(
        resolved_layer, success_count, len(frames)
    )
    print(summary_msg)

    return {
        "success": len(errors) == 0,
        "layer": resolved_layer,
        "frames": frames,
        "count": success_count,
        "total": len(frames),
        "errors": errors,
        "message": summary_msg,
    }


# ==============================================================================
# 原生 Maya GUI 界面
# ==============================================================================

class AnimLayerKeyRunnerUI(object):
    """动画层逐关键帧命令执行器主窗口"""

    WINDOW_NAME = "AnimLayerKeyRunnerUIWindow"

    def __init__(self):
        self.layer_option_menu = None
        self.cmd_field = None
        self.lang_radio_collection = None
        self.mel_radio = None
        self.py_radio = None
        self.range_checkbox = None
        self.info_text = None

    def show(self):
        """打开或刷新主窗口"""
        if cmds.window(self.WINDOW_NAME, exists=True):
            cmds.deleteUI(self.WINDOW_NAME)

        window = cmds.window(
            self.WINDOW_NAME,
            title="动画层逐关键帧命令执行器 (Anim Layer Key Runner)",
            widthHeight=(460, 420),
            sizeable=False,
        )

        main_layout = cmds.columnLayout(
            adjustableColumn=True,
            rowSpacing=8,
            columnOffset=("both", 12),
        )

        # 顶部标题栏
        cmds.separator(height=6, style="none")
        cmds.text(
            label="⚡ 动画层逐关键帧批量命令执行器",
            font="boldLabelFont",
            align="center",
            height=26,
        )
        cmds.text(
            label="智能定位选中物体在指定动画层的关键帧，逐帧跳转并批量触发 MEL / Python 命令",
            align="center",
            font="smallPlainLabelFont",
        )
        cmds.separator(height=8, style="in")

        # 1. 动画层设置区
        layer_frame = cmds.frameLayout(
            label=" 1. 目标动画层 (Animation Layer) ",
            marginHeight=8,
            marginWidth=8,
            collapsable=False,
        )
        cmds.rowLayout(
            numberOfColumns=3,
            columnWidth3=(90, 240, 80),
            adjustableColumn=2,
        )
        cmds.text(label="选择层级: ", align="right")
        self.layer_option_menu = cmds.optionMenu(changeCommand=self._on_layer_changed)
        cmds.button(label="🔄 刷新层", command=lambda *_: self.refresh_layers(), height=22)
        cmds.setParent("..")
        cmds.setParent("..")  # frameLayout

        # 2. 执行命令与语言设置区
        cmd_frame = cmds.frameLayout(
            label=" 2. 待执行命令与配置 (Command & Engine) ",
            marginHeight=8,
            marginWidth=8,
            collapsable=False,
        )
        
        # 预设命令快速填充
        cmds.rowLayout(
            numberOfColumns=2,
            columnWidth2=(90, 320),
            adjustableColumn=2,
        )
        cmds.text(label="快捷预设: ", align="right")
        preset_menu = cmds.optionMenu(changeCommand=self._on_preset_selected)
        cmds.menuItem(label="-- 自定义输入 --")
        for p in PRESET_COMMANDS:
            cmds.menuItem(label=p["name"])
        cmds.setParent("..")

        cmds.separator(height=4, style="none")

        # 命令输入框
        cmds.rowLayout(
            numberOfColumns=2,
            columnWidth2=(90, 320),
            adjustableColumn=2,
        )
        cmds.text(label="执行命令: ", align="right")
        self.cmd_field = cmds.textField(text="asAutoSwitchFKIK")
        cmds.setParent("..")

        cmds.separator(height=4, style="none")

        # 语言选择 (MEL / Python)
        cmds.rowLayout(
            numberOfColumns=3,
            columnWidth3=(90, 100, 100),
        )
        cmds.text(label="脚本语言: ", align="right")
        self.lang_radio_collection = cmds.radioCollection()
        self.mel_radio = cmds.radioButton(label="MEL", select=True)
        self.py_radio = cmds.radioButton(label="Python")
        cmds.setParent("..")

        cmds.separator(height=4, style="none")

        # 范围筛选
        cmds.rowLayout(
            numberOfColumns=2,
            columnWidth2=(90, 320),
            adjustableColumn=2,
        )
        cmds.text(label="", align="right")
        self.range_checkbox = cmds.checkBox(
            label="仅处理时间轴播放范围 (Playback Range) 内的关键帧",
            value=True,
        )
        cmds.setParent("..")
        cmds.setParent("..")  # frameLayout

        # 3. 底部操作按钮
        cmds.separator(height=6, style="none")
        cmds.button(
            label="🚀 一键逐关键帧执行 (Run On Keyframes)",
            backgroundColor=(0.20, 0.55, 0.85),
            height=38,
            command=self._on_execute,
        )

        cmds.rowLayout(numberOfColumns=2, columnWidth2=(220, 210))
        cmds.button(
            label="🔍 预检关键帧数量 (Dry Run)",
            backgroundColor=(0.35, 0.40, 0.45),
            height=26,
            command=self._on_inspect,
        )
        cmds.button(
            label="📋 查看日志 (Script Editor)",
            backgroundColor=(0.30, 0.30, 0.32),
            height=26,
            command=lambda *_: mel.eval("ScriptEditor;"),
        )
        cmds.setParent("..")

        # 4. 状态提示栏
        cmds.separator(height=8, style="in")
        self.info_text = cmds.text(
            label="就绪：选中控制器后点击【一键逐关键帧执行】即可。",
            align="left",
            font="obliqueLabelFont",
        )
        cmds.separator(height=4, style="none")

        self.refresh_layers()
        cmds.showWindow(window)

    def refresh_layers(self):
        """刷新层级下拉列表并自动定位至当前高亮层"""
        existing_items = cmds.optionMenu(self.layer_option_menu, query=True, itemListLong=True) or []
        for item in existing_items:
            cmds.deleteUI(item)

        cmds.menuItem(label="[自动识别当前高亮层]", parent=self.layer_option_menu)
        cmds.menuItem(label="[所有动画层合并 (All)]", parent=self.layer_option_menu)

        scene_layers = get_scene_anim_layers()
        for l in scene_layers:
            cmds.menuItem(label=l, parent=self.layer_option_menu)

        # 默认选中第一项（自动识别）
        cmds.optionMenu(self.layer_option_menu, edit=True, select=1)

    def _on_layer_changed(self, selected_item):
        pass

    def _on_preset_selected(self, selected_label):
        for p in PRESET_COMMANDS:
            if p["name"] == selected_label:
                cmds.textField(self.cmd_field, edit=True, text=p["cmd"])
                if p["lang"] == "python":
                    cmds.radioButton(self.py_radio, edit=True, select=True)
                else:
                    cmds.radioButton(self.mel_radio, edit=True, select=True)
                break

    def _get_ui_layer_target(self):
        selected_label = cmds.optionMenu(self.layer_option_menu, query=True, value=True)
        if not selected_label or selected_label.startswith("[自动识别"):
            return "auto"
        if selected_label.startswith("[所有动画层"):
            return "All"
        return selected_label

    def _on_inspect(self, *_):
        objects = cmds.ls(selection=True) or []
        if not objects:
            cmds.confirmDialog(
                title="提示",
                message="请先在场景中选中需要检查的控制器或物体！",
                button=["好的"],
            )
            return

        layer_target = self._get_ui_layer_target()
        only_playback = cmds.checkBox(self.range_checkbox, query=True, value=True)

        res = run_command_on_keyframes(
            objects=objects,
            command="",
            layer=layer_target,
            only_in_playback=only_playback,
            dry_run=True,
        )

        cmds.text(
            self.info_text,
            edit=True,
            label=u"预检：检测到动画层 [{}] 包含 {} 个关键帧。".format(
                res["layer"], res["count"]
            ),
        )
        cmds.confirmDialog(
            title="关键帧预检结果",
            message=u"动画层: [{}]\n有效关键帧数: {} 帧\n\n关键帧时间列表:\n{}".format(
                res["layer"], res["count"], res["frames"]
            ),
            button=["确定"],
        )

    def _on_execute(self, *_):
        objects = cmds.ls(selection=True) or []
        if not objects:
            cmds.confirmDialog(
                title="提示",
                message="请先在场景中选中需要处理的控制器或物体！",
                button=["好的"],
            )
            return

        cmd = cmds.textField(self.cmd_field, query=True, text=True)
        is_python = cmds.radioButton(self.py_radio, query=True, select=True)
        lang = "python" if is_python else "mel"
        layer_target = self._get_ui_layer_target()
        only_playback = cmds.checkBox(self.range_checkbox, query=True, value=True)

        cmds.text(self.info_text, edit=True, label="正在逐关键帧执行中，请稍候...")
        cmds.refresh()

        result = run_command_on_keyframes(
            objects=objects,
            command=cmd,
            layer=layer_target,
            language=lang,
            only_in_playback=only_playback,
            dry_run=False,
        )

        if result["success"]:
            cmds.text(
                self.info_text,
                edit=True,
                label=u"完成：已在动画层 [{}] 的 {} 帧上执行完毕！".format(
                    result["layer"], result["count"]
                ),
            )
        else:
            cmds.text(
                self.info_text,
                edit=True,
                label=u"执行提示：{}".format(result["message"]),
            )


# ==============================================================================
# 模块快捷启动函数
# ==============================================================================

_RUNNER_UI_INSTANCE = None


def show_ui():
    """打开动画层逐关键帧命令执行器图形界面"""
    global _RUNNER_UI_INSTANCE
    if _RUNNER_UI_INSTANCE is None:
        _RUNNER_UI_INSTANCE = AnimLayerKeyRunnerUI()
    _RUNNER_UI_INSTANCE.show()
    return _RUNNER_UI_INSTANCE


if __name__ == "__main__":
    show_ui()
