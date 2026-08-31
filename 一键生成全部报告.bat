@echo off
chcp 65001 >nul
cd /d "%~dp0"
title AI 数据分析工作台 · 一键生成全部报告

echo ============================================
echo   AI 数据分析工作台 - 重新生成全部报告
echo ============================================
echo.

rem ---- 尝试定位 Python（venv 优先，其次 python/py）----
set "PY="
if exist ".venv\Scripts\python.exe" set "PY=.venv\Scripts\python.exe"
if not defined PY where python >nul 2>nul && set "PY=python"
if not defined PY where py >nul 2>nul && set "PY=py -3"
if not defined PY (
    echo [错误] 未找到 Python，请先安装 Python 3.10+：https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/3] 检查依赖（pandas / numpy / matplotlib / scipy）...
%PY% -c "import pandas, numpy, matplotlib, scipy, pptx" >nul 2>nul
if errorlevel 1 (
    echo [提示] 缺少依赖，正在尝试安装 python-pptx（pandas/numpy/matplotlib/scipy 通常已随环境提供）...
    %PY% -m pip install python-pptx --quiet
    %PY% -c "import pandas, numpy, matplotlib, scipy, pptx" >nul 2>nul
    if errorlevel 1 (
        echo [错误] 依赖不全，请手动执行：
        echo        pip install pandas numpy matplotlib scipy python-pptx
        pause
        exit /b 1
    )
)

echo [2/3] 重新生成全部报告（9 个任务，02 占位跳过）...
%PY% scripts\run_all.py
if errorlevel 1 (
    echo [错误] 构建过程出错，请查看上方日志。
    pause
    exit /b 1
)

echo [3/3] 导出交付 PPT...
%PY% -m engine.ppt_out

echo.
echo ============================================
echo   完成！双击 index.html 即可查看全部报告
echo   报告位置：output/taskNN/report.html
echo   交付 PPT ：output/交付总览.pptx
echo ============================================
pause
