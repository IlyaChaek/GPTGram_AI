@echo off

net session >nul 2>&1
if %errorlevel% NEQ 0 (
    echo This script requires Administrator privileges. 
    powershell -Command "Start-Process '%~f0' -Verb runAs"
    exit /b
)

set "current_dir=%~dp0"

set "font_folder=%current_dir%fonts"

set "fonts_dir=C:\Windows\Fonts"

for %%F in (%font_folder%\*.ttf %font_folder%\*.otf) do (
    copy "%%F" %fonts_dir%
    echo Font installed: %%F
)

reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Fonts" /f

exit
