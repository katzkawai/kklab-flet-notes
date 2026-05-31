"""Python flet で作る簡易メモ帳 UI。

- 個人用のタイトル付きメモを保存する。
- タグ、状態、作成日時、更新日時を表示する。
"""

import flet as ft

import db

STATUS_OPTIONS = ["通常", "TODO", "進行中", "完了", "保留", "重要"]

STATUS_STYLES = {
    "TODO": (ft.Icons.CHECKLIST, "#FFFFFF", "#E7A84B"),
    "進行中": (ft.Icons.PENDING_ACTIONS, "#FFFFFF", "#6FA8DC"),
    "完了": (ft.Icons.TASK_ALT, "#FFFFFF", "#70AD7E"),
    "保留": (
        ft.Icons.PAUSE_CIRCLE_OUTLINE,
        "#FFFFFF",
        "#8FA1AE",
    ),
    "重要": (ft.Icons.PRIORITY_HIGH, "#FFFFFF", "#D9717D"),
}

TAG_STYLES = {
    "研究": (ft.Icons.SCIENCE_OUTLINED, "#FFFFFF", "#8A8ED8"),
    "論文": (ft.Icons.ARTICLE_OUTLINED, "#FFFFFF", "#8A8ED8"),
    "仕事": (ft.Icons.WORK_OUTLINE, "#FFFFFF", "#63B0A7"),
    "アイデア": (
        ft.Icons.LIGHTBULB_OUTLINE,
        "#FFFFFF",
        "#D5B34F",
    ),
    "買い物": (
        ft.Icons.SHOPPING_CART_OUTLINED,
        "#FFFFFF",
        "#D58BB1",
    ),
    "TODO": (ft.Icons.CHECKLIST, "#FFFFFF", "#E7A84B"),
}


def choose_note_style(status: str, tags: list[str]):
    if status in STATUS_STYLES:
        return STATUS_STYLES[status]
    for tag in tags:
        if tag in TAG_STYLES:
            return TAG_STYLES[tag]
    return ft.Icons.STICKY_NOTE_2_OUTLINED, "#FFFFFF", "#7FAED4"


def get_tag_style(tag: str):
    return TAG_STYLES.get(
        tag,
        (
            ft.Icons.LABEL_OUTLINE,
            "#FFFFFF",
            "#9AA8B3",
        ),
    )


def build_pill(text: str, icon, text_color: str, bgcolor: str, show_icon=False):
    controls = []
    if show_icon:
        controls.append(ft.Icon(icon, color=text_color, size=18))
    controls.append(
        ft.Text(
            text,
            color=text_color,
            weight=ft.FontWeight.BOLD,
            size=15,
        )
    )
    return ft.Container(
        bgcolor=bgcolor,
        border_radius=16,
        padding=ft.Padding.symmetric(horizontal=13, vertical=6),
        content=ft.Row(
            tight=True,
            spacing=6,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=controls,
        ),
    )


def main(page: ft.Page, database=db, app_title: str = "kklab メモ帳"):
    page.title = app_title
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = ft.Colors.BLUE_GREY_50
    page.padding = 20

    # データベースを初期化（テーブルが無ければ作成）
    database.init_db()

    # --- 入力フォームの各フィールド ---------------------------------------
    title_field = ft.TextField(label="タイトル", expand=True, text_size=17)
    tags_field = ft.TextField(
        label="タグ",
        width=260,
        hint_text="例: 研究, TODO",
        text_size=17,
    )
    status_field = ft.Dropdown(
        label="状態",
        value="通常",
        width=180,
        text_size=17,
        options=[ft.DropdownOption(status) for status in STATUS_OPTIONS],
    )
    body_field = ft.TextField(
        label="本文",
        multiline=True,
        min_lines=3,
        max_lines=6,
        expand=True,
        text_size=17,
    )
    # 入力に対するフィードバックを出す行
    form_message = ft.Text("", color=ft.Colors.RED)

    # メモ一覧を並べる領域（縦スクロール）
    notes_list = ft.ListView(expand=True, spacing=16, padding=ft.Padding.only(top=8))

    def show_snack(text: str, color=ft.Colors.GREEN_700):
        """画面下部に一時メッセージを表示する。"""
        page.show_dialog(
            ft.SnackBar(content=ft.Text(text), bgcolor=color)
        )

    def show_install_steps(e):
        page.show_dialog(
            ft.AlertDialog(
                modal=True,
                title=ft.Text("アプリとしてインストール"),
                content=ft.Column(
                    tight=True,
                    spacing=8,
                    controls=[
                        ft.Text("Chrome / Edge では、アドレスバー右側のインストールアイコンを押してください。"),
                        ft.Text("アイコンが出ない場合は、ブラウザメニューから「アプリをインストール」を選びます。"),
                    ],
                ),
                actions=[
                    ft.TextButton("閉じる", on_click=lambda e: page.pop_dialog()),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
        )

    def close_install_prompt(e):
        install_prompt.visible = False
        page.update()

    install_prompt = ft.Container(
        visible=page.web,
        bgcolor="#EEF7FF",
        border_radius=8,
        padding=ft.Padding.symmetric(horizontal=14, vertical=10),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Row(
                    spacing=8,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Icon(ft.Icons.INSTALL_DESKTOP, color="#4F7FA8"),
                        ft.Text(
                            "このメモ帳をアプリとしてインストールできます。",
                            color="#2F4F68",
                            weight=ft.FontWeight.BOLD,
                        ),
                    ],
                ),
                ft.Row(
                    spacing=4,
                    controls=[
                        ft.TextButton("手順", on_click=show_install_steps),
                        ft.IconButton(
                            icon=ft.Icons.CLOSE,
                            tooltip="閉じる",
                            on_click=close_install_prompt,
                        ),
                    ],
                ),
            ],
        ),
    )

    # --- メモ一覧の再描画 --------------------------------------------------
    def refresh_notes():
        notes_list.controls.clear()
        rows = database.get_notes()
        if not rows:
            notes_list.controls.append(
                ft.Container(
                    content=ft.Text(
                        "まだメモがありません。最初の書き込みをしてみましょう。",
                        color=ft.Colors.BLUE_GREY_400,
                        italic=True,
                        size=16,
                    ),
                    padding=20,
                    alignment=ft.Alignment.CENTER,
                )
            )
        for row in rows:
            notes_list.controls.append(build_note_card(row))
        page.update()

    # --- 1 件分のメモカードを作る -----------------------------------------
    def build_note_card(row) -> ft.Card:
        note_id = row["id"]
        tags = [tag.strip() for tag in row["tags"].split(",") if tag.strip()]
        status = row["status"]
        icon, chip_text_color, chip_bgcolor = choose_note_style(status, tags)
        status_chip = build_pill(
            status,
            icon,
            chip_text_color,
            chip_bgcolor,
            show_icon=True,
        )
        chip_row = ft.Row(
            spacing=8,
            wrap=True,
            controls=[
                status_chip,
                *[build_pill(tag, *get_tag_style(tag)) for tag in tags],
            ],
        )
        timestamps = f"作成: {row['created_at']} / 更新: {row['updated_at']}"
        return ft.Card(
            content=ft.Container(
                padding=20,
                content=ft.Column(
                    spacing=10,
                    controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            vertical_alignment=ft.CrossAxisAlignment.START,
                            controls=[
                                ft.Row(
                                    spacing=10,
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                    controls=[
                                        ft.Icon(
                                            icon,
                                            color=chip_bgcolor,
                                            size=26,
                                        ),
                                        ft.Text(
                                            row["title"],
                                            weight=ft.FontWeight.BOLD,
                                            size=19,
                                        ),
                                        ft.Text(
                                            f"#{note_id}",
                                            color=ft.Colors.BLUE_GREY_300,
                                            size=14,
                                        ),
                                    ],
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE_OUTLINE,
                                    icon_color=ft.Colors.RED_400,
                                    icon_size=26,
                                    tooltip="削除",
                                    on_click=lambda e, nid=note_id: open_delete_dialog(nid),
                                ),
                            ],
                        ),
                        ft.Text(row["body"], selectable=True, size=16),
                        chip_row,
                        ft.Text(
                            timestamps,
                            size=13,
                            color=ft.Colors.BLUE_GREY_400,
                        ),
                    ],
                ),
            )
        )

    # --- 書き込み処理 ------------------------------------------------------
    def submit_note(e):
        title = title_field.value.strip()
        body = body_field.value.strip()
        tags = tags_field.value.strip()
        status = status_field.value or "通常"

        if not title:
            form_message.value = "タイトルを入力してください。"
            page.update()
            return
        if not body:
            form_message.value = "本文を入力してください。"
            page.update()
            return

        database.add_note(title, body, tags, status)

        title_field.value = ""
        body_field.value = ""
        tags_field.value = ""
        status_field.value = "通常"
        form_message.value = ""
        refresh_notes()
        show_snack("保存しました。")

    # --- 削除処理（確認ダイアログ） ----------------------------------------
    def open_delete_dialog(note_id: int):
        def confirm_delete(e):
            database.delete_note(note_id)
            page.pop_dialog()
            refresh_notes()
            show_snack("削除しました。", color=ft.Colors.RED_400)

        def cancel(e):
            page.pop_dialog()

        page.show_dialog(
            ft.AlertDialog(
                modal=True,
                title=ft.Text(f"メモ #{note_id} を削除"),
                content=ft.Column(
                    tight=True,
                    spacing=10,
                    controls=[
                        ft.Text("このメモを削除します。元に戻せません。"),
                    ],
                ),
                actions=[
                    ft.TextButton("キャンセル", on_click=cancel),
                    ft.FilledButton(
                        "削除",
                        on_click=confirm_delete,
                        style=ft.ButtonStyle(bgcolor=ft.Colors.RED_400),
                    ),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
        )

    # --- 画面構成 ----------------------------------------------------------
    header = ft.Row(
        spacing=12,
        controls=[
            ft.Icon(ft.Icons.EDIT_NOTE, color=ft.Colors.BLUE_700, size=36),
            ft.Text(app_title, size=32, weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLUE_900),
        ],
    )

    form_card = ft.Card(
        content=ft.Container(
            padding=22,
            content=ft.Column(
                spacing=14,
                controls=[
                    ft.Row(
                        spacing=14,
                        controls=[title_field, tags_field, status_field],
                    ),
                    body_field,
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            form_message,
                            ft.FilledButton(
                                "書き込む",
                                icon=ft.Icons.SEND,
                                on_click=submit_note,
                                style=ft.ButtonStyle(
                                    padding=ft.Padding.symmetric(horizontal=22, vertical=16),
                                    text_style=ft.TextStyle(size=16),
                                ),
                            ),
                        ],
                    ),
                ],
            ),
        )
    )

    page.add(
        ft.Column(
            expand=True,
            spacing=18,
            controls=[
                header,
                install_prompt,
                form_card,
                ft.Divider(),
                ft.Text("メモ一覧", size=20, weight=ft.FontWeight.BOLD,
                        color=ft.Colors.BLUE_GREY_700),
                notes_list,
            ],
        )
    )

    refresh_notes()


if __name__ == "__main__":
    import os

    if os.environ.get("KKLAB_SERVE_WEB") == "1":
        # PWA のバックエンドとして、ローカル Web サーバーのみを起動する。
        # FLET_FORCE_WEB_SERVER=true で HTTP 配信を強制し、ブラウザの自動起動を抑止する
        # （起動後はインストール済み PWA から開いて使う）。
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
