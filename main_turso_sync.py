"""Turso Sync 版の Flet エントリポイント。"""

import os

import flet as ft

import db_turso_sync
from main import main as app_main

APP_TITLE = "kklab メモ帳 (Turso Sync)"


def main(page: ft.Page) -> None:
    app_main(page, database=db_turso_sync, app_title=APP_TITLE)


if __name__ == "__main__":
    if os.environ.get("KKLAB_SERVE_WEB") == "1":
        os.environ.setdefault("FLET_FORCE_WEB_SERVER", "true")
        base_dir = os.path.dirname(os.path.abspath(__file__))
        ft.run(
            main,
            host=os.environ.get("KKLAB_HOST", "127.0.0.1"),
            port=int(os.environ.get("KKLAB_PORT", "8550")),
            assets_dir=os.path.join(base_dir, "assets"),
        )
    else:
        ft.run(main)
