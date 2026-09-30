import ast
import hashlib
import json
from pathlib import Path
import runpy
import sys
import tempfile
import unittest

RC = Path(__file__).resolve().parents[1]
if (RC / 'launch_candidate.py').exists():
    TOOL = runpy.run_path(str(RC / 'launch_candidate.py'))['load_tool']()
else:
    sys.path.insert(0, str(RC))
    from maya_toolkit.tools.mov_playblast import MovPlayblastTool
    TOOL = MovPlayblastTool()
from maya_toolkit.tools.mov_playblast import media
from maya_toolkit.tools.mov_playblast.tool import normalize
PACKAGE = Path(sys.modules['maya_toolkit.tools.mov_playblast'].__file__).parent


class OfflineTests(unittest.TestCase):
    def test_complete_source_methods_lazy_and_schema(self):
        data = json.loads((PACKAGE / 'catalog.json').read_text(encoding='utf-8'))
        self.assertEqual(3, len(data['raw_files']))
        for item in data['raw_files']:
            self.assertEqual(item['sha256'], hashlib.sha256((PACKAGE / item['path']).read_bytes()).hexdigest())
        tree = ast.parse((PACKAGE / 'native.py').read_text(encoding='utf-8'))
        cls = next(n for n in tree.body if isinstance(n, ast.ClassDef))
        self.assertEqual(43, len(data['methods']))
        self.assertEqual(data['methods'], [n.name for n in cls.body if isinstance(n, ast.FunctionDef)])
        self.assertEqual(data['functions'], [n.name for n in tree.body if isinstance(n, ast.FunctionDef)])
        self.assertNotIn('maya.cmds', sys.modules)
        self.assertEqual('mov_playblast', TOOL.to_mcp_tool()['name'])
        for a in ({'action': 'bad'}, {'unknown': 1}, {'overwrite': 1}, {'hold': 11}, {'start': 2.5}, {'scale': float('nan')}, {'mode': 'qt', 'hold': 2}, {'cameras': ['a', 'a']}):
            with self.assertRaises(ValueError):
                normalize(**a)

    def test_atomic_conflicts_increment_all_extensions_and_ownership(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'film.mp4').write_bytes(b'original')
            with self.assertRaises(ValueError):
                media.destinations(directory, [('film', ['.mov', '.mp4'])])
            output = media.destinations(directory, [('film', ['.mov', '.mp4'])], increment=True)
            self.assertEqual('film_1.mov', Path(output[0][0]['path']).name)
            stage = root / 'stage.mov'
            stage.write_bytes(b'new')
            raced = media.destinations(directory, [('race', ['.mov'])])[0][0]
            (root / 'race.mov').write_bytes(b'foreign')
            with self.assertRaises(RuntimeError):
                media.publish(stage, raced)
            self.assertEqual(b'foreign', (root / 'race.mov').read_bytes())
            target = media.destinations(directory, [('film', ['.mp4'])], overwrite=True)[0][0]
            media.publish(stage, target, overwrite=True)
            self.assertEqual(b'new', (root / 'film.mp4').read_bytes())
            for name in ('../escape', 'a/b', 'CON', 'bad:cam', 'tail.'):
                with self.assertRaises(ValueError):
                    media.destinations(directory, [(name, ['.mov'])])

    def test_hold_sort_and_readonly_original_images(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            src = root / 'src'; src.mkdir()
            for index, contents in ((-3, b'a'), (-2, b'b'), (-1, b'c')):
                (src / ('capture.%04d.jpg' % index)).write_bytes(contents)
            originals = {p.name: p.read_bytes() for p in src.iterdir()}
            count = media.prepare_sequence(media.sequence_files(str(src)), root / 'seq', hold=2)
            self.assertEqual(4, count)
            self.assertEqual([b'a', b'a', b'c', b'c'], [p.read_bytes() for p in sorted((root / 'seq').iterdir())])
            self.assertEqual(originals, {p.name: p.read_bytes() for p in src.iterdir()})


if __name__ == '__main__':
    unittest.main(verbosity=2)
