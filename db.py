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
    """テーブルが無ければ作成し、古い形式なら移行する。"""
    with _connect() as conn:
        columns = _get_columns(conn)
        if columns and "message" in columns:
            _migrate_from_message_schema(conn)
            columns = _get_columns(conn)
        if columns and "status" not in columns:
            conn.execute(
                "ALTER TABLE notes ADD COLUMN status TEXT NOT NULL DEFAULT '通常'"
            )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS notes (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                title      TEXT NOT NULL,
                body       TEXT NOT NULL,
                tags       TEXT NOT NULL DEFAULT '',
                status     TEXT NOT NULL DEFAULT '通常',
                created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
            )
            """
        )


def _get_columns(conn: sqlite3.Connection) -> set[str]:
    cur = conn.execute("PRAGMA table_info(notes)")
    return {row["name"] for row in cur.fetchall()}


def _migrate_from_message_schema(conn: sqlite3.Connection) -> None:
    """旧 name/message 形式の notes テーブルを title/body/tags 形式へ移行する。"""
    conn.execute("ALTER TABLE notes RENAME TO notes_old")
    conn.execute(
        """
        CREATE TABLE notes (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            title      TEXT NOT NULL,
            body       TEXT NOT NULL,
            tags       TEXT NOT NULL DEFAULT '',
            status     TEXT NOT NULL DEFAULT '通常',
            created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
        )
        """
    )
    conn.execute(
        """
        INSERT INTO notes (id, title, body, tags, status, created_at, updated_at)
        SELECT
            id,
            substr(message, 1, 30),
            message,
            '',
            '通常',
            created_at,
            created_at
        FROM notes_old
        """
    )
    conn.execute("DROP TABLE notes_old")


def add_note(title: str, body: str, tags: str = "", status: str = "通常") -> int:
    """メモを追加し、採番された id を返す。"""
    with _connect() as conn:
        cur = conn.execute(
            "INSERT INTO notes (title, body, tags, status) VALUES (?, ?, ?, ?)",
            (title, body, tags, status),
        )
        return cur.lastrowid


def get_notes() -> list[sqlite3.Row]:
    """全メモを新しい順で返す。"""
    with _connect() as conn:
        cur = conn.execute(
            """
            SELECT id, title, body, tags, status, created_at, updated_at
            FROM notes
            ORDER BY id DESC
            """
        )
        return cur.fetchall()


def delete_note(note_id: int) -> None:
    """指定 id のメモを削除する。"""
    with _connect() as conn:
        conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
