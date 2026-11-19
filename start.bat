@echo off
chcp 65001 > nul
echo ============================================================
echo   📓 Open Notebook Bilingual - 一键启动
echo   基于 Open Notebook 框架 · 全面强化对标 Google NotebookLM
echo ============================================================
echo.

cd /d "%~dp0"

echo 正在检查 Python 环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [提示] 未在系统 PATH 中检测到 python 命令。
    echo 请确认已安装 Python 3.10+ 并将其勾选加入系统环境变量。
    pause
    exit /b 1
)

echo 正在启动服务...
python start.py

pause
