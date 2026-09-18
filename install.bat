@echo off
chcp 65001 >nul
title Maya FBX 材质录入工具 - 环境配置与部署助手

echo ==============================================================================
echo        Maya FBX 材质录入与同名物体指定工具 - 一键环境部署助手
echo ==============================================================================
echo.
echo 本工具采用纯内存直读技术，绝不把外部 FBX 的几何体/骨骼/灯光导入视口！
echo 正在扫描本台计算机上已安装的 Autodesk Maya 版本...
echo.

set CURRENT_DIR=%~dp0
set SDK_DIST=%CURRENT_DIR%fbx_sdk_dist

set FOUND_MAYA=0

:: 探测 Maya 2026
if exist "C:\Program Files\Autodesk\Maya2026\bin\mayapy.exe" (
    set FOUND_MAYA=1
    echo [发现] Autodesk Maya 2026
    echo 正在安装 Python 3.11 FBX SDK 依赖...
    "C:\Program Files\Autodesk\Maya2026\bin\mayapy.exe" -m pip install "%SDK_DIST%\fbx-2020.3.11-cp311-none-win_amd64.whl" --user --no-warn-script-location
    echo [完成] Maya 2026 配置完成。
    echo.
)

:: 探测 Maya 2025
if exist "C:\Program Files\Autodesk\Maya2025\bin\mayapy.exe" (
    set FOUND_MAYA=1
    echo [发现] Autodesk Maya 2025
    echo 正在安装 Python 3.11 FBX SDK 依赖...
    "C:\Program Files\Autodesk\Maya2025\bin\mayapy.exe" -m pip install "%SDK_DIST%\fbx-2020.3.11-cp311-none-win_amd64.whl" --user --no-warn-script-location
    echo [完成] Maya 2025 配置完成。
    echo.
)

:: 探测 Maya 2024
if exist "C:\Program Files\Autodesk\Maya2024\bin\mayapy.exe" (
    set FOUND_MAYA=1
    echo [发现] Autodesk Maya 2024
    echo 正在安装 Python 3.10 FBX SDK 依赖...
    "C:\Program Files\Autodesk\Maya2024\bin\mayapy.exe" -m pip install "%SDK_DIST%\fbx-2020.3.4-cp310-none-win_amd64.whl" --user --no-warn-script-location
    echo [完成] Maya 2024 配置完成。
    echo.
)

:: 探测 Maya 2023
if exist "C:\Program Files\Autodesk\Maya2023\bin\mayapy.exe" (
    set FOUND_MAYA=1
    echo [发现] Autodesk Maya 2023
    echo Maya 2023 默认运行在安全沙箱隔离引擎模式（无需额外安装，开箱即用）。
    echo.
)

:: 探测 Maya 2022
if exist "C:\Program Files\Autodesk\Maya2022\bin\mayapy.exe" (
    set FOUND_MAYA=1
    echo [发现] Autodesk Maya 2022
    echo Maya 2022 默认运行在安全沙箱隔离引擎模式（无需额外安装，开箱即用）。
    echo.
)

if %FOUND_MAYA%==0 (
    echo [提示] 未在默认 C:\Program Files\Autodesk 目录下检测到常见 Maya 安装。
    echo 别担心！本工具文件夹内已自带 Python 3.11 与 3.10 预编译库及沙箱后备引擎。
    echo 您只需打开 Maya，将 drag_and_drop_install.mel 拖入 Maya 视口即可直接使用！
    echo.
)

echo ==============================================================================
echo 部署已就绪！
echo 使用方式：打开 Maya，将本文件夹中的 drag_and_drop_install.mel 直接拖入视口即可！
echo ==============================================================================
echo.
pause
