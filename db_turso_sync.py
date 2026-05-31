"""Turso Sync データアクセス層。

既存の `db.py` と同じ関数名を提供し、Flet UI から差し替えて使う。
Turso Cloud との同期には `TURSO_DATABASE_URL` と `TURSO_AUTH_TOKEN` が必要。
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import turso
import turso.sync

ROOT = Path(__file__).resolve().parent
DB_PATH = Path(
    os.environ.get("TURSO_LOCAL_DB_PATH", ROOT / "notes_turso_sync.db")
).expanduser()

_CONNECTION: Any | None = None
_LAST_SYNC_ERROR: str | None = None


def _env_bool(name: str, default: bool) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() not in {"0", "false", "no", "off"}


def _env_int(name: str, default: int) -> int:
    value = os.environ.get(name)
    if value is None:
        return default
    return int(value)


def _required_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(
            f"{name} が未設定です。Turso Sync 版を起動する前に環境変数を設定してください。"
        )
    return value


def _connect():
    global _CONNECTION
    if _CONNECTION is None:
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        _CONNECTION = turso.sync.connect(
            str(DB_PATH),
            remote_url=_required_env("TURSO_DATABASE_URL"),
            auth_token=_required_env("TURSO_AUTH_TOKEN"),
            long_poll_timeout_ms=_env_int("TURSO_LONG_POLL_TIMEOUT_MS", 1000),
        )
        _CONNECTION.row_factory = turso.Row
    return _CONNECTION


def _remember_sync_error(action: str, exc: Exception) -> None:
    global _LAST_SYNC_ERROR
    _LAST_SYNC_ERROR = f"{action}: {exc}"
    print(f"[turso-sync] {_LAST_SYNC_ERROR}", flush=True)


def _pull(conn) -> None:
    global _LAST_SYNC_ERROR
    try:
        conn.pull()
        _LAST_SYNC_ERROR = None
    except Exception as exc:  # noqa: BLE001 - keep local data usable on sync failure
        _remember_sync_error("pull failed", exc)


def _push(conn) -> None:
    global _LAST_SYNC_ERROR
    try:
        conn.push()
        _LAST_SYNC_ERROR = None
    except Exception as exc:  # noqa: BLE001 - keep local data usable on sync failure
        _remember_sync_error("push failed", exc)


def init_db() -> None:
    """テーブルが無ければ作成し、古い形式なら移行する。"""
    conn = _connect()
    if _env_bool("TURSO_PULL_ON_START", True):
        _pull(conn)

    columns = _get_columns(conn)
    if columns and "message" in columns:
        _migrate_from_message_schema(conn)
        columns = _get_columns(conn)
    if columns and "status" not in columns:
        conn.execute("ALTER TABLE notes ADD COLUMN status TEXT NOT NULL DEFAULT '通常'")

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
    conn.commit()

    if _env_bool("TURSO_PUSH_ON_START", True):
        _push(conn)


def _get_columns(conn) -> set[str]:
    cur = conn.execute("PRAGMA table_info(notes)")
    return {row["name"] for row in cur.fetchall()}


def _migrate_from_message_schema(conn) -> None:
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
    conn.commit()


def add_note(title: str, body: str, tags: str = "", status: str = "通常") -> int:
    """メモを追加し、採番された id を返す。"""
    conn = _connect()
    cur = conn.execute(
        "INSERT INTO notes (title, body, tags, status) VALUES (?, ?, ?, ?)",
        (title, body, tags, status),
    )
    conn.commit()
    if _env_bool("TURSO_PUSH_AFTER_WRITE", True):
        _push(conn)
    return cur.lastrowid


def get_notes() -> list[turso.Row]:
    """全メモを新しい順で返す。"""
    conn = _connect()
    if _env_bool("TURSO_PULL_BEFORE_READ", True):
        _pull(conn)
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
    conn = _connect()
    conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    conn.commit()
    if _env_bool("TURSO_PUSH_AFTER_WRITE", True):
        _push(conn)


def sync_status() -> str:
    """直近の同期エラーを返す。UI やデバッグ用。"""
    if _LAST_SYNC_ERROR:
        return _LAST_SYNC_ERROR
    return "ok"
