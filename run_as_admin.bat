@echo off
:: 检查是否以管理员权限运行
net session >nul 2>&1
if %errorLevel% == 0 (
    echo 已获取管理员权限
) else (
    echo 请求管理员权限...
    powershell -Command "Start-Process python -ArgumentList 'window_detector.py' -Verb RunAs"
    exit
)

:: 如果已经是管理员权限，直接运行程序
python window_detector.py 