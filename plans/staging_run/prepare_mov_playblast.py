import ast
import difflib
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[2]
UNIT = ROOT / 'tools_staging_pool/01_animation/mov_playblast_v11'
RC = UNIT / 'release_candidate'
PACKAGE = RC / 'maya_toolkit/tools/mov_playblast'


def body(text):
    return ast.parse(text).body


def main():
    PACKAGE.mkdir(parents=True, exist_ok=True)
    raw = []
    for source in sorted(UNIT.iterdir()):
        if source.suffix not in ('.py', '.bat'):
            continue
        target = PACKAGE / 'upstream' / (source.name + '.original' if source.suffix == '.py' else source.name)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        raw.append({'path': target.relative_to(PACKAGE).as_posix(), 'source': source.name, 'sha256': hashlib.sha256(source.read_bytes()).hexdigest()})
    (UNIT / '.gitattributes').write_text('*.py -text\n*.bat -text\n', encoding='utf-8', newline='\n')
    (RC / '.gitattributes').write_text('* -text\n', encoding='utf-8', newline='\n')
    (PACKAGE / 'upstream/.gitattributes').write_text('* -text\n', encoding='utf-8', newline='\n')
    original = (UNIT / 'mov拍屏v11.py').read_text(encoding='utf-8-sig')
    tree = ast.parse(original)
    functions = [n.name for n in tree.body if isinstance(n, ast.FunctionDef)]
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef))
    methods = [n.name for n in cls.body if isinstance(n, ast.FunctionDef)]
    # Remove only the original unconditional UI instance.
    tree.body = [n for n in tree.body if not isinstance(n, ast.Assign) or not any(isinstance(t, ast.Name) and t.id == 'ui_instance' for t in n.targets)]
    tree.body.insert(0, ast.ImportFrom(module=None, names=[ast.alias(name='ui_bridge', asname='bridge'), ast.alias(name='runtime'), ast.alias(name='media')], level=1))
    globals_replace = {
        'get_settings_file_path': 'return "本次Maya会话设置；使用导出设置保存JSON"',
        'save_ffmpeg_settings': 'return bridge.save_settings(ffmpeg_mode, ffmpeg_custom_path)',
        'load_ffmpeg_settings': 'return dict(runtime.SETTINGS)',
        'auto_detect_ffmpeg': 'path = shutil.which("ffmpeg")\nreturn (path, "PATH: " + path) if path else (None, None)',
        'get_ffmpeg_path': 'try:\n    return media.executable(custom_path or "")\nexcept ValueError as error:\n    cmds.warning(str(error))\n    return None',
        'onMayaDroppedPythonFile': 'return runtime.run_api(action="open_ui")'
    }
    for n in tree.body:
        if isinstance(n, ast.FunctionDef) and n.name in globals_replace:
            n.body = body(globals_replace[n.name])
    replaces = {
        'capture_action': 'return runtime.ui_capture(self, "images")',
        'qt_playblast_action': 'return runtime.ui_capture(self, "qt")',
        'convert_to_mp4': 'return bridge.convert(self, "convert_mp4", mov_file)',
        'convert_mov_to_gif': 'return bridge.convert(self, "convert_gif", mov_file, fps, resolution, output_gif_path)',
        'convert_images_to_video': 'target = output_video_path or str(Path(image_folder).parent / "capture.mov")\nresult = runtime.run_api(action="encode_images", image_folder=image_folder, fps=frame_rate, audio_file=audio_file or "", audio_offset_frames=audio_offset_frames, output_dir=str(Path(target).parent), basename=Path(target).stem, ffmpeg_path=self.ffmpeg_custom_path if self.ffmpeg_mode == "local" else "")\nreturn result.data["files"][0], None',
        'open_default_player': 'return bridge.open_path(video_file)',
        'open_current_path': 'return bridge.open_path(cmds.textField(self.path_field, query=True, text=True))',
        'open_settings_directory': 'return bridge.settings_io(self, True)',
        'save_ffmpeg_settings': 'return bridge.save_settings(self.ffmpeg_mode, self.ffmpeg_custom_path)',
        'refresh_plugin': 'global ui_instance\nif cmds.window(self.window_name, exists=True):\n    cmds.deleteUI(self.window_name, window=True)\nif cmds.window("mtk_mov_playblast_ffmpeg_settings", exists=True):\n    cmds.deleteUI("mtk_mov_playblast_ffmpeg_settings", window=True)\nui_instance = PlayblastConverterUI()\nruntime.UI = ui_instance\nreturn ui_instance',
        'get_camera_suffix': 'import re\nreturn "_currentView" if camera is None else "_" + re.sub(r"[^\\w.-]", "_", camera.rsplit("|", 1)[-1])',
        'get_current_ffmpeg_path': 'return get_ffmpeg_path(self.ffmpeg_custom_path if self.ffmpeg_mode == "local" else None)'
    }
    tree.body.insert(0, ast.ImportFrom(module='pathlib', names=[ast.alias(name='Path')], level=0))
    for n in cls.body:
        if not isinstance(n, ast.FunctionDef):
            continue
        if n.name in replaces:
            n.body = body(replaces[n.name])
        if n.name in ('playblast_camera', 'playblast_current_camera', 'rename_images', 'cleanup_temp_dir'):
            n.decorator_list.append(ast.Attribute(value=ast.Name(id='bridge', ctx=ast.Load()), attr='helper_guard', ctx=ast.Load()))
        if n.name == 'open_ffmpeg_settings':
            n.body.extend(body('cmds.setParent(main_column)\ncmds.button(label="导入设置JSON", command=lambda *args: bridge.settings_io(self, False))\ncmds.window(settings_window, edit=True, height=270)'))
    for n in ast.walk(tree):
        if isinstance(n, ast.Constant) and isinstance(n.value, str):
            if n.value == 'screen_capture_tool':
                n.value = 'mtk_mov_playblast_candidate'
            elif n.value == 'ffmpeg_settings_window':
                n.value = 'mtk_mov_playblast_ffmpeg_settings'
            elif n.value == 'FFmpeg设置保存成功':
                n.value = 'FFmpeg设置已保存到本次Maya会话；跨会话请导出JSON'
            elif n.value == '打开设置目录':
                n.value = '导出设置JSON'
        if isinstance(n, ast.keyword) and n.arg == 'shell' and isinstance(n.value, ast.Constant):
            n.value.value = False
    converted = '# Full v11.1 source UI adaptation; original source/resources retained in upstream.\n' + ast.unparse(ast.fix_missing_locations(tree)) + '\n'
    (PACKAGE / 'native.py').write_text('\n'.join(s.rstrip() for s in converted.splitlines()) + '\n', encoding='utf-8', newline='\n')
    docs = RC / 'docs/tools'
    docs.mkdir(parents=True, exist_ok=True)
    (docs / 'mov_playblast_changes.diff').write_text(''.join(difflib.unified_diff(original.splitlines(True), converted.splitlines(True), fromfile='upstream/mov-v11.py', tofile='native.py')), encoding='utf-8', newline='\n')
    (PACKAGE / 'catalog.json').write_text(json.dumps({'raw_files': raw, 'functions': functions, 'methods': methods, 'license': 'User personal script; no independent redistribution license supplied. Local only; no publication.', 'alternate_encoding': 'mov拍屏v11_alt.py GB18030 bytes retained, UTF8 primary is executable source'}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    launcher = (ROOT / 'tools_staging_pool/01_animation/maya_timeline_marker/release_candidate/launch_candidate.py').read_text(encoding='utf-8').replace('timeline_marker', 'mov_playblast').replace('TimelineMarkerTool', 'MovPlayblastTool')
    (RC / 'launch_candidate.py').write_text(launcher, encoding='utf-8', newline='\n')
    files = [p for folder in (RC / 'maya_toolkit', RC / 'docs', RC / 'tests') for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc']
    data = {'tool_id': 'mov_playblast', 'registration': {'module': 'mov_playblast', 'class_name': 'MovPlayblastTool'}, 'files': [{'source': p.relative_to(RC).as_posix(), 'target': p.relative_to(RC).as_posix()} for p in sorted(files)], 'resources': [r['path'] for r in raw] + ['catalog.json'], 'dependencies': ['Maya Python3 cmds/API2', 'Real viewport/QuickTime-H264 support for capture', 'FFmpeg libx264/aac/gif; explicit executable or PATH, no install/download', 'Output filesystem hardlinks for atomic no-overwrite publication'], 'source': '../mov拍屏v11.py', 'change_summary': 'Full source UI and original helpers archived/adapted; images/Qt multi-camera capture, audio offset, sequence hold, incremental MOV/MP4/GIF, standard dry/API and explicit external output protection, checked shell-free FFmpeg and finally view state, session/JSON settings.', 'verification_limitations': ['Real Maya viewport/native GUI/QuickTime playback unverified', 'Output files/overwrites cannot Maya Undo; partial published outputs reported', 'hold extends to complete groups only in image mode; QT hold refused', 'Settings changed from automatic Documents writes to session plus explicit JSON I/O', 'Multi-camera suffix sanitized and UUID-qualified; output directory must already exist'], 'acceptance_required': True}
    (RC / 'promotion.json').write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({'resources': len(raw), 'methods': len(methods), 'functions': len(functions)}))


if __name__ == '__main__':
    main()
