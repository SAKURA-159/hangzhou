@echo off
chcp 65001 >nul
echo ============================================
echo   杭州房价分析系统 - 一键启动
echo ============================================
echo.

cd /d "%~dp0"

:: Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到 Python，请先安装 Python 3.11+
    pause
    exit /b 1
)

:: Check and seed database
echo [1/3] 检查数据库...
cd backend
if not exist "data\hangzhou.db" (
    echo        数据库不存在，正在导入数据...
    pip install -e ".[dev]" -q 2>nul
    python scripts\seed.py
) else (
    echo        数据库已就绪
)

:: Start backend
echo [2/3] 启动后端 API (端口 8000)...
start "杭州房价-后端API" cmd /c "cd /d %~dp0backend && uvicorn app.main:app --host 0.0.0.0 --port 8000"

:: Wait for backend
timeout /t 3 /nobreak >nul

:: Start frontend
echo [3/3] 启动前端仪表盘 (端口 8501)...
start "杭州房价-前端仪表盘" cmd /c "cd /d %~dp0frontend && streamlit run app.py --server.port 8501"

echo.
echo ============================================
echo   启动完成！
echo   后端 API 文档: http://localhost:8000/docs
echo   前端仪表盘:   http://localhost:8501
echo ============================================
echo.
echo 按任意键退出此窗口（不影响后台服务）
pause >nul
