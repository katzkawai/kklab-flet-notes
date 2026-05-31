#!/usr/bin/env bash
# kklab メモ帳を PWA バックエンド（ローカル Web サーバー）として起動する手動ランチャー。
#
# 起動後、ブラウザまたはインストール済み PWA から http://localhost:8550 を開いて使う。
# ポートは固定（既定 8550）。PWA の start_url を安定させるため、毎回同じポートで起動する。
# 停止するには Ctrl+C。
set -euo pipefail

cd "$(dirname "$0")"

PORT="${KKLAB_PORT:-8550}"

echo "kklab メモ帳サーバーを起動します … http://localhost:${PORT}"
echo "ブラウザかインストール済み PWA でこの URL を開いてください。"
echo "（停止するには Ctrl+C）"

KKLAB_SERVE_WEB=1 KKLAB_PORT="${PORT}" exec uv run python main.py
