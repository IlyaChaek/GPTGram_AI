@echo off
setlocal

:: Define the Python installation URL based on system architecture
if "%PROCESSOR_ARCHITECTURE%"=="AMD64" (
    set "PYTHON_URL=https://www.python.org/ftp/python/3.12.1/python-3.12.1-amd64.exe"
    echo 64-bit system detected.
) else (
    set "PYTHON_URL=https://www.python.org/ftp/python/3.12.1/python-3.12.1.exe"
    echo 32-bit system detected.
)

:: Check if Python is already installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found. Downloading and installing...

    powershell -Command "Invoke-WebRequest -Uri !PYTHON_URL! -OutFile python-installer.exe"

    python-installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0

    timeout /t 10 >nul
    del python-installer.exe

    :: Check if Python was installed successfully
    python --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo Error: Python installation failed.
        pause
        exit /b 1
    )
    echo Python successfully installed!
) else (
    echo Python is already installed!
)

:: Run installer_libraries.py
echo Running installer_libraries.py...
python installer_libraries.py
if %errorlevel% neq 0 (
    echo Error running installer_libraries.py
    pause
    exit /b 1
)

:: Run generator.py after successful installer_libraries.py
echo installer_libraries.py finished successfully. Running generator.py...
python generator.py
if %errorlevel% neq 0 (
    echo Error running generator.py
    pause
    exit /b 1
)

echo All scripts completed successfully!
endlocal
pause
