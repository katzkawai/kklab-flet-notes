#!/usr/bin/env bash
# kklab 掲示板を GitHub Pages（gh-pages ブランチ）へデプロイするスクリプト。
#
#   1. flet build web で WebAssembly 静的サイトをビルド
#   2. patch_web.py で GitHub Pages 用パッチを適用
#      （coi-serviceworker 注入 / Flutter SW 無効化 / .nojekyll 追加）
#   3. build/web を gh-pages ブランチへ force-push
#
# 使い方:  ./deploy.sh
set -euo pipefail

REPO_URL="https://github.com/katzkawai/kklab-flet-board.git"
BASE_URL="kklab-flet-board"   # 公開パス（/kklab-flet-board/）に合わせる
WEB_DIR="build/web"

echo "==> 1/3 flet build web …"
yes | uv run flet build web --no-cdn --base-url "$BASE_URL"

echo "==> 2/3 GitHub Pages 用パッチ適用 …"
uv run python patch_web.py "$WEB_DIR"

echo "==> 3/3 gh-pages へデプロイ …"
TMP="$(mktemp -d)"
cp -r "$WEB_DIR/." "$TMP/"
git -C "$TMP" init -q
git -C "$TMP" checkout -q -b gh-pages
git -C "$TMP" add -A
git -C "$TMP" commit -q -m "Deploy flet web build to GitHub Pages"
git -C "$TMP" remote add origin "$REPO_URL"
git -C "$TMP" push -f -q origin gh-pages
rm -rf "$TMP"

echo "完了 ✅  数十秒後に https://katzkawai.org/$BASE_URL/ で公開されます"
