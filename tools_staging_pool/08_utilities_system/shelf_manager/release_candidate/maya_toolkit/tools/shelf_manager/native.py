
from maya_toolkit.tools.shelf_manager.session import cmds
# MEL import deferred to explicit session.load_shelf
import os
import sys
import traceback
import glob
import re
import shutil

# --- 主类定义 ---
class ShelfManager:
    """
    Maya工具架管理工具 - 重新设计版
    功能:
    1. 自动识别用户名和正确的Maya路径格式
    2. 支持2018-2026版本的自动检测和分类
    3. 区分中英文版本的工具架（分左右两列显示）
    4. 版本号切换功能
    """
    def __init__(self):
        self.window_name = "MTB_ShelfManagerWindow"
        self.window_title = "Maya工具架管理工具 v4.0"

        # 数据存储
        self.maya_versions = []  # 存储找到的所有Maya版本号
        self.current_version = None  # 当前选中的版本

        # 工具架数据结构 {版本号: {'zh': [路径列表], 'en': [路径列表]}}
        self.shelf_data = {}

        # 映射UI名称到文件路径
        self.zh_shelf_map = {}  # 中文工具架映射
        self.en_shelf_map = {}  # 英文工具架映射

        # 默认工具架列表
        self.default_shelves = [
            "Animation", "Arnold", "Bifrost", "Cexport",
            "CurvesSurfaces", "Custom", "FX", "FXCaching",
            "MASH", "MotionGraphics", "MSPlugin", "Polygons",
            "Rendering", "Rigging", "Sculpting", "TURTLE", "XGen",
            "Brushes", "Display", "Dynamics", "General",
            "Help", "Modeling", "Paint Effects",
            "Stereo", "Subdivision", "Surfaces", "UV"
        ]

        # 显示默认工具架选项
        self.show_default_shelves = False

        # 自动检测用户路径
        self.user_paths = self._detect_maya_user_paths()

        # 如果窗口已存在，则删除
        if cmds.window(self.window_name, exists=True):
            cmds.deleteUI(self.window_name, window=True)

        # 创建新窗口
        self.window = cmds.window(self.window_name, title=self.window_title, widthHeight=(800, 650))

        self.build_ui()

        # 显示窗口
        cmds.showWindow(self.window)

        # 初始化扫描
        self._initial_scan()

    def _detect_maya_user_paths(self):
        from maya_toolkit.tools.shelf_manager import session,backend
        return session.source_roots or backend.detect()

    def build_ui(self):
        """构建UI界面"""
        main_layout = cmds.columnLayout(adjustableColumn=True, parent=self.window)

        # 标题和说明
        cmds.text(label="Maya工具架管理工具", font="boldLabelFont", height=30, align="center")
        cmds.text(label="此工具可以帮助您管理不同版本和语言的Maya工具架文件", align="center")
        cmds.separator(height=10, style='in')

        # 版本选择区域
        cmds.frameLayout(label="版本选择", collapsable=False, parent=main_layout)
        version_row = cmds.rowLayout(numberOfColumns=2, adjustableColumn=1, parent=main_layout)

        cmds.text(label="选择Maya版本:", parent=version_row)
        self.version_menu = cmds.optionMenu(changeCommand=self.change_version, parent=version_row)
        cmds.menuItem(label="等待扫描...", parent=self.version_menu)

        cmds.setParent(main_layout)

        # 显示默认工具架选项
        cmds.checkBox(label="显示Maya默认工具架", value=self.show_default_shelves, changeCommand=self.toggle_default_shelves)

        # 重新扫描按钮 - 单个按钮，居中
        cmds.button(label="重新扫描所有版本", command=self.rescan_all, height=30, backgroundColor=(0.2, 0.7, 0.2))

        # 工具架显示区域
        cmds.frameLayout(label="工具架列表", collapsable=False, parent=main_layout)

        # 创建标题行 - 使用formLayout代替rowLayout避免列宽问题
        title_form = cmds.formLayout(parent=main_layout)
        zh_title = cmds.text(label="中文工具架 (zh_CN)", font="boldLabelFont", align="center", parent=title_form)
        en_title = cmds.text(label="英文工具架 (en_US)", font="boldLabelFont", align="center", parent=title_form)

        # 设置formLayout的约束
        cmds.formLayout(title_form, edit=True,
                        attachForm=[(zh_title, 'left', 5), (zh_title, 'top', 5),
                                   (en_title, 'right', 5), (en_title, 'top', 5)],
                        attachPosition=[(zh_title, 'right', 5, 50),
                                       (en_title, 'left', 5, 50)])

        cmds.setParent(main_layout)

        # 创建一个水平布局来容纳两个列表
        list_form = cmds.formLayout(parent=main_layout)

        # 左侧 - 中文工具架
        self.zh_shelf_list = cmds.textScrollList(
            numberOfRows=15,
            allowMultiSelection=True,  # 启用多选
            height=250,
            selectCommand=self.on_shelf_selected,
            parent=list_form
        )

        # 右侧 - 英文工具架
        self.en_shelf_list = cmds.textScrollList(
            numberOfRows=15,
            allowMultiSelection=True,  # 启用多选
            height=250,
            selectCommand=self.on_shelf_selected,
            parent=list_form
        )

        # 设置formLayout的约束，确保两个列表并排显示
        cmds.formLayout(list_form, edit=True,
                       attachForm=[(self.zh_shelf_list, 'left', 5), (self.zh_shelf_list, 'top', 5), (self.zh_shelf_list, 'bottom', 5),
                                  (self.en_shelf_list, 'right', 5), (self.en_shelf_list, 'top', 5), (self.en_shelf_list, 'bottom', 5)],
                       attachPosition=[(self.zh_shelf_list, 'right', 2, 50),
                                      (self.en_shelf_list, 'left', 2, 50)])

        cmds.setParent(main_layout)

        # 操作按钮行 - 使用formLayout确保均匀分布
        button_form = cmds.formLayout(height=40, parent=main_layout)

        # 创建三个操作按钮 - 横向排列
        load_btn = cmds.button(label="加载选中的工具架", command=self.load_shelves, height=35, parent=button_form)
        delete_btn = cmds.button(label="删除选中的工具架", command=self.delete_shelves, height=35, backgroundColor=(1.0, 0.4, 0.4), parent=button_form)
        migrate_btn = cmds.button(label="迁移选中的工具架", command=self.migrate_shelves, height=35, backgroundColor=(0.4, 0.7, 1.0), parent=button_form)

        # 设置formLayout的约束 - 确保三个按钮等宽并排
        cmds.formLayout(button_form, edit=True,
                       attachForm=[
                           (load_btn, 'left', 5), (load_btn, 'top', 5), (load_btn, 'bottom', 5),
                           (delete_btn, 'top', 5), (delete_btn, 'bottom', 5),
                           (migrate_btn, 'right', 5), (migrate_btn, 'top', 5), (migrate_btn, 'bottom', 5)
                       ],
                       attachPosition=[
                           (load_btn, 'right', 2, 33),
                           (delete_btn, 'left', 2, 33), (delete_btn, 'right', 2, 67),
                           (migrate_btn, 'left', 2, 67)
                       ])

        cmds.setParent(main_layout)

        # 状态栏
        cmds.separator(height=10, style='in')
        self.status_text = cmds.text(label="正在初始化...", align="left")

    def _initial_scan(self):
        """初始化扫描所有可能的Maya版本"""
        cmds.text(self.status_text, edit=True, label="正在扫描Maya版本...")

        # 清空数据
        self.maya_versions = []
        self.shelf_data = {}

        # 扫描所有检测到的用户路径
        found_any = False
        for base_path in self.user_paths:
            if self._scan_versions_in_path(base_path):
                found_any = True

        # 更新版本菜单
        cmds.optionMenu(self.version_menu, edit=True, deleteAllItems=True)

        if self.maya_versions:
            # 按版本号排序（从新到旧）
            self.maya_versions.sort(reverse=True)

            for version in self.maya_versions:
                cmds.menuItem(label=version, parent=self.version_menu)

            # 默认选择最新版本
            self.current_version = self.maya_versions[0]
            cmds.optionMenu(self.version_menu, edit=True, value=self.current_version)

            # 更新工具架列表
            self._update_shelf_lists()

            cmds.text(self.status_text, edit=True, label="扫描完成！共找到 {} 个Maya版本".format(len(self.maya_versions)))
        else:
            cmds.menuItem(label="未找到Maya版本", parent=self.version_menu)
            cmds.text(self.status_text, edit=True, label="未找到任何Maya版本，请尝试添加自定义路径")

    def _scan_versions_in_path(self,base_path):
        from maya_toolkit.tools.shelf_manager.backend import scan
        rows=scan([base_path],True)
        for row in rows:
            version=row['version'];lang=row['language']
            if version not in self.maya_versions:self.maya_versions.append(version);self.shelf_data[version]={'zh':[],'en':[]}
            if row['path'] not in self.shelf_data[version][lang]:self.shelf_data[version][lang].append(row['path'])
        return bool(rows)

    def _scan_shelves_in_path(self, shelves_path, version, lang):
        """扫描指定路径下的工具架文件"""
        try:
            # 确保路径存在
            if not os.path.isdir(shelves_path):
                return

            # 查找所有shelf_*.mel文件
            shelf_files = []
            for f in os.listdir(shelves_path):
                if f.startswith("shelf_") and f.endswith(".mel"):
                    shelf_files.append(f)

            if shelf_files:
                print("      找到 {} 个工具架文件".format(len(shelf_files)))

            for mel_file in shelf_files:
                full_path = os.path.join(shelves_path, mel_file).replace("\\", "/")

                # 获取工具架名称 (去掉"shelf_"前缀和".mel"后缀)
                shelf_name = mel_file[6:-4]  # 从索引6开始，去掉".mel"的4个字符

                # 判断是否是默认工具架
                is_default = shelf_name in self.default_shelves

                # 如果是默认工具架且不显示默认工具架，则跳过
                if is_default and not self.show_default_shelves:
                    continue

                # 添加到对应版本和语言的列表中
                if full_path not in self.shelf_data[version][lang]:
                    self.shelf_data[version][lang].append(full_path)

                    # 更新映射 - 使用版本+语言+名称作为唯一键
                    shelf_key = "{}_{}".format(shelf_name, version)

                    if lang == 'zh':
                        self.zh_shelf_map[shelf_key] = full_path
                    else:
                        self.en_shelf_map[shelf_key] = full_path
        except Exception as e:
            print("扫描工具架时出错: {}".format(e))
            traceback.print_exc()

    def _update_shelf_lists(self):
        if not self.current_version:return
        self.zh_shelf_map.clear();self.en_shelf_map.clear()
        for lang,control,mapping in [('zh',self.zh_shelf_list,self.zh_shelf_map),('en',self.en_shelf_list,self.en_shelf_map)]:
            cmds.textScrollList(control,edit=True,removeAll=True)
            for shelf_path in sorted(self.shelf_data.get(self.current_version,{}).get(lang,[])):
                name=os.path.basename(shelf_path)[6:-4]
                if not self.show_default_shelves and name in self.default_shelves:continue
                display=name+' ['+shelf_path+']';mapping[display]=shelf_path
                cmds.textScrollList(control,edit=True,append=[display])

    def toggle_default_shelves(self, value):
        """切换是否显示默认工具架"""
        self.show_default_shelves = value
        self._update_shelf_lists()
        status = "显示" if value else "隐藏"
        cmds.text(self.status_text, edit=True, label="已{}Maya默认工具架".format(status))

    def change_version(self, version):
        """切换Maya版本"""
        self.current_version = version
        self._update_shelf_lists()
        cmds.text(self.status_text, edit=True, label="已切换到Maya {} 版本".format(version))

    def rescan_all(self, *args):
        """重新扫描所有版本"""
        self._initial_scan()

    def on_shelf_selected(self):
        """工具架被选中时的处理"""
        # 不需要互斥选择，中英文工具架可以同时选择
        pass

    def _get_selected_shelves(self):
        rows=[]
        for lang,control,mapping in [('zh',self.zh_shelf_list,self.zh_shelf_map),('en',self.en_shelf_list,self.en_shelf_map)]:
            for display in cmds.textScrollList(control,query=True,selectItem=True) or []:
                if display in mapping:
                    p=mapping[display];rows.append((os.path.basename(p)[6:-4],p,lang))
        return rows

    def load_shelves(self,*args):
        from maya_toolkit.tools.shelf_manager.session import gui_load
        return gui_load(self)

    def delete_shelves(self,*args):
        from maya_toolkit.tools.shelf_manager.session import gui_delete
        return gui_delete(self)

    def migrate_shelves(self,*args):
        from maya_toolkit.tools.shelf_manager.session import gui_migrate
        return gui_migrate(self)

# --- 启动函数 ---
def run():
    """启动工具"""
    try:
        # 检查是否已有实例
        if 'shelf_manager_app' in globals() and isinstance(globals()['shelf_manager_app'], ShelfManager):
            if cmds.window(globals()['shelf_manager_app'].window_name, exists=True):
                cmds.showWindow(globals()['shelf_manager_app'].window_name)
                print("工具窗口已存在，已为您重新显示。")
                return

        # 创建新实例
        globals()['shelf_manager_app'] = ShelfManager()
    except Exception as e:
        error_msg = "启动工具失败: {}".format(e)
        print(error_msg)
        traceback.print_exc()
        cmds.error(error_msg)

# 直接运行
if __name__ == "__main__":
    run()
