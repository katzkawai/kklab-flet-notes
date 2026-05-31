# Turso Sync 版メモ帳

この文書は、通常版の `notes.db` ではなく、Turso Cloud と同期できるローカル DB を使う別実装の説明です。通常版は `main.py` / `db.py`、同期版は `main_turso_sync.py` / `db_turso_sync.py` から起動します。

Turso の Python SDK では、ローカルファイルに読み書きしながら必要に応じて Turso Cloud と `push()` / `pull()` する `pyturso` / `turso.sync` が用意されています。この実装はその方式を使います。

- 公式ドキュメント: [Turso Python Quickstart](https://docs.turso.tech/sdk/python/quickstart)
- API リファレンス: [Turso Python Reference](https://docs.turso.tech/sdk/python/reference)

## 通常版との違い

| 項目 | 通常版 | Turso Sync 版 |
| --- | --- | --- |
| 起動ファイル | `main.py` | `main_turso_sync.py` |
| DB 層 | `db.py` | `db_turso_sync.py` |
| ローカル DB | `notes.db` | `notes_turso_sync.db` |
| 同期 | なし | Turso Cloud に `push()` / `pull()` |
| 必須環境変数 | なし | `TURSO_DATABASE_URL`, `TURSO_AUTH_TOKEN` |

通常版の `notes.db` はそのまま残ります。Turso Sync 版は `notes_turso_sync.db` を使うため、既存データは自動では移行されません。

## 事前準備

Turso 側にデータベースを作成し、URL と認証トークンを用意します。

```bash
turso db show --url <database-name>
turso db tokens create <database-name>
```

このアプリは `.env` を自動では読み込みません。起動するシェルで環境変数を設定してください。

```bash
export TURSO_DATABASE_URL="libsql://..."
export TURSO_AUTH_TOKEN="..."
```

`.env` と `.env.*` は Git 管理から除外しています。トークンを README、ソースコード、コミット履歴に入れないでください。

## 起動方法

依存関係を同期します。`pyturso` は `pyproject.toml` に含めています。

```bash
uv sync
```

デスクトップアプリとして起動します。

```bash
uv run python main_turso_sync.py
```

開発用 Web 表示で起動する場合は次のようにします。

```bash
uv run flet run --web main_turso_sync.py
```

PWA バックエンドと同じ起動方法で使う場合は、既存の通常版と衝突しないようにポートを分けると扱いやすくなります。

```bash
KKLAB_SERVE_WEB=1 KKLAB_PORT=8551 uv run python main_turso_sync.py
```

## 同期タイミング

`db_turso_sync.py` は、通常版の `db.py` と同じ `init_db()`、`add_note()`、`get_notes()`、`delete_note()` を提供します。UI 側は同じまま、DB 層だけを差し替えています。

既定の同期タイミングは次の通りです。

| 環境変数 | 既定 | 動作 |
| --- | --- | --- |
| `TURSO_PULL_ON_START` | `1` | 起動時に Turso Cloud から pull する |
| `TURSO_PUSH_ON_START` | `1` | 起動時のスキーマ作成・移行後に push する |
| `TURSO_PULL_BEFORE_READ` | `1` | メモ一覧を読む前に pull する |
| `TURSO_PUSH_AFTER_WRITE` | `1` | 書き込み・削除後に push する |
| `TURSO_LONG_POLL_TIMEOUT_MS` | `1000` | pull 時の long-poll 待ち時間をミリ秒で指定する |

真偽値の環境変数は、値を `0`、`false`、`no`、`off` にすると、その同期処理を無効にできます。

```bash
TURSO_PULL_BEFORE_READ=0 uv run python main_turso_sync.py
```

ローカル DB の場所を変えたい場合は `TURSO_LOCAL_DB_PATH` を指定します。

```bash
TURSO_LOCAL_DB_PATH="$HOME/.local/share/kklab-flet-notes/notes.db" uv run python main_turso_sync.py
```

## 設計上の注意

- 同期版は、通常版の `main.py` の UI を再利用し、DB 層だけを `db_turso_sync.py` に差し替えています。
- 同期失敗時はターミナルに `[turso-sync] ...` の警告を出します。ローカルへの書き込みは維持しますが、Turso Cloud に反映されていない可能性があります。
- 複数端末で同じメモを同時編集するための衝突解決 UI はありません。
- 既存の `notes.db` から Turso Sync 版へのデータ移行はまだ自動化していません。必要になったら、Markdown / JSON エクスポートとインポートを追加するのが安全です。
- `TURSO_AUTH_TOKEN` は秘密情報です。`.env` は Git 管理外ですが、アプリは `.env` を自動ロードしないため、起動時のシェル環境に明示的に設定してください。

## 実装ファイル

- `main_turso_sync.py`: Turso Sync 版の起動エントリポイント。
- `db_turso_sync.py`: `turso.sync` を使う DB 層。
- `.gitignore`: `notes_turso_sync.db*` と `.env*` を除外。
- `pyproject.toml`: `pyturso` を依存関係に追加。
