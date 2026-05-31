@echo off
rem Windows 用ランチャー。エクスプローラーからダブルクリックして起動できる。
rem kklab メモ帳を PWA バックエンド（ローカル Web サーバー）として起動する。
rem 起動後、ブラウザまたはインストール済み PWA から http://localhost:8550 を開いて使う。
rem 停止するには Ctrl+C、またはこのウィンドウを閉じる。

rem 日本語表示のためコンソールを UTF-8 に切り替える（Windows 10 1903 以降）。
chcp 65001 >nul
setlocal

rem このバッチファイルのあるフォルダへ移動する。
cd /d "%~dp0"

rem ポートは固定（既定 8550）。PWA の start_url を安定させるため毎回同じポートで起動する。
if "%KKLAB_PORT%"=="" set "KKLAB_PORT=8550"

echo kklab メモ帳サーバーを起動します ... http://localhost:%KKLAB_PORT%
echo ブラウザかインストール済み PWA でこの URL を開いてください。
echo (停止するには Ctrl+C、またはこのウィンドウを閉じる)

set "KKLAB_SERVE_WEB=1"
uv run python main.py

echo.
echo サーバーを停止しました。
pause
endlocal
