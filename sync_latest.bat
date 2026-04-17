@echo off
chcp 932 > nul
setlocal enabledelayedexpansion

REM ============================================================
REM  fishing log sync and analyze script (v2)
REM ============================================================
REM  Flow:
REM    [1/4] git pull - V6.0 and ocean current
REM    [2/4] build - run build_database.py in muroto local folder
REM    [3/4] copy  - 3 CSVs to analysis folder (no rename needed)
REM    [4/4] run   - analyze_engine.py then open development.html
REM
REM  Note (2026-04-17):
REM    - analyze_engine.py は analysis_result.json を書き、
REM      development.html 内の window.ANALYSIS_DATA 行を毎回更新する。
REM    - 本番 index.html は公開版として無改修で放置（手動昇格のみ）。
REM    - 屋外/ローカル閲覧は development.html を開く運用に統一。
REM
REM  Option: set PULL_FORECAST=1 to also pull forecast repo
REM
REM  Usage: place this file in the analysis v2 folder and
REM         double-click to run.
REM ============================================================

echo ============================================
echo  Fishing Log 一括同期・解析 v2
echo  %DATE% %TIME%
echo ============================================
echo.

cd /d "%~dp0"
echo [作業フォルダ] %CD%
echo.

REM ── オプション設定 ─────────────────────────────
REM 1 にすると出船可否判断（muroto_fishing_forecast）も pull する
set "PULL_FORECAST=0"

REM ── 各フォルダへの相対パス ─────────────────────
set "V6_DIR=..\..\fishing log 開発　釣果データ収集ソフトｖ6.0\釣果データ収集ソフトV6.0開発"
set "OCEAN_DIR=..\..\fishing log 開発　室戸沖釣果データ収集ソフト\室戸沖の海流データの収集とデータ化"
set "MUROTO_DIR=..\..\fishing log 開発　室戸沖釣果データ収集ソフト\室戸沖釣果データ収集ソフト"
set "FORECAST_DIR=..\..\fishing log 開発　室戸岬沖出船可否判断システム"

REM ── 前提チェック ──────────────────────────────
echo [0/4] 前提チェック
if not exist "%V6_DIR%\.git" (
    echo *** エラー: V6.0 フォルダが git clone されていません ***
    echo   %V6_DIR%
    pause
    exit /b 1
)
if not exist "%OCEAN_DIR%\.git" (
    echo *** エラー: 潮流フォルダが git clone されていません ***
    echo   %OCEAN_DIR%
    pause
    exit /b 1
)
if not exist "%MUROTO_DIR%\scripts\build_database.py" (
    echo *** エラー: 室戸沖釣果DB フォルダが見つかりません ***
    echo   %MUROTO_DIR%
    pause
    exit /b 1
)
if not exist "analyze_engine.py" (
    echo *** エラー: analyze_engine.py が見つかりません ***
    pause
    exit /b 1
)
echo OK
echo.

REM ── Python コマンド検出 ───────────────────────
set PYTHON_CMD=
where python > nul 2>&1
if %errorlevel% == 0 (set PYTHON_CMD=python) else (
    where py > nul 2>&1
    if %errorlevel% == 0 (set PYTHON_CMD=py) else (
        where python3 > nul 2>&1
        if %errorlevel% == 0 (set PYTHON_CMD=python3) else (
            echo *** エラー: Python が見つかりません ***
            pause
            exit /b 1
        )
    )
)

REM ── [1/4] 上流リポジトリを pull ─────────────────
echo [1/4] 上流リポジトリを最新化
echo.

echo   -^> V6.0 fishing-collector
pushd "%V6_DIR%"
git pull --ff-only
if errorlevel 1 (
    echo *** 警告: V6.0 の git pull に失敗しました ***
    echo   finish_task5.bat で事前整備してください。
    popd
    pause
    exit /b 1
)
popd
echo.

echo   -^> 潮流 muroto-ocean-current
pushd "%OCEAN_DIR%"
git pull --ff-only
if errorlevel 1 (
    echo *** 警告: 潮流 の git pull に失敗しました ***
    echo   fix_ocean_sync.bat で事前整備してください。
    popd
    pause
    exit /b 1
)
popd
echo.

if "%PULL_FORECAST%"=="1" (
    if exist "%FORECAST_DIR%\.git" (
        echo   -^> 出船可否判断 muroto_fishing_forecast
        pushd "%FORECAST_DIR%"
        git pull --ff-only
        popd
        echo.
    )
)

echo 全リポジトリの pull 完了
echo.

REM ── [2/4] 室戸沖釣果DB V2.0 のビルド ─────────────
echo [2/4] 室戸沖釣果DB V2.0 をビルド
pushd "%MUROTO_DIR%"

REM data/ フォルダへ V6.0・潮流 の最新 CSV をコピー
if not exist "data" mkdir data
copy /Y "..\..\fishing log 開発　釣果データ収集ソフトｖ6.0\釣果データ収集ソフトV6.0開発\fishing_data.csv" "data\fishing_data.csv" > nul
copy /Y "..\..\fishing log 開発　釣果データ収集ソフトｖ6.0\釣果データ収集ソフトV6.0開発\fishing_condition_db.csv" "data\fishing_condition_db.csv" > nul
copy /Y "..\..\fishing log 開発　室戸沖釣果データ収集ソフト\室戸沖の海流データの収集とデータ化\output\muroto_offshore_current_all.csv" "data\muroto_offshore_current_all.csv" > nul

%PYTHON_CMD% scripts\build_database.py
if errorlevel 1 (
    echo *** エラー: build_database.py の実行に失敗しました ***
    popd
    pause
    exit /b 1
)
popd
echo.

REM ── [3/4] 解析ソフトに最新CSVを配置 ─────────────
REM  2026-04-17: analyze_engine.py の DB1_CSV を fishing_muroto_v1.csv に変更済み。
REM  従来の v1 to v2_filtered リネームコピー工程を廃止し、そのままの名前で配置する。
echo [3/4] 解析ソフトに最新CSVを配置
copy /Y "%MUROTO_DIR%\fishing_muroto_v1.csv" "fishing_muroto_v1.csv" > nul
copy /Y "%V6_DIR%\fishing_condition_db.csv" "fishing_condition_db.csv" > nul
copy /Y "%OCEAN_DIR%\output\muroto_offshore_current_all.csv" "muroto_offshore_current_all.csv" > nul
echo コピー完了
echo.

REM ── [4/4] 解析実行 & development.html 起動 ───────
REM  2026-04-17: dashboard.html は廃止。屋外/ローカル閲覧は development.html を使用する。
REM  analyze_engine.py が development.html の埋め込みデータを最新化する。
echo [4/4] 解析エンジン実行 ^& development.html 起動
%PYTHON_CMD% analyze_engine.py
if errorlevel 1 (
    echo *** エラー: analyze_engine.py の実行に失敗しました ***
    pause
    exit /b 1
)

if not exist "analysis_result.json" (
    echo *** エラー: analysis_result.json が生成されていません ***
    pause
    exit /b 1
)

if not exist "development.html" (
    echo *** エラー: development.html が見つかりません ***
    pause
    exit /b 1
)

start "" "%CD%\development.html"
echo.

echo ============================================
echo  全処理完了
echo.
echo  - 本番公開版 index.html は未更新です（手動昇格運用）
echo  - development.html に最新データが埋め込まれました
echo ============================================
echo.
pause
