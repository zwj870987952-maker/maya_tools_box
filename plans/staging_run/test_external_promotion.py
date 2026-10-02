"""Exercise external acceptance gate and untouched Maya registry using a temp repo."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
class Tests(unittest.TestCase):
    def test_preview_gate_apply_and_conflict(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            script = root / 'plans/staging_run/promote_candidate.py'
            script.parent.mkdir(parents=True)
            script.write_bytes((HERE / script.name).read_bytes())
            registry = root / 'maya_toolkit/tools/__init__.py'
            registry.parent.mkdir(parents=True); registry.write_bytes(b'unchanged registry\n')
            rc = root / 'tools_staging_pool/ue_test/release_candidate'
            src = rc / 'engine_toolkit/tools/ue_test/__init__.py'
            src.parent.mkdir(parents=True); src.write_bytes(b'def run(): return 1\n')
            desc = {'tool_id': 'ue_test', 'runtime': 'unreal_editor', 'registration': None,
                'entry_module': 'engine_toolkit.tools.ue_test', 'files': [{'source': 'engine_toolkit/tools/ue_test/__init__.py', 'target': 'engine_toolkit/tools/ue_test/__init__.py'}]}
            (rc / 'promotion.json').write_text(json.dumps(desc))
            def call(*args):
                return subprocess.run([sys.executable, str(script), '--candidate', str(rc), *args], capture_output=True)
            preview = call(); self.assertEqual(preview.returncode, 0, preview.stderr)
            hash_value = json.loads(preview.stdout)['candidate_sha256']
            self.assertNotEqual(call('--apply').returncode, 0)
            target = root / desc['files'][0]['target']; self.assertFalse(target.exists())
            accepted = root / 'accepted.json'
            evidence = {'passed': True, 'tool_id': 'ue_test', 'candidate_sha256': 'wrong', 'runtime_version': 'UE test', 'accepted_by': 'test', 'date': '2026-10-02'}
            accepted.write_text(json.dumps(evidence))
            self.assertNotEqual(call('--apply', '--acceptance', str(accepted)).returncode, 0)
            self.assertFalse(target.exists())
            evidence['candidate_sha256'] = hash_value
            accepted.write_text(json.dumps(evidence))
            result = call('--apply', '--acceptance', str(accepted)); self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(target.read_bytes(), src.read_bytes()); self.assertEqual(registry.read_bytes(), b'unchanged registry\n')
            self.assertNotEqual(call('--apply', '--acceptance', str(accepted)).returncode, 0)
    def test_external_cannot_target_formal_maya(self):
        import promote_candidate as m
        with tempfile.TemporaryDirectory() as d:
            candidate = Path(d)
            desc = {'tool_id': 'ue_test', 'runtime': 'unreal_editor', 'files': [{'source': 'maya_toolkit/tools/injection.py', 'target': 'maya_toolkit/tools/injection.py'}]}
            with self.assertRaisesRegex(ValueError, 'namespace'): m.payload(candidate, desc)

if __name__ == '__main__': unittest.main()
