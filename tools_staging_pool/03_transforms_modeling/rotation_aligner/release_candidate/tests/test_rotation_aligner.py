import ast
import hashlib
import json
from pathlib import Path
import runpy
import unittest
RC=Path(__file__).resolve().parents[1]
if (RC/'launch_candidate.py').is_file(): TOOL=runpy.run_path(str(RC/'launch_candidate.py'))['load_tool']()
else:
    from maya_toolkit.tools.rotation_aligner import RotationAlignerTool
    TOOL=RotationAlignerTool()
from maya_toolkit.tools.rotation_aligner.tool import normalize
import maya_toolkit.tools.rotation_aligner as package


class Checks(unittest.TestCase):
    def test_full_definitions_ui_original_archive_and_schema(self):
        pkg=Path(package.__file__).parent
        rows=json.loads((pkg/'catalog.json').read_text(encoding='utf8'))['files']
        self.assertEqual(2,len(rows))
        for row in rows: self.assertEqual(row['sha256'],hashlib.sha256((pkg/row['archive']).read_bytes()).hexdigest())
        row=next(row for row in rows if row['archive'].endswith('.py.original')); raw=(pkg/row['archive']).read_bytes()
        original=ast.parse(raw); native=ast.parse((pkg/'native.py').read_text(encoding='utf8'))
        self.assertEqual({n.name for n in ast.walk(original) if isinstance(n,ast.FunctionDef)},{n.name for n in ast.walk(native) if isinstance(n,ast.FunctionDef)})
        self.assertFalse(any(isinstance(n,ast.Expr) and isinstance(n.value,ast.Call) for n in native.body))
        self.assertEqual('rotation_aligner',TOOL.to_mcp_tool()['name'])

    def test_strict_fields_signed_axes_time_and_pairs(self):
        self.assertEqual('timeline',normalize({})['time_mode'])
        for p in ({'full_alignment':1},{'source_axis':'Y'},{'per_frame_iters':0},{'per_frame_iters':101},{'custom_start':1.5},{'rotate_axes':{'x':False,'y':False,'z':False}},{'pairs':[{'source':'a'}]},{'time_next_frame':True},{'objects':['a']}):
            with self.assertRaises(ValueError): normalize(p)


if __name__=='__main__': unittest.main()
