"""SQLite データアクセス層。

掲示板の投稿（posts）を保存・取得・削除する関数群。
スレッド安全のため、操作ごとに接続を開いて閉じる。
"""

import sqlite3
from pathlib import Path

# データベースファイルはこのスクリプトと同じ場所に置く
DB_PATH = Path(__file__).resolve().parent / "board.db"


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # カラム名でアクセスできるようにする
    return conn


def init_db() -> None:
    """テーブルが無ければ作成する。"""
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS posts (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                name       TEXT NOT NULL,
                message    TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
            )
            """
        )


def add_post(name: str, message: str) -> int:
    """投稿を追加し、採番された id を返す。"""
    with _connect() as conn:
        cur = conn.execute(
            "INSERT INTO posts (name, message) VALUES (?, ?)",
            (name, message),
        )
        return cur.lastrowid


def get_posts() -> list[sqlite3.Row]:
    """全投稿を新しい順で返す。"""
    with _connect() as conn:
        cur = conn.execute(
            "SELECT id, name, message, created_at FROM posts ORDER BY id DESC"
        )
        return cur.fetchall()


def delete_post(post_id: int) -> None:
    """指定 id の投稿を削除する。"""
    with _connect() as conn:
        conn.execute("DELETE FROM posts WHERE id = ?", (post_id,))
