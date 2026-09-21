
# -*- coding: utf-8 -*-

# =============================================================================
# 更新日志 (Update Log)
# =============================================================================
# v11.1 - 2024年最新更新
#   - 合并了FFmpeg调取方式，简化检测逻辑
#   - 移除了不可靠的本地路径检测，专注于系统环境变量和用户手动选择
#   - 修改UI布局，在路径浏览按钮右侧添加"打开"按钮
#   - 优化了代码结构，移除了get_script_directory()等冗余函数
#   - 提升了工具的稳定性和用户体验
#
# v11 - 多功能版本
#   - 新增输出命名功能
#   - 新增输出路径选择
#   - 新增多相机模式支持
#   - 新增强制覆盖功能
#   - 新增"拍一"动画效果
#   - 修复GIF多相机重名问题
#   - FFmpeg部署版支持
# =============================================================================


import maya.cmds as cmds
import os
import subprocess
import shutil
import tempfile
import sys
from datetime import datetime
import re
import maya.mel as mel
import json

def get_settings_file_path():
    """获取设置文件的完整路径"""
    try:
        # 获取用户文档目录
        documents_dir = os.path.expanduser("~/Documents")
        maya_scripts_dir = os.path.join(documents_dir, "maya", "scripts")
        
        # 确保目录存在
        if not os.path.exists(maya_scripts_dir):
            os.makedirs(maya_scripts_dir, exist_ok=True)
            
        settings_file = os.path.join(maya_scripts_dir, "playblast_tool_settings.json")
        return settings_file
    except Exception as e:
        print(f"获取设置文件路径失败: {e}")
        # 回退到临时目录
        import tempfile
        return os.path.join(tempfile.gettempdir(), "playblast_tool_settings.json")

def save_ffmpeg_settings(ffmpeg_mode, ffmpeg_custom_path):
    """保存FFmpeg设置到文件"""
    try:
        settings = {
            "ffmpeg_mode": ffmpeg_mode,
            "ffmpeg_custom_path": ffmpeg_custom_path,
            "version": "v9",
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        settings_file = get_settings_file_path()
        with open(settings_file, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
            
        print(f"FFmpeg设置已保存到: {settings_file}")
        return True
    except Exception as e:
        print(f"保存FFmpeg设置失败: {e}")
        return False

def load_ffmpeg_settings():
    """从文件加载FFmpeg设置"""
    try:
        settings_file = get_settings_file_path()
        if not os.path.exists(settings_file):
            print("未找到设置文件，使用默认设置")
            return {"ffmpeg_mode": "system", "ffmpeg_custom_path": ""}
            
        with open(settings_file, 'r', encoding='utf-8') as f:
            settings = json.load(f)
            
        # 验证设置内容
        ffmpeg_mode = settings.get("ffmpeg_mode", "system")
        ffmpeg_custom_path = settings.get("ffmpeg_custom_path", "")
        
        # 如果是本地路径模式，验证路径是否存在
        if ffmpeg_mode == "local" and ffmpeg_custom_path:
            if not os.path.exists(ffmpeg_custom_path):
                print(f"保存的FFmpeg路径不存在: {ffmpeg_custom_path}，回退到系统模式")
                ffmpeg_mode = "system"
                ffmpeg_custom_path = ""
        
        print(f"已加载FFmpeg设置: 模式={ffmpeg_mode}, 路径={ffmpeg_custom_path}")
        return {"ffmpeg_mode": ffmpeg_mode, "ffmpeg_custom_path": ffmpeg_custom_path}
        
    except Exception as e:
        print(f"加载FFmpeg设置失败: {e}，使用默认设置")
        return {"ffmpeg_mode": "system", "ffmpeg_custom_path": ""}

def auto_detect_ffmpeg():
    """
    自动检测FFmpeg路径 - 只检测系统环境变量
    返回: (ffmpeg_path, source_description) 或 (None, None)
    """
    # 检查系统环境变量
    try:
        import shutil
        system_ffmpeg = shutil.which('ffmpeg')
        if system_ffmpeg:
            return 'ffmpeg', f"系统环境变量: {system_ffmpeg}"
    except Exception:
        pass
    
    return None, None

def manual_select_ffmpeg():
    """
    手动选择FFmpeg路径
    返回: ffmpeg_path_code 字符串
    """
    # 弹出文件选择对话框
    ffmpeg_path = cmds.fileDialog2(
        fileMode=1,
        fileFilter="FFmpeg可执行文件 (*.exe)",
        caption="选择ffmpeg.exe",
        startingDirectory=os.path.expanduser("~/Documents")
    )
    
    if ffmpeg_path and len(ffmpeg_path) > 0:
        ffmpeg_path = ffmpeg_path[0].replace("\\", "/")
        return f'''
# 使用手动选择的ffmpeg路径
custom_ffmpeg_path = r"{ffmpeg_path}"
'''
    else:
        # 用户取消了选择，使用系统ffmpeg（如果可用）
        try:
            import shutil
            if shutil.which('ffmpeg'):
                return '''
# 用户取消选择，回退到系统环境变量中的ffmpeg
custom_ffmpeg_path = None
'''
        except Exception:
            pass
        
        # 完全找不到ffmpeg
        cmds.warning("未选择FFmpeg路径，工具可能无法正常工作")
        return '''
# 未找到有效的ffmpeg路径
custom_ffmpeg_path = None
'''

def onMayaDroppedPythonFile(*args, **kwargs):
    """
    在Maya中拖放此脚本时自动执行此函数
    用于在当前工具架上创建按钮，默认使用系统环境变量中的FFmpeg
    """
    try:
        # 获取当前工具架
        gShelfTopLevel = mel.eval('$tmpVar=$gShelfTopLevel')
        current_shelf = cmds.tabLayout(gShelfTopLevel, query=True, selectTab=True)
        
        # 默认使用系统环境变量中的FFmpeg（用户可以在工具界面中更改）
        ffmpeg_path_code = '''
# 默认使用系统环境变量中的ffmpeg（可在工具界面中更改设置）
custom_ffmpeg_path = None
'''

        # 创建用于打开工具的Python代码
        tool_command = f'''
# 清理旧窗口
import maya.cmds as cmds
try:
    if cmds.window("screen_capture_tool", exists=True):
        cmds.deleteUI("screen_capture_tool", window=True)
except Exception as e:
    print(f"清理窗口时出错: {{str(e)}}")

{ffmpeg_path_code}

# 启动工具
try:
    # 导入模块
    import mov拍屏v9
    # 确保重新加载模块
    try:
        import importlib
        importlib.reload(mov拍屏v9)
    except:
        pass
    
    # 创建UI实例，并传入自定义ffmpeg路径参数
    mov拍屏v9.PlayblastConverterUI(custom_ffmpeg_path)
except Exception as e:
    import traceback
    cmds.warning(f"启动拍屏工具时出错: {{str(e)}}")
    traceback.print_exc()
'''
        
        # 创建工具架按钮
        cmds.shelfButton(
            parent=current_shelf,
            image='commandButton.png',
            label='拍屏工具',
            annotation='拍屏工具 - 支持多相机、GIF转换等功能',
            sourceType='Python',
            command=tool_command
        )
        
        cmds.confirmDialog(
            title='安装成功',
            message=f'已在工具架 {current_shelf} 上创建拍屏工具按钮\n\n默认使用系统环境变量中的FFmpeg\n可在工具界面的"FFmpeg设置"中更改路径配置',
            button=['确定'],
            defaultButton='确定'
        )
        
    except Exception as e:
        cmds.warning(f"创建拍屏工具按钮时出错: {str(e)}")
        import traceback
        traceback.print_exc()

def get_ffmpeg_path(custom_path=None):
    """
    获取ffmpeg可执行文件的路径
    如果提供了自定义路径，则使用自定义路径
    否则尝试使用系统环境变量中的ffmpeg
    """
    # 1. 如果提供了自定义路径且文件存在，直接使用
    if custom_path and os.path.exists(custom_path):
        return custom_path
    
    # 2. 检查系统PATH中是否有ffmpeg
    try:
        import shutil
        system_ffmpeg = shutil.which('ffmpeg')
        if system_ffmpeg:
            return 'ffmpeg'  # 直接返回命令名称，让系统解析
    except Exception:
        pass
        
    # 3. 所有方式都找不到，返回警告
    cmds.warning("找不到ffmpeg，请在FFmpeg设置中配置正确的路径")
    return None

class PlayblastConverterUI:
    def __init__(self, custom_ffmpeg_path=None):
        self.custom_ffmpeg_path = custom_ffmpeg_path
        self.window_name = "screen_capture_tool"
        
        # 加载保存的FFmpeg设置
        saved_settings = load_ffmpeg_settings()
        self.ffmpeg_mode = saved_settings["ffmpeg_mode"]
        self.ffmpeg_custom_path = saved_settings["ffmpeg_custom_path"]
        if cmds.window(self.window_name, exists=True):
            cmds.deleteUI(self.window_name, window=True)

        # 窗口创建时设置适当的初始大小
        self.window = cmds.window(
            self.window_name, 
            title="拍屏工具", 
            sizeable=False,  # 禁用手动调整窗口大小
            minimizeButton=True, 
            maximizeButton=False,
            widthHeight=(270, 320)  # 进一步压缩右侧空白
        )

        # 使用垂直布局，紧凑间距
        main_layout = cmds.columnLayout(adjustableColumn=True, columnAlign="center", rowSpacing=3)
        
        # 顶部菜单区域 - 压缩空白
        menu_layout = cmds.rowColumnLayout(numberOfColumns=2, columnWidth=[(1, 55), (2, 55)], parent=main_layout)
        cmds.button(label="FFmpeg", command=self.open_ffmpeg_settings, height=20, backgroundColor=[0.4, 0.5, 0.6], annotation="FFmpeg设置")
        cmds.button(label="刷新", command=self.refresh_plugin, height=20, backgroundColor=[0.5, 0.6, 0.4])
        
        cmds.setParent(main_layout)
        cmds.separator(height=2, style='none')
        
        # 文件信息区域 - 紧凑布局
        file_frame = cmds.frameLayout(labelVisible=False, borderVisible=False, parent=main_layout)
        file_layout = cmds.columnLayout(adjustableColumn=True, rowSpacing=2, parent=file_frame)
        
        # 文件名 - 压缩空白
        filename_row = cmds.rowColumnLayout(numberOfColumns=3, columnWidth=[(1, 45), (2, 175), (3, 20)], parent=file_layout)
        cmds.text(label="文件:", align='left', font="smallPlainLabelFont")
        current_file_path = cmds.file(q=True, sceneName=True)
        current_file_name = os.path.splitext(os.path.basename(current_file_path))[0] if current_file_path else "untitled"
        self.filename_field = cmds.textField(text=current_file_name, width=175, height=18)
        cmds.button(label="R", command=self.refresh_filename, width=20, height=18, annotation="刷新文件名")
        
        # 路径 - 压缩空白
        cmds.setParent(file_layout)
        path_row = cmds.rowColumnLayout(numberOfColumns=5, columnWidth=[(1, 45), (2, 125), (3, 20), (4, 35), (5, 35)], parent=file_layout)
        cmds.text(label="路径:", align='left', font="smallPlainLabelFont")
        current_dir = os.path.dirname(current_file_path) if current_file_path else ""
        self.path_field = cmds.textField(text=current_dir, width=125, height=18)
        cmds.button(label="R", command=self.refresh_path, width=20, height=18, annotation="刷新路径")
        cmds.button(label="浏览", command=self.browse_path, width=35, height=18)
        cmds.button(label="打开", command=self.open_current_path, width=35, height=18, annotation="打开当前路径")
        
        # 相机选择区域 - 紧凑设计
        cmds.setParent(main_layout)
        cmds.separator(height=2, style='none')
        
        camera_frame = cmds.frameLayout(labelVisible=False, borderVisible=False, parent=main_layout)
        camera_section = cmds.columnLayout(adjustableColumn=True, rowSpacing=2, parent=camera_frame)
        
        # 相机模式选择 - 压缩空白
        mode_row = cmds.rowColumnLayout(numberOfColumns=3, columnWidth=[(1, 35), (2, 55), (3, 55)], parent=camera_section)
        cmds.text(label="相机:", align='left', font="smallPlainLabelFont")
        self.single_mode_button = cmds.button(
            label="单机",
            width=55,
            height=18,
            backgroundColor=[0.3, 0.45, 0.7],
            command=lambda x: self.switch_camera_mode("single")
        )
        
        self.multi_mode_button = cmds.button(
            label="多机",
            width=55,
            height=18,
            backgroundColor=[0.45, 0.45, 0.45],
            command=lambda x: self.switch_camera_mode("multi")
        )
        
        cmds.setParent(camera_section)
        
        # 相机选择界面
        self.single_camera_frame = cmds.frameLayout(labelVisible=False, visible=True, borderVisible=False, parent=camera_section)
        
        # 单相机模式 - 压缩空白
        self.camera_menu = cmds.optionMenu(width=260, height=18)
        cmds.menuItem(label="<当前视图>")
        # 获取场景中所有相机
        all_cameras = cmds.listCameras()
        # 过滤掉默认相机，但保留前、侧、顶视图相机
        filtered_cameras = [cam for cam in all_cameras if not (cam == 'persp')]
        # 添加三个正交相机
        ortho_cameras = [cam for cam in all_cameras if cam in ['front', 'side', 'top']]
        for cam in ortho_cameras:
            if cam == 'front':
                display_name = "前视图 (front)"
            elif cam == 'side':
                display_name = "侧视图 (side)"
            elif cam == 'top':
                display_name = "顶视图 (top)"
            cmds.menuItem(label=display_name)
        # 添加其他自定义相机
        custom_cameras = [cam for cam in filtered_cameras if cam not in ortho_cameras]
        for cam in custom_cameras:
            cmds.menuItem(label=cam)
        
        # 多相机模式界面（初始隐藏）
        cmds.setParent(camera_section)
        self.multi_camera_frame = cmds.frameLayout(labelVisible=False, visible=False, borderVisible=False)
        
        multi_cam_layout = cmds.columnLayout(adjustableColumn=True, rowSpacing=2)
        
        # 操作按钮 - 压缩空白
        cmds.rowLayout(numberOfColumns=3, columnWidth3=(50, 50, 50), parent=multi_cam_layout)
        cmds.button(label="全选", height=16, command=lambda x: self.select_all_cameras(True))
        cmds.button(label="全不选", height=16, command=lambda x: self.select_all_cameras(False))
        cmds.button(label="反选", height=16, command=self.invert_camera_selection)
        cmds.setParent(multi_cam_layout)
        
        # 相机复选框滚动区域 - 压缩空白
        self.camera_scroll = cmds.scrollLayout(
            horizontalScrollBarThickness=0,
            verticalScrollBarThickness=10,
            height=70,
            width=260
        )
        
        # 初始化相机复选框
        self.camera_checkboxes = {}
        self.camera_checkboxes["<当前视图>"] = cmds.checkBox(
            label="<当前视图>",
            value=True
        )
        
        # 添加三个正交相机复选框
        for cam in ortho_cameras:
            if cam == 'front':
                display_name = "前视图 (front)"
            elif cam == 'side':
                display_name = "侧视图 (side)"
            elif cam == 'top':
                display_name = "顶视图 (top)"
            self.camera_checkboxes[cam] = cmds.checkBox(
                label=display_name,
                value=False
            )
        
        # 添加其他自定义相机复选框
        for cam in custom_cameras:
            self.camera_checkboxes[cam] = cmds.checkBox(
                label=cam,
                value=False
            )
            
        # 设置当前相机模式标志
        self.multi_camera_mode = False
        
        # 录制按钮区域 - 紧凑设计
        cmds.setParent(main_layout)
        cmds.separator(height=3, style='none')
        
        record_frame = cmds.frameLayout(labelVisible=False, borderVisible=False, parent=main_layout)
        record_layout = cmds.columnLayout(adjustableColumn=True, rowSpacing=2, parent=record_frame)
        
        # 主录制按钮 - 压缩空白
        button_row = cmds.rowColumnLayout(numberOfColumns=2, columnWidth=[(1, 130), (2, 130)], parent=record_layout)
        self.high_button = cmds.button(label="高分辨率", height=24, backgroundColor=[0.3, 0.45, 0.7], command=self.capture_action)
        self.low_button = cmds.button(label="低分辨率", height=24, backgroundColor=[0.7, 0.45, 0.3], command=self.qt_playblast_action)
        
        # 选项行 - 压缩空白
        cmds.setParent(record_layout)
        options_row = cmds.rowColumnLayout(numberOfColumns=4, columnWidth=[(1, 60), (2, 60), (3, 35), (4, 50)], parent=record_layout)
        self.audio_checkbox = cmds.checkBox(label="音频", value=False, changeCommand=self.toggle_audio_options)
        self.offset_field = cmds.intField(value=0, width=40, height=16, enable=False, annotation="音频偏移帧")
        cmds.text(label="缩放:", align='right', font="smallPlainLabelFont")
        self.scale_field = cmds.floatField(value=1.0, minValue=0.1, maxValue=1.0, width=50, height=16, precision=1, changeCommand=self.on_scale_change)
        
        # 分隔线
        cmds.setParent(main_layout)
        cmds.separator(height=5, style='none')
        
        # 高级选项区域 - 无框架设计
        options_section = cmds.frameLayout(
            labelVisible=False,
            borderVisible=False,
            parent=main_layout,
            marginWidth=0,
            marginHeight=2
        )
        
        options_column = cmds.columnLayout(adjustableColumn=True, rowSpacing=2, parent=options_section)
        
        # 高级选项标题
        cmds.text(label="高级选项", align='left', font="smallBoldLabelFont")
        cmds.separator(height=3, style='none')
        
        # 第一行选项 - 压缩空白，确保总宽度不超过260px
        row1 = cmds.rowColumnLayout(numberOfColumns=3, columnWidth=[(1, 70), (2, 70), (3, 70)], parent=options_column)
        self.increment_checkbox = cmds.checkBox(label="增序", value=False)
        self.convert_checkbox = cmds.checkBox(label="转MP4", value=False)
        self.force_overwrite_checkbox = cmds.checkBox(label="覆盖", value=False)
        
        # 第二行选项 - 压缩空白，确保总宽度不超过260px
        cmds.setParent(options_column)
        row2 = cmds.rowColumnLayout(numberOfColumns=4, columnWidth=[(1, 70), (2, 70), (3, 25), (4, 15)], parent=options_column)
        self.gif_checkbox = cmds.checkBox(label="转GIF", value=False)
        self.on_hold_checkbox = cmds.checkBox(label="拍一", value=False)
        
        self.hold_frames_field = cmds.textField(
            text="2",
            width=25,
            height=16,
            annotation="设置几拍一效果，例如2表示二拍一，3表示三拍一"
        )
        cmds.text(label="拍", font="smallPlainLabelFont")
        
        # 显示窗口并调整大小
        cmds.showWindow(self.window)
        
        # 确保UI正确初始化和显示
        self.initialize_ui()
        
        # 注意：由于FFmpeg设置已移至独立窗口，不再需要应用设置到主界面
        # self.apply_loaded_settings()

    def initialize_ui(self):
        """确保UI正确初始化和显示"""
        def delayed_init():
            # 确保高级选项内部所有控件可见
            for control in [self.increment_checkbox, self.convert_checkbox, 
                            self.force_overwrite_checkbox, self.gif_checkbox, 
                            self.on_hold_checkbox, self.hold_frames_field]:
                try:
                    cmds.control(control, edit=True, visible=True)
                except:
                    pass
                
            
            # 重新计算窗口大小
            self.adjust_window_size()
            
            # 刷新视图
            cmds.refresh(force=True)
            
        # 使用evalDeferred确保在UI完全加载后执行
        cmds.evalDeferred(delayed_init)

    def adjust_window_size(self, *args):
        """根据内容自动调整窗口大小"""
        # 计算适当的窗口高度
        try:
            # 超紧凑设计的基础高度
            base_height = 260  # 超紧凑设计后的基础高度
            multi_camera_height = 70  # 多相机模式的额外高度（超紧凑）
            
            target_height = base_height
            if self.multi_camera_mode:
                target_height += multi_camera_height
            
            # 使用延迟执行避免闪烁，并确保窗口大小不可调整
            def adjust_size():
                try:
                    # 先设置大小
                    cmds.window(self.window_name, edit=True, widthHeight=(280, target_height))
                    # 再确保不可调整大小
                    cmds.window(self.window_name, edit=True, sizeable=False)
                    # 高级选项现在总是可见，无需特殊处理
                    # 刷新UI
                    cmds.refresh(force=True)
                except Exception as e:
                    cmds.warning(f"调整窗口大小时出错: {str(e)}")
                
            # 使用evalDeferred确保UI更新后再调整大小
            cmds.evalDeferred(adjust_size)
        except Exception as e:
            cmds.warning(f"计算窗口大小时出错: {str(e)}")

    def toggle_audio_options(self, *args):
        audio_enabled = cmds.checkBox(self.audio_checkbox, query=True, value=True)
        cmds.intField(self.offset_field, edit=True, enable=audio_enabled)

    def browse_path(self, *args):
        """打开文件浏览器选择保存路径"""
        current_path = cmds.textField(self.path_field, query=True, text=True)
        if not current_path or not os.path.exists(current_path):
            current_path = cmds.workspace(q=True, rd=True)
        
        result = cmds.fileDialog2(
            fileMode=3,  # 目录模式
            dialogStyle=2,  # Maya风格对话框
            caption="选择输出目录",
            okCaption="选择",
            startingDirectory=current_path
        )
        
        if result and len(result):
            selected_path = result[0]
            cmds.textField(self.path_field, edit=True, text=selected_path)

    def get_camera_list(self):
        """获取场景中所有相机"""
        all_cameras = cmds.listCameras()
        # 过滤掉默认相机
        filtered_cameras = [cam for cam in all_cameras if not (cam.startswith('front') or cam.startswith('side') or cam.startswith('top') or cam == 'persp')]
        return filtered_cameras
        
    def get_selected_camera(self):
        """获取用户选择的相机，如果选择了<当前视图>则返回None"""
        if self.multi_camera_mode:
            # 多相机模式下，这个函数已经不被使用，为向后兼容而保留
            selected_cameras = self.get_selected_cameras()
            return selected_cameras[0] if selected_cameras else None
        else:
            # 单相机模式
            try:
                selected_item = cmds.optionMenu(self.camera_menu, query=True, value=True)
                if selected_item == "<当前视图>":
                    return None
                # 处理正交相机的显示格式
                if selected_item.startswith("前视图"):
                    return "front"
                elif selected_item.startswith("侧视图"):
                    return "side"
                elif selected_item.startswith("顶视图"):
                    return "top"
                return selected_item
            except Exception as e:
                cmds.warning(f"获取选择相机时出错: {str(e)}")
                return None
        
    def on_scale_change(self, *args):
        scale_value = cmds.floatField(self.scale_field, query=True, value=True)
        cmds.checkBox(self.convert_checkbox, edit=True)

    def convert_to_mp4(self, mov_file):
        mov_file = mov_file.replace("\\", "/")
        mp4_file = mov_file.replace(".mov", ".mp4")
        ffmpeg_path = self.get_current_ffmpeg_path()
        if not ffmpeg_path:
            return
            
        command = [
            ffmpeg_path, '-y', '-i', mov_file, 
            '-c:v', 'libx264', '-preset', 'medium', 
            '-crf', '23', '-c:a', 'aac', '-b:a', '128k', 
            mp4_file
        ]
        try:
            subprocess.check_output(command, stderr=subprocess.STDOUT, universal_newlines=True)
            print(f"转换完成: {mp4_file}")
        except subprocess.CalledProcessError as e:
            print(f"转换失败: {mov_file}")
            print(f"错误信息: {e.output}")

    def capture_action(self, *args):
        # 高分辨率模式：先捕捉图像序列，再转换为 MOV
        
        # 获取用户指定的文件名和路径
        base_output_filename = cmds.textField(self.filename_field, query=True, text=True)
        output_path = cmds.textField(self.path_field, query=True, text=True)
        
        # 验证文件名和路径
        if not base_output_filename:
            cmds.confirmDialog(title='错误',
                               message='请输入输出文件名。',
                               button=['确定'],
                               icon='error')
            return
        
        if not output_path:
            cmds.confirmDialog(title='错误',
                               message='请选择输出路径。',
                               button=['确定'],
                               icon='error')
            return
        
        if not os.path.exists(output_path):
            user_choice = cmds.confirmDialog(title='路径不存在',
                               message=f'输出路径 "{output_path}" 不存在。是否创建此路径？',
                               button=['创建', '取消'],
                               defaultButton='创建',
                               cancelButton='取消',
                               dismissString='取消')
            if user_choice == '创建':
                try:
                    os.makedirs(output_path, exist_ok=True)
                except Exception as e:
                    cmds.confirmDialog(title='错误',
                                   message=f'无法创建路径: {str(e)}',
                                   button=['确定'],
                                   icon='error')
                    return
            else:
                return

        # 获取选择的相机
        selected_cameras = self.get_selected_cameras()
        
        # 检查是否开启强制覆盖模式
        force_overwrite = cmds.checkBox(self.force_overwrite_checkbox, query=True, value=True)
        
        # 简化重名确认弹窗
        if not force_overwrite:
            for camera in selected_cameras:
                # 设置当前相机的输出文件名
                # 单相机模式下不添加相机后缀
                if self.multi_camera_mode:
                    camera_suffix = self.get_camera_suffix(camera)
                    output_filename = f"{base_output_filename}{camera_suffix}"
                else:
                    output_filename = base_output_filename
                
                output_video_name = f"{output_filename}.mov"
                output_video_path = os.path.join(output_path, output_video_name)
                
                # 检查增序保存选项
                increment_save = cmds.checkBox(self.increment_checkbox, query=True, value=True)
                
                if not increment_save and os.path.exists(output_video_path):
                    # 使用简单的确认对话框
                    user_choice = cmds.confirmDialog(
                        title='文件已存在',
                        message=f"{output_video_path} 已存在。是否覆盖？",
                        button=['是', '否'],
                        defaultButton='否',
                        cancelButton='否',
                        dismissString='否'
                    )
                    
                    if user_choice == '否':
                        cmds.warning(f"用户取消了覆盖 {output_video_path}，拍屏操作被中止。")
                        return
                    break

        # 音频相关设置
        audio_offset_frames = cmds.intField(self.offset_field, query=True, value=True)
        include_audio = cmds.checkBox(self.audio_checkbox, query=True, value=True)
        audio_file_path = None
        if include_audio:
            current_audio = cmds.timeControl('timeControl1', query=True, sound=True)
            if current_audio:
                audio_start_frame = cmds.getAttr(f"{current_audio}.offset")
                timeline_start_frame = cmds.playbackOptions(q=True, min=True)
                audio_offset_frames = int(audio_start_frame - timeline_start_frame) + audio_offset_frames
                audio_file_path = cmds.getAttr(f"{current_audio}.filename")
            else:
                cmds.warning("时间轴未绑定任何音频，将跳过音频相关操作。")
                include_audio = False
        
        # 记录原始相机
        original_camera = cmds.lookThru(q=True)
        
        # 创建临时目录（确保在循环外部创建一次即可）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.temp_dir = tempfile.mkdtemp(prefix=f"maya_playblast_{timestamp}_")
        
        # 处理每个选定的相机
        video_files = []
        for camera in selected_cameras:
            # 设置当前相机的输出文件名
            camera_display_name = self.get_camera_display_name(camera)
            
            # 单相机模式下不添加相机后缀
            if self.multi_camera_mode:
                camera_suffix = self.get_camera_suffix(camera)
                output_filename = f"{base_output_filename}{camera_suffix}"
            else:
                camera_suffix = ""
                output_filename = base_output_filename
            
            print(f"======= 开始处理相机: {camera_display_name} =======")
            
            # 为此相机执行playblast
            image_folder = self.playblast_camera(camera)
            if not image_folder:
                cmds.warning(f"相机 {camera_display_name} 的 Playblast 失败，跳过此相机。")
                continue
            
            # 处理图像序列
            self.rename_images(image_folder)
            import maya.mel as mel
            frame_rate_in_maya = mel.eval('currentTimeUnitToFPS')
            resolution_width = cmds.getAttr("defaultResolution.width")
            resolution_height = cmds.getAttr("defaultResolution.height")
            
            # 构建完整的输出路径
            output_video_name = f"{output_filename}.mov"
            output_video_path = os.path.join(output_path, output_video_name)
            
            # 检查增序保存选项
            increment_save = cmds.checkBox(self.increment_checkbox, query=True, value=True)
            if increment_save:
                base_name, ext = os.path.splitext(output_video_name)
                output_video_path = self.incremented_filename(output_path, base_name, ext)
                
            # 转换为视频
            video_file, _ = self.convert_images_to_video(
                image_folder=image_folder,
                frame_rate=frame_rate_in_maya,
                audio_file=audio_file_path,
                output_video_path=output_video_path,
                audio_offset_frames=audio_offset_frames
            )
            
            if video_file:
                print(f"相机 {camera_display_name} 的视频文件创建成功: {video_file}")
                video_files.append(video_file)
                
                # 处理转换选项
                self.check_and_convert_to_mp4(video_file)
                
                # 处理GIF转换
                if cmds.checkBox(self.gif_checkbox, query=True, value=True):
                    fps = mel.eval('currentTimeUnitToFPS')
                    
                    # 生成GIF文件路径，单相机模式不添加后缀
                    gif_output_path = self.get_gif_output_path(video_file, camera_suffix if self.multi_camera_mode else "")
                    
                    gif_file = self.convert_mov_to_gif(video_file, fps, (resolution_width, resolution_height), gif_output_path)
                    if gif_file:
                        print(f"相机 {camera_display_name} 的GIF文件创建成功: {gif_file}")
            else:
                cmds.warning(f"相机 {camera_display_name} 的视频转换失败。")
            
            print(f"======= 完成处理相机: {camera_display_name} =======")
        
        # 恢复原始相机视图
        cmds.lookThru(original_camera)
        
        # 清理临时目录
        self.cleanup_temp_dir()
        
        # 打开创建的视频文件
        for video_file in video_files:
            self.open_default_player(video_file)

    def qt_playblast_action(self, *args):
        # 低分辨率模式：直接生成 MOV 视频
        scale_value = cmds.floatField(self.scale_field, query=True, value=True)
        scale_value = round(scale_value, 1)
        
        # 获取用户指定的文件名和路径
        base_output_filename = cmds.textField(self.filename_field, query=True, text=True)
        output_path = cmds.textField(self.path_field, query=True, text=True)
        
        # 验证文件名和路径
        if not base_output_filename:
            cmds.confirmDialog(title='错误',
                               message='请输入输出文件名。',
                               button=['确定'],
                               icon='error')
            return
        
        if not output_path:
            cmds.confirmDialog(title='错误',
                               message='请选择输出路径。',
                               button=['确定'],
                               icon='error')
            return
        
        if not os.path.exists(output_path):
            user_choice = cmds.confirmDialog(title='路径不存在',
                               message=f'输出路径 "{output_path}" 不存在。是否创建此路径？',
                               button=['创建', '取消'],
                               defaultButton='创建',
                               cancelButton='取消',
                               dismissString='取消')
            if user_choice == '创建':
                try:
                    os.makedirs(output_path, exist_ok=True)
                except Exception as e:
                    cmds.confirmDialog(title='错误',
                                   message=f'无法创建路径: {str(e)}',
                                   button=['确定'],
                                   icon='error')
                    return
            else:
                return
                
        if not (0.1 <= scale_value <= 1.0):
            cmds.warning("缩放值应在0.1到1.0之间。")
            return

        # 获取选择的相机
        selected_cameras = self.get_selected_cameras()
        
        # 检查是否开启强制覆盖模式
        force_overwrite = cmds.checkBox(self.force_overwrite_checkbox, query=True, value=True)
        
        # 简化重名确认弹窗
        if not force_overwrite:
            for camera in selected_cameras:
                # 单相机模式下不添加相机后缀
                if self.multi_camera_mode:
                    camera_suffix = self.get_camera_suffix(camera)
                    output_filename = f"{base_output_filename}{camera_suffix}"
                else:
                    output_filename = base_output_filename
                
                output_video_name = f"{output_filename}.mov"
                output_video_path = os.path.join(output_path, output_video_name)
                
                # 检查增序保存选项
                increment_save = cmds.checkBox(self.increment_checkbox, query=True, value=True)
                
                if not increment_save and os.path.exists(output_video_path):
                    # 使用简单的确认对话框
                    user_choice = cmds.confirmDialog(
                        title='文件已存在',
                        message=f"{output_video_path} 已存在。是否覆盖？",
                        button=['是', '否'],
                        defaultButton='否',
                        cancelButton='否',
                        dismissString='否'
                    )
                    
                    if user_choice == '否':
                        cmds.warning(f"用户取消了覆盖 {output_video_path}，拍屏操作被中止。")
                        return
                    break

        resolution_width = cmds.getAttr("defaultResolution.width")
        resolution_height = cmds.getAttr("defaultResolution.height")
        include_audio = cmds.checkBox(self.audio_checkbox, query=True, value=True)
        audio_node = None
        if include_audio:
            current_audio = cmds.timeControl('timeControl1', query=True, sound=True)
            if current_audio:
                audio_node = current_audio
            else:
                cmds.warning("时间轴未绑定任何音频。")
        
        # 记录原始相机
        original_camera = cmds.lookThru(q=True)
        
        # 处理每个选定的相机
        video_files = []
        for camera in selected_cameras:
            # 设置当前相机的输出文件名
            camera_display_name = self.get_camera_display_name(camera)
            
            # 单相机模式下不添加相机后缀
            if self.multi_camera_mode:
                camera_suffix = self.get_camera_suffix(camera)
                output_filename = f"{base_output_filename}{camera_suffix}"
            else:
                camera_suffix = ""
                output_filename = base_output_filename
            
            print(f"======= 开始处理相机: {camera_display_name} =======")
            
            # 构建完整的输出路径
            output_video_name = f"{output_filename}.mov"
            output_video_path = os.path.join(output_path, output_video_name)
            
            # 检查增序保存选项
            increment_save = cmds.checkBox(self.increment_checkbox, query=True, value=True)
            if increment_save:
                base_name, ext = os.path.splitext(output_video_name)
                output_video_path = self.incremented_filename(output_path, base_name, ext)
            
            # 如果有指定相机，切换到该相机
            previous_camera = None
            if camera:
                previous_camera = cmds.lookThru(q=True)
                cmds.lookThru(camera)
                
            try:
                playblast_args = {
                    "format": "qt",
                    "filename": output_video_path,
                    "forceOverwrite": True,
                    "sequenceTime": 0,
                    "clearCache": 1,
                    "showOrnaments": 1,
                    "widthHeight": (resolution_width, resolution_height),
                    "percent": int(scale_value * 100),
                    "quality": 100,
                    "compression": "H.264",
                    "viewer": False
                }
                if audio_node:
                    playblast_args["sound"] = audio_node

                cmds.playblast(**playblast_args)
                
                # 如果切换了相机，切回原来的相机
                if previous_camera:
                    cmds.lookThru(previous_camera)
                    
                print(f"相机 {camera_display_name} 的QT拍屏成功: {output_video_path}")
                video_files.append(output_video_path)
                
                # 处理转换选项
                self.check_and_convert_to_mp4(output_video_path)
                
                # 处理GIF转换
                if cmds.checkBox(self.gif_checkbox, query=True, value=True):
                    import maya.mel as mel
                    fps = mel.eval('currentTimeUnitToFPS')
                    final_width = int(resolution_width * scale_value)
                    final_height = int(resolution_height * scale_value)
                    
                    # 生成GIF文件路径，单相机模式不添加后缀
                    gif_output_path = self.get_gif_output_path(output_video_path, camera_suffix if self.multi_camera_mode else "")
                    
                    gif_file = self.convert_mov_to_gif(output_video_path, fps, (final_width, final_height), gif_output_path)
                    if gif_file:
                        print(f"相机 {camera_display_name} 的GIF文件创建成功: {gif_file}")

            except Exception as e:
                # 如果切换了相机，确保切回原来的相机
                if previous_camera:
                    cmds.lookThru(previous_camera)
                    
                cmds.warning(f"相机 {camera_display_name} 的QT拍屏失败: {str(e)}")
                
            print(f"======= 完成处理相机: {camera_display_name} =======")
        
        # 恢复原始相机视图
        cmds.lookThru(original_camera)
        
        # 打开创建的视频文件
        for video_file in video_files:
            self.open_default_player(video_file)

    def check_and_convert_to_mp4(self, mov_file_path):
        if cmds.checkBox(self.convert_checkbox, query=True, value=True):
            self.convert_to_mp4(mov_file_path)

    def incremented_filename(self, dir_path, base_name, extension):
        i = 1
        new_name = f"{base_name}_{i}{extension}"
        while os.path.exists(os.path.join(dir_path, new_name)):
            i += 1
            new_name = f"{base_name}_{i}{extension}"
        return os.path.join(dir_path, new_name)

    def playblast_camera(self, camera):
        """为指定相机执行playblast，如果camera为None则使用当前视图"""
        if camera is not None:
            # 检查相机是否存在
            if not cmds.objExists(camera):
                cmds.warning(f"相机 {camera} 不存在。")
                return None
                
        # 获取活动相机或使用指定相机
        active_camera = camera if camera else cmds.lookThru(q=True)
        
        if not active_camera and not camera:
            cmds.warning("没有活动相机，请设置一个活动相机。")
            return None

        resolution_width = cmds.getAttr("defaultResolution.width")
        resolution_height = cmds.getAttr("defaultResolution.height")
        
        output_folder = os.path.join(self.temp_dir, f"camera_{camera if camera else 'current'}")
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        output_file = os.path.join(output_folder, "capture")
        
        # 如果指定了相机，切换到该相机视图
        previous_camera = None
        if camera:
            previous_camera = cmds.lookThru(q=True)
            cmds.lookThru(camera)
            
        try:
            cmds.playblast(
                format="image",
                sequenceTime=0,
                clearCache=1,
                showOrnaments=1,
                fp=4,
                percent=100,
                compression="jpg",
                quality=100,
                widthHeight=(resolution_width, resolution_height),
                filename=output_file,
                forceOverwrite=True,
                viewer=False
            )
            
            # 如果切换了相机，切回原来的相机
            if previous_camera:
                cmds.lookThru(previous_camera)
                
        except Exception as e:
            # 如果切换了相机，确保切回原来的相机
            if previous_camera:
                cmds.lookThru(previous_camera)
                
            cmds.warning(f"相机 {camera if camera else '当前视图'} 的Playblast失败: {str(e)}")
            return None
            
        return output_folder

    def playblast_current_camera(self):
        """为当前相机执行playblast（向后兼容，实际调用playblast_camera）"""
        # 获取用户选择的相机，或使用当前视图
        selected_camera = self.get_selected_camera()
        return self.playblast_camera(selected_camera)

    def rename_images(self, folder_path, prefix='renamed_capture.', extension='jpg'):
        files = os.listdir(folder_path)
        image_files = [f for f in files if f.lower().endswith('.' + extension.lower())]
        def extract_number(f):
            match = re.search(r'capture\.([-+]?\d+)\.' + re.escape(extension), f)
            if match:
                try:
                    return int(match.group(1))
                except ValueError:
                    return float('inf')
            else:
                return float('inf')
        image_files_sorted = sorted(image_files, key=extract_number)
        
        # 检查是否启用了"拍一"效果
        on_hold = cmds.checkBox(self.on_hold_checkbox, query=True, value=True)
        if on_hold:
            # 获取"几拍一"的设置值，验证输入
            hold_frames_text = cmds.textField(self.hold_frames_field, query=True, text=True)
            try:
                hold_frames = int(hold_frames_text)
                # 确保值在合理范围内
                if hold_frames < 2:
                    hold_frames = 2
                    cmds.textField(self.hold_frames_field, edit=True, text="2")
                    cmds.warning("拍一值必须大于等于2，已自动设置为2。")
                elif hold_frames > 10:
                    hold_frames = 10
                    cmds.textField(self.hold_frames_field, edit=True, text="10")
                    cmds.warning("拍一值必须小于等于10，已自动设置为10。")
            except ValueError:
                # 如果输入不是有效数字，默认为2
                hold_frames = 2
                cmds.textField(self.hold_frames_field, edit=True, text="2")
                cmds.warning("拍一值必须是数字，已自动设置为2。")
                
            # 创建新的文件列表，只包含第一帧并重复指定次数
            processed_files = []
            for i in range(0, len(image_files_sorted), hold_frames):
                if i < len(image_files_sorted):
                    # 将第一帧重复指定次数
                    processed_files.extend([image_files_sorted[i]] * hold_frames)
            image_files_sorted = processed_files
            
        for i, image_file in enumerate(image_files_sorted):
            new_name = f'{prefix}{i:04d}.{extension}'
            if on_hold:
                # 对于"拍一"效果，我们复制文件而不是重命名
                src_path = os.path.join(folder_path, image_file)
                dst_path = os.path.join(folder_path, new_name)
                try:
                    shutil.copy2(src_path, dst_path)
                except Exception as e:
                    cmds.warning(f"无法复制 {image_file} 到 {new_name}: {str(e)}")
            else:
                # 原有的重命名逻辑
                old_path = os.path.join(folder_path, image_file)
                new_path = os.path.join(folder_path, new_name)
                try:
                    os.rename(old_path, new_path)
                except Exception as e:
                    cmds.warning(f"无法重命名 {image_file} 到 {new_name}: {str(e)}")

    def get_audio_file(self):
        audio_nodes = cmds.ls(type='audio')
        if not audio_nodes:
            return None
        for node in audio_nodes:
            try:
                audio_file = cmds.getAttr(node + '.filename')
                if not os.path.isabs(audio_file):
                    scene_dir = os.path.dirname(cmds.file(q=True, sceneName=True))
                    audio_file = os.path.abspath(os.path.join(scene_dir, audio_file))
                if os.path.exists(audio_file):
                    return audio_file
            except:
                continue
        return None

    def convert_images_to_video(self, image_folder, frame_rate, audio_file=None, output_video_path=None, audio_offset_frames=0):
        try:
            if not output_video_path:
                folder_name = os.path.basename(image_folder.rstrip(os.sep))
                parent_folder = os.path.dirname(image_folder)
                output_video_name = f"{folder_name}.mov"
                output_video_path = os.path.join(parent_folder, output_video_name)
            offset_str = str(audio_offset_frames / frame_rate) if audio_offset_frames != 0 else None
            image_files = [f for f in os.listdir(image_folder) if f.lower().endswith('.jpg')]
            total_frames = len(image_files)
            if total_frames == 0:
                raise FileNotFoundError(f"图像序列为空：{image_folder}")
                
            ffmpeg_path = self.get_current_ffmpeg_path()
            if not ffmpeg_path:
                return None, None
                
            ffmpeg_input = os.path.join(image_folder, 'renamed_capture.%04d.jpg')
            ffmpeg_cmd = [
                ffmpeg_path,
                '-y',
                '-thread_queue_size', '8',
                '-framerate', str(frame_rate),
                '-i', ffmpeg_input,
            ]
            if audio_file:
                if offset_str:
                    ffmpeg_cmd.extend(['-itsoffset', offset_str, '-i', audio_file])
                else:
                    ffmpeg_cmd.extend(['-i', audio_file])
                ffmpeg_cmd.extend([
                    '-c:v', 'libx264',
                    '-c:a', 'aac',
                    '-pix_fmt', 'yuv420p',
                    '-frames:v', str(total_frames),
                    output_video_path
                ])
            else:
                ffmpeg_cmd.extend([
                    '-c:v', 'libx264',
                    '-pix_fmt', 'yuv420p',
                    '-frames:v', str(total_frames),
                    output_video_path
                ])
            subprocess.run(ffmpeg_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
            if not os.path.exists(output_video_path):
                raise Exception("FFmpeg 未能创建视频文件。")
            return output_video_path, None
        except Exception as e:
            cmds.warning("图像序列转视频失败: {}".format(str(e)))
            return None, None

    def convert_mov_to_gif(self, mov_file, fps, resolution, output_gif_path=None):
        """
        将 MOV 视频转换为 GIF
        :param mov_file: 输入的视频文件路径
        :param fps: 视频帧率
        :param resolution: (width, height) 输出 GIF 的分辨率
        :param output_gif_path: 可选，输出 GIF 文件路径
        :return: 输出 GIF 文件路径（转换成功时），否则返回 None
        """
        try:
            if not output_gif_path:
                # 使用与视频相同的基本名称，但确保保留相机后缀
                dir_name = os.path.dirname(mov_file)
                base_name = os.path.splitext(os.path.basename(mov_file))[0]
                output_gif_path = os.path.join(dir_name, f"{base_name}.gif")
                
            ffmpeg_path = self.get_current_ffmpeg_path()
            if not ffmpeg_path:
                return None
                
            width, height = resolution
            ffmpeg_cmd = [
                ffmpeg_path,
                '-y',
                '-i', mov_file,
                '-vf', f'fps={fps},scale={width}:{height}:flags=lanczos',
                output_gif_path
            ]
            subprocess.run(ffmpeg_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
            if not os.path.exists(output_gif_path):
                raise Exception("FFmpeg 未能生成 GIF 文件。")
            print(f"GIF 生成成功: {output_gif_path}")
            return output_gif_path
        except Exception as e:
            cmds.warning("转换 MOV 为 GIF 失败: {}".format(str(e)))
            return None

    def open_default_player(self, video_file):
        try:
            if os.name == 'nt':
                os.startfile(video_file)
            elif os.name == 'posix':
                subprocess.call(['open', video_file] if sys.platform == 'darwin' else ['xdg-open', video_file])
            else:
                cmds.warning("无法识别的操作系统，无法打开视频文件。")
        except Exception as e:
            cmds.warning("打开视频文件失败: {}".format(str(e)))

    def cleanup_temp_dir(self):
        try:
            if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
        except Exception as e:
            cmds.warning("清理临时文件夹失败: {}".format(str(e)))

    def switch_camera_mode(self, mode):
        """安全地切换相机选择模式"""
        try:
            if mode == "single" and self.multi_camera_mode:
                # 从多相机模式切换到单相机模式
                self.multi_camera_mode = False
                
                # 更新UI
                cmds.frameLayout(self.single_camera_frame, edit=True, visible=True)
                cmds.frameLayout(self.multi_camera_frame, edit=True, visible=False)
                
                # 更新按钮样式
                cmds.button(self.single_mode_button, edit=True, backgroundColor=[0.3, 0.5, 0.8])
                cmds.button(self.multi_mode_button, edit=True, backgroundColor=[0.5, 0.5, 0.5])
                
                # 调整窗口高度
                self.adjust_window_size()
                
            elif mode == "multi" and not self.multi_camera_mode:
                # 从单相机模式切换到多相机模式
                self.multi_camera_mode = True
                
                # 更新UI
                cmds.frameLayout(self.single_camera_frame, edit=True, visible=False)
                cmds.frameLayout(self.multi_camera_frame, edit=True, visible=True)
                
                # 更新按钮样式
                cmds.button(self.single_mode_button, edit=True, backgroundColor=[0.5, 0.5, 0.5])
                cmds.button(self.multi_mode_button, edit=True, backgroundColor=[0.3, 0.5, 0.8])
                
                # 调整窗口高度
                self.adjust_window_size()
                
        except Exception as e:
            cmds.warning(f"切换相机模式时出错: {str(e)}")
            # 出错时强制恢复到单相机模式
            self.multi_camera_mode = False
            try:
                cmds.frameLayout(self.single_camera_frame, edit=True, visible=True)
                cmds.frameLayout(self.multi_camera_frame, edit=True, visible=False)
                cmds.button(self.single_mode_button, edit=True, backgroundColor=[0.3, 0.5, 0.8])
                cmds.button(self.multi_mode_button, edit=True, backgroundColor=[0.5, 0.5, 0.5])
            except:
                pass
            
    def select_all_cameras(self, value, *args):
        """选择或取消选择所有相机"""
        if not self.multi_camera_mode:
            return
        
        try:
            for cam, checkbox in self.camera_checkboxes.items():
                if cmds.checkBox(checkbox, exists=True):
                    cmds.checkBox(checkbox, edit=True, value=value)
        except Exception as e:
            cmds.warning(f"选择所有相机时出错: {str(e)}")
    
    def invert_camera_selection(self, *args):
        """反转相机选择状态"""
        if not self.multi_camera_mode:
            return
        
        try:
            for cam, checkbox in self.camera_checkboxes.items():
                if cmds.checkBox(checkbox, exists=True):
                    current_value = cmds.checkBox(checkbox, query=True, value=True)
                    cmds.checkBox(checkbox, edit=True, value=not current_value)
        except Exception as e:
            cmds.warning(f"反转相机选择时出错: {str(e)}")
    
    def get_selected_cameras(self):
        """获取用户选择的所有相机列表"""
        if not self.multi_camera_mode:
            # 单相机模式
            try:
                selected_item = cmds.optionMenu(self.camera_menu, query=True, value=True)
                if selected_item == "<当前视图>":
                    return [None]
                # 处理正交相机的显示格式
                if selected_item.startswith("前视图"):
                    return ["front"]
                elif selected_item.startswith("侧视图"):
                    return ["side"]
                elif selected_item.startswith("顶视图"):
                    return ["top"]
                return [selected_item]
            except Exception as e:
                cmds.warning(f"获取选择相机时出错: {str(e)}")
                return [None]
        else:
            # 多相机模式
            try:
                selected_cameras = []
                for cam, checkbox in self.camera_checkboxes.items():
                    if not cmds.checkBox(checkbox, exists=True):
                        continue
                    if cmds.checkBox(checkbox, query=True, value=True):
                        if cam == "<当前视图>":
                            selected_cameras.append(None)
                        else:
                            selected_cameras.append(cam)
                
                # 如果没有选择任何相机，默认使用当前视图
                if not selected_cameras:
                    selected_cameras = [None]
                
                return selected_cameras
            except Exception as e:
                cmds.warning(f"获取选择相机列表时出错: {str(e)}")
                return [None]

    def get_camera_display_name(self, camera):
        """获取相机的显示名称"""
        if camera is None:
            return "当前视图"
        elif camera == "front":
            return "前视图 (front)"
        elif camera == "side":
            return "侧视图 (side)"
        elif camera == "top":
            return "顶视图 (top)"
        else:
            return camera
            
    def get_camera_suffix(self, camera):
        """获取相机的文件名后缀"""
        if camera is None:
            return "_currentView"
        else:
            return f"_{camera}"
            
    def get_gif_output_path(self, mov_file, camera_suffix):
        """根据MOV文件路径和相机后缀生成GIF输出路径"""
        dir_name = os.path.dirname(mov_file)
        base_name = os.path.splitext(os.path.basename(mov_file))[0]
        
        # 确保base_name中已经包含了相机后缀，避免重复添加
        if camera_suffix and not base_name.endswith(camera_suffix):
            base_name += camera_suffix
            
        return os.path.join(dir_name, f"{base_name}.gif")

    # 注意：FFmpeg设置相关的UI方法已移至独立设置窗口中
    
    def test_ffmpeg_path(self, *args):
        """测试当前FFmpeg路径是否有效"""
        try:
            print("=" * 60)
            print("FFmpeg 路径测试开始")
            print("=" * 60)
            
            # 显示当前设置信息
            print(f"当前FFmpeg模式: {self.ffmpeg_mode}")
            if self.ffmpeg_mode == "local":
                print(f"自定义路径: {self.ffmpeg_custom_path}")
            else:
                print("使用系统环境变量中的FFmpeg")
            
            ffmpeg_path = self.get_current_ffmpeg_path()
            if not ffmpeg_path:
                error_msg = "未找到有效的FFmpeg路径"
                print(f"错误: {error_msg}")
                cmds.confirmDialog(
                    title='测试失败',
                    message='未找到FFmpeg',
                    button=['确定'],
                    icon='warning'
                )
                return
            
            print(f"实际测试路径: {ffmpeg_path}")
            
            # 测试FFmpeg是否可以运行
            if ffmpeg_path == 'ffmpeg':
                # 系统环境变量
                test_cmd = ['ffmpeg', '-version']
                print("测试命令: ffmpeg -version (系统环境变量)")
            else:
                # 自定义路径
                test_cmd = [ffmpeg_path, '-version']
                print(f"测试命令: \"{ffmpeg_path}\" -version")
                
            try:
                print("正在执行测试...")
                result = subprocess.run(test_cmd, capture_output=True, text=True, timeout=5)
                
                print(f"进程返回码: {result.returncode}")
                
                if result.returncode == 0:
                    print("? FFmpeg测试成功！")
                    
                    # 输出版本信息到控制台
                    if result.stdout:
                        print("FFmpeg版本信息:")
                        version_lines = result.stdout.split('\n')[:3]  # 只显示前3行
                        for line in version_lines:
                            if line.strip():
                                print(f"  {line.strip()}")
                    
                    cmds.confirmDialog(
                        title='测试成功',
                        message='FFmpeg配置正确',
                        button=['确定'],
                        icon='information'
                    )
                else:
                    error_info = result.stderr.strip() if result.stderr else "未知错误"
                    print("? FFmpeg测试失败")
                    print(f"错误信息: {error_info}")
                    
                    cmds.confirmDialog(
                        title='测试失败',
                        message='FFmpeg配置有误',
                        button=['确定'],
                        icon='critical'
                    )
            except subprocess.TimeoutExpired:
                error_msg = "FFmpeg测试超时（5秒），可能路径不正确或FFmpeg响应缓慢"
                print(f"? {error_msg}")
                cmds.confirmDialog(
                    title='测试失败',
                    message='FFmpeg响应超时',
                    button=['确定'],
                    icon='warning'
                )
            except Exception as e:
                error_msg = f"执行测试时出错: {str(e)}"
                print(f"? {error_msg}")
                cmds.confirmDialog(
                    title='测试失败',
                    message='FFmpeg配置错误',
                    button=['确定'],
                    icon='critical'
                )
        except Exception as e:
            error_msg = f"测试FFmpeg时出错: {str(e)}"
            print(f"? {error_msg}")
            cmds.warning(error_msg)
        finally:
            print("=" * 60)
            print("FFmpeg 路径测试结束")
            print("=" * 60)
            
    # 注意：reset_ffmpeg_settings 方法已移至设置窗口中
        
    def get_current_ffmpeg_path(self):
        """获取当前设置的FFmpeg路径"""
        if self.ffmpeg_mode == "local" and self.ffmpeg_custom_path:
            if os.path.exists(self.ffmpeg_custom_path):
                return self.ffmpeg_custom_path
            else:
                cmds.warning(f"自定义FFmpeg路径不存在: {self.ffmpeg_custom_path}")
                return None
        else:
            # 使用系统环境变量或回退检测
            return get_ffmpeg_path(None)
    
    def save_ffmpeg_settings(self, *args):
        """保存当前FFmpeg设置到文件"""
        try:
            success = save_ffmpeg_settings(self.ffmpeg_mode, self.ffmpeg_custom_path)
            
            if success:
                cmds.confirmDialog(
                    title='保存成功',
                    message=f'FFmpeg设置已保存到:\n{get_settings_file_path()}\n\n模式: {self.ffmpeg_mode}\n路径: {self.ffmpeg_custom_path if self.ffmpeg_mode == "local" else "系统环境变量"}',
                    button=['确定'],
                    icon='information'
                )
            else:
                cmds.confirmDialog(
                    title='保存失败',
                    message='无法保存FFmpeg设置，请检查文件权限',
                    button=['确定'],
                    icon='warning'
                )
        except Exception as e:
            cmds.warning(f"保存设置时出错: {str(e)}")
            
    def open_settings_directory(self, *args):
        """打开设置文件所在目录"""
        try:
            settings_file = get_settings_file_path()
            settings_dir = os.path.dirname(settings_file)
            
            # 确保目录存在
            if not os.path.exists(settings_dir):
                os.makedirs(settings_dir, exist_ok=True)
            
            # 打开目录
            if os.name == 'nt':  # Windows
                os.startfile(settings_dir)
            elif os.name == 'posix':  # macOS/Linux
                subprocess.call(['open', settings_dir] if sys.platform == 'darwin' else ['xdg-open', settings_dir])
            else:
                cmds.confirmDialog(
                    title='设置目录',
                    message=f'设置文件位于:\n{settings_file}',
                    button=['确定'],
                    icon='information'
                )
        except Exception as e:
            cmds.warning(f"打开设置目录时出错: {str(e)}")
            cmds.confirmDialog(
                title='设置目录',
                message=f'设置文件位于:\n{get_settings_file_path()}',
                button=['确定'],
                icon='information'
            )
    
    def open_ffmpeg_settings(self, *args):
        """打开FFmpeg设置窗口"""
        settings_window_name = "ffmpeg_settings_window"
        
        # 如果窗口已存在，先删除
        if cmds.window(settings_window_name, exists=True):
            cmds.deleteUI(settings_window_name, window=True)
        
        # 创建设置窗口
        settings_window = cmds.window(
            settings_window_name,
            title="FFmpeg设置",
            sizeable=False,
            minimizeButton=False,
            maximizeButton=False,
            widthHeight=(260, 230)
        )
        
        # 添加边距的框架
        margin_frame = cmds.frameLayout(labelVisible=False, borderVisible=False, marginWidth=10, marginHeight=10)
        main_column = cmds.columnLayout(adjustableColumn=True, columnAlign="center", rowSpacing=8, parent=margin_frame)
        
        # 标题
        cmds.text(label="FFmpeg路径配置", font="boldLabelFont", height=15)
        cmds.separator(height=1, style='in')
        
        # FFmpeg路径模式选择
        mode_row = cmds.rowColumnLayout(numberOfColumns=2, columnWidth=[(1, 80), (2, 100)], parent=main_column)
        cmds.text(label="FFmpeg模式:", align='left')
        self.settings_ffmpeg_mode_menu = cmds.optionMenu(width=100, changeCommand=self.on_settings_ffmpeg_mode_change)
        cmds.menuItem(label="系统环境变量")
        cmds.menuItem(label="本地文件路径")
        
        # 自定义路径输入区域
        cmds.setParent(main_column)
        path_row = cmds.rowColumnLayout(numberOfColumns=3, columnWidth=[(1, 80), (2, 100), (3, 60)], parent=main_column)
        cmds.text(label="自定义路径:", align='left')
        self.settings_ffmpeg_path_field = cmds.textField(text="", width=100, enable=False)
        self.settings_ffmpeg_browse_button = cmds.button(label="浏览", command=self.settings_browse_ffmpeg_path, width=60, enable=False)
        
        # 路径状态显示
        cmds.setParent(main_column)
        self.settings_ffmpeg_status_text = cmds.text(label="状态: 使用系统环境变量中的FFmpeg", align='center', wordWrap=True, height=20)
        
        cmds.separator(height=5, style='in')
        
        # 操作按钮
        button_row1 = cmds.rowColumnLayout(numberOfColumns=2, columnWidth=[(1, 120), (2, 120)], parent=main_column)
        cmds.button(label="测试FFmpeg", command=self.test_ffmpeg_path, height=30)
        cmds.button(label="保存设置", command=self.settings_save_and_close, height=30, backgroundColor=[0.4, 0.6, 0.4])
        
        cmds.setParent(main_column)
        button_row2 = cmds.rowColumnLayout(numberOfColumns=2, columnWidth=[(1, 120), (2, 120)], parent=main_column)
        cmds.button(label="重置为默认", command=self.settings_reset_ffmpeg, height=30)
        cmds.button(label="打开设置目录", command=self.open_settings_directory, height=30)
        
        # 应用当前设置到设置窗口
        self.apply_settings_to_window()
        
        # 显示窗口
        cmds.showWindow(settings_window)
    
    def apply_settings_to_window(self):
        """将当前设置应用到设置窗口"""
        try:
            if self.ffmpeg_mode == "local" and self.ffmpeg_custom_path:
                # 应用本地路径设置
                cmds.optionMenu(self.settings_ffmpeg_mode_menu, edit=True, value="本地文件路径")
                cmds.textField(self.settings_ffmpeg_path_field, edit=True, enable=True, text=self.ffmpeg_custom_path)
                cmds.button(self.settings_ffmpeg_browse_button, edit=True, enable=True)
                
                # 验证路径是否存在
                if os.path.exists(self.ffmpeg_custom_path):
                    cmds.text(self.settings_ffmpeg_status_text, edit=True, label="状态: 使用本地FFmpeg路径")
                else:
                    cmds.text(self.settings_ffmpeg_status_text, edit=True, label="状态: 路径不存在，请重新选择")
            else:
                # 应用系统环境变量设置
                cmds.optionMenu(self.settings_ffmpeg_mode_menu, edit=True, value="系统环境变量")
                cmds.textField(self.settings_ffmpeg_path_field, edit=True, enable=False, text="")
                cmds.button(self.settings_ffmpeg_browse_button, edit=True, enable=False)
                cmds.text(self.settings_ffmpeg_status_text, edit=True, label="状态: 使用系统环境变量中的FFmpeg")
        except Exception as e:
            print(f"应用设置到窗口时出错: {str(e)}")
    
    def on_settings_ffmpeg_mode_change(self, *args):
        """设置窗口中FFmpeg模式切换时的回调"""
        try:
            selected_mode = cmds.optionMenu(self.settings_ffmpeg_mode_menu, query=True, value=True)
            
            if selected_mode == "系统环境变量":
                self.ffmpeg_mode = "system"
                self.ffmpeg_custom_path = ""
                # 禁用路径输入
                cmds.textField(self.settings_ffmpeg_path_field, edit=True, enable=False, text="")
                cmds.button(self.settings_ffmpeg_browse_button, edit=True, enable=False)
                cmds.text(self.settings_ffmpeg_status_text, edit=True, label="状态: 使用系统环境变量中的FFmpeg")
            elif selected_mode == "本地文件路径":
                self.ffmpeg_mode = "local"
                # 启用路径输入
                cmds.textField(self.settings_ffmpeg_path_field, edit=True, enable=True, text=self.ffmpeg_custom_path)
                cmds.button(self.settings_ffmpeg_browse_button, edit=True, enable=True)
                # 自动检测本地FFmpeg
                self.settings_auto_detect_local_ffmpeg()
        except Exception as e:
            print(f"设置窗口模式切换出错: {str(e)}")
    
    def settings_auto_detect_local_ffmpeg(self):
        """设置窗口中自动检测FFmpeg路径"""
        try:
            detected_ffmpeg, _ = auto_detect_ffmpeg()
            
            if detected_ffmpeg and detected_ffmpeg != 'ffmpeg':
                # 系统环境变量中的FFmpeg
                cmds.text(self.settings_ffmpeg_status_text, edit=True, label="状态: 已检测到系统环境变量中的FFmpeg")
            else:
                cmds.text(self.settings_ffmpeg_status_text, edit=True, label="状态: 请手动选择FFmpeg.exe文件")
        except Exception as e:
            error_msg = f"状态: 自动检测失败，请手动选择"
            cmds.text(self.settings_ffmpeg_status_text, edit=True, label=error_msg)
            print(f"设置窗口FFmpeg自动检测详细错误: {str(e)}")
    
    def settings_browse_ffmpeg_path(self, *args):
        """设置窗口中浏览选择FFmpeg路径"""
        try:
            # 使用用户文档目录作为初始目录
            initial_dir = os.path.expanduser("~/Documents")
                
            result = cmds.fileDialog2(
                fileMode=1,
                fileFilter="FFmpeg可执行文件 (*.exe)",
                caption="选择ffmpeg.exe",
                startingDirectory=initial_dir
            )
            
            if result and len(result) > 0:
                selected_path = result[0].replace("\\", "/")
                self.ffmpeg_custom_path = selected_path
                cmds.textField(self.settings_ffmpeg_path_field, edit=True, text=selected_path)
                cmds.text(self.settings_ffmpeg_status_text, edit=True, label="状态: 已设置自定义FFmpeg路径")
        except Exception as e:
            error_msg = f"选择FFmpeg路径时出错: {str(e)}"
            cmds.warning(error_msg)
            cmds.text(self.settings_ffmpeg_status_text, edit=True, label="状态: 路径选择失败，请重试")
            print(f"设置窗口FFmpeg路径选择详细错误: {str(e)}")
    
    def settings_reset_ffmpeg(self, *args):
        """设置窗口中重置FFmpeg设置为默认值"""
        self.ffmpeg_mode = "system"
        self.ffmpeg_custom_path = ""
        
        # 重置UI
        cmds.optionMenu(self.settings_ffmpeg_mode_menu, edit=True, value="系统环境变量")
        cmds.textField(self.settings_ffmpeg_path_field, edit=True, enable=False, text="")
        cmds.button(self.settings_ffmpeg_browse_button, edit=True, enable=False)
        cmds.text(self.settings_ffmpeg_status_text, edit=True, label="状态: 已重置为默认设置（系统环境变量）")
    
    def settings_save_and_close(self, *args):
        """保存设置并关闭设置窗口"""
        try:
            # 保存设置
            success = save_ffmpeg_settings(self.ffmpeg_mode, self.ffmpeg_custom_path)
            
            if success:
                # 关闭设置窗口
                settings_window_name = "ffmpeg_settings_window"
                if cmds.window(settings_window_name, exists=True):
                    cmds.deleteUI(settings_window_name, window=True)
                
                # 显示保存成功提示
                cmds.confirmDialog(
                    title='设置已保存',
                    message='FFmpeg设置保存成功',
                    button=['确定'],
                    icon='information'
                )
            else:
                cmds.confirmDialog(
                    title='保存失败',
                    message='无法保存FFmpeg设置',
                    button=['确定'],
                    icon='warning'
                )
        except Exception as e:
            cmds.warning(f"保存设置时出错: {str(e)}")
    
    def refresh_plugin(self, *args):
        """刷新插件 - 相当于重启插件"""
        try:
            # 关闭当前主窗口
            if cmds.window(self.window_name, exists=True):
                cmds.deleteUI(self.window_name, window=True)
            
            # 关闭FFmpeg设置窗口（如果存在）
            settings_window_name = "ffmpeg_settings_window"
            if cmds.window(settings_window_name, exists=True):
                cmds.deleteUI(settings_window_name, window=True)
            
            # 重新加载模块（如果可能）
            try:
                import importlib
                import sys
                
                # 尝试重新加载当前模块
                current_module_name = __name__ if __name__ != '__main__' else 'mov拍屏v9'
                if current_module_name in sys.modules:
                    importlib.reload(sys.modules[current_module_name])
            except:
                pass
            
            # 延迟创建新实例，确保UI完全清理
            def create_new_instance():
                try:
                    # 创建新的工具实例
                    global ui_instance
                    ui_instance = PlayblastConverterUI()
                except:
                    pass
            
            # 使用evalDeferred确保在UI清理完成后再创建新实例
            cmds.evalDeferred(create_new_instance)
            
        except:
            pass
    
    def refresh_filename(self, *args):
        """刷新输出文件名 - 重新获取当前场景文件名"""
        try:
            current_file_path = cmds.file(q=True, sceneName=True)
            current_file_name = os.path.splitext(os.path.basename(current_file_path))[0] if current_file_path else "untitled"
            cmds.textField(self.filename_field, edit=True, text=current_file_name)
        except:
            pass
    
    def refresh_path(self, *args):
        """刷新输出路径 - 重新获取当前场景文件目录"""
        try:
            current_file_path = cmds.file(q=True, sceneName=True)
            current_dir = os.path.dirname(current_file_path) if current_file_path else ""
            cmds.textField(self.path_field, edit=True, text=current_dir)
        except:
            pass
    
    def open_current_path(self, *args):
        """打开当前路径文件夹"""
        try:
            current_path = cmds.textField(self.path_field, query=True, text=True)
            
            # 如果路径为空，使用Maya工作空间目录
            if not current_path:
                current_path = cmds.workspace(q=True, rd=True)
            
            # 如果路径仍然为空，使用用户文档目录
            if not current_path:
                current_path = os.path.expanduser("~/Documents")
            
            # 确保路径存在
            if not os.path.exists(current_path):
                # 尝试创建目录
                try:
                    os.makedirs(current_path, exist_ok=True)
                except Exception as e:
                    cmds.warning(f"无法创建路径 {current_path}: {str(e)}")
                    return
            
            # 打开文件夹
            if os.name == 'nt':  # Windows
                os.startfile(current_path)
            elif os.name == 'posix':  # macOS/Linux
                subprocess.call(['open', current_path] if sys.platform == 'darwin' else ['xdg-open', current_path])
            else:
                cmds.warning("无法识别的操作系统，无法打开文件夹")
                
        except Exception as e:
            cmds.warning(f"打开路径失败: {str(e)}")

ui_instance = PlayblastConverterUI()