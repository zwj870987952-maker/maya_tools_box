"""Legacy UI delegates output work to the standard API; session settings never auto-write."""
from pathlib import Path
import os
import subprocess
from . import media, runtime


def save_settings(mode, path):
    runtime.SETTINGS.update(runtime.settings({'ffmpeg_mode': mode, 'ffmpeg_custom_path': path}))
    return True


def settings_io(ui, exporting):
    from maya import cmds
    paths = cmds.fileDialog2(fileMode=0 if exporting else 1, fileFilter='JSON (*.json)', caption='导出FFmpeg设置' if exporting else '导入FFmpeg设置')
    if not paths:
        return
    kwargs = {'action': 'settings_export' if exporting else 'settings_import', 'settings_file': paths[0]}
    if exporting:
        save_settings(ui.ffmpeg_mode, ui.ffmpeg_custom_path)
    result = runtime.run_api(**kwargs)
    ui.ffmpeg_mode = runtime.SETTINGS['ffmpeg_mode']
    ui.ffmpeg_custom_path = runtime.SETTINGS['ffmpeg_custom_path']
    if hasattr(ui, 'settings_ffmpeg_mode_menu'):
        ui.apply_settings_to_window()
    return result


def open_path(path):
    path = media.absolute(path)
    if not path.exists():
        raise ValueError('只能打开已有输出/目录')
    if os.name == 'nt':
        os.startfile(str(path))
    else:
        import sys
        subprocess.run(['open' if sys.platform == 'darwin' else 'xdg-open', str(path)], check=True)


def convert(ui, action, source, fps=0, resolution=(0, 0), destination=None):
    source = media.absolute(source)
    target = Path(destination) if destination else source.with_suffix('.mp4' if action == 'convert_mp4' else '.gif')
    result = runtime.run_api(action=action, source_file=str(source), output_dir=str(target.parent), basename=target.stem, fps=fps, width=resolution[0], height=resolution[1], ffmpeg_path=ui.ffmpeg_custom_path if ui.ffmpeg_mode == 'local' else '')
    return result.data['files'][0]


def helper_guard(function):
    """Raw internal capture helpers cannot bypass the candidate's export transaction."""
    from functools import wraps
    @wraps(function)
    def wrapper(self, *args, **kwargs):
        if not runtime.ACTIVE:
            raise RuntimeError('内部capture/rename helper仅允许标准API export上下文')
        temp = getattr(self, 'temp_dir', None)
        if not temp or Path(temp).resolve() not in runtime.OWNED_ROOTS or not Path(temp).is_dir() or Path(temp).is_symlink():
            raise RuntimeError('需要本次自有临时目录')
        for value in list(args) + list(kwargs.values()):
            if isinstance(value, str) and Path(value).is_absolute() and not Path(value).resolve().is_relative_to(Path(temp).resolve()):
                raise RuntimeError('内部helper不得访问外部路径')
        return function(self, *args, **kwargs)
    return wrapper
