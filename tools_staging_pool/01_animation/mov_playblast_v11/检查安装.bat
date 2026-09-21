@echo off
where ffmpeg > nul 2>&1
if %errorlevel% equ 0 (
    echo FFmpeg is installed.
) else (
    echo FFmpeg is not installed or not in the system's PATH.
)

pause