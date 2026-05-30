"""Python flet + SQLite3 で作る簡易メモ帳。

- 書き込みと消去にはパスワードが必要。
- パスワードは "kklab"。
"""

import flet as ft

import db

# 書き込み・消去に必要な共通パスワード
PASSWORD = "kklab"


def main(page: ft.Page):
    page.title = "kklab メモ帳"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = ft.Colors.BLUE_GREY_50
    page.padding = 20

    # データベースを初期化（テーブルが無ければ作成）
    db.init_db()

    # --- 入力フォームの各フィールド ---------------------------------------
    name_field = ft.TextField(label="名前", width=200)
    message_field = ft.TextField(
        label="メッセージ",
        multiline=True,
        min_lines=2,
        max_lines=5,
        expand=True,
    )
    password_field = ft.TextField(
        label="パスワード",
        password=True,
        can_reveal_password=True,
        width=200,
    )
    # 入力に対するフィードバックを出す行
    form_message = ft.Text("", color=ft.Colors.RED)

    # メモ一覧を並べる領域（縦スクロール）
    notes_list = ft.ListView(expand=True, spacing=12, padding=ft.Padding.only(top=8))

    def show_snack(text: str, color=ft.Colors.GREEN_700):
        """画面下部に一時メッセージを表示する。"""
        page.show_dialog(
            ft.SnackBar(content=ft.Text(text), bgcolor=color)
        )

    # --- メモ一覧の再描画 --------------------------------------------------
    def refresh_notes():
        notes_list.controls.clear()
        rows = db.get_notes()
        if not rows:
            notes_list.controls.append(
                ft.Container(
                    content=ft.Text(
                        "まだメモがありません。最初の書き込みをしてみましょう。",
                        color=ft.Colors.BLUE_GREY_400,
                        italic=True,
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
        return ft.Card(
            content=ft.Container(
                padding=14,
                content=ft.Column(
                    spacing=6,
                    controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            vertical_alignment=ft.CrossAxisAlignment.START,
                            controls=[
                                ft.Row(
                                    spacing=8,
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                    controls=[
                                        ft.Icon(
                                            ft.Icons.ACCOUNT_CIRCLE,
                                            color=ft.Colors.BLUE_400,
                                        ),
                                        ft.Text(
                                            row["name"],
                                            weight=ft.FontWeight.BOLD,
                                            size=15,
                                        ),
                                        ft.Text(
                                            f"#{note_id}",
                                            color=ft.Colors.BLUE_GREY_300,
                                            size=12,
                                        ),
                                    ],
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE_OUTLINE,
                                    icon_color=ft.Colors.RED_400,
                                    tooltip="削除",
                                    on_click=lambda e, nid=note_id: open_delete_dialog(nid),
                                ),
                            ],
                        ),
                        ft.Text(row["message"], selectable=True),
                        ft.Text(
                            row["created_at"],
                            size=11,
                            color=ft.Colors.BLUE_GREY_400,
                        ),
                    ],
                ),
            )
        )

    # --- 書き込み処理 ------------------------------------------------------
    def submit_note(e):
        name = name_field.value.strip()
        message = message_field.value.strip()
        password = password_field.value

        if not message:
            form_message.value = "メッセージを入力してください。"
            page.update()
            return
        if password != PASSWORD:
            form_message.value = "パスワードが違います。"
            page.update()
            return

        db.add_note(name or "名無しさん", message)

        # フォームをクリア
        name_field.value = ""
        message_field.value = ""
        password_field.value = ""
        form_message.value = ""
        refresh_notes()
        show_snack("書き込みました。")

    # --- 削除処理（パスワード確認ダイアログ） ------------------------------
    def open_delete_dialog(note_id: int):
        del_password = ft.TextField(
            label="パスワード",
            password=True,
            can_reveal_password=True,
            autofocus=True,
        )
        del_error = ft.Text("", color=ft.Colors.RED)

        def confirm_delete(e):
            if del_password.value != PASSWORD:
                del_error.value = "パスワードが違います。"
                page.update()
                return
            db.delete_note(note_id)
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
                        ft.Text("削除するにはパスワードを入力してください。"),
                        del_password,
                        del_error,
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
        spacing=10,
        controls=[
            ft.Icon(ft.Icons.EDIT_NOTE, color=ft.Colors.BLUE_700, size=30),
            ft.Text("kklab メモ帳", size=26, weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLUE_900),
        ],
    )

    form_card = ft.Card(
        content=ft.Container(
            padding=16,
            content=ft.Column(
                spacing=10,
                controls=[
                    ft.Row(
                        spacing=12,
                        controls=[name_field, password_field],
                    ),
                    message_field,
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            form_message,
                            ft.FilledButton(
                                "書き込む",
                                icon=ft.Icons.SEND,
                                on_click=submit_note,
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
            spacing=14,
            controls=[
                header,
                form_card,
                ft.Divider(),
                ft.Text("メモ一覧", size=16, weight=ft.FontWeight.BOLD,
                        color=ft.Colors.BLUE_GREY_700),
                notes_list,
            ],
        )
    )

    refresh_notes()


if __name__ == "__main__":
    ft.run(main)
