#!/usr/bin/env bash
# macOS 用ランチャー。Finder からダブルクリックすると Terminal で起動する。
# 実体は同じフォルダの start-notes.sh を呼び出すだけ（ロジックは共通）。
#
# ※ ターミナルから使う場合は start-notes.sh を直接実行しても同じ。
cd "$(dirname "$0")" || exit 1
exec ./start-notes.sh
