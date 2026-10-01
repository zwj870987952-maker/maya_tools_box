import os
from pathlib import Path
import runpy
import sys
import unittest
if os.environ.get('STAGING_ISOLATED_MAYAPY')!='1':
    raise RuntimeError('Isolated Maya only')
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds,mel
TOOL=runpy.run_path(str(Path(__file__).resolve().parents[1]/'launch_candidate.py'))['load_tool']()
from maya_toolkit.tools.cvwrap_weightdriver import runtime


class Checks(unittest.TestCase):
    def setUp(self):
        cmds.file(new=True,force=True)
        cmds.undoInfo(state=True)
        self.mesh=cmds.polyPlane(name='surface')[0]
        cmds.select(self.mesh)

    def state(self):
        return (set(cmds.ls(long=True)),cmds.ls(selection=True,long=True),cmds.currentTime(query=True),cmds.undoInfo(query=True,undoName=True),runtime.plugins(),list(sys.path),os.environ.get('MAYA_ICON_PATH'),sorted(n for n in sys.modules if n=='mgear' or n.startswith('mgear.') or n=='cvwrap' or n.startswith('cvwrap.')))

    def test_status_and_missing_dependencies_never_load_or_activate(self):
        before=self.state()
        result=TOOL.run(action='status',dry_run=True)
        self.assertTrue(result.success,result.message)
        self.assertEqual(532,result.data['files'])
        self.assertEqual(4614,result.data['definitions'])
        self.assertEqual(before,self.state())
        # This isolated Maya has no supplied third-party binaries. Missing
        # dependencies are genuine failures, not mock plugin implementations.
        for action in ('create_wrap','cvwrap_rebind_ui','weightdriver_editor','rbf_manager','mgear_menu'):
            p={'action':action}
            if action=='create_wrap':
                p['objects']=[self.mesh,'persp']
            result=TOOL.run(dry_run=True,**p)
            self.assertFalse(result.success,result.message)
            self.assertTrue('native' in result.message.lower() or 'PyMel' in result.message or 'interactive' in result.message.lower())
            self.assertEqual(before,self.state())
        with self.assertRaises(RuntimeError):
            TOOL.show_ui()

    def test_all_complete_native_mel_procedures_compile_without_scene_writes(self):
        before=self.state()
        for path in sorted(runtime.NATIVE.glob('*.mel')):
            mel.eval('source "'+path.as_posix()+'";')
        self.assertEqual(before,self.state())
        self.assertTrue(mel.eval('exists weightDriverEditRBF'))
        self.assertTrue(mel.eval('exists AEcvWrapTemplate'))
        self.assertTrue(mel.eval('exists weightDriverUpdateEvaluation'))


if __name__=='__main__':
    unittest.main()
