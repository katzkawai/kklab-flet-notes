"""SQLite データアクセス層。

メモ（notes）を保存・取得・削除する関数群。
スレッド安全のため、操作ごとに接続を開いて閉じる。
"""

import sqlite3
from pathlib import Path

# データベースファイルはこのスクリプトと同じ場所に置く
DB_PATH = Path(__file__).resolve().parent / "notes.db"


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # カラム名でアクセスできるようにする
    return conn


def init_db() -> None:
    """テーブルが無ければ作成する。"""
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS notes (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                name       TEXT NOT NULL,
                message    TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
            )
            """
        )


def add_note(name: str, message: str) -> int:
    """メモを追加し、採番された id を返す。"""
    with _connect() as conn:
        cur = conn.execute(
            "INSERT INTO notes (name, message) VALUES (?, ?)",
            (name, message),
        )
        return cur.lastrowid


def get_notes() -> list[sqlite3.Row]:
    """全メモを新しい順で返す。"""
    with _connect() as conn:
        cur = conn.execute(
            "SELECT id, name, message, created_at FROM notes ORDER BY id DESC"
        )
        return cur.fetchall()


def delete_note(note_id: int) -> None:
    """指定 id のメモを削除する。"""
    with _connect() as conn:
        conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
