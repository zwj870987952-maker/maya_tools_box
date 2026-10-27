import json
import math
from pathlib import Path
import re
import shutil
import tempfile
from contextlib import contextmanager
from . import media

ACTIVE = False
SETTINGS = {'ffmpeg_mode': 'system', 'ffmpeg_custom_path': ''}
UI = None
OWNED_ROOTS = set()


class PartialFailure(RuntimeError):
    def __init__(self, message, data):
        super().__init__(message)
        self.data = data


def settings(value):
    if not isinstance(value, dict) or set(value) != {'ffmpeg_mode', 'ffmpeg_custom_path'} or value['ffmpeg_mode'] not in ('system', 'local') or not isinstance(value['ffmpeg_custom_path'], str):
        raise ValueError('设置须ffmpeg_mode/system|local与ffmpeg_custom_path')
    if value['ffmpeg_mode'] == 'local':
        media.executable(value['ffmpeg_custom_path'])
    return dict(value)


def read_settings(path):
    return settings(json.loads(Path(path).read_text(encoding='utf-8')))


def scene_plan(a):
    from maya import cmds
    import maya.api.OpenMaya as om
    if cmds.about(batch=True):
        raise ValueError('真实Maya viewport需要；mayapy不执行真实拍屏')
    panel = a['panel'] or cmds.getPanel(withFocus=True)
    panels = cmds.getPanel(type='modelPanel') or []
    if panel not in panels:
        visible = [p for p in panels if p in (cmds.getPanel(visiblePanels=True) or [])]
        if not visible:
            raise ValueError('需要可见modelPanel')
        panel = visible[0]
    a['panel'] = panel
    current = cmds.modelEditor(panel, query=True, camera=True)
    cameras = a['cameras'] or [current]
    identities = []
    names = []
    for name in cameras:
        found = cmds.ls(name, long=True) or []
        if len(found) != 1:
            raise ValueError('相机需要唯一长路径: ' + name)
        node = found[0]
        if cmds.nodeType(node) == 'transform':
            shapes = cmds.listRelatives(node, shapes=True, fullPath=True, type='camera') or []
            if len(shapes) != 1:
                raise ValueError('唯一cameraShape需要')
            node = shapes[0]
        if cmds.nodeType(node) != 'camera' or len(cmds.ls(node, allPaths=True, long=True) or []) != 1:
            raise ValueError('不接受非camera/实例相机')
        identity = cmds.ls(node, uuid=True)[0]
        if identity in identities:
            raise ValueError('重复实际相机')
        identities.append(identity)
        names.append(node)
    if len(names) > 1 and not a['multi_camera']:
        raise ValueError('多相机须multi_camera=true')
    a['cameras'] = names
    a['start'] = int(cmds.playbackOptions(query=True, min=True)) if a['start'] is None else a['start']
    a['end'] = int(cmds.playbackOptions(query=True, max=True)) if a['end'] is None else a['end']
    count = a['end'] - a['start'] + 1
    if count < 1 or count > 10000 or count * len(names) > 100000:
        raise ValueError('拍屏范围1..10000帧，总相机帧≤100000')
    a['width'] = a['width'] or int(cmds.getAttr('defaultResolution.width'))
    a['height'] = a['height'] or int(cmds.getAttr('defaultResolution.height'))
    if not 1 <= a['width'] <= 8192 or not 1 <= a['height'] <= 8192:
        raise ValueError('实际分辨率无效')
    a['fps'] = a['fps'] or om.MTime(1, om.MTime.kSeconds).asUnits(om.MTime.uiUnit())
    if not math.isfinite(a['fps']) or not 0 < a['fps'] <= 1000:
        raise ValueError('实际fps无效')
    if a['include_audio']:
        node = a['audio_node']
        if not node and not a['audio_file']:
            from maya import mel
            timeline = mel.eval('$tmpVar=$gPlayBackSlider')
            node = cmds.timeControl(timeline, query=True, sound=True) or ''
        if node:
            found = cmds.ls(node, type='audio') or []
            if len(found) != 1:
                raise ValueError('唯一audio节点需要')
            a['audio_node'] = found[0]
            a['audio_file'] = cmds.getAttr(node + '.filename')
            a['audio_offset_frames'] += cmds.getAttr(node + '.offset') - a['start']
        if not a['audio_file']:
            raise ValueError('音频已请求但没有有效音频')
        if not Path(a['audio_file']).is_absolute():
            a['audio_file'] = str(Path(cmds.file(query=True, sceneName=True)).parent / a['audio_file'])
        a['audio_file'] = str(media.absolute(a['audio_file']))
        if not Path(a['audio_file']).is_file():
            raise ValueError('音频文件不存在')
    else:
        a['audio_file'] = ''
    if a['mode'] == 'images' or a['convert_mp4'] or a['convert_gif'] or a['audio_file']:
        a['ffmpeg_path'] = media.executable(a['ffmpeg_path'])
    extensions = ['.mov'] + (['.mp4'] if a['convert_mp4'] else []) + (['.gif'] if a['convert_gif'] else [])
    groups = []
    for node, identity in zip(names, identities):
        suffix = ''
        if a['multi_camera']:
            label = node.rsplit('|', 1)[-1]
            if label.endswith('Shape'):
                label = label[:-5]
            label = re.sub(r'[^\w.-]', '_', label)[:50]
            suffix = '_' + label + '_' + identity.replace('-', '')[:8]
        groups.append((a['basename'] + suffix, extensions))
    a['outputs'] = media.destinations(a['output_dir'], groups, a['overwrite'], a['increment'])


@contextmanager
def owned_directory(parent):
    root = Path(parent).resolve()
    context = tempfile.TemporaryDirectory(prefix='mtk_playblast_', dir=str(root))
    target = Path(context.name).resolve()
    if target.parent != root or not target.name.startswith('mtk_playblast_'):
        raise RuntimeError('临时目录未落在指定输出目录内')
    OWNED_ROOTS.add(target)
    try:
        with context as directory:
            yield directory
    finally:
        OWNED_ROOTS.discard(target)


def execute(a):
    global ACTIVE, UI
    from maya import cmds
    action = a['action']
    if action == 'inspect':
        return {'settings': dict(SETTINGS), 'ffmpeg_found': shutil.which('ffmpeg'), 'gui_required_for_capture': True}
    if action == 'open_ui':
        from .native import PlayblastConverterUI
        if UI is not None and cmds.window(UI.window_name, exists=True):
            raise RuntimeError('候选拍屏窗口已打开')
        UI = PlayblastConverterUI()
        return {'ui_open': True}
    if action == 'settings_import':
        SETTINGS.update(a['settings'])
        return {'settings': dict(SETTINGS)}
    if action == 'ffmpeg_version':
        result = media.invoke([a['ffmpeg_path'], '-version'], min(a['timeout'], 30))
        return {'ffmpeg_path': a['ffmpeg_path'], 'version': result.stdout.splitlines()[:3]}
    ACTIVE = True
    completed = []
    try:
        output_parent = str(Path(a['outputs'][0][0]['path']).parent)
        with owned_directory(output_parent) as temp:
            temp = Path(temp)
            if action == 'settings_export':
                staged = temp / 'settings.json'
                staged.write_text(json.dumps(SETTINGS, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
                completed.append(media.publish(staged, a['outputs'][0][0], a['overwrite']))
            elif action == 'export':
                capture(a, temp, completed)
            else:
                staged = temp / ('output' + Path(a['outputs'][0][0]['path']).suffix)
                if action == 'encode_images':
                    count = media.prepare_sequence([Path(p) for p in a['images']], temp / 'sequence', a['hold'])
                    media.encode_images(a['ffmpeg_path'], temp / 'sequence', a['fps'], count, staged, a['audio_file'], a['audio_offset_frames'], a['timeout'])
                elif action == 'convert_mp4':
                    media.mp4(a['ffmpeg_path'], a['source_file'], staged, a['timeout'])
                elif action == 'convert_gif':
                    media.gif(a['ffmpeg_path'], a['source_file'], a['fps'], [a['width'], a['height']], staged, a['timeout'])
                completed.append(media.publish(staged, a['outputs'][0][0], a['overwrite']))
        return {'files': completed, 'action': action}
    except Exception as error:
        raise PartialFailure(str(error), {'completed_files': completed, 'external_undo': False}) from error
    finally:
        ACTIVE = False


def capture(a, temp, completed):
    from maya import cmds
    panel = a['panel']
    previous = cmds.modelEditor(panel, query=True, camera=True)
    time = cmds.currentTime(query=True)
    selection = cmds.ls(selection=True, long=True) or []
    auto = cmds.autoKeyframe(query=True, state=True)
    try:
        for i, (camera, outputs) in enumerate(zip(a['cameras'], a['outputs'])):
            folder = temp / ('camera_' + str(i))
            folder.mkdir()
            cmds.lookThru(panel, camera)
            mov = folder / 'result.mov'
            options = dict(sequenceTime=0, clearCache=1, showOrnaments=1, widthHeight=(a['width'], a['height']), quality=100, viewer=False, forceOverwrite=True, startTime=a['start'], endTime=a['end'], editorPanelName=panel)
            if a['mode'] == 'images':
                raw = folder / 'raw'
                raw.mkdir()
                cmds.playblast(format='image', filename=str(raw / 'capture'), fp=4, percent=100, compression='jpg', **options)
                files = media.sequence_files(str(raw))
                expected = a['end'] - a['start'] + 1
                if len(files) != expected:
                    raise RuntimeError('playblast图像帧数不符，拒绝生成截断视频')
                count = media.prepare_sequence(files, folder / 'sequence', a['hold'])
                media.encode_images(a['ffmpeg_path'], folder / 'sequence', a['fps'], count, mov, a['audio_file'], a['audio_offset_frames'], a['timeout'])
            else:
                raw = folder / 'raw.mov'
                cmds.playblast(format='qt', filename=str(raw), percent=int(round(a['scale'], 1) * 100), compression='H.264', **options)
                if a['audio_file']:
                    media.mux_audio(a['ffmpeg_path'], raw, a['audio_file'], a['audio_offset_frames'] / a['fps'], (a['end'] - a['start'] + 1) / a['fps'], mov, a['timeout'])
                else:
                    shutil.copy2(raw, mov)
            artifacts = [mov]
            if a['convert_mp4']:
                artifacts.append(Path(media.mp4(a['ffmpeg_path'], mov, folder / 'result.mp4', a['timeout'])))
            if a['convert_gif']:
                percent = 1 if a['mode'] == 'images' else round(a['scale'], 1)
                size = [max(1, int(a['width'] * percent)), max(1, int(a['height'] * percent))]
                artifacts.append(Path(media.gif(a['ffmpeg_path'], mov, a['fps'], size, folder / 'result.gif', a['timeout'])))
            for staged, destination in zip(artifacts, outputs):
                completed.append(media.publish(staged, destination, a['overwrite']))
    finally:
        errors = []
        operations = [lambda: cmds.lookThru(panel, previous),
                      lambda: cmds.currentTime(time) if cmds.currentTime(query=True) != time else None,
                      lambda: cmds.autoKeyframe(state=auto) if cmds.autoKeyframe(query=True, state=True) != auto else None,
                      lambda: (cmds.select(selection, replace=True) if selection else cmds.select(clear=True)) if (cmds.ls(selection=True, long=True) or []) != selection else None]
        for operation in operations:
            try:
                operation()
            except Exception as error:
                errors.append(str(error))
        if errors:
            raise RuntimeError('拍屏状态恢复失败（其余恢复仍已尝试）: ' + '; '.join(errors))


def run_api(**kwargs):
    from .tool import MovPlayblastTool
    result = MovPlayblastTool().run(**kwargs)
    if not result.success:
        raise RuntimeError(result.message + ' ' + str(result.data))
    return result


def ui_capture(ui, mode):
    from maya import cmds
    cameras = ui.get_selected_cameras()
    if any(c is None for c in cameras):
        panel = cmds.getPanel(withFocus=True)
        if panel not in (cmds.getPanel(type='modelPanel') or []):
            panels = [p for p in cmds.getPanel(type='modelPanel') or [] if p in (cmds.getPanel(visiblePanels=True) or [])]
            if not panels:
                raise RuntimeError('无可见modelPanel')
            panel = panels[0]
        current = cmds.modelEditor(panel, query=True, camera=True)
        cameras = [current if c is None else c for c in cameras]
    hold = 1
    if mode == 'images' and cmds.checkBox(ui.on_hold_checkbox, query=True, value=True):
        hold = int(cmds.textField(ui.hold_frames_field, query=True, text=True))
        if not 2 <= hold <= 10:
            raise ValueError('几拍一须2..10')
    result = run_api(action='export', mode=mode, output_dir=cmds.textField(ui.path_field, query=True, text=True), basename=cmds.textField(ui.filename_field, query=True, text=True), cameras=cameras, multi_camera=bool(ui.multi_camera_mode), scale=cmds.floatField(ui.scale_field, query=True, value=True), include_audio=cmds.checkBox(ui.audio_checkbox, query=True, value=True), audio_offset_frames=cmds.intField(ui.offset_field, query=True, value=True), hold=hold, convert_mp4=cmds.checkBox(ui.convert_checkbox, query=True, value=True), convert_gif=cmds.checkBox(ui.gif_checkbox, query=True, value=True), overwrite=cmds.checkBox(ui.force_overwrite_checkbox, query=True, value=True), increment=cmds.checkBox(ui.increment_checkbox, query=True, value=True), ffmpeg_path=ui.ffmpeg_custom_path if ui.ffmpeg_mode == 'local' else '')
    # Preserve the original UI's explicit capture-button playback; API never launches a viewer.
    for file in result.data['files']:
        if file.lower().endswith('.mov'):
            ui.open_default_player(file)
    return result
