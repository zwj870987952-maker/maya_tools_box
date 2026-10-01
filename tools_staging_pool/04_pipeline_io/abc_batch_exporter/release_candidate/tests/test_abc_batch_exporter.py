import hashlib
import json
from pathlib import Path
import runpy
import unittest
RC=Path(__file__).resolve().parents[1]
if (RC/'launch_candidate.py').is_file(): TOOL=runpy.run_path(str(RC/'launch_candidate.py'))['load_tool']()
else:
    from maya_toolkit.tools.abc_batch_exporter import ABCBatchExporterTool
    TOOL=ABCBatchExporterTool()
from maya_toolkit.tools.abc_batch_exporter.tool import normalize,make_job,quote
import maya_toolkit.tools.abc_batch_exporter as package


class Checks(unittest.TestCase):
    def test_archive_schema_and_job_flags_quotes(self):
        pkg=Path(package.__file__).parent; rows=json.loads((pkg/'catalog.json').read_text(encoding='utf8'))['files']; self.assertEqual(2,len(rows))
        for row in rows: self.assertEqual(row['sha256'],hashlib.sha256((pkg/row['archive']).read_bytes()).hexdigest())
        self.assertEqual('abc_batch_exporter',TOOL.to_mcp_tool()['name']); self.assertEqual('inspect',normalize({})['action'])
        p=normalize({}); j=make_job(dict(start=1,end=2,step=1,roots=['|a:b'],options=p['options']),'/tmp/with space/file.abc')
        self.assertIn('-root "|a:b"',j); self.assertIn('-file "/tmp/with space/file.abc"',j); self.assertNotIn('True',j); self.assertNotIn('-stripNamespaces',j)

    def test_strict_parameters(self):
        for p in ({'options':{'foo':True}},{'options':{'uv_write':1}},{'step':0},{'step':True},{'start':2,'end':1},{'action':'export','output':'relative.abc'},{'objects':[]},{'objects':['x;\ncallback']},{'set_name':'set*'},{'action':'batch','folder':'relative'},{'action':'materials','step':1}):
            with self.assertRaises(ValueError): normalize(p)
        for s in ('x" -pythonPerFrameCallback malicious','a\nb'):
            with self.assertRaises(ValueError): quote(s)


if __name__=='__main__': unittest.main()
