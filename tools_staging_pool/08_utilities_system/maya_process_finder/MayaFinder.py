#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Maya进程查找器 - 使用Ctrl+点击定位Maya窗口并在任务管理器中打开
"""

import os
import sys
import time
import ctypes
import subprocess
from ctypes import wintypes
import keyboard

# 设置控制台输出编码为UTF-8
if sys.stdout.encoding != 'utf-8':
    try:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except:
        pass

# 定义Windows API常量和结构
user32 = ctypes.WinDLL('user32', use_last_error=True)
kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)

class POINT(ctypes.Structure):
    _fields_ = [("x", wintypes.LONG),
                ("y", wintypes.LONG)]

# 定义Windows API函数
user32.GetCursorPos.argtypes = [ctypes.POINTER(POINT)]
user32.GetCursorPos.restype = wintypes.BOOL
user32.WindowFromPoint.argtypes = [POINT]
user32.WindowFromPoint.restype = wintypes.HWND
user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
user32.GetWindowThreadProcessId.restype = wintypes.DWORD
user32.GetKeyState.argtypes = [ctypes.c_int]
user32.GetKeyState.restype = ctypes.c_short

# 定义键盘和鼠标常量
VK_CONTROL = 0x11
VK_LBUTTON = 0x01

# 颜色常量
class Colors:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    GRAY = '\033[90m'
    RESET = '\033[0m'

def clear_screen():
    """清除屏幕"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_colored(text, color):
    """打印彩色文本"""
    print(f"{color}{text}{Colors.RESET}")

def is_ctrl_and_left_mouse_down():
    """检查是否同时按下Ctrl键和鼠标左键"""
    ctrl_down = (user32.GetKeyState(VK_CONTROL) & 0x8000) != 0
    left_mouse_down = (user32.GetKeyState(VK_LBUTTON) & 0x8000) != 0
    return ctrl_down and left_mouse_down

def get_process_info_under_cursor():
    """获取鼠标所在位置窗口的进程信息"""
    # 获取光标位置
    pt = POINT()
    user32.GetCursorPos(ctypes.byref(pt))
    
    # 获取光标下窗口句柄
    hwnd = user32.WindowFromPoint(pt)
    
    # 获取窗口进程ID
    process_id = wintypes.DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(process_id))
    
    return process_id.value

def get_process_details(process_id):
    """获取进程详细信息"""
    try:
        # 使用WMI获取进程详情
        import wmi
        w = wmi.WMI()
        for process in w.Win32_Process(ProcessId=process_id):
            return {
                'name': process.Name,
                'path': process.ExecutablePath,
                'window_title': process.WindowTitle if hasattr(process, 'WindowTitle') else '未知'
            }
    except:
        # 如果WMI失败，使用tasklist命令
        try:
            output = subprocess.check_output(f'tasklist /fi "PID eq {process_id}" /fo csv /nh', shell=True).decode('gbk')
            if ',"' in output:
                process_name = output.split(',"')[0].strip('"')
                return {
                    'name': process_name,
                    'path': '未知',
                    'window_title': '未知'
                }
        except:
            pass
    
    return None

def open_task_manager_with_process(process_id):
    """打开任务管理器并定位到指定进程"""
    try:
        subprocess.Popen(f'taskmgr.exe /select,{process_id}')
        return True
    except Exception as e:
        print_colored(f"打开任务管理器失败: {e}", Colors.RED)
        return False

def main():
    """主函数"""
    # 清屏并显示说明
    clear_screen()
    print_colored("=============== Maya进程查找器 ===============", Colors.CYAN)
    print_colored("请按住Ctrl键并点击Maya窗口", Colors.YELLOW)
    print_colored("程序会自动获取该窗口的进程信息并打开任务管理器", Colors.YELLOW)
    print_colored("按Ctrl+C可以随时退出程序", Colors.GRAY)
    print_colored("=============================================", Colors.CYAN)
    print()
    print_colored("等待Ctrl+点击操作...", Colors.GREEN)
    
    # 等待用户按住Ctrl并点击
    try:
        while True:
            if is_ctrl_and_left_mouse_down():
                # 等待一下以确保点击已完成
                time.sleep(0.1)
                
                # 获取进程ID
                process_id = get_process_info_under_cursor()
                
                if not process_id:
                    print_colored("无法获取窗口进程ID", Colors.RED)
                    continue
                
                # 获取进程详情
                process_info = get_process_details(process_id)
                
                if not process_info:
                    print_colored(f"无法获取进程(ID:{process_id})的详细信息", Colors.RED)
                    continue
                
                # 显示进程信息
                print()
                print_colored("获取到的窗口信息:", Colors.CYAN)
                print_colored("-----------------------------------", Colors.CYAN)
                print("进程名称: ", end="")
                print_colored(process_info['name'], Colors.GREEN)
                print("进程ID: ", end="")
                print_colored(str(process_id), Colors.GREEN)
                print("窗口标题: ", end="")
                print_colored(process_info['window_title'], Colors.GREEN)
                print("可执行文件: ", end="")
                print_colored(process_info['path'], Colors.GREEN)
                print_colored("-----------------------------------", Colors.CYAN)
                
                # 检查是否为Maya进程
                is_maya = 'maya' in process_info['name'].lower()
                
                if is_maya:
                    print_colored("✓ 确认为Maya进程", Colors.GREEN)
                else:
                    print_colored("✗ 这不是Maya进程", Colors.RED)
                
                # 自动打开任务管理器
                print_colored("正在打开任务管理器并定位到进程...", Colors.YELLOW)
                open_task_manager_with_process(process_id)
                
                # 等待用户按任意键继续
                print()
                input("按Enter键继续...")
                clear_screen()
                print_colored("等待下一次Ctrl+点击操作...", Colors.GREEN)
            
            time.sleep(0.01)  # 减少CPU使用率
    except KeyboardInterrupt:
        print()
        print_colored("程序已退出", Colors.YELLOW)

if __name__ == "__main__":
    main() 