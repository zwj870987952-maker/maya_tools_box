import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

from maya_toolkit.core import advanced_skeleton as discovery


class TestAdvancedSkeletonDiscovery(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.root = Path(self.directory.name)
        discovery._CACHE.clear()

    def tearDown(self):
        self.directory.cleanup()

    def install(self, folder, version, proc=True):
        root = self.root/folder
        (root/'AdvancedSkeletonFiles').mkdir(parents=True)
        path = root/'AdvancedSkeleton.mel'
        path.write_text('// Version '+version+'\n'+('global proc asMirror () {}\n' if proc else ''), encoding='utf-8')
        return path

    def test_selects_header_version_not_directory_name(self):
        self.install('AdvancedSkeleton9.999','6.580')
        latest = self.install('old_folder_name','6.640')
        with patch.object(discovery, '_roots', return_value=[str(self.root)]):
            self.assertEqual(discovery.resolve()['source_path'],latest.resolve().as_posix())

    def test_explicit_override(self):
        older = self.install('older','6.580')
        self.install('newer','6.640')
        self.assertEqual(discovery.resolve(str(older))['version'],'6.580')

    def test_missing_entrypoint_fails_without_fallback(self):
        self.install('older','6.580')
        self.install('newer','6.640')
        with patch.object(discovery, '_roots', return_value=[str(self.root)]):
            with self.assertRaisesRegex(ValueError,'未自动回退'):
                discovery.resolve(required_procedures=['asNotPresent'])

    def test_refresh_discovers_added_version(self):
        self.install('older','6.580')
        with patch.object(discovery, '_roots', return_value=[str(self.root)]):
            self.assertEqual(discovery.resolve()['version'],'6.580')
            self.install('newer','6.640')
            self.assertEqual(discovery.resolve(refresh=True)['version'],'6.640')

    def test_missing_resources_rejected(self):
        path=self.install('broken','6.640')
        (path.parent/'AdvancedSkeletonFiles').rmdir()
        with self.assertRaisesRegex(ValueError,'资源目录'):
            discovery.inspect(path)

    def test_no_install_is_explicit_error(self):
        with patch.object(discovery, '_roots', return_value=[]):
            with self.assertRaisesRegex(ValueError,'未找到'):
                discovery.resolve()


if __name__ == '__main__':
    unittest.main()
