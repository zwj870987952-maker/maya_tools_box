import json
import os
from pathlib import Path
import runpy
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

if os.environ.get('STAGING_ISOLATED_MAYAPY') != '1':
    raise RuntimeError('Disposable isolated mayapy only')
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds
RC = Path(__file__).resolve().parents[1]
TOOL = runpy.run_path(str(RC / 'launch_candidate.py'))['load_tool']()
from maya_toolkit.tools.mov_playblast import media, runtime, native

FFMPEG = shutil.which('ffmpeg')


def fixture_images(root):
    source = root / 'images'; source.mkdir()
    # Use actual FFmpeg to create two JPEG fixtures; no GUI renderer.
    for frame, color in ((1, 'red'), (2, 'blue'), (3, 'green')):
        media.invoke([FFMPEG, '-nostdin', '-y', '-f', 'lavfi', '-i', 'color=c=' + color + ':s=32x32', '-frames:v', '1', str(source / ('capture.%04d.jpg' % frame))], 20)
    return source


class MayaTests(unittest.TestCase):
    def setUp(self):
        cmds.file(new=True, force=True)
        cmds.undoInfo(state=True)
        self.node = cmds.createNode('transform', name='control')
        cmds.setKeyframe(self.node, attribute='tx', time=1, value=2)
        cmds.setKeyframe(self.node, attribute='tx', time=3, value=6)
        cmds.currentTime(2)
        cmds.select(self.node)
        cmds.autoKeyframe(state=True)

    def ok(self, **kwargs):
        result = TOOL.run(**kwargs)
        self.assertTrue(result.success, str((result.message, result.errors)))
        return result.data

    @unittest.skipUnless(FFMPEG, 'Actual FFmpeg unavailable')
    def test_real_ffmpeg_movies_mp4_gif_hold_audio_and_settings(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = fixture_images(root)
            original = {p.name: p.read_bytes() for p in source.iterdir()}
            a = dict(action='encode_images', image_folder=str(source), output_dir=directory, basename='film', fps=24, hold=2, ffmpeg_path=FFMPEG)
            before = (sorted(p.name for p in root.iterdir()), cmds.currentTime(query=True), cmds.ls(selection=True), cmds.undoInfo(query=True, undoName=True))
            self.assertTrue(TOOL.run(dry_run=True, **a).success)
            self.assertEqual(before, (sorted(p.name for p in root.iterdir()), cmds.currentTime(query=True), cmds.ls(selection=True), cmds.undoInfo(query=True, undoName=True)))
            movie = self.ok(**a)['files'][0]
            decoded = root / 'frames'; decoded.mkdir()
            media.invoke([FFMPEG, '-nostdin', '-i', movie, '-vsync', '0', str(decoded / 'frame.%04d.png')], 20)
            frames = sorted(decoded.iterdir())
            self.assertEqual(4, len(frames))
            self.assertEqual(frames[0].read_bytes(), frames[1].read_bytes())
            self.assertEqual(frames[2].read_bytes(), frames[3].read_bytes())
            self.ok(action='convert_mp4', source_file=movie, output_dir=directory, basename='film', ffmpeg_path=FFMPEG)
            self.ok(action='convert_gif', source_file=movie, output_dir=directory, basename='film', ffmpeg_path=FFMPEG, fps=24, width=32, height=32)
            audio = root / 'tone.wav'
            media.invoke([FFMPEG, '-nostdin', '-y', '-f', 'lavfi', '-i', 'sine=frequency=440:duration=0.5', str(audio)], 20)
            self.ok(**dict(a, basename='with_audio', audio_file=str(audio), audio_offset_frames=1))
            self.assertEqual(original, {p.name: p.read_bytes() for p in source.iterdir()})
            self.assertFalse(TOOL.run(**a).success)
            settings = str(root / 'settings.json')
            self.ok(action='settings_export', settings_file=settings)
            self.assertFalse(TOOL.run(action='settings_export', settings_file=settings).success)
            self.ok(action='settings_import', settings_file=settings)
            self.assertTrue(self.ok(action='ffmpeg_version', ffmpeg_path=FFMPEG)['version'])
            self.assertEqual(2, cmds.currentTime(query=True))
            self.assertTrue(cmds.autoKeyframe(query=True, state=True))
            self.assertFalse(runtime.OWNED_ROOTS)
            self.assertFalse([p for p in root.iterdir() if p.name.startswith('mtk_playblast_')])
            bad = root / 'bad_images'; bad.mkdir()
            (bad / 'capture.0001.jpg').write_bytes(b'invalid JPEG')
            protected = root / 'protected.mov'
            protected.write_bytes(b'original output bytes')
            failed = TOOL.run(action='encode_images', image_folder=str(bad), output_dir=directory, basename='protected', fps=24, ffmpeg_path=FFMPEG, overwrite=True)
            self.assertFalse(failed.success)
            self.assertIn('FFmpeg', failed.message)
            self.assertEqual(b'original output bytes', protected.read_bytes())
            self.assertEqual([], failed.data['completed_files'])
            self.assertFalse(runtime.ACTIVE)
            self.assertFalse(runtime.OWNED_ROOTS)

    @unittest.skipUnless(FFMPEG, 'Actual FFmpeg unavailable')
    def test_capture_transaction_shim_failure_restores_view_and_reports_partial(self):
        # Real Maya camera/time/scene data; modelPanel and playblast are explicit shims.
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = fixture_images(root)
            camera1 = cmds.camera(name='rig:camA')[0]
            camera2 = cmds.camera(name='rig:camB')[0]
            view = {'camera': 'persp'}
            real_about = cmds.about
            def about(**kwargs):
                return False if kwargs.get('batch') else real_about(**kwargs)
            def panels(**kwargs):
                return 'fixturePanel' if kwargs.get('withFocus') else ['fixturePanel']
            def editor(panel, **kwargs):
                return view['camera']
            def look(panel, camera):
                view['camera'] = camera
            def blast(**kwargs):
                if 'camB' in view['camera']:
                    raise RuntimeError('injected second camera capture failure')
                dest = Path(kwargs['filename']).parent
                for p in source.iterdir():
                    shutil.copy2(p, dest / p.name)
                cmds.currentTime(3)
                cmds.select(clear=True)
                return str(dest)
            cmds.select(self.node)
            selection = cmds.ls(selection=True, long=True)
            with patch.object(cmds, 'about', about), patch.object(cmds, 'getPanel', panels), patch.object(cmds, 'modelEditor', editor), patch.object(cmds, 'lookThru', look), patch.object(cmds, 'playblast', blast):
                args = dict(action='export', output_dir=directory, basename='shot', cameras=[camera1, camera2], multi_camera=True, start=1, end=3, width=32, height=32, ffmpeg_path=FFMPEG)
                self.assertTrue(TOOL.run(dry_run=True, **args).success)
                self.assertFalse(list(root.glob('*.mov')))
                result = TOOL.run(**args)
                self.assertFalse(result.success)
                self.assertEqual(1, len(result.data['completed_files']))
            self.assertEqual('persp', view['camera'])
            self.assertEqual(2, cmds.currentTime(query=True))
            self.assertEqual(selection, cmds.ls(selection=True, long=True))
            self.assertTrue(cmds.autoKeyframe(query=True, state=True))
            self.assertFalse(runtime.ACTIVE)
            self.assertFalse(runtime.OWNED_ROOTS)
            self.assertFalse([p for p in root.iterdir() if p.name.startswith('mtk_playblast_')])

    def test_lazy_native_import_batch_refusal_and_helpers_guard(self):
        self.assertFalse(TOOL.validate(action='open_ui').success)
        self.assertFalse(TOOL.validate(action='export', output_dir=tempfile.gettempdir()).success)
        obj = native.PlayblastConverterUI.__new__(native.PlayblastConverterUI)
        with self.assertRaises(RuntimeError):
            obj.cleanup_temp_dir()
        with self.assertRaises(RuntimeError):
            obj.rename_images(tempfile.gettempdir())
        self.assertEqual(runtime.SETTINGS, native.load_ffmpeg_settings())

    @unittest.skipUnless(FFMPEG, 'Actual FFmpeg unavailable')
    def test_qt_branch_with_shim_audio_and_post_conversion(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = fixture_images(root)
            raw_movie = self.ok(action='encode_images', image_folder=str(source), output_dir=directory, basename='raw_fixture', fps=24, ffmpeg_path=FFMPEG)['files'][0]
            audio_file = root / 'tone.wav'
            media.invoke([FFMPEG, '-nostdin', '-y', '-f', 'lavfi', '-i', 'sine=frequency=440:duration=0.5', str(audio_file)], 20)
            audio = cmds.createNode('audio', name='fixtureSound')
            cmds.setAttr(audio + '.filename', str(audio_file), type='string')
            cmds.setAttr(audio + '.offset', 1)
            camera = cmds.camera(name='captureCamera')[0]
            view = {'camera': 'persp'}
            calls = []
            real_about = cmds.about
            def about(**kwargs):
                return False if kwargs.get('batch') else real_about(**kwargs)
            def panels(**kwargs):
                return 'fixturePanel' if kwargs.get('withFocus') else ['fixturePanel']
            def look(panel, value):
                view['camera'] = value
            def blast(**kwargs):
                calls.append(kwargs)
                shutil.copy2(raw_movie, kwargs['filename'])
            cmds.select(self.node)
            with patch.object(cmds, 'about', about), patch.object(cmds, 'getPanel', panels), patch.object(cmds, 'modelEditor', lambda *args, **kwargs: view['camera']), patch.object(cmds, 'lookThru', look), patch.object(cmds, 'playblast', blast):
                data = self.ok(action='export', mode='qt', output_dir=directory, basename='qt_result', cameras=[camera], start=1, end=3, scale=.5, width=32, height=32, include_audio=True, audio_node=audio, audio_offset_frames=1, convert_mp4=True, convert_gif=True, ffmpeg_path=FFMPEG)
            self.assertEqual(3, len(data['files']))
            self.assertTrue(all(Path(f).is_file() and Path(f).stat().st_size for f in data['files']))
            self.assertEqual('qt', calls[0]['format'])
            self.assertEqual(50, calls[0]['percent'])
            self.assertEqual('persp', view['camera'])
            self.assertEqual(2, cmds.currentTime(query=True))
            self.assertFalse(runtime.OWNED_ROOTS)


if __name__ == '__main__':
    try:
        unittest.main(verbosity=2)
    finally:
        maya.standalone.uninitialize()
