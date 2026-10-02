"""Windows standalone process finder. Import/preflight never elevates or hooks."""
import math,os,queue,threading,time
parameters_schema={'type':'object','additionalProperties':False,'properties':{
    'action':{'type':'string','enum':['inspect','query_pid','query_cursor','start_monitor','stop_monitor','drain_events','open_task_manager','terminate'],'default':'inspect'},
    'pid':{'type':'integer','minimum':1,'maximum':4294967295},'mode':{'type':'string','enum':['poll','hook'],'default':'poll'},
    'confirm_terminate':{'type':'boolean','default':False},'force':{'type':'boolean','default':False},'create_time':{'type':'number','minimum':0}}}
_monitor=None
def pid(value):
    if type(value) is not int or not 0<value<=4294967295:raise ValueError('Valid Windows DWORD PID required')
    return value
def _psutil():
    import psutil
    return psutil
def details(value):
    process=_psutil().Process(pid(value))
    with process.oneshot():
        result={'pid':value,'name':process.name(),'create_time':process.create_time(),'status':process.status()}
        try:result['exe']=process.exe()
        except _psutil().AccessDenied:result['exe']=None
    result['is_maya']=result['name'].lower()=='maya.exe';return result
def identity(p):
    row=details(p['pid'])
    if row['create_time']!=p['create_time']:raise ValueError('PID lifetime changed; refresh process identity')
    if not row['is_maya'] or p['pid'] in (os.getpid(),os.getppid()):raise ValueError('Only an explicitly selected separate Maya.exe can be ended')
    return row
def validate(**kwargs):
    p=dict(action='inspect',mode='poll',confirm_terminate=False,force=False);p.update(kwargs)
    if set(p)-set(parameters_schema['properties']) or p['action'] not in parameters_schema['properties']['action']['enum'] or p['mode'] not in ('poll','hook'):raise ValueError('Unknown action/mode/argument')
    for key in ('confirm_terminate','force'):
        if type(p[key]) is not bool:raise ValueError('Strict boolean '+key)
    if 'pid' in p:pid(p['pid'])
    if p['action'] in ('query_pid','terminate') and 'pid' not in p:raise ValueError('Explicit pid required')
    if p['action']=='terminate':
        if not p['confirm_terminate'] or type(p.get('create_time')) not in (int,float) or not math.isfinite(p['create_time']) or p['create_time']<0:raise ValueError('Explicit confirmation and queried creation time required; unsaved work will be lost')
        identity(p)
    return p
class Windows:
    def __init__(self):
        if os.name!='nt':raise RuntimeError('Windows required')
        import ctypes
        from ctypes import wintypes
        self.ctypes=ctypes;self.types=wintypes;self.user=ctypes.WinDLL('user32',use_last_error=True);self.kernel=ctypes.WinDLL('kernel32',use_last_error=True)
        U=self.user;K=self.kernel;C=ctypes;W=wintypes
        self.HOOKPROC=C.WINFUNCTYPE(C.c_ssize_t,C.c_int,W.WPARAM,W.LPARAM)
        class MSLL(C.Structure):_fields_=[('pt',W.POINT),('mouseData',W.DWORD),('flags',W.DWORD),('time',W.DWORD),('dwExtraInfo',C.c_size_t)]
        self.MSLL=MSLL
        signatures={'GetCursorPos':([C.POINTER(W.POINT)],W.BOOL),'WindowFromPoint':([W.POINT],W.HWND),'GetWindowThreadProcessId':([W.HWND,C.POINTER(W.DWORD)],W.DWORD),'GetWindowTextLengthW':([W.HWND],C.c_int),'GetWindowTextW':([W.HWND,W.LPWSTR,C.c_int],C.c_int),'GetAsyncKeyState':([C.c_int],C.c_short),'SetWindowsHookExW':([C.c_int,self.HOOKPROC,W.HINSTANCE,W.DWORD],W.HANDLE),'CallNextHookEx':([W.HANDLE,C.c_int,W.WPARAM,W.LPARAM],C.c_ssize_t),'UnhookWindowsHookEx':([W.HANDLE],W.BOOL),'GetMessageW':([C.POINTER(W.MSG),W.HWND,W.UINT,W.UINT],C.c_int),'PeekMessageW':([C.POINTER(W.MSG),W.HWND,W.UINT,W.UINT,W.UINT],W.BOOL),'PostThreadMessageW':([W.DWORD,W.UINT,W.WPARAM,W.LPARAM],W.BOOL),'TranslateMessage':([C.POINTER(W.MSG)],W.BOOL),'DispatchMessageW':([C.POINTER(W.MSG)],C.c_ssize_t)}
        for name,(args,result) in signatures.items():getattr(U,name).argtypes=args;getattr(U,name).restype=result
        K.GetCurrentThreadId.argtypes=[];K.GetCurrentThreadId.restype=W.DWORD;K.GetModuleHandleW.argtypes=[W.LPCWSTR];K.GetModuleHandleW.restype=W.HMODULE
    def cursor(self):
        point=self.types.POINT()
        if not self.user.GetCursorPos(self.ctypes.byref(point)):raise self.ctypes.WinError(self.ctypes.get_last_error())
        return self.at_point(point)
    def at_point(self,point):
        hwnd=self.user.WindowFromPoint(point)
        if not hwnd:raise RuntimeError('No window under cursor')
        value=self.types.DWORD()
        if not self.user.GetWindowThreadProcessId(hwnd,self.ctypes.byref(value)):raise self.ctypes.WinError(self.ctypes.get_last_error())
        size=min(32768,self.user.GetWindowTextLengthW(hwnd));buffer=self.ctypes.create_unicode_buffer(size+1);self.user.GetWindowTextW(hwnd,buffer,size+1)
        return {'pid':value.value,'hwnd':int(hwnd),'window_title':buffer.value}
class Monitor:
    def __init__(self,mode='poll'):
        self.mode=mode;self.events=queue.Queue(maxsize=256);self.stop_event=threading.Event();self.ready=threading.Event();self.thread=None;self.thread_id=None;self.api=None;self.handle=None;self.callback=None;self.error=None
    def start(self):
        if self.thread and self.thread.is_alive():raise RuntimeError('Monitor already running')
        self.thread=threading.Thread(target=self.loop,name='MTB_MayaProcessFinder',daemon=True);self.thread.start()
        if not self.ready.wait(3) or self.error:
            self.stop();raise RuntimeError(self.error or 'Monitor initialization timeout')
    def enqueue(self,value):
        try:self.events.put_nowait(value)
        except queue.Full:pass
    def loop(self):
        try:
            self.api=api=Windows()
            if self.mode=='poll':
                self.ready.set();held=False
                while not self.stop_event.wait(.05):
                    down=bool(api.user.GetAsyncKeyState(0x11)&0x8000 and api.user.GetAsyncKeyState(0x01)&0x8000)
                    if down and not held:
                        try:self.enqueue(api.cursor())
                        except Exception as e:self.enqueue({'error':str(e)})
                    held=down
            else:
                C=api.ctypes;W=api.types;self.thread_id=api.kernel.GetCurrentThreadId();msg=W.MSG();api.user.PeekMessageW(C.byref(msg),None,0,0,0)
                def callback(code,wp,lp):
                    try:
                        if code>=0 and wp==0x0201 and api.user.GetAsyncKeyState(0x11)&0x8000:
                            event=C.cast(lp,C.POINTER(api.MSLL)).contents;self.enqueue(api.at_point(event.pt))
                    except Exception as e:self.enqueue({'error':str(e)})
                    return api.user.CallNextHookEx(self.handle,code,wp,lp)
                self.callback=api.HOOKPROC(callback);self.handle=api.user.SetWindowsHookExW(14,self.callback,api.kernel.GetModuleHandleW(None),0)
                if not self.handle:raise C.WinError(C.get_last_error())
                self.ready.set()
                while not self.stop_event.is_set():
                    result=api.user.GetMessageW(C.byref(msg),None,0,0)
                    if result==-1:raise C.WinError(C.get_last_error())
                    if result==0:break
                    api.user.TranslateMessage(C.byref(msg));api.user.DispatchMessageW(C.byref(msg))
        except Exception as e:self.error=str(e);self.enqueue({'error':self.error});self.ready.set()
        finally:
            if self.handle:
                if self.api.user.UnhookWindowsHookEx(self.handle):self.handle=None
                else:self.error='Own hook cleanup failed; keep callback and handle for retry'
    def stop(self):
        self.stop_event.set()
        if self.api and self.thread_id:self.api.user.PostThreadMessageW(self.thread_id,0x0012,0,0)
        if self.thread:self.thread.join(3)
        if self.thread and self.thread.is_alive():raise RuntimeError('Monitor still running; preserve state and retry stop')
        if self.handle:
            if not self.api.user.UnhookWindowsHookEx(self.handle):raise RuntimeError('Own hook cleanup still failed; preserve handle/callback and retry stop')
            self.handle=None
    def drain(self):
        result=[]
        while True:
            try:row=self.events.get_nowait()
            except queue.Empty:break
            if 'pid' in row:
                try:row.update(details(row['pid']))
                except Exception as e:row['error']=str(e)
            result.append(row)
        return result
def execute(**p):
    global _monitor
    p=validate(**p)
    action=p['action']
    if action=='inspect':return {'runtime':'windows_standalone','monitor_active':bool(_monitor and _monitor.thread and _monitor.thread.is_alive()),'default_click':'query_only','auto_elevation':False}
    if action=='query_pid':return details(p['pid'])
    if action=='query_cursor':
        row=Windows().cursor();row.update(details(row['pid']));return row
    if action=='start_monitor':
        if _monitor:raise RuntimeError('Stop the existing owned monitor first')
        monitor=Monitor(p['mode']);_monitor=monitor
        try:monitor.start()
        except Exception:
            if not monitor.handle and not (monitor.thread and monitor.thread.is_alive()):_monitor=None
            raise
        return {'started':True,'mode':p['mode']}
    if action=='stop_monitor':
        if _monitor:_monitor.stop();_monitor=None
        return {'stopped':True}
    if action=='drain_events':return {'events':_monitor.drain() if _monitor else []}
    if action=='open_task_manager':
        if os.name!='nt':raise RuntimeError('Windows required')
        import subprocess
        process=subprocess.Popen([os.path.join(os.environ.get('SystemRoot',r'C:\Windows'),'System32','Taskmgr.exe')],shell=False)
        return {'opened_pid':process.pid,'select_pid_supported':False,'note':'Use Details tab to locate the queried PID manually'}
    row=identity(p);process=_psutil().Process(p['pid'])
    if process.create_time()!=p['create_time'] or process.name().lower()!='maya.exe':raise ValueError('Process identity changed immediately before ending')
    (process.kill if p['force'] else process.terminate)();return {'ended':row,'forced':p['force'],'children_ended':False,'undoable':False}
def run(dry_run=True,**kwargs):
    try:
        if type(dry_run) is not bool:raise ValueError('Strict dry_run boolean')
        p=validate(**kwargs)
        return {'success':True,'dry_run':dry_run,'data':p if dry_run else execute(**p),'errors':[]}
    except Exception as e:return {'success':False,'dry_run':dry_run,'data':None,'errors':[str(e)]}
def show_ui():
    return main()
def main():
    import argparse,json
    parser=argparse.ArgumentParser(description='Ctrl+left-click process finder; query only, Ctrl+C exits')
    parser.add_argument('--mode',choices=('poll','hook'),default='poll');args=parser.parse_args()
    result=run(False,action='start_monitor',mode=args.mode)
    if not result['success']:raise RuntimeError(result['errors'])
    print('Ctrl+左键查询窗口PID和路径；不会自动结束进程或提权。Ctrl+C退出。',flush=True)
    try:
        while True:
            for row in execute(action='drain_events')['events']:print(json.dumps(row,ensure_ascii=False),flush=True)
            time.sleep(.1)
    except KeyboardInterrupt:pass
    finally:run(False,action='stop_monitor')
