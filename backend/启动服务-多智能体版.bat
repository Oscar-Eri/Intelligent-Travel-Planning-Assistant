@echo off
chcp 65001 >nul
echo ============================================================
echo 🤖 旅行地图AI助手 - 多智能体版
echo ============================================================
echo.

echo [1/3] 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)
echo ✅ Python环境正常
echo.

echo [2/3] 检查依赖包...
python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  依赖包未安装，正在安装...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ 依赖安装失败
        pause
        exit /b 1
    )
)
echo ✅ 依赖包已就绪
echo.

echo [3/3] 启动服务...
echo.
echo ============================================================
echo 📡 服务地址: http://localhost:8000
echo 🌐 API文档: http://localhost:8000/docs
echo 🤖 智能体状态: http://localhost:8000/agents/status
echo 💬 聊天接口: http://localhost:8000/api/chat
echo ============================================================
echo.
echo 按 Ctrl+C 停止服务
echo.

python main.py

pause
