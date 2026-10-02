from pathlib import Path
import importlib.util
import sys
import tempfile
import unittest
rc=Path(__file__).resolve().parents[1]
if (rc/'launch_candidate.py').is_file():
    spec=importlib.util.spec_from_file_location('launch',rc/'launch_candidate.py');launch=importlib.util.module_from_spec(spec);spec.loader.exec_module(launch);tool=launch.load_tool()
else:
    sys.path.insert(0,str(rc));from maya_toolkit.tools.scene_virus_cleaner import SceneVirusCleanerTool;tool=SceneVirusCleanerTool()
from maya_toolkit.tools.scene_virus_cleaner import ascii_filter as a,normalize,clean_files
DATA=b'//Maya ASCII 2025 scene\r\nrequires maya "2025";\r\nrequires "legalPlugin" "1.0";\r\ncurrentUnit -l centimeter;\r\ncreateNode transform -n "cube";\r\nsetAttr ".tx" 4;\r\ncreateNode script -n "vaccine_gene";\r\nsetAttr ".b" -type "string" "python(\\"a; //payload\\");\\nfoo";\r\ncreateNode script -n "myLegitScript";\r\nsetAttr ".b" -type "string" "keep; // quoted";\r\ncreateNode script -n "sceneConfigurationScriptNode";\r\nsetAttr ".st" 6;\r\nconnectAttr "vaccine_gene.message" "cube.message";\r\n// tail \xff\r\n'
class Tests(unittest.TestCase):
    def test_quoted_multiline_payload_and_legacy_bytes_preserved(self):
        out,report=a.clean_bytes(DATA)
        self.assertNotIn(b'vaccine_gene',out);self.assertNotIn(b'//payload',out)
        self.assertIn(b'legalPlugin',out);self.assertIn(b'myLegitScript',out);self.assertIn(b'keep; // quoted',out);self.assertIn(b'// tail \xff\r\n',out)
        self.assertEqual(report['removed_script_nodes'],['vaccine_gene'])
        extra=b'createNode network -n "validData";setAttr ".notes" -type "string" "vaccine_gene.message";'
        kept,_=a.clean_bytes(DATA+extra);self.assertIn(extra,kept)
        broad,report=a.clean_bytes(DATA,'all_scripts',remove_plugin_requires=True)
        self.assertNotIn(b'myLegitScript',broad);self.assertNotIn(b'legalPlugin',broad);self.assertIn(b'sceneConfigurationScriptNode',broad)
        with self.assertRaises(ValueError):a.clean_bytes(DATA+b'setAttr ".b" "unterminated')
    def test_fresh_output_exact_backup_and_invalid_last_preflight(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);source=root/'source.ma';source.write_bytes(DATA);out=root/'new'
            kwargs=dict(action='clean',files=[str(source)],output_dir=str(out))
            self.assertTrue(tool.validate(**kwargs).success);self.assertFalse(out.exists())
            result=clean_files(normalize(kwargs));row=result['completed'][0]
            self.assertEqual(Path(row['backup']).read_bytes(),DATA);self.assertEqual(source.read_bytes(),DATA);self.assertNotIn(b'vaccine_gene',Path(row['output']).read_bytes())
            self.assertFalse(tool.validate(**kwargs).success)
            bad=root/'bad.ma';bad.write_bytes(DATA+b'incompleteCommand');another=root/'another'
            self.assertFalse(tool.validate(action='clean',files=[str(source),str(bad)],output_dir=str(another)).success);self.assertFalse(another.exists())
    def test_cancel_partial_report_and_broad_guard(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);first=root/'a.ma';second=root/'b.ma';first.write_bytes(DATA);second.write_bytes(DATA);calls=[]
            p=normalize(dict(action='clean',files=[str(first),str(second)],output_dir=str(root/'output')))
            result=clean_files(p,progress=lambda *a:calls.append(a),cancel=lambda:bool(calls))
            self.assertTrue(result['cancelled']);self.assertEqual(len(result['completed']),1);self.assertTrue((root/'output/report.json').is_file());self.assertEqual(second.read_bytes(),DATA)
        with self.assertRaises(ValueError):normalize({'script_policy':'all_scripts'})
if __name__=='__main__':unittest.main()
