"""Exercise promotion on a disposable miniature repository, never the real registry."""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

SCRIPT = Path(__file__).resolve().parents[1] / "promote_candidate.py"
spec = importlib.util.spec_from_file_location("promotion_under_test", SCRIPT)
promotion = importlib.util.module_from_spec(spec)
spec.loader.exec_module(promotion)


class PromotionTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="promotion_test_")
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.patch = mock.patch.object(promotion, "ROOT", self.root)
        self.patch.start()
        self.addCleanup(self.patch.stop)
        self.registry = self.root / "maya_toolkit/tools/__init__.py"
        self.registry.parent.mkdir(parents=True)
        self.original = b"ALL_TOOL_CLASSES = [\n]\n__all__ = [\n]\n"
        self.registry.write_bytes(self.original)
        self.candidate = self.root / "tools_staging_pool/group/tool/release_candidate"
        self.candidate.mkdir(parents=True)
        (self.candidate / "tool.py").write_text("class SampleTool:\n    pass\n", encoding="utf-8")
        self.description = {"tool_id": "sample", "registration": {"module": "sample", "class_name": "SampleTool"}, "files": [{"source": "tool.py", "target": "maya_toolkit/tools/sample/__init__.py"}]}
        (self.candidate / "promotion.json").write_text(json.dumps(self.description), encoding="utf-8")

    def run_main(self, *arguments):
        with mock.patch.object(sys, "argv", ["promote", "--candidate", str(self.candidate)] + list(arguments)), mock.patch("builtins.print"):
            promotion.main()

    def test_preview_creates_no_target_and_leaves_registry_unchanged(self):
        self.run_main()
        self.assertFalse((self.root / "maya_toolkit/tools/sample").exists())
        self.assertEqual(self.registry.read_bytes(), self.original)

    def test_apply_without_acceptance_refuses_before_mutation(self):
        with self.assertRaises(ValueError):
            self.run_main("--apply")
        self.assertEqual(self.registry.read_bytes(), self.original)

    def test_changed_candidate_is_rejected_with_stale_fingerprint(self):
        acceptance = self.root / "acceptance.json"
        acceptance.write_text(json.dumps({"tool_id": "sample", "passed": True, "maya_version": "mock-only", "accepted_by": "unit-test fixture", "date": "fixture", "candidate_sha256": promotion.fingerprint(self.candidate, self.description)}))
        (self.candidate / "tool.py").write_text("class SampleTool:\n    changed = True\n")
        with self.assertRaises(ValueError):
            self.run_main("--acceptance", str(acceptance), "--apply")
        self.assertEqual(self.registry.read_bytes(), self.original)

    def test_existing_target_is_never_overwritten(self):
        target = self.root / self.description["files"][0]["target"]
        target.parent.mkdir(parents=True)
        target.write_text("user content")
        with self.assertRaises(ValueError):
            self.run_main()
        self.assertEqual(target.read_text(), "user content")

    def test_target_path_cannot_escape_repo(self):
        self.description["files"][0]["target"] = "../outside.py"
        with self.assertRaises(ValueError):
            promotion.payload(self.candidate, self.description)

    def test_registry_patch_merges_into_current_lists(self):
        self.registry.write_text("from .existing import ExistingTool\nALL_TOOL_CLASSES = [\n    ExistingTool,\n]\n__all__ = [\n    'ExistingTool',\n]\n")
        unused_path, unused_original, patched = promotion.registry_change(self.description)
        text = patched.decode("utf-8")
        self.assertIn("from .sample import SampleTool", text)
        self.assertIn("    ExistingTool,", text)
        self.assertIn("    SampleTool,", text)
        self.assertIn("    'SampleTool',", text)
        compile(text, "registry", "exec")


if __name__ == "__main__":
    unittest.main()
