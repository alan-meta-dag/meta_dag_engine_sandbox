@echo off
echo === Sandbox Hygiene Auto-Clean ===

:: 清除未追蹤暫存檔案
git clean -fd -e "!CHANGELOG*" -e "!README*"
echo [OK] Removed untracked tmp files

:: 清除 *.log 與 IDE 噪音
del /S /Q *.log 2>nul
del /S /Q Thumbs.db Desktop.ini .DS_Store 2>nul
echo [OK] Removed logs + OS trash

:: 保留正式 snapshots，清除 *.tmp
del /S /Q state\*.tmp 2>nul
del /S /Q state\drift_snapshots\*.tmp 2>nul
echo [OK] Removed snapshot tmp

echo Done ✓
pause
