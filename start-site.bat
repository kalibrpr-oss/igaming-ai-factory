@echo off
chcp 65001 >nul
title iGaming AI-Factory — сайт
cd /d "%~dp0apps\web"

if not exist "node_modules\" (
    echo [1/2] Первый запуск: ставим зависимости...
    call npm install
    if errorlevel 1 (
        echo.
        echo ОШИБКА: npm не сработал. Установи Node.js с https://nodejs.org LTS и запусти этот файл снова.
        pause
        exit /b 1
    )
)

echo.
echo [2/2] Запускаю сайт. Окно НЕ закрывай — пока оно открыто, сайт работает.
echo.
echo   === ОТКРОЙ В БРАУЗЕРЕ ТОЛЬКО ЭТОТ АДРЕС: ===
echo   http://localhost:3333
echo.
echo   Не используй :3000 — там часто висит другая программа и даёт ошибку.
echo.
call npm run dev
echo.
pause
