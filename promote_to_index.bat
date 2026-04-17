@echo off
chcp 65001 > nul
cd /d "%~dp0"
echo ============================================
echo  development.html → index.html 昇格ツール
echo ============================================
echo.
echo development.html の内容で index.html を上書きします。
echo この操作は元に戻せません。
echo.
set /p CONFIRM=続行しますか？ (Y/N):
if /i not "%CONFIRM%"=="Y" (
    echo 中止しました。
    pause
    exit /b 0
)
copy /Y "development.html" "index.html"
echo.
echo 昇格完了！ index.html が更新されました。
echo git push でGitHub Pagesに反映してください。
echo.
pause
