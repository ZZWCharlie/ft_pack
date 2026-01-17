@echo off
chcp 65001 >nul
echo ==============================================
echo 🔑 FastAPI SSH隧道连接工具 (Windows)
echo ==============================================
echo.

REM 配置信息 - 请根据实际情况修改
set REMOTE_HOST=192.168.31.196
set REMOTE_PORT=30800
set LOCAL_PORT=8080
set SSH_USER=user

echo 远程服务器: %REMOTE_HOST%
echo 远程端口: %REMOTE_PORT%
echo 本地端口: %LOCAL_PORT%
echo SSH用户: %SSH_USER%
echo ==============================================
echo.

echo 📡 正在建立SSH隧道连接...
echo 请输入SSH密码：
echo.

echo 🌍 连接成功后，请在浏览器中访问：
echo   • 主页: http://localhost:%LOCAL_PORT%/
echo   • API文档: http://localhost:%LOCAL_PORT%/docs
echo   • 报告列表: http://localhost:%LOCAL_PORT%/reports
echo.

echo 💡 保持此窗口打开以维持连接
echo    按 Ctrl+C 可断开连接
echo ==============================================
echo.

REM 建立SSH隧道
ssh -L %LOCAL_PORT%:localhost:%REMOTE_PORT% %SSH_USER%@%REMOTE_HOST%

echo.
echo 🔌 SSH隧道已断开
pause
