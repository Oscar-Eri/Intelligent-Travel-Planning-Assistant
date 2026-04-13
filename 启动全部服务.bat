@echo off
chcp 65001 >nul
title 旅行地图 - 完整启动脚本

echo.
echo ╔════════════════════════════════════════╗
echo ║   旅行地图 - 智能旅游规划助手          ║
echo ║   正在启动前后端服务...                ║
echo ╚════════════════════════════════════════╝
echo.

REM ==================== 检查 Python ====================
echo [检查] Python 环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)
echo [成功] Python 已安装
echo.

REM ==================== 检查 Node.js ====================
echo [检查] Node.js 环境...
node --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Node.js，请先安装 Node.js 16+
    pause
    exit /b 1
)
echo [成功] Node.js 已安装
echo.

REM ==================== 启动后端 ====================
echo ════════════════════════════════════════
echo [1/2] 启动后端服务
echo ════════════════════════════════════════
echo.

cd backend

REM 检查 .env 文件
if not exist .env (
    echo [提示] 未找到 .env 文件，正在创建...
    copy .env.example .env >nul
    echo [警告] 请编辑 backend\.env 文件配置你的 API Key
    echo.
)

REM 检查依赖
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo [安装] 正在安装 Python 依赖...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [错误] 依赖安装失败
        pause
        exit /b 1
    )
)

echo [启动] 后端服务将在 http://localhost:8000 运行
echo [提示] 按 Ctrl+C 可停止后端服务
echo.

start "旅行地图-后端" cmd /k "cd backend && python main.py"

timeout /t 3 /nobreak >nul

cd ..

REM ==================== 启动前端 ====================
echo.
echo ════════════════════════════════════════
echo [2/2] 启动前端服务
echo ════════════════════════════════════════
echo.

cd frontend

REM 检查 node_modules
if not exist node_modules (
    echo [安装] 正在安装前端依赖（这可能需要几分钟）...
    call npm install
    if errorlevel 1 (
        echo [错误] 前端依赖安装失败
        pause
        exit /b 1
    )
)

echo [启动] 前端服务将在 http://localhost:5173 运行
echo [提示] 浏览器将自动打开应用
echo.

start "旅行地图-前端" cmd /k "cd frontend && npm run dev"

cd ..

REM ==================== 完成 ====================
echo.
echo ════════════════════════════════════════
echo   启动完成！
echo ════════════════════════════════════════
echo.
echo 📡 后端服务：http://localhost:8000
echo 🌐 前端应用：http://localhost:5173
echo 📖 API 文档：http://localhost:8000/docs
echo.
echo 提示：
echo - 两个命令行窗口已打开（后端和前端）
echo - 关闭这些窗口将停止服务
echo - 在浏览器中访问 http://localhost:5173 开始使用
echo.
echo 按任意键退出此窗口...
pause >nul
