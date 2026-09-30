import maya.cmds as cmds
import maya.mel as mel
from .operations import get_scene_anim_layers

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
