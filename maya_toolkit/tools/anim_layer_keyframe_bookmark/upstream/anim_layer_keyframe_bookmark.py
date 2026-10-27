# -*- coding: utf-8 -*-
"""
Anim Layer Keyframe Bookmark Generator (动画层关键帧区间书签生成器)
================================================================
根据当前选中的物体及其所在的动画层级（AnimLayer），提取所有关键帧，
在相邻两两关键帧之间创建时间滑块书签（Time Slider Bookmark），
并应用高对比/交替色彩方案，确保相邻书签颜色互不相同。

支持：
- 自动检测 Maya 动画层面板当前激活/选中的层级
- 提取特定动画层或 BaseAnimation 基础层上的专属关键帧
- 多物体关键帧合并去重排序
- 4 组专业动画调色方案（双色交替、彩虹轮转、柔和粉彩、霓虹荧光）
- 完整的 Maya UndoChunk 安全撤销 (Ctrl+Z 一键撤销)
- 独立 API 函数接口与原生 Maya 交互式 UI
"""

import sys
import maya.cmds as cmds

# ==============================================================================
# 色彩预设库 (Normalized RGB: 0.0 ~ 1.0)
# ==============================================================================
COLOR_PALETTES = {
    "dual": {
        "label": "经典双色交替 (Dual High-Contrast)",
        "colors": [
            (0.18, 0.65, 0.92),  # 晴空蓝
            (0.95, 0.42, 0.35),  # 珊瑚红
        ],
    },
    "vibrant": {
        "label": "彩虹六色轮转 (Vibrant Rainbow)",
        "colors": [
            (0.20, 0.60, 0.95),  # 海蓝
            (0.95, 0.55, 0.20),  # 暖橙
            (0.25, 0.78, 0.45),  # 薄荷绿
            (0.88, 0.32, 0.72),  # 洋红
            (0.96, 0.78, 0.22),  # 琥珀金
            (0.58, 0.40, 0.88),  # 罗兰紫
        ],
    },
    "pastel": {
        "label": "马卡龙柔和色 (Pastel Soft)",
        "colors": [
            (0.52, 0.74, 0.90),  # 柔蓝
            (0.92, 0.64, 0.64),  # 浅粉
            (0.62, 0.82, 0.68),  # 柔绿
            (0.90, 0.82, 0.58),  # 奶油黄
            (0.75, 0.65, 0.85),  # 浅紫
        ],
    },
    "cyberpunk": {
        "label": "赛博霓虹 (Cyberpunk Neon)",
        "colors": [
            (0.00, 0.90, 0.85),  # 电光青
            (1.00, 0.15, 0.60),  # 荧光玫红
            (0.60, 0.10, 0.95),  # 紫外光
            (0.20, 1.00, 0.40),  # 荧光绿
        ],
    },
}


# ==============================================================================
# 核心底层接口与关键帧检索
# ==============================================================================
def ensure_bookmark_plugin():
    """确保 Maya 内置的 timeSliderBookmark 插件已加载"""
    if not cmds.pluginInfo("timeSliderBookmark", query=True, loaded=True):
        try:
            cmds.loadPlugin("timeSliderBookmark")
        except Exception as err:
            cmds.warning(u"加载 timeSliderBookmark 插件失败: {}".format(err))
            return False
    return True


def get_scene_anim_layers():
    """获取当前场景中所有的动画层列表（按显示次序排序）"""
    layers = cmds.ls(type="animLayer") or []
    # 过滤掉系统内部可能产生的无名或临时节点
    valid_layers = [l for l in layers if cmds.objExists(l)]
    # 将 BaseAnimation 放在首位
    if "BaseAnimation" in valid_layers:
        valid_layers.remove("BaseAnimation")
        valid_layers.insert(0, "BaseAnimation")
    return valid_layers


def get_active_anim_layer():
    """
    自动检测当前在 Maya 动画层面板中选中的层。
    若未选中任何层或仅选中 BaseAnimation，则返回 'BaseAnimation'。
    """
    layers = cmds.ls(type="animLayer") or []
    selected = [l for l in layers if cmds.animLayer(l, query=True, selected=True)]
    # 若有自定义选中的层（非 BaseAnimation），优先使用自定义层
    custom_selected = [l for l in selected if l != "BaseAnimation"]
    if custom_selected:
        return custom_selected[0]
    if "BaseAnimation" in selected:
        return "BaseAnimation"
    return "BaseAnimation"


def get_keyframes_from_objects(objects, layer=None):
    """
    检索指定对象在特定动画层上的所有关键帧时间戳。

    参数:
        objects (list[str]): 目标 DAG 节点/控制器列表。
        layer (str, optional): 动画层名称。
            - None 或 'auto': 自动检测当前高亮的动画层。
            - 'BaseAnimation': 仅获取基础动画层关键帧。
            - 'All': 获取所有动画层及基础层的关键帧合集。
            - 具体层名 (如 'Layer_Walk'): 仅获取该层曲线上的关键帧。

    返回:
        list[float]: 去重并升序排列的浮点数关键帧列表。
    """
    if not objects:
        return []

    # 规范化 objects，支持单个字符串传入
    if isinstance(objects, (str, bytes)):
        objects = [objects]

    # 自动识别层
    if not layer or layer == "auto":
        target_layer = get_active_anim_layer()
    else:
        target_layer = layer

    all_keyframes = set()

    # 情况 A: 获取所有动画层的关键帧并集
    if target_layer == "All":
        # 1. 提取 Base 关键帧
        base_keys = cmds.keyframe(objects, query=True, timeChange=True) or []
        for k in base_keys:
            all_keyframes.add(round(float(k), 4))

        # 2. 遍历所有非 Base 层的专属曲线
        all_layers = get_scene_anim_layers()
        for l in all_layers:
            if l == "BaseAnimation":
                continue
            layer_curves = cmds.animLayer(l, query=True, animCurves=True) or []
            if not layer_curves:
                continue
            # 过滤属于 target objects 的曲线
            target_curves = _filter_curves_by_objects(layer_curves, objects)
            if target_curves:
                l_keys = cmds.keyframe(target_curves, query=True, timeChange=True) or []
                for k in l_keys:
                    all_keyframes.add(round(float(k), 4))

    # 情况 B: 仅获取基础动画层 BaseAnimation
    elif target_layer == "BaseAnimation":
        keys = cmds.keyframe(objects, query=True, timeChange=True) or []
        for k in keys:
            all_keyframes.add(round(float(k), 4))

    # 情况 C: 获取特定自定义动画层
    else:
        if not cmds.objExists(target_layer) or cmds.nodeType(target_layer) != "animLayer":
            cmds.warning(u"指定的动画层不存在: {}".format(target_layer))
            return []

        layer_curves = cmds.animLayer(target_layer, query=True, animCurves=True) or []
        if layer_curves:
            target_curves = _filter_curves_by_objects(layer_curves, objects)
            if target_curves:
                l_keys = cmds.keyframe(target_curves, query=True, timeChange=True) or []
                for k in l_keys:
                    all_keyframes.add(round(float(k), 4))

    return sorted(list(all_keyframes))


def _filter_curves_by_objects(curves, objects):
    """通过历史依赖下游连接，筛选出驱动目标 objects 的动画曲线"""
    obj_set = set(objects)
    matched_curves = []
    for curve in curves:
        # 查询 curve 的未来影响历史链路
        future_history = cmds.listHistory(curve, future=True) or []
        if any(obj in obj_set for obj in future_history):
            matched_curves.append(curve)
    return matched_curves


# ==============================================================================
# 书签创建与管理
# ==============================================================================
def create_time_slider_bookmark(name, start, stop, color=None, priority=0):
    """
    底层快速创建单个 timeSliderBookmark 节点（避免触发冗余的时间滑块指针跳跃）。

    参数:
        name (str): 书签显示名称。
        start (float): 起始帧。
        stop (float): 结束帧。
        color (tuple[float, float, float]): RGB 0~1 色值。
        priority (int): 优先级（默认 0）。

    返回:
        str: 创建成功的 bookmark 节点名称。
    """
    ensure_bookmark_plugin()
    cmds.pluginInfo("timeSliderBookmark", edit=True, writeRequires=True)

    bm = cmds.createNode("timeSliderBookmark")
    if float(start) > float(stop):
        start, stop = stop, start

    cmds.setAttr(bm + ".timeRangeStart", float(start))
    cmds.setAttr(bm + ".timeRangeStop", float(stop))

    if name:
        cmds.setAttr(bm + ".name", str(name), type="string")
    if color:
        cmds.setAttr(bm + ".color", float(color[0]), float(color[1]), float(color[2]))
    if priority:
        cmds.setAttr(bm + ".priority", int(priority))

    return bm


def delete_all_bookmarks():
    """清空场景中所有时间滑块书签"""
    bookmarks = cmds.ls(type="timeSliderBookmark") or []
    if bookmarks:
        cmds.delete(bookmarks)
    return len(bookmarks)


def generate_keyframe_bookmarks(
    objects=None,
    layer="auto",
    palette_name="dual",
    prefix="BM",
    clear_existing=False,
):
    """
    主执行逻辑：提取关键帧，并在相邻两两关键帧之间创建颜色互斥的书签。

    参数:
        objects (list[str], optional): 目标物体列表。若为 None 则使用当前选中的物体。
        layer (str): 动画层，支持 'auto', 'BaseAnimation', 'All' 或具体层名称。
        palette_name (str): 调色方案名 ('dual', 'vibrant', 'pastel', 'cyberpunk')。
        prefix (str): 书签名命名前缀。
        clear_existing (bool): 是否在创建前清空旧书签。

    返回:
        dict: 包含 success, count, bookmarks, keyframes, message 的结果字典。
    """
    if not ensure_bookmark_plugin():
        return {
            "success": False,
            "count": 0,
            "message": u"未能加载 timeSliderBookmark 插件，创建中止。",
        }

    # 获取目标物体
    target_objs = objects if objects is not None else (cmds.ls(sl=True) or [])
    if not target_objs:
        msg = u"未选择任何物体！请先在场景中选择带有关键帧的物体或控制器。"
        cmds.warning(msg)
        return {"success": False, "count": 0, "message": msg}

    # 解析层级名称
    actual_layer = get_active_anim_layer() if (layer == "auto" or not layer) else layer

    # 提取关键帧
    keyframes = get_keyframes_from_objects(target_objs, layer=actual_layer)
    if len(keyframes) < 2:
        msg = u"物体在层 [{}] 上的关键帧少于 2 帧 (找到 {} 帧: {})，无法形成区间！".format(
            actual_layer, len(keyframes), keyframes
        )
        cmds.warning(msg)
        return {"success": False, "count": 0, "keyframes": keyframes, "message": msg}

    # 获取颜色调色板
    palette_cfg = COLOR_PALETTES.get(palette_name, COLOR_PALETTES["dual"])
    colors = palette_cfg["colors"]
    num_colors = len(colors)

    created_bms = []

    # 开启 Undo 事务包裹
    cmds.undoInfo(openChunk=True, chunkName="CreateAnimLayerBookmarks")
    try:
        if clear_existing:
            delete_all_bookmarks()

        # 两两关键帧生成区间书签
        for i in range(len(keyframes) - 1):
            start_f = keyframes[i]
            stop_f = keyframes[i + 1]

            # 相邻书签颜色互斥选取：第 i 个区间对应 colors[i % num_colors]
            # 只要 num_colors >= 2，相邻必不相同
            assigned_color = colors[i % num_colors]

            # 格式化书签名称
            bm_name = "{}_{}_{}".format(prefix, int(round(start_f)), int(round(stop_f)))

            bm_node = create_time_slider_bookmark(
                name=bm_name,
                start=start_f,
                stop=stop_f,
                color=assigned_color,
                priority=i,
            )
            created_bms.append(bm_node)

    finally:
        cmds.undoInfo(closeChunk=True)

    success_msg = u"成功在层 [{}] 的 {} 个关键帧之间创建了 {} 个区间书签！".format(
        actual_layer, len(keyframes), len(created_bms)
    )
    return {
        "success": True,
        "count": len(created_bms),
        "bookmarks": created_bms,
        "keyframes": keyframes,
        "layer": actual_layer,
        "message": success_msg,
    }


# ==============================================================================
# 原生 Maya 界面 (Maya UI)
# ==============================================================================
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


def show_ui():
    """打开界面的全局便捷入口"""
    ui = AnimLayerBookmarkUI()
    ui.show()
    return ui


if __name__ == "__main__":
    show_ui()
