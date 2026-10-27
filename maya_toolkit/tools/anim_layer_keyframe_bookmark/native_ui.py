import maya.cmds as cmds
from .palettes import COLOR_PALETTES
from .layer_queries import get_scene_anim_layers, get_active_anim_layer

class AnimLayerBookmarkUI(object):
    """动画层关键帧书签生成器图形界面"""

    WINDOW_NAME = "AnimLayerBookmarkWindow"

    def __init__(self):
        self.layer_option_menu = None
        self.palette_option_menu = None
        self.prefix_field = None
        self.clear_checkbox = None
        self.info_text = None

    def show(self):
        """打开界面，若已存在则激活并刷新"""
        if cmds.window(self.WINDOW_NAME, exists=True):
            cmds.deleteUI(self.WINDOW_NAME)

        window = cmds.window(
            self.WINDOW_NAME,
            title="动画层关键帧书签生成器 (Keyframe Bookmarks)",
            widthHeight=(420, 360),
            sizeable=False,
        )

        main_layout = cmds.columnLayout(adjustableColumn=True, rowSpacing=10, columnOffset=("both", 12))

        # 顶部标题横幅
        cmds.separator(height=6, style="none")
        cmds.text(label="🎬 动画层关键帧区间书签工具", font="boldLabelFont", align="center", height=26)
        cmds.text(
            label="根据当前选中物体的关键帧自动创建相邻颜色交替的时间滑块书签",
            align="center",
            font="smallPlainLabelFont",
        )
        cmds.separator(height=10, style="in")

        # 动画层选择区
        layer_frame = cmds.frameLayout(label=" 1. 动画层设置 (Animation Layer) ", marginHeight=8, marginWidth=8)
        cmds.rowLayout(numberOfColumns=3, columnWidth3=(90, 210, 80), adjustableColumn=2)
        cmds.text(label="选择层级: ", align="right")
        self.layer_option_menu = cmds.optionMenu(changeCommand=self._on_layer_changed)
        cmds.button(label="🔄 刷新", command=lambda *_: self.refresh_layers(), height=22)
        cmds.setParent("..")  # rowLayout
        cmds.setParent("..")  # frameLayout

        # 书签与颜色配置区
        config_frame = cmds.frameLayout(label=" 2. 颜色与命名配置 (Appearance) ", marginHeight=8, marginWidth=8)
        cmds.rowLayout(numberOfColumns=2, columnWidth2=(90, 280), adjustableColumn=2)
        cmds.text(label="色彩方案: ", align="right")
        self.palette_option_menu = cmds.optionMenu()
        for p_key, p_val in COLOR_PALETTES.items():
            cmds.menuItem(label=p_val["label"])
        cmds.setParent("..")

        cmds.separator(height=6, style="none")
        cmds.rowLayout(numberOfColumns=2, columnWidth2=(90, 280), adjustableColumn=2)
        cmds.text(label="命名前缀: ", align="right")
        self.prefix_field = cmds.textField(text="BM")
        cmds.setParent("..")

        cmds.separator(height=6, style="none")
        cmds.rowLayout(numberOfColumns=2, columnWidth2=(90, 280), adjustableColumn=2)
        cmds.text(label="", align="right")
        self.clear_checkbox = cmds.checkBox(label="生成前清空场景中所有已有书签", value=True)
        cmds.setParent("..")
        cmds.setParent("..")  # frameLayout

        # 执行按钮区
        cmds.separator(height=6, style="none")
        cmds.button(
            label="✨ 一键生成区间书签 (Generate Bookmarks)",
            backgroundColor=(0.22, 0.55, 0.85),
            height=38,
            command=self._on_execute,
        )

        cmds.rowLayout(numberOfColumns=2, columnWidth2=(200, 190))
        cmds.button(
            label="🧹 清空所有书签",
            backgroundColor=(0.45, 0.35, 0.35),
            height=26,
            command=self._on_clear_all,
        )
        cmds.button(
            label="🔍 检查当前关键帧",
            backgroundColor=(0.35, 0.40, 0.45),
            height=26,
            command=self._on_inspect_keys,
        )
        cmds.setParent("..")

        # 状态提示区
        cmds.separator(height=8, style="in")
        self.info_text = cmds.text(label="就绪：请选择物体后点击生成按钮。", align="left", font="obliqueLabelFont")
        cmds.separator(height=4, style="none")

        self.refresh_layers()
        cmds.showWindow(window)

    def refresh_layers(self):
        """刷新层级下拉列表并自动定位至当前激活层"""
        # 清空已有选项
        existing_items = cmds.optionMenu(self.layer_option_menu, query=True, itemListLong=True) or []
        for item in existing_items:
            cmds.deleteUI(item)

        # 添加固定快捷项
        cmds.menuItem(label="[自动识别当前高亮层]", parent=self.layer_option_menu)
        cmds.menuItem(label="[所有动画层合并 (All)]", parent=self.layer_option_menu)

        scene_layers = get_scene_anim_layers()
        for l in scene_layers:
            cmds.menuItem(label=l, parent=self.layer_option_menu)

        # 默认选中自动识别项
        cmds.optionMenu(self.layer_option_menu, edit=True, select=1)
        active = get_active_anim_layer()
        self._set_status(u"动画层已刷新。当前激活层为: {}".format(active))

    def _get_selected_layer_mode(self):
        """根据界面下拉框返回对应的层级模式"""
        label = cmds.optionMenu(self.layer_option_menu, query=True, value=True)
        if label == "[自动识别当前高亮层]":
            return "auto"
        elif label == "[所有动画层合并 (All)]":
            return "All"
        return label

    def _get_selected_palette_key(self):
        """获取当前选择的调色板 key"""
        idx = cmds.optionMenu(self.palette_option_menu, query=True, select=True) - 1
        keys = list(COLOR_PALETTES.keys())
        if 0 <= idx < len(keys):
            return keys[idx]
        return "dual"

    def _on_layer_changed(self, value):
        self._set_status(u"目标层已切换为: {}".format(value))

    def _on_inspect_keys(self, *_):
        """快速检查选中物体的关键帧"""
        objs = cmds.ls(sl=True) or []
        if not objs:
            self._set_status(u"⚠️ 提示: 请先在场景中选择物体！")
            return
        layer_mode = self._get_selected_layer_mode()
        keys = get_keyframes_from_objects(objs, layer=layer_mode)
        self._set_status(u"选中 {} 个物体，在 [{}] 找到 {} 个关键帧: {}".format(
            len(objs), layer_mode, len(keys), [round(k, 1) for k in keys[:8]]
        ))

    def _on_clear_all(self, *_):
        """清空所有书签"""
        cnt = delete_all_bookmarks()
        self._set_status(u"已清空场景中全部 {} 个时间滑块书签。".format(cnt))

    def _on_execute(self, *_):
        """点击生成书签"""
        objs = cmds.ls(sl=True) or []
        if not objs:
            self._set_status(u"❌ 错误: 未选中任何物体，请先选择要处理的对象。")
            return

        layer_mode = self._get_selected_layer_mode()
        palette_key = self._get_selected_palette_key()
        prefix = cmds.textField(self.prefix_field, query=True, text=True) or "BM"
        clear_old = cmds.checkBox(self.clear_checkbox, query=True, value=True)

        res = generate_keyframe_bookmarks(
            objects=objs,
            layer=layer_mode,
            palette_name=palette_key,
            prefix=prefix,
            clear_existing=clear_old,
        )

        if res["success"]:
            self._set_status(u"✅ " + res["message"])
        else:
            self._set_status(u"⚠️ " + res["message"])

    def _set_status(self, text):
        if self.info_text and cmds.text(self.info_text, exists=True):
            cmds.text(self.info_text, edit=True, label=text)
        print("[AnimLayerBookmark] " + text)
