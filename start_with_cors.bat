@echo off
chcp 65001 >nul
echo 启动FastAPI服务器（已修复CORS问题）
echo =====================================
echo.

cd /d "d:\work\ustc\yuancheng\ft_pack_3"

echo 正在获取服务器IP地址...
for /f "tokens=2 delims=:" %%i in ('ipconfig ^| findstr /i "IPv4"') do (
    set "ip=%%i"
    set "ip=!ip: =!"
    if not "!ip!"=="127.0.0.1" (
        echo 📍 服务器IP: !ip!
        echo 🔗 网络访问地址: http://!ip!:30800
        goto :found_ip
    )
)
:found_ip

echo 🌐 服务端口: 30800
echo.
echo 🌍 可用访问地址:
echo   • 本地访问: http://localhost:30800
echo   • 本地访问: http://127.0.0.1:30800
if defined ip echo   • 网络访问: http://!ip!:30800
echo.
echo 📖 可用页面:
if defined ip (
    echo   • 主页: http://!ip!:30800/
    echo   • API文档: http://!ip!:30800/docs
    echo   • 报告列表: http://!ip!:30800/reports
    echo   • 领域上传: http://!ip!:30800/domain-upload
) else (
    echo   • 主页: http://localhost:30800/
    echo   • API文档: http://localhost:30800/docs
    echo   • 报告列表: http://localhost:30800/reports
    echo   • 领域上传: http://localhost:30800/domain-upload
)
echo.
echo 按 Ctrl+C 停止服务器
echo =====================================
echo.

setlocal enabledelayedexpansion
python fastapi_app.py

pause
