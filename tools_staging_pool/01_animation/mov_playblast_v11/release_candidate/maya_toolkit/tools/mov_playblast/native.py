# Full v11.1 source UI adaptation; original source/resources retained in upstream.
from pathlib import Path
from . import ui_bridge as bridge, runtime, media
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
    return '本次Maya会话设置；使用导出设置保存JSON'

def save_ffmpeg_settings(ffmpeg_mode, ffmpeg_custom_path):
    return bridge.save_settings(ffmpeg_mode, ffmpeg_custom_path)

def load_ffmpeg_settings():
    return dict(runtime.SETTINGS)

def auto_detect_ffmpeg():
    path = shutil.which('ffmpeg')
    return (path, 'PATH: ' + path) if path else (None, None)

def manual_select_ffmpeg():
    """
    手动选择FFmpeg路径
    返回: ffmpeg_path_code 字符串
    """
    ffmpeg_path = cmds.fileDialog2(fileMode=1, fileFilter='FFmpeg可执行文件 (*.exe)', caption='选择ffmpeg.exe', startingDirectory=os.path.expanduser('~/Documents'))
    if ffmpeg_path and len(ffmpeg_path) > 0:
        ffmpeg_path = ffmpeg_path[0].replace('\\', '/')
        return f'\n# 使用手动选择的ffmpeg路径\ncustom_ffmpeg_path = r"{ffmpeg_path}"\n'
    else:
        try:
            import shutil
            if shutil.which('ffmpeg'):
                return '\n# 用户取消选择，回退到系统环境变量中的ffmpeg\ncustom_ffmpeg_path = None\n'
        except Exception:
            pass
        cmds.warning('未选择FFmpeg路径，工具可能无法正常工作')
        return '\n# 未找到有效的ffmpeg路径\ncustom_ffmpeg_path = None\n'

def onMayaDroppedPythonFile(*args, **kwargs):
    return runtime.run_api(action='open_ui')

def get_ffmpeg_path(custom_path=None):
    try:
        return media.executable(custom_path or '')
    except ValueError as error:
        cmds.warning(str(error))
        return None

class PlayblastConverterUI:

    def __init__(self, custom_ffmpeg_path=None):
        self.custom_ffmpeg_path = custom_ffmpeg_path
        self.window_name = 'mtk_mov_playblast_candidate'
        saved_settings = load_ffmpeg_settings()
        self.ffmpeg_mode = saved_settings['ffmpeg_mode']
        self.ffmpeg_custom_path = saved_settings['ffmpeg_custom_path']
        if cmds.window(self.window_name, exists=True):
            cmds.deleteUI(self.window_name, window=True)
        self.window = cmds.window(self.window_name, title='拍屏工具', sizeable=False, minimizeButton=True, maximizeButton=False, widthHeight=(270, 320))
        main_layout = cmds.columnLayout(adjustableColumn=True, columnAlign='center', rowSpacing=3)
        menu_layout = cmds.rowColumnLayout(numberOfColumns=2, columnWidth=[(1, 55), (2, 55)], parent=main_layout)
        cmds.button(label='FFmpeg', command=self.open_ffmpeg_settings, height=20, backgroundColor=[0.4, 0.5, 0.6], annotation='FFmpeg设置')
        cmds.button(label='刷新', command=self.refresh_plugin, height=20, backgroundColor=[0.5, 0.6, 0.4])
        cmds.setParent(main_layout)
        cmds.separator(height=2, style='none')
        file_frame = cmds.frameLayout(labelVisible=False, borderVisible=False, parent=main_layout)
        file_layout = cmds.columnLayout(adjustableColumn=True, rowSpacing=2, parent=file_frame)
        filename_row = cmds.rowColumnLayout(numberOfColumns=3, columnWidth=[(1, 45), (2, 175), (3, 20)], parent=file_layout)
        cmds.text(label='文件:', align='left', font='smallPlainLabelFont')
        current_file_path = cmds.file(q=True, sceneName=True)
        current_file_name = os.path.splitext(os.path.basename(current_file_path))[0] if current_file_path else 'untitled'
        self.filename_field = cmds.textField(text=current_file_name, width=175, height=18)
        cmds.button(label='R', command=self.refresh_filename, width=20, height=18, annotation='刷新文件名')
        cmds.setParent(file_layout)
        path_row = cmds.rowColumnLayout(numberOfColumns=5, columnWidth=[(1, 45), (2, 125), (3, 20), (4, 35), (5, 35)], parent=file_layout)
        cmds.text(label='路径:', align='left', font='smallPlainLabelFont')
        current_dir = os.path.dirname(current_file_path) if current_file_path else ''
        self.path_field = cmds.textField(text=current_dir, width=125, height=18)
        cmds.button(label='R', command=self.refresh_path, width=20, height=18, annotation='刷新路径')
        cmds.button(label='浏览', command=self.browse_path, width=35, height=18)
        cmds.button(label='打开', command=self.open_current_path, width=35, height=18, annotation='打开当前路径')
        cmds.setParent(main_layout)
        cmds.separator(height=2, style='none')
        camera_frame = cmds.frameLayout(labelVisible=False, borderVisible=False, parent=main_layout)
        camera_section = cmds.columnLayout(adjustableColumn=True, rowSpacing=2, parent=camera_frame)
        mode_row = cmds.rowColumnLayout(numberOfColumns=3, columnWidth=[(1, 35), (2, 55), (3, 55)], parent=camera_section)
        cmds.text(label='相机:', align='left', font='smallPlainLabelFont')
        self.single_mode_button = cmds.button(label='单机', width=55, height=18, backgroundColor=[0.3, 0.45, 0.7], command=lambda x: self.switch_camera_mode('single'))
        self.multi_mode_button = cmds.button(label='多机', width=55, height=18, backgroundColor=[0.45, 0.45, 0.45], command=lambda x: self.switch_camera_mode('multi'))
        cmds.setParent(camera_section)
        self.single_camera_frame = cmds.frameLayout(labelVisible=False, visible=True, borderVisible=False, parent=camera_section)
        self.camera_menu = cmds.optionMenu(width=260, height=18)
        cmds.menuItem(label='<当前视图>')
        all_cameras = cmds.listCameras()
        filtered_cameras = [cam for cam in all_cameras if not cam == 'persp']
        ortho_cameras = [cam for cam in all_cameras if cam in ['front', 'side', 'top']]
        for cam in ortho_cameras:
            if cam == 'front':
                display_name = '前视图 (front)'
            elif cam == 'side':
                display_name = '侧视图 (side)'
            elif cam == 'top':
                display_name = '顶视图 (top)'
            cmds.menuItem(label=display_name)
        custom_cameras = [cam for cam in filtered_cameras if cam not in ortho_cameras]
        for cam in custom_cameras:
            cmds.menuItem(label=cam)
        cmds.setParent(camera_section)
        self.multi_camera_frame = cmds.frameLayout(labelVisible=False, visible=False, borderVisible=False)
        multi_cam_layout = cmds.columnLayout(adjustableColumn=True, rowSpacing=2)
        cmds.rowLayout(numberOfColumns=3, columnWidth3=(50, 50, 50), parent=multi_cam_layout)
        cmds.button(label='全选', height=16, command=lambda x: self.select_all_cameras(True))
        cmds.button(label='全不选', height=16, command=lambda x: self.select_all_cameras(False))
        cmds.button(label='反选', height=16, command=self.invert_camera_selection)
        cmds.setParent(multi_cam_layout)
        self.camera_scroll = cmds.scrollLayout(horizontalScrollBarThickness=0, verticalScrollBarThickness=10, height=70, width=260)
        self.camera_checkboxes = {}
        self.camera_checkboxes['<当前视图>'] = cmds.checkBox(label='<当前视图>', value=True)
        for cam in ortho_cameras:
            if cam == 'front':
                display_name = '前视图 (front)'
            elif cam == 'side':
                display_name = '侧视图 (side)'
            elif cam == 'top':
                display_name = '顶视图 (top)'
            self.camera_checkboxes[cam] = cmds.checkBox(label=display_name, value=False)
        for cam in custom_cameras:
            self.camera_checkboxes[cam] = cmds.checkBox(label=cam, value=False)
        self.multi_camera_mode = False
        cmds.setParent(main_layout)
        cmds.separator(height=3, style='none')
        record_frame = cmds.frameLayout(labelVisible=False, borderVisible=False, parent=main_layout)
        record_layout = cmds.columnLayout(adjustableColumn=True, rowSpacing=2, parent=record_frame)
        button_row = cmds.rowColumnLayout(numberOfColumns=2, columnWidth=[(1, 130), (2, 130)], parent=record_layout)
        self.high_button = cmds.button(label='高分辨率', height=24, backgroundColor=[0.3, 0.45, 0.7], command=self.capture_action)
        self.low_button = cmds.button(label='低分辨率', height=24, backgroundColor=[0.7, 0.45, 0.3], command=self.qt_playblast_action)
        cmds.setParent(record_layout)
        options_row = cmds.rowColumnLayout(numberOfColumns=4, columnWidth=[(1, 60), (2, 60), (3, 35), (4, 50)], parent=record_layout)
        self.audio_checkbox = cmds.checkBox(label='音频', value=False, changeCommand=self.toggle_audio_options)
        self.offset_field = cmds.intField(value=0, width=40, height=16, enable=False, annotation='音频偏移帧')
        cmds.text(label='缩放:', align='right', font='smallPlainLabelFont')
        self.scale_field = cmds.floatField(value=1.0, minValue=0.1, maxValue=1.0, width=50, height=16, precision=1, changeCommand=self.on_scale_change)
        cmds.setParent(main_layout)
        cmds.separator(height=5, style='none')
        options_section = cmds.frameLayout(labelVisible=False, borderVisible=False, parent=main_layout, marginWidth=0, marginHeight=2)
        options_column = cmds.columnLayout(adjustableColumn=True, rowSpacing=2, parent=options_section)
        cmds.text(label='高级选项', align='left', font='smallBoldLabelFont')
        cmds.separator(height=3, style='none')
        row1 = cmds.rowColumnLayout(numberOfColumns=3, columnWidth=[(1, 70), (2, 70), (3, 70)], parent=options_column)
        self.increment_checkbox = cmds.checkBox(label='增序', value=False)
        self.convert_checkbox = cmds.checkBox(label='转MP4', value=False)
        self.force_overwrite_checkbox = cmds.checkBox(label='覆盖', value=False)
        cmds.setParent(options_column)
        row2 = cmds.rowColumnLayout(numberOfColumns=4, columnWidth=[(1, 70), (2, 70), (3, 25), (4, 15)], parent=options_column)
        self.gif_checkbox = cmds.checkBox(label='转GIF', value=False)
        self.on_hold_checkbox = cmds.checkBox(label='拍一', value=False)
        self.hold_frames_field = cmds.textField(text='2', width=25, height=16, annotation='设置几拍一效果，例如2表示二拍一，3表示三拍一')
        cmds.text(label='拍', font='smallPlainLabelFont')
        cmds.showWindow(self.window)
        self.initialize_ui()

    def initialize_ui(self):
        """确保UI正确初始化和显示"""

        def delayed_init():
            for control in [self.increment_checkbox, self.convert_checkbox, self.force_overwrite_checkbox, self.gif_checkbox, self.on_hold_checkbox, self.hold_frames_field]:
                try:
                    cmds.control(control, edit=True, visible=True)
                except:
                    pass
            self.adjust_window_size()
            cmds.refresh(force=True)
        cmds.evalDeferred(delayed_init)

    def adjust_window_size(self, *args):
        """根据内容自动调整窗口大小"""
        try:
            base_height = 260
            multi_camera_height = 70
            target_height = base_height
            if self.multi_camera_mode:
                target_height += multi_camera_height

            def adjust_size():
                try:
                    cmds.window(self.window_name, edit=True, widthHeight=(280, target_height))
                    cmds.window(self.window_name, edit=True, sizeable=False)
                    cmds.refresh(force=True)
                except Exception as e:
                    cmds.warning(f'调整窗口大小时出错: {str(e)}')
            cmds.evalDeferred(adjust_size)
        except Exception as e:
            cmds.warning(f'计算窗口大小时出错: {str(e)}')

    def toggle_audio_options(self, *args):
        audio_enabled = cmds.checkBox(self.audio_checkbox, query=True, value=True)
        cmds.intField(self.offset_field, edit=True, enable=audio_enabled)

    def browse_path(self, *args):
        """打开文件浏览器选择保存路径"""
        current_path = cmds.textField(self.path_field, query=True, text=True)
        if not current_path or not os.path.exists(current_path):
            current_path = cmds.workspace(q=True, rd=True)
        result = cmds.fileDialog2(fileMode=3, dialogStyle=2, caption='选择输出目录', okCaption='选择', startingDirectory=current_path)
        if result and len(result):
            selected_path = result[0]
            cmds.textField(self.path_field, edit=True, text=selected_path)

    def get_camera_list(self):
        """获取场景中所有相机"""
        all_cameras = cmds.listCameras()
        filtered_cameras = [cam for cam in all_cameras if not (cam.startswith('front') or cam.startswith('side') or cam.startswith('top') or (cam == 'persp'))]
        return filtered_cameras

    def get_selected_camera(self):
        """获取用户选择的相机，如果选择了<当前视图>则返回None"""
        if self.multi_camera_mode:
            selected_cameras = self.get_selected_cameras()
            return selected_cameras[0] if selected_cameras else None
        else:
            try:
                selected_item = cmds.optionMenu(self.camera_menu, query=True, value=True)
                if selected_item == '<当前视图>':
                    return None
                if selected_item.startswith('前视图'):
                    return 'front'
                elif selected_item.startswith('侧视图'):
                    return 'side'
                elif selected_item.startswith('顶视图'):
                    return 'top'
                return selected_item
            except Exception as e:
                cmds.warning(f'获取选择相机时出错: {str(e)}')
                return None

    def on_scale_change(self, *args):
        scale_value = cmds.floatField(self.scale_field, query=True, value=True)
        cmds.checkBox(self.convert_checkbox, edit=True)

    def convert_to_mp4(self, mov_file):
        return bridge.convert(self, 'convert_mp4', mov_file)

    def capture_action(self, *args):
        return runtime.ui_capture(self, 'images')

    def qt_playblast_action(self, *args):
        return runtime.ui_capture(self, 'qt')

    def check_and_convert_to_mp4(self, mov_file_path):
        if cmds.checkBox(self.convert_checkbox, query=True, value=True):
            self.convert_to_mp4(mov_file_path)

    def incremented_filename(self, dir_path, base_name, extension):
        i = 1
        new_name = f'{base_name}_{i}{extension}'
        while os.path.exists(os.path.join(dir_path, new_name)):
            i += 1
            new_name = f'{base_name}_{i}{extension}'
        return os.path.join(dir_path, new_name)

    @bridge.helper_guard
    def playblast_camera(self, camera):
        """为指定相机执行playblast，如果camera为None则使用当前视图"""
        if camera is not None:
            if not cmds.objExists(camera):
                cmds.warning(f'相机 {camera} 不存在。')
                return None
        active_camera = camera if camera else cmds.lookThru(q=True)
        if not active_camera and (not camera):
            cmds.warning('没有活动相机，请设置一个活动相机。')
            return None
        resolution_width = cmds.getAttr('defaultResolution.width')
        resolution_height = cmds.getAttr('defaultResolution.height')
        output_folder = os.path.join(self.temp_dir, f"camera_{(camera if camera else 'current')}")
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        output_file = os.path.join(output_folder, 'capture')
        previous_camera = None
        if camera:
            previous_camera = cmds.lookThru(q=True)
            cmds.lookThru(camera)
        try:
            cmds.playblast(format='image', sequenceTime=0, clearCache=1, showOrnaments=1, fp=4, percent=100, compression='jpg', quality=100, widthHeight=(resolution_width, resolution_height), filename=output_file, forceOverwrite=True, viewer=False)
            if previous_camera:
                cmds.lookThru(previous_camera)
        except Exception as e:
            if previous_camera:
                cmds.lookThru(previous_camera)
            cmds.warning(f"相机 {(camera if camera else '当前视图')} 的Playblast失败: {str(e)}")
            return None
        return output_folder

    @bridge.helper_guard
    def playblast_current_camera(self):
        """为当前相机执行playblast（向后兼容，实际调用playblast_camera）"""
        selected_camera = self.get_selected_camera()
        return self.playblast_camera(selected_camera)

    @bridge.helper_guard
    def rename_images(self, folder_path, prefix='renamed_capture.', extension='jpg'):
        files = os.listdir(folder_path)
        image_files = [f for f in files if f.lower().endswith('.' + extension.lower())]

        def extract_number(f):
            match = re.search('capture\\.([-+]?\\d+)\\.' + re.escape(extension), f)
            if match:
                try:
                    return int(match.group(1))
                except ValueError:
                    return float('inf')
            else:
                return float('inf')
        image_files_sorted = sorted(image_files, key=extract_number)
        on_hold = cmds.checkBox(self.on_hold_checkbox, query=True, value=True)
        if on_hold:
            hold_frames_text = cmds.textField(self.hold_frames_field, query=True, text=True)
            try:
                hold_frames = int(hold_frames_text)
                if hold_frames < 2:
                    hold_frames = 2
                    cmds.textField(self.hold_frames_field, edit=True, text='2')
                    cmds.warning('拍一值必须大于等于2，已自动设置为2。')
                elif hold_frames > 10:
                    hold_frames = 10
                    cmds.textField(self.hold_frames_field, edit=True, text='10')
                    cmds.warning('拍一值必须小于等于10，已自动设置为10。')
            except ValueError:
                hold_frames = 2
                cmds.textField(self.hold_frames_field, edit=True, text='2')
                cmds.warning('拍一值必须是数字，已自动设置为2。')
            processed_files = []
            for i in range(0, len(image_files_sorted), hold_frames):
                if i < len(image_files_sorted):
                    processed_files.extend([image_files_sorted[i]] * hold_frames)
            image_files_sorted = processed_files
        for i, image_file in enumerate(image_files_sorted):
            new_name = f'{prefix}{i:04d}.{extension}'
            if on_hold:
                src_path = os.path.join(folder_path, image_file)
                dst_path = os.path.join(folder_path, new_name)
                try:
                    shutil.copy2(src_path, dst_path)
                except Exception as e:
                    cmds.warning(f'无法复制 {image_file} 到 {new_name}: {str(e)}')
            else:
                old_path = os.path.join(folder_path, image_file)
                new_path = os.path.join(folder_path, new_name)
                try:
                    os.rename(old_path, new_path)
                except Exception as e:
                    cmds.warning(f'无法重命名 {image_file} 到 {new_name}: {str(e)}')

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
        target = output_video_path or str(Path(image_folder).parent / 'capture.mov')
        result = runtime.run_api(action='encode_images', image_folder=image_folder, fps=frame_rate, audio_file=audio_file or '', audio_offset_frames=audio_offset_frames, output_dir=str(Path(target).parent), basename=Path(target).stem, ffmpeg_path=self.ffmpeg_custom_path if self.ffmpeg_mode == 'local' else '')
        return (result.data['files'][0], None)

    def convert_mov_to_gif(self, mov_file, fps, resolution, output_gif_path=None):
        return bridge.convert(self, 'convert_gif', mov_file, fps, resolution, output_gif_path)

    def open_default_player(self, video_file):
        return bridge.open_path(video_file)

    @bridge.helper_guard
    def cleanup_temp_dir(self):
        try:
            if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
        except Exception as e:
            cmds.warning('清理临时文件夹失败: {}'.format(str(e)))

    def switch_camera_mode(self, mode):
        """安全地切换相机选择模式"""
        try:
            if mode == 'single' and self.multi_camera_mode:
                self.multi_camera_mode = False
                cmds.frameLayout(self.single_camera_frame, edit=True, visible=True)
                cmds.frameLayout(self.multi_camera_frame, edit=True, visible=False)
                cmds.button(self.single_mode_button, edit=True, backgroundColor=[0.3, 0.5, 0.8])
                cmds.button(self.multi_mode_button, edit=True, backgroundColor=[0.5, 0.5, 0.5])
                self.adjust_window_size()
            elif mode == 'multi' and (not self.multi_camera_mode):
                self.multi_camera_mode = True
                cmds.frameLayout(self.single_camera_frame, edit=True, visible=False)
                cmds.frameLayout(self.multi_camera_frame, edit=True, visible=True)
                cmds.button(self.single_mode_button, edit=True, backgroundColor=[0.5, 0.5, 0.5])
                cmds.button(self.multi_mode_button, edit=True, backgroundColor=[0.3, 0.5, 0.8])
                self.adjust_window_size()
        except Exception as e:
            cmds.warning(f'切换相机模式时出错: {str(e)}')
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
            cmds.warning(f'选择所有相机时出错: {str(e)}')

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
            cmds.warning(f'反转相机选择时出错: {str(e)}')

    def get_selected_cameras(self):
        """获取用户选择的所有相机列表"""
        if not self.multi_camera_mode:
            try:
                selected_item = cmds.optionMenu(self.camera_menu, query=True, value=True)
                if selected_item == '<当前视图>':
                    return [None]
                if selected_item.startswith('前视图'):
                    return ['front']
                elif selected_item.startswith('侧视图'):
                    return ['side']
                elif selected_item.startswith('顶视图'):
                    return ['top']
                return [selected_item]
            except Exception as e:
                cmds.warning(f'获取选择相机时出错: {str(e)}')
                return [None]
        else:
            try:
                selected_cameras = []
                for cam, checkbox in self.camera_checkboxes.items():
                    if not cmds.checkBox(checkbox, exists=True):
                        continue
                    if cmds.checkBox(checkbox, query=True, value=True):
                        if cam == '<当前视图>':
                            selected_cameras.append(None)
                        else:
                            selected_cameras.append(cam)
                if not selected_cameras:
                    selected_cameras = [None]
                return selected_cameras
            except Exception as e:
                cmds.warning(f'获取选择相机列表时出错: {str(e)}')
                return [None]

    def get_camera_display_name(self, camera):
        """获取相机的显示名称"""
        if camera is None:
            return '当前视图'
        elif camera == 'front':
            return '前视图 (front)'
        elif camera == 'side':
            return '侧视图 (side)'
        elif camera == 'top':
            return '顶视图 (top)'
        else:
            return camera

    def get_camera_suffix(self, camera):
        import re
        return '_currentView' if camera is None else '_' + re.sub('[^\\w.-]', '_', camera.rsplit('|', 1)[-1])

    def get_gif_output_path(self, mov_file, camera_suffix):
        """根据MOV文件路径和相机后缀生成GIF输出路径"""
        dir_name = os.path.dirname(mov_file)
        base_name = os.path.splitext(os.path.basename(mov_file))[0]
        if camera_suffix and (not base_name.endswith(camera_suffix)):
            base_name += camera_suffix
        return os.path.join(dir_name, f'{base_name}.gif')

    def test_ffmpeg_path(self, *args):
        """测试当前FFmpeg路径是否有效"""
        try:
            print('=' * 60)
            print('FFmpeg 路径测试开始')
            print('=' * 60)
            print(f'当前FFmpeg模式: {self.ffmpeg_mode}')
            if self.ffmpeg_mode == 'local':
                print(f'自定义路径: {self.ffmpeg_custom_path}')
            else:
                print('使用系统环境变量中的FFmpeg')
            ffmpeg_path = self.get_current_ffmpeg_path()
            if not ffmpeg_path:
                error_msg = '未找到有效的FFmpeg路径'
                print(f'错误: {error_msg}')
                cmds.confirmDialog(title='测试失败', message='未找到FFmpeg', button=['确定'], icon='warning')
                return
            print(f'实际测试路径: {ffmpeg_path}')
            if ffmpeg_path == 'ffmpeg':
                test_cmd = ['ffmpeg', '-version']
                print('测试命令: ffmpeg -version (系统环境变量)')
            else:
                test_cmd = [ffmpeg_path, '-version']
                print(f'测试命令: "{ffmpeg_path}" -version')
            try:
                print('正在执行测试...')
                result = subprocess.run(test_cmd, capture_output=True, text=True, timeout=5)
                print(f'进程返回码: {result.returncode}')
                if result.returncode == 0:
                    print('? FFmpeg测试成功！')
                    if result.stdout:
                        print('FFmpeg版本信息:')
                        version_lines = result.stdout.split('\n')[:3]
                        for line in version_lines:
                            if line.strip():
                                print(f'  {line.strip()}')
                    cmds.confirmDialog(title='测试成功', message='FFmpeg配置正确', button=['确定'], icon='information')
                else:
                    error_info = result.stderr.strip() if result.stderr else '未知错误'
                    print('? FFmpeg测试失败')
                    print(f'错误信息: {error_info}')
                    cmds.confirmDialog(title='测试失败', message='FFmpeg配置有误', button=['确定'], icon='critical')
            except subprocess.TimeoutExpired:
                error_msg = 'FFmpeg测试超时（5秒），可能路径不正确或FFmpeg响应缓慢'
                print(f'? {error_msg}')
                cmds.confirmDialog(title='测试失败', message='FFmpeg响应超时', button=['确定'], icon='warning')
            except Exception as e:
                error_msg = f'执行测试时出错: {str(e)}'
                print(f'? {error_msg}')
                cmds.confirmDialog(title='测试失败', message='FFmpeg配置错误', button=['确定'], icon='critical')
        except Exception as e:
            error_msg = f'测试FFmpeg时出错: {str(e)}'
            print(f'? {error_msg}')
            cmds.warning(error_msg)
        finally:
            print('=' * 60)
            print('FFmpeg 路径测试结束')
            print('=' * 60)

    def get_current_ffmpeg_path(self):
        return get_ffmpeg_path(self.ffmpeg_custom_path if self.ffmpeg_mode == 'local' else None)

    def save_ffmpeg_settings(self, *args):
        return bridge.save_settings(self.ffmpeg_mode, self.ffmpeg_custom_path)

    def open_settings_directory(self, *args):
        return bridge.settings_io(self, True)

    def open_ffmpeg_settings(self, *args):
        """打开FFmpeg设置窗口"""
        settings_window_name = 'mtk_mov_playblast_ffmpeg_settings'
        if cmds.window(settings_window_name, exists=True):
            cmds.deleteUI(settings_window_name, window=True)
        settings_window = cmds.window(settings_window_name, title='FFmpeg设置', sizeable=False, minimizeButton=False, maximizeButton=False, widthHeight=(260, 230))
        margin_frame = cmds.frameLayout(labelVisible=False, borderVisible=False, marginWidth=10, marginHeight=10)
        main_column = cmds.columnLayout(adjustableColumn=True, columnAlign='center', rowSpacing=8, parent=margin_frame)
        cmds.text(label='FFmpeg路径配置', font='boldLabelFont', height=15)
        cmds.separator(height=1, style='in')
        mode_row = cmds.rowColumnLayout(numberOfColumns=2, columnWidth=[(1, 80), (2, 100)], parent=main_column)
        cmds.text(label='FFmpeg模式:', align='left')
        self.settings_ffmpeg_mode_menu = cmds.optionMenu(width=100, changeCommand=self.on_settings_ffmpeg_mode_change)
        cmds.menuItem(label='系统环境变量')
        cmds.menuItem(label='本地文件路径')
        cmds.setParent(main_column)
        path_row = cmds.rowColumnLayout(numberOfColumns=3, columnWidth=[(1, 80), (2, 100), (3, 60)], parent=main_column)
        cmds.text(label='自定义路径:', align='left')
        self.settings_ffmpeg_path_field = cmds.textField(text='', width=100, enable=False)
        self.settings_ffmpeg_browse_button = cmds.button(label='浏览', command=self.settings_browse_ffmpeg_path, width=60, enable=False)
        cmds.setParent(main_column)
        self.settings_ffmpeg_status_text = cmds.text(label='状态: 使用系统环境变量中的FFmpeg', align='center', wordWrap=True, height=20)
        cmds.separator(height=5, style='in')
        button_row1 = cmds.rowColumnLayout(numberOfColumns=2, columnWidth=[(1, 120), (2, 120)], parent=main_column)
        cmds.button(label='测试FFmpeg', command=self.test_ffmpeg_path, height=30)
        cmds.button(label='保存设置', command=self.settings_save_and_close, height=30, backgroundColor=[0.4, 0.6, 0.4])
        cmds.setParent(main_column)
        button_row2 = cmds.rowColumnLayout(numberOfColumns=2, columnWidth=[(1, 120), (2, 120)], parent=main_column)
        cmds.button(label='重置为默认', command=self.settings_reset_ffmpeg, height=30)
        cmds.button(label='导出设置JSON', command=self.open_settings_directory, height=30)
        self.apply_settings_to_window()
        cmds.showWindow(settings_window)
        cmds.setParent(main_column)
        cmds.button(label='导入设置JSON', command=lambda *args: bridge.settings_io(self, False))
        cmds.window(settings_window, edit=True, height=270)

    def apply_settings_to_window(self):
        """将当前设置应用到设置窗口"""
        try:
            if self.ffmpeg_mode == 'local' and self.ffmpeg_custom_path:
                cmds.optionMenu(self.settings_ffmpeg_mode_menu, edit=True, value='本地文件路径')
                cmds.textField(self.settings_ffmpeg_path_field, edit=True, enable=True, text=self.ffmpeg_custom_path)
                cmds.button(self.settings_ffmpeg_browse_button, edit=True, enable=True)
                if os.path.exists(self.ffmpeg_custom_path):
                    cmds.text(self.settings_ffmpeg_status_text, edit=True, label='状态: 使用本地FFmpeg路径')
                else:
                    cmds.text(self.settings_ffmpeg_status_text, edit=True, label='状态: 路径不存在，请重新选择')
            else:
                cmds.optionMenu(self.settings_ffmpeg_mode_menu, edit=True, value='系统环境变量')
                cmds.textField(self.settings_ffmpeg_path_field, edit=True, enable=False, text='')
                cmds.button(self.settings_ffmpeg_browse_button, edit=True, enable=False)
                cmds.text(self.settings_ffmpeg_status_text, edit=True, label='状态: 使用系统环境变量中的FFmpeg')
        except Exception as e:
            print(f'应用设置到窗口时出错: {str(e)}')

    def on_settings_ffmpeg_mode_change(self, *args):
        """设置窗口中FFmpeg模式切换时的回调"""
        try:
            selected_mode = cmds.optionMenu(self.settings_ffmpeg_mode_menu, query=True, value=True)
            if selected_mode == '系统环境变量':
                self.ffmpeg_mode = 'system'
                self.ffmpeg_custom_path = ''
                cmds.textField(self.settings_ffmpeg_path_field, edit=True, enable=False, text='')
                cmds.button(self.settings_ffmpeg_browse_button, edit=True, enable=False)
                cmds.text(self.settings_ffmpeg_status_text, edit=True, label='状态: 使用系统环境变量中的FFmpeg')
            elif selected_mode == '本地文件路径':
                self.ffmpeg_mode = 'local'
                cmds.textField(self.settings_ffmpeg_path_field, edit=True, enable=True, text=self.ffmpeg_custom_path)
                cmds.button(self.settings_ffmpeg_browse_button, edit=True, enable=True)
                self.settings_auto_detect_local_ffmpeg()
        except Exception as e:
            print(f'设置窗口模式切换出错: {str(e)}')

    def settings_auto_detect_local_ffmpeg(self):
        """设置窗口中自动检测FFmpeg路径"""
        try:
            detected_ffmpeg, _ = auto_detect_ffmpeg()
            if detected_ffmpeg and detected_ffmpeg != 'ffmpeg':
                cmds.text(self.settings_ffmpeg_status_text, edit=True, label='状态: 已检测到系统环境变量中的FFmpeg')
            else:
                cmds.text(self.settings_ffmpeg_status_text, edit=True, label='状态: 请手动选择FFmpeg.exe文件')
        except Exception as e:
            error_msg = f'状态: 自动检测失败，请手动选择'
            cmds.text(self.settings_ffmpeg_status_text, edit=True, label=error_msg)
            print(f'设置窗口FFmpeg自动检测详细错误: {str(e)}')

    def settings_browse_ffmpeg_path(self, *args):
        """设置窗口中浏览选择FFmpeg路径"""
        try:
            initial_dir = os.path.expanduser('~/Documents')
            result = cmds.fileDialog2(fileMode=1, fileFilter='FFmpeg可执行文件 (*.exe)', caption='选择ffmpeg.exe', startingDirectory=initial_dir)
            if result and len(result) > 0:
                selected_path = result[0].replace('\\', '/')
                self.ffmpeg_custom_path = selected_path
                cmds.textField(self.settings_ffmpeg_path_field, edit=True, text=selected_path)
                cmds.text(self.settings_ffmpeg_status_text, edit=True, label='状态: 已设置自定义FFmpeg路径')
        except Exception as e:
            error_msg = f'选择FFmpeg路径时出错: {str(e)}'
            cmds.warning(error_msg)
            cmds.text(self.settings_ffmpeg_status_text, edit=True, label='状态: 路径选择失败，请重试')
            print(f'设置窗口FFmpeg路径选择详细错误: {str(e)}')

    def settings_reset_ffmpeg(self, *args):
        """设置窗口中重置FFmpeg设置为默认值"""
        self.ffmpeg_mode = 'system'
        self.ffmpeg_custom_path = ''
        cmds.optionMenu(self.settings_ffmpeg_mode_menu, edit=True, value='系统环境变量')
        cmds.textField(self.settings_ffmpeg_path_field, edit=True, enable=False, text='')
        cmds.button(self.settings_ffmpeg_browse_button, edit=True, enable=False)
        cmds.text(self.settings_ffmpeg_status_text, edit=True, label='状态: 已重置为默认设置（系统环境变量）')

    def settings_save_and_close(self, *args):
        """保存设置并关闭设置窗口"""
        try:
            success = save_ffmpeg_settings(self.ffmpeg_mode, self.ffmpeg_custom_path)
            if success:
                settings_window_name = 'mtk_mov_playblast_ffmpeg_settings'
                if cmds.window(settings_window_name, exists=True):
                    cmds.deleteUI(settings_window_name, window=True)
                cmds.confirmDialog(title='设置已保存', message='FFmpeg设置已保存到本次Maya会话；跨会话请导出JSON', button=['确定'], icon='information')
            else:
                cmds.confirmDialog(title='保存失败', message='无法保存FFmpeg设置', button=['确定'], icon='warning')
        except Exception as e:
            cmds.warning(f'保存设置时出错: {str(e)}')

    def refresh_plugin(self, *args):
        global ui_instance
        if cmds.window(self.window_name, exists=True):
            cmds.deleteUI(self.window_name, window=True)
        if cmds.window('mtk_mov_playblast_ffmpeg_settings', exists=True):
            cmds.deleteUI('mtk_mov_playblast_ffmpeg_settings', window=True)
        ui_instance = PlayblastConverterUI()
        runtime.UI = ui_instance
        return ui_instance

    def refresh_filename(self, *args):
        """刷新输出文件名 - 重新获取当前场景文件名"""
        try:
            current_file_path = cmds.file(q=True, sceneName=True)
            current_file_name = os.path.splitext(os.path.basename(current_file_path))[0] if current_file_path else 'untitled'
            cmds.textField(self.filename_field, edit=True, text=current_file_name)
        except:
            pass

    def refresh_path(self, *args):
        """刷新输出路径 - 重新获取当前场景文件目录"""
        try:
            current_file_path = cmds.file(q=True, sceneName=True)
            current_dir = os.path.dirname(current_file_path) if current_file_path else ''
            cmds.textField(self.path_field, edit=True, text=current_dir)
        except:
            pass

    def open_current_path(self, *args):
        return bridge.open_path(cmds.textField(self.path_field, query=True, text=True))
