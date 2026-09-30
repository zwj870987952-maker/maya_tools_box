"""Offline contract tests; do not claim real Maya acceptance."""
import importlib.util
from pathlib import Path
import sys
import unittest
from unittest import mock

HERE = Path(__file__).resolve()
REPO = next(parent for parent in HERE.parents if (parent / "maya_toolkit/framework/base_tool.py").is_file())
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from maya_toolkit.framework import ToolRegistry
REGISTERED_BEFORE = ToolRegistry.get("reset_pivot")
PACKAGE = HERE.parents[1] / "maya_toolkit/tools/reset_pivot"
NAME = "offline_reset_pivot"
spec = importlib.util.spec_from_file_location(NAME, PACKAGE / "__init__.py", submodule_search_locations=[str(PACKAGE)])
package = importlib.util.module_from_spec(spec)
sys.modules[NAME] = package
spec.loader.exec_module(package)
operations = sys.modules[NAME + ".operations"]


class SceneCommands:
    def __init__(self):
        self.nodes = {"group-id": {"name": "group", "parent": None, "type": "transform"}, "cube-id": {"name": "cube", "parent": "group-id", "type": "transform"}, "joint-id": {"name": "joint", "parent": None, "type": "joint"}}
        self.selection = ["cube-id"]
        self.writes = []
        self.blocked = set()
        self.fail_xform = False

    def path(self, uid):
        data = self.nodes[uid]
        return (self.path(data["parent"]) if data["parent"] else "") + "|" + data["name"]

    def uid(self, node):
        if node in self.nodes:
            return node
        matches = [uid for uid in self.nodes if node in (self.path(uid), self.nodes[uid]["name"])]
        if len(matches) != 1:
            raise ValueError("Ambiguous or stale node: " + node)
        return matches[0]

    def ls(self, node=None, selection=False, long=False, uuid=False, allPaths=False):
        if selection:
            return [self.path(uid) for uid in self.selection]
        try:
            uid = self.uid(node)
            return [uid if uuid else self.path(uid)]
        except ValueError:
            return []

    def nodeType(self, node):
        return self.nodes[self.uid(node)]["type"]

    def referenceQuery(self, node, **kwargs):
        return False

    def lockNode(self, node, **kwargs):
        return [False]

    def getAttr(self, plug, settable=False):
        if settable:
            return plug not in self.blocked
        if plug.endswith(".jointOrient"):
            return [(10.0, 20.0, 30.0)]
        raise ValueError(plug)

    def listRelatives(self, node, **kwargs):
        if kwargs.get("shapes"):
            return []
        parent = self.nodes[self.uid(node)]["parent"]
        return [self.path(parent)] if parent else []

    def listConnections(self, plug, **kwargs):
        return []

    def parent(self, node, parent=None, world=False):
        uid = self.uid(node)
        parent_id = self.uid(parent) if parent else None
        self.nodes[uid]["parent"] = parent_id
        self.writes.append(("parent", uid, parent_id))
        return [self.path(uid)]

    def xform(self, node, query=False, **kwargs):
        uid = self.uid(node)
        if query:
            return [0, 0, 0, 0, 0, 0] if kwargs.get("pivots") else [1, 2, 3]
        if self.fail_xform:
            raise RuntimeError("Injected xform failure")
        self.writes.append(("xform", uid, kwargs))

    def makeIdentity(self, node, **kwargs):
        self.writes.append(("freeze", self.uid(node), kwargs))


class ResetPivotTests(unittest.TestCase):
    def setUp(self):
        self.scene = SceneCommands()
        self.tool = package.ResetPivotTool()
        self.patch = mock.patch.object(operations, "maya_commands", return_value=self.scene)
        self.patch.start()
        self.addCleanup(self.patch.stop)

    def test_all_dry_runs_keep_selection_parent_and_scene_unchanged(self):
        for action in operations.ACTIONS:
            kwargs = {"action": action, "target_nodes": ["|group|cube"]}
            if action == "joint":
                kwargs["source_joint"] = "|joint"
            result = self.tool.run(dry_run=True, **kwargs)
            self.assertTrue(result.success, result.message)
            self.assertTrue(result.dry_run)
            self.assertEqual(self.scene.writes, [])
            self.assertEqual(self.scene.path("cube-id"), "|group|cube")
            self.assertEqual(self.scene.selection, ["cube-id"])

    def test_empty_explicit_targets_and_unknown_arguments_reject_before_writes(self):
        for kwargs in ({"target_nodes": []}, {"target_nodes": "cube"}, {"action": "bogus"}, {"unexpected": True}):
            self.assertFalse(self.tool.run(dry_run=True, **kwargs).success)
        self.assertEqual(self.scene.writes, [])

    def test_locked_or_driven_attribute_blocks_whole_batch(self):
        self.scene.blocked.add("|group|cube.rotateX")
        result = self.tool.run(target_nodes=["|joint", "|group|cube"])
        self.assertFalse(result.success)
        self.assertEqual(self.scene.writes, [])

    def test_old_long_path_invalid_after_reparent_but_world_action_succeeds(self):
        result = self.tool.run(action="world", target_nodes=["|group|cube"])
        self.assertTrue(result.success, result.message)
        self.assertEqual(result.data["processed_nodes"], ["|group|cube"])
        self.assertEqual(self.scene.nodes["cube-id"]["parent"], "group-id")

    def test_failure_restores_parent_and_reports_partial_effects(self):
        self.scene.fail_xform = True
        result = self.tool.run(action="world", target_nodes=["|group|cube"])
        self.assertFalse(result.success)
        self.assertTrue(result.data["partial_changes_possible"])
        self.assertEqual(self.scene.nodes["cube-id"]["parent"], "group-id")
        self.assertIn("Injected xform failure", result.errors)

    def test_no_parent_is_skipped_with_warning(self):
        result = self.tool.run(action="parent", target_nodes=["|group"])
        self.assertTrue(result.success)
        self.assertEqual(result.data["processed_count"], 0)
        self.assertTrue(result.warnings)
        self.assertEqual(self.scene.writes, [])

    def test_duplicate_targets_execute_once(self):
        result = self.tool.run(action="origin", target_nodes=["cube", "|group|cube"])
        self.assertTrue(result.success)
        self.assertEqual(result.data["processed_count"], 1)

    def test_joint_source_cannot_be_a_target_and_explicit_targets_require_source(self):
        for kwargs in ({"action": "joint", "target_nodes": ["cube"]}, {"action": "joint", "source_joint": "joint", "target_nodes": ["joint"]}):
            self.assertFalse(self.tool.run(**kwargs).success)
        self.assertEqual(self.scene.writes, [])

    def test_result_serializes_and_schema_exports(self):
        result = self.tool.run(dry_run=True, target_nodes=["cube"])
        self.assertIn("reset_pivot", result.to_json())
        self.assertEqual(self.tool.to_mcp_tool()["inputSchema"]["additionalProperties"], False)
        self.assertEqual(self.tool.to_openai_tool()["function"]["name"], "reset_pivot")

    def test_candidate_does_not_register_itself(self):
        self.assertIs(ToolRegistry.get("reset_pivot"), REGISTERED_BEFORE)


if __name__ == "__main__":
    unittest.main()
