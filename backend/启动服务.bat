@echo off
chcp 65001 >nul
echo ========================================
echo   旅行地图后端服务启动脚本
echo ========================================
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)

echo [1/3] 检查依赖包...
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo [提示] 正在安装依赖包...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [错误] 依赖包安装失败
        pause
        exit /b 1
    )
    echo [成功] 依赖包安装完成
) else (
    echo [成功] 依赖包已安装
)

echo.
echo [2/3] 检查配置文件...
if not exist .env (
    echo [提示] 未找到 .env 文件，正在从 .env.example 复制...
    copy .env.example .env >nul
    echo [警告] 请编辑 .env 文件配置你的 API Key
    pause
)

echo.
echo [3/3] 启动服务...
echo.
python main.py

pause
