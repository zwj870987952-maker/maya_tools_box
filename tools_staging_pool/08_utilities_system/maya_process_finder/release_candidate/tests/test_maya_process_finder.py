import importlib.util,sys,unittest
from pathlib import Path
from unittest.mock import patch
rc=Path(__file__).resolve().parents[1]
if (rc/'launch_candidate.py').exists():
    spec=importlib.util.spec_from_file_location('launch_finder',rc/'launch_candidate.py');launch=importlib.util.module_from_spec(spec);spec.loader.exec_module(launch);tool=launch.load_tool()
else:
    import engine_toolkit.tools.maya_process_finder as tool
class Process:
    ended=[]
    def __init__(self,pid):self.pid=pid
    def oneshot(self):return self
    def __enter__(self):return self
    def __exit__(self,*args):pass
    def name(self):return 'maya.exe'
    def create_time(self):return 123.5
    def status(self):return 'running'
    def exe(self):return 'C:/mock/maya.exe'
    def terminate(self):self.ended.append(self.pid)
    def kill(self):self.ended.append(self.pid)
class FakePsutil:Process=Process
class Checks(unittest.TestCase):
    def test_import_dry_run_and_pid_reuse_guard_without_real_actions(self):
        self.assertIsNone(tool._monitor)
        with patch.object(tool,'Windows',side_effect=AssertionError('No WinAPI allowed')):
            self.assertTrue(tool.run(action='start_monitor')['success']);self.assertIsNone(tool._monitor)
        with patch.object(tool,'_psutil',return_value=FakePsutil):
            self.assertFalse(tool.run(False,action='terminate',pid=429490001)['success'])
            self.assertFalse(tool.run(False,action='terminate',pid=429490001,create_time=1,confirm_terminate=True)['success'])
            self.assertTrue(tool.run(action='terminate',pid=429490001,create_time=123.5,confirm_terminate=True)['success']);self.assertEqual(Process.ended,[])
            self.assertTrue(tool.run(False,action='terminate',pid=429490001,create_time=123.5,confirm_terminate=True)['success']);self.assertEqual(Process.ended,[429490001])
    def test_monitor_queue_is_bounded_and_no_background_work_on_construction(self):
        monitor=tool.Monitor('hook');self.assertIsNone(monitor.thread);self.assertIsNone(monitor.handle)
        for n in range(300):monitor.enqueue({'event':n})
        self.assertEqual(len(monitor.drain()),256);monitor.stop()
if __name__=='__main__':unittest.main()
