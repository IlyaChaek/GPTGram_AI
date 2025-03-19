@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: Определяем разрядность ОС
if "%PROCESSOR_ARCHITECTURE%"=="AMD64" (
    set "PYTHON_URL=https://www.python.org/ftp/python/3.12.1/python-3.12.1-amd64.exe"
    echo Обнаружена 64-битная система.
) else (
    set "PYTHON_URL=https://www.python.org/ftp/python/3.12.1/python-3.12.1.exe"
    echo Обнаружена 32-битная система.
)

:: Проверка наличия Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python не найден. Скачиваю и устанавливаю...

    powershell -Command "Invoke-WebRequest -Uri !PYTHON_URL! -OutFile python-installer.exe"

    python-installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0

    timeout /t 10 >nul
    del python-installer.exe

    python --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo Ошибка: Python не удалось установить.
        pause
        exit /b 1
    )
    echo Python успешно установлен!
) else (
    echo Python уже установлен!
)

:: Запуск installer_libraries.py
echo Запускаю installer_libraries.py...
python installer_libraries.py
if %errorlevel% neq 0 (
    echo Ошибка при выполнении installer_libraries.py
    pause
    exit /b 1
)

:: Запуск generator.py после успешного installer_libraries.py
echo installer_libraries.py завершён успешно. Запускаю generator.py...
python generator.py
if %errorlevel% neq 0 (
    echo Ошибка при выполнении generator.py
    pause
    exit /b 1
)

echo Все скрипты успешно завершены!
endlocal
pause
