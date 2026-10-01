import ast
import hashlib
import json
from pathlib import Path
import runpy
import sys
import unittest
RC = Path(__file__).resolve().parents[1]
if (RC/'launch_candidate.py').is_file():
    TOOL = runpy.run_path(str(RC/'launch_candidate.py'))['load_tool']()
else:
    from maya_toolkit.tools.hierarchy_analyzer import HierarchyAnalyzerTool
    TOOL = HierarchyAnalyzerTool()
mod = sys.modules[TOOL.__class__.__module__]
graph = __import__(mod.__package__+'.graph', fromlist=['graph'])
PKG = Path(mod.__file__).parent


class OfflineChecks(unittest.TestCase):
    def test_complete_seven_functions_and_original_bytes_preserved(self):
        c = json.loads((PKG/'catalog.json').read_text(encoding='utf-8'))
        for row in c['files']:
            self.assertEqual(row['sha256'], hashlib.sha256((PKG/row['archive']).read_bytes()).hexdigest())
        tree = ast.parse((PKG/'original_logic.py').read_text(encoding='utf-8'))
        self.assertEqual(c['functions'], [n.name for n in tree.body if isinstance(n, ast.FunctionDef)])
        self.assertEqual(7, len(c['functions']))
        self.assertFalse(any(isinstance(n, ast.Expr) and isinstance(n.value, ast.Call) for n in tree.body))
        self.assertEqual('hierarchy_analyzer', TOOL.to_mcp_tool()['name'])

    def test_stable_actual_layers_indirect_projection_and_same_layer_guard(self):
        g = {'A': {'hidden'}, 'hidden': {'B'}, 'B': {'C'}, 'C': set(), 'isolated': set()}
        nodes = ['C', 'isolated', 'B', 'A']
        selected = graph.project(g, nodes)
        out = graph.layers(selected, nodes)
        self.assertEqual([['isolated', 'A'], ['B'], ['C']], out['layers'])
        self.assertTrue(graph.verify(selected, out['layers'], nodes))
        self.assertFalse(graph.verify(selected, [nodes], nodes))
        self.assertFalse(graph.verify(selected, [['A'], ['B'], ['C']], nodes))

    def test_cycles_and_downstream_blocking_not_fake_layers(self):
        g = {'A': {'B'}, 'B': {'A', 'C'}, 'C': set(), 'free': set()}
        out = graph.layers(g, ['A', 'B', 'C', 'free'])
        self.assertEqual([['free']], out['layers'])
        self.assertEqual([['A', 'B']], out['cycles'])
        self.assertEqual(['A', 'B', 'C'], out['unresolved'])
        self.assertFalse(out['valid'])
        self.assertEqual([['x']], graph.layers({'x': {'x'}}, ['x'])['cycles'])

    def test_long_chain_does_not_recurse_and_typed_bounds(self):
        nodes = [str(i) for i in range(1500)]
        g = {n: {nodes[i+1]} if i+1 < len(nodes) else set() for i, n in enumerate(nodes)}
        self.assertEqual(1500, len(graph.components(g, nodes)))
        for args in ({'objects': []}, {'objects': ['a', 'a']}, {'max_nodes': 0}, {'max_nodes': True}, {'include_graph': 'yes'}, {'max_edges': float('inf')}):
            with self.assertRaises(ValueError):
                mod.normalize(**args)


if __name__ == '__main__':
    unittest.main()
