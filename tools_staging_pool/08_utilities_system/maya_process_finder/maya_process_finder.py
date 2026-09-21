import ctypes
import sys
import psutil
import time
import os
import subprocess
from ctypes import wintypes, byref, windll
import threading
import traceback

# 检查管理员权限
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

# 如果没有管理员权限，重新以管理员身份运行
if not is_admin():
    # 命令行参数
    args = [sys.executable] + sys.argv
    # 使用管理员权限运行
    windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join('"' + arg + '"' for arg in sys.argv), None, 1)
    sys.exit(0)

# Windows API常量和结构体
WM_LBUTTONDOWN = 0x0201
WM_LBUTTONUP = 0x0202
WH_MOUSE_LL = 14
WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101
WM_MOUSEMOVE = 0x0200
VK_CONTROL = 0x11

# 导入Windows API函数
user32 = ctypes.WinDLL('user32', use_last_error=True)
kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)

# 定义必要的Windows API函数
user32.GetCursorPos.argtypes = [ctypes.POINTER(wintypes.POINT)]
user32.WindowFromPoint.argtypes = [wintypes.POINT]
user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
user32.GetWindowTextLengthW.argtypes = [wintypes.HWND]
user32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
user32.IsWindowVisible.argtypes = [wintypes.HWND]
user32.GetWindowLongW.argtypes = [wintypes.HWND, ctypes.c_int]
user32.GetAsyncKeyState.argtypes = [ctypes.c_int]
user32.SetWindowsHookExW.argtypes = [ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint]
user32.CallNextHookEx.argtypes = [ctypes.c_void_p, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM]
user32.UnhookWindowsHookEx.argtypes = [ctypes.c_void_p]
user32.GetMessageW.argtypes = [ctypes.POINTER(wintypes.MSG), wintypes.HWND, ctypes.c_uint, ctypes.c_uint]
user32.TranslateMessage.argtypes = [ctypes.POINTER(wintypes.MSG)]
user32.DispatchMessageW.argtypes = [ctypes.POINTER(wintypes.MSG)]

# 定义鼠标钩子回调函数所需结构体
class MSLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ("pt", wintypes.POINT),
        ("mouseData", wintypes.DWORD),
        ("flags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.c_void_p)
    ]

# 定义回调函数类型
HOOKPROC = ctypes.CFUNCTYPE(
    ctypes.c_int, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM
)

# 全局变量
ctrl_pressed = False
hook_handle = None
running = True
hook_callback = None  # 保持引用，防止被垃圾回收

def get_window_at_cursor():
    """获取光标下的窗口句柄"""
    point = wintypes.POINT()
    user32.GetCursorPos(ctypes.byref(point))
    return user32.WindowFromPoint(point)

def get_window_process_id(hwnd):
    """获取窗口对应的进程ID"""
    process_id = wintypes.DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(process_id))
    return process_id.value

def get_window_title(hwnd):
    """获取窗口标题"""
    length = user32.GetWindowTextLengthW(hwnd)
    if length == 0:
        return ""
    
    buffer = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hwnd, buffer, length + 1)
    return buffer.value

def get_process_info(pid):
    """获取进程信息"""
    try:
        process = psutil.Process(pid)
        return {
            "name": process.name(),
            "exe": process.exe(),
            "cmdline": process.cmdline(),
            "create_time": process.create_time(),
            "status": process.status(),
            "pid": pid
        }
    except psutil.NoSuchProcess:
        return None
    except Exception as e:
        print(f"获取进程信息时发生错误: {e}")
        return None

def open_task_manager_and_select_process(pid):
    """打开任务管理器并选中指定进程"""
    try:
        # 先检查任务管理器是否已打开
        taskmgr_running = False
        for proc in psutil.process_iter(['name']):
            if proc.info['name'].lower() == 'taskmgr.exe':
                taskmgr_running = True
                break
                
        # 如果未打开，则启动任务管理器
        if not taskmgr_running:
            subprocess.Popen("taskmgr.exe", shell=True)
            # 等待任务管理器启动
            time.sleep(2)
            
        # 使用简单方法 - 直接使用系统命令打开任务管理器
        os.system(f"taskkill /f /pid {pid} /t")
        return True
    except Exception as e:
        print(f"打开任务管理器时发生错误: {e}")
        traceback.print_exc()
        return False

def mouse_hook_callback(n_code, w_param, l_param):
    """鼠标钩子回调函数"""
    global ctrl_pressed, running
    
    if n_code >= 0:
        if w_param == WM_LBUTTONDOWN:
            # 检查Ctrl键是否被按下
            ctrl_state = user32.GetAsyncKeyState(VK_CONTROL)
            if ctrl_state & 0x8000:  # 最高位为1表示按键被按下
                try:
                    # 获取鼠标下窗口的进程ID
                    hwnd = get_window_at_cursor()
                    if hwnd:
                        window_title = get_window_title(hwnd)
                        pid = get_window_process_id(hwnd)
                        
                        print("\n==== 窗口信息 ====")
                        print(f"窗口标题: {window_title}")
                        print(f"进程ID (PID): {pid}")
                        
                        # 获取进程详细信息
                        process_info = get_process_info(pid)
                        if process_info:
                            print("\n==== 进程信息 ====")
                            print(f"进程名称: {process_info['name']}")
                            print(f"可执行文件路径: {process_info['exe']}")
                            
                            # 判断是否为Maya进程
                            is_maya = False
                            if "maya" in process_info['name'].lower():
                                print("\n这是一个Maya进程!")
                                is_maya = True
                                
                            # 杀死进程
                            print("\n正在结束进程...")
                            if open_task_manager_and_select_process(pid):
                                print("成功结束进程!")
                            else:
                                print("无法结束进程，请手动在任务管理器中查找并结束PID:", pid)
                            
                        else:
                            print(f"无法获取PID为{pid}的进程信息")
                except Exception as e:
                    print(f"处理鼠标点击时发生错误: {e}")
                    traceback.print_exc()
    
    # 调用下一个钩子
    return user32.CallNextHookEx(hook_handle, n_code, w_param, l_param)

def setup_hook():
    """设置全局鼠标钩子"""
    global hook_handle, hook_callback
    
    try:
        # 转换回调函数为C函数指针
        hook_callback = HOOKPROC(mouse_hook_callback)
        
        # 设置钩子
        hook_handle = user32.SetWindowsHookExW(
            WH_MOUSE_LL,            # 钩子类型
            hook_callback,          # 回调函数
            kernel32.GetModuleHandleW(None),  # 实例句柄
            0                       # 线程ID（0表示全局钩子）
        )
        
        if not hook_handle:
            error_code = ctypes.get_last_error()
            print(f"设置鼠标钩子失败，错误代码: {error_code}")
            return False
            
        return True
    except Exception as e:
        print(f"设置钩子时发生错误: {e}")
        traceback.print_exc()
        return False

def message_loop():
    """消息循环，保持程序运行"""
    msg = wintypes.MSG()
    while running:
        try:
            # 获取消息
            result = user32.GetMessageW(byref(msg), None, 0, 0)
            if result > 0:
                user32.TranslateMessage(byref(msg))
                user32.DispatchMessageW(byref(msg))
            elif result == 0:
                break
            else:
                error_code = ctypes.get_last_error()
                print(f"获取消息失败，错误代码: {error_code}")
                break
        except Exception as e:
            print(f"消息循环发生错误: {e}")
            traceback.print_exc()
            break
        # 防止CPU占用过高
        time.sleep(0.01)

def main():
    """主函数"""
    global running
    
    try:
        print("=" * 50)
        print("Maya进程查找器 - Ctrl+鼠标左键版")
        print("=" * 50)
        print("\n使用Ctrl+鼠标左键点击Maya窗口，将自动结束Maya进程.")
        print("按Ctrl+C退出程序。")
        
        # 等待用户确认
        input("按Enter键开始监听鼠标事件...")
        
        # 设置鼠标钩子
        if not setup_hook():
            print("无法设置鼠标钩子，程序退出。")
            print("请尝试以管理员身份运行此程序。")
            input("按Enter键退出...")
            return
        
        print("钩子设置成功，现在可以使用Ctrl+鼠标左键点击Maya窗口了。")
        
        # 启动消息循环
        message_loop()
            
    except KeyboardInterrupt:
        print("\n程序已被用户中断。")
    except Exception as e:
        print(f"发生错误: {e}")
        traceback.print_exc()
    finally:
        # 卸载钩子
        if hook_handle:
            try:
                if not user32.UnhookWindowsHookEx(hook_handle):
                    error_code = ctypes.get_last_error()
                    print(f"卸载钩子失败，错误代码: {error_code}")
            except Exception as e:
                print(f"卸载钩子时发生错误: {e}")
        
        print("\n程序已退出。")
        input("按Enter键关闭窗口...")
    
if __name__ == "__main__":
    main() 