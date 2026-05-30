"""Python flet + SQLite3 で作る簡易掲示板。

- 投稿（書き込み）と削除（消去）にはパスワードが必要。
- パスワードは "kklab"。
"""

import flet as ft

import db

# 書き込み・消去に必要な共通パスワード
PASSWORD = "kklab"


def main(page: ft.Page):
    page.title = "kklab 掲示板"
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

    # 投稿一覧を並べる領域（縦スクロール）
    posts_list = ft.ListView(expand=True, spacing=12, padding=ft.Padding.only(top=8))

    def show_snack(text: str, color=ft.Colors.GREEN_700):
        """画面下部に一時メッセージを表示する。"""
        page.show_dialog(
            ft.SnackBar(content=ft.Text(text), bgcolor=color)
        )

    # --- 投稿一覧の再描画 --------------------------------------------------
    def refresh_posts():
        posts_list.controls.clear()
        rows = db.get_posts()
        if not rows:
            posts_list.controls.append(
                ft.Container(
                    content=ft.Text(
                        "まだ投稿がありません。最初の書き込みをしてみましょう。",
                        color=ft.Colors.BLUE_GREY_400,
                        italic=True,
                    ),
                    padding=20,
                    alignment=ft.Alignment.CENTER,
                )
            )
        for row in rows:
            posts_list.controls.append(build_post_card(row))
        page.update()

    # --- 1 件分の投稿カードを作る -----------------------------------------
    def build_post_card(row) -> ft.Card:
        post_id = row["id"]
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
                                            f"#{post_id}",
                                            color=ft.Colors.BLUE_GREY_300,
                                            size=12,
                                        ),
                                    ],
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE_OUTLINE,
                                    icon_color=ft.Colors.RED_400,
                                    tooltip="削除",
                                    on_click=lambda e, pid=post_id: open_delete_dialog(pid),
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

    # --- 投稿処理 ----------------------------------------------------------
    def submit_post(e):
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

        db.add_post(name or "名無しさん", message)

        # フォームをクリア
        name_field.value = ""
        message_field.value = ""
        password_field.value = ""
        form_message.value = ""
        refresh_posts()
        show_snack("投稿しました。")

    # --- 削除処理（パスワード確認ダイアログ） ------------------------------
    def open_delete_dialog(post_id: int):
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
            db.delete_post(post_id)
            page.pop_dialog()
            refresh_posts()
            show_snack("削除しました。", color=ft.Colors.RED_400)

        def cancel(e):
            page.pop_dialog()

        page.show_dialog(
            ft.AlertDialog(
                modal=True,
                title=ft.Text(f"投稿 #{post_id} を削除"),
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
            ft.Icon(ft.Icons.FORUM, color=ft.Colors.BLUE_700, size=30),
            ft.Text("kklab 掲示板", size=26, weight=ft.FontWeight.BOLD,
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
                                "投稿する",
                                icon=ft.Icons.SEND,
                                on_click=submit_post,
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
                ft.Text("投稿一覧", size=16, weight=ft.FontWeight.BOLD,
                        color=ft.Colors.BLUE_GREY_700),
                posts_list,
            ],
        )
    )

    refresh_posts()


if __name__ == "__main__":
    ft.run(main)
