import ast
import hashlib
import io
import json
from pathlib import Path
import runpy
import stat
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

RC = Path(__file__).resolve().parents[1]
if (RC / 'launch_candidate.py').is_file():
    TOOL = runpy.run_path(str(RC / 'launch_candidate.py'))['load_tool']()
else:
    from maya_toolkit.tools.tb_anim_tools import TBAnimToolsTool
    TOOL = TBAnimToolsTool()
from maya_toolkit.tools.tb_anim_tools import files
from maya_toolkit.tools.tb_anim_tools.tool import normalize
PKG = files.PACKAGE


class Offline(unittest.TestCase):
    def test_complete_source_zip_originals_and_lazy_import(self):
        data = files.snapshot()
        self.assertEqual(files.COMMIT, data['commit'])
        self.assertGreater(len(data['files']), 200)
        paths = {x['path'] for x in data['files']}
        for part in ('Icons/', 'apps/', 'plugins/', 'appData/', 'proApps/'):
            self.assertTrue(any(x.startswith(part) for x in paths), part)
        catalog = json.loads((PKG / 'catalog.json').read_text(encoding='utf-8'))
        self.assertEqual(5, len(catalog['original_files']))
        for row in catalog['original_files']:
            self.assertEqual(row['sha256'], files.digest((PKG / row['archive']).read_bytes()))
        original = ast.parse((PKG / 'upstream/tbAnimToolsInstaller.py.original').read_bytes())
        port = ast.parse((PKG / 'ui.py').read_bytes())
        original_methods = {x.name for n in original.body if isinstance(n, ast.ClassDef) for x in n.body if isinstance(x, ast.FunctionDef)}
        candidate_methods = {x.name for n in port.body if isinstance(n, ast.ClassDef) for x in n.body if isinstance(x, ast.FunctionDef)}
        self.assertTrue(original_methods <= candidate_methods)
        self.assertNotIn('maya.cmds', sys.modules)
        self.assertNotIn('tbtoolsInstaller', sys.modules)
        self.assertEqual('tb_anim_tools', TOOL.to_openai_tool()['function']['name'])

    def test_zip_traversal_alias_link_and_collision_guards(self):
        cases = ['../escape', '/outside', files.PREFIX + '/../../outside', files.PREFIX + '/C:evil', files.PREFIX + '/CON.txt', files.PREFIX + '/tail.', files.PREFIX + '/folder\\bad', files.PREFIX + '/a/../b']
        for name in cases:
            with self.subTest(name=name):
                stream = io.BytesIO()
                with zipfile.ZipFile(stream, 'w') as archive:
                    archive.writestr(name, b'x')
                stream.seek(0)
                with zipfile.ZipFile(stream) as archive, self.assertRaises(ValueError):
                    files.members(archive)
        for kind in ('link', 'case', 'collision'):
            stream = io.BytesIO()
            with zipfile.ZipFile(stream, 'w') as archive:
                if kind == 'link':
                    info = zipfile.ZipInfo(files.PREFIX + '/link')
                    info.external_attr = (stat.S_IFLNK | 0o777) << 16
                    archive.writestr(info, 'outside')
                else:
                    archive.writestr(files.PREFIX + '/a', b'x')
                    archive.writestr(files.PREFIX + ('/A' if kind == 'case' else '/a/b'), b'y')
            stream.seek(0)
            with zipfile.ZipFile(stream) as archive, self.assertRaises(ValueError):
                files.members(archive)

    def test_full_install_no_overwrite_and_failure_cleanup(self):
        with tempfile.TemporaryDirectory() as folder:
            dest = Path(folder) / 'suite'
            before = list(Path(folder).iterdir())
            files.install_plan(str(dest))
            self.assertEqual(before, list(Path(folder).iterdir()))
            plan = files.install(str(dest))
            self.assertEqual(len(plan['files']), len(files.installed(str(dest))['files']))
            for row in plan['files']:
                self.assertEqual(row['sha256'], files.digest((dest / row['path']).read_bytes()))
            with self.assertRaises(ValueError):
                files.install(str(dest))
            (dest / 'tbtoolsInstaller.py').write_bytes(b'user-changed')
            with self.assertRaises(ValueError):
                files.installed(str(dest))
            failed = Path(folder) / 'failed'
            with patch.object(files.os, 'rename', side_effect=OSError('simulated publish failure')):
                with self.assertRaises(OSError):
                    files.install(str(failed))
            self.assertFalse(failed.exists())
            self.assertFalse(any(p.name.startswith('.tb-staging-') for p in Path(folder).iterdir()))
            (Path(folder) / 'foreign').mkdir()
            with self.assertRaises(ValueError):
                files.install(str(Path(folder) / 'foreign'))

    def test_schema_and_paths_reject_ambiguous_input(self):
        for params in ({'action': 'install_files'}, {'action': 'other'}, {'unknown': 1}, {'acknowledge_external_effects': 1}, {'destination': 'x'}, {'action': 'install_files', 'destination': 'x', 'module_dir': 'y'}):
            with self.assertRaises(ValueError):
                normalize(**params)
        for path in ('relative', 'C:/a/../b', 'C:/a\nfile', 'C:/a/"file'):
            with self.assertRaises(ValueError):
                files.explicit_path(path)


if __name__ == '__main__':
    unittest.main(verbosity=2)
