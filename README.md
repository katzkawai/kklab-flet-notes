# kklab 掲示板

Python の [flet](https://flet.dev/) と SQLite3 で作成した、シンプルな掲示板アプリです。
投稿（書き込み）と削除（消去）に共通パスワードを設けています。

## 公開デモ（GitHub Pages）

🔗 **https://katzkawai.org/kklab-flet-board/**

`flet build web` で WebAssembly（Pyodide）にビルドし、GitHub Pages（`gh-pages` ブランチ）で配信しています。

> ⚠️ **注意:** 公開デモは Pyodide により **各訪問者のブラウザ内で完結**して動作します。
> そのため SQLite のデータは**ブラウザごとに別々**で、**リロードすると消え**、**利用者間で共有されません**。
> また初回読み込みで Pyodide / Flutter / アプリ一式（約90MB）を取得するため、最初の表示に時間がかかります。
> 「みんなで書き込む共有掲示板」として使うには、Python を実行できるサーバー型ホスティング（Render など）が必要です。

## 機能

- **書き込み** — 名前・メッセージ・パスワードを入力して投稿。パスワードが一致しないと投稿できません（メッセージ未入力もブロック）。名前が空の場合は「名無しさん」になります。
- **消去** — 各投稿の削除ボタンから確認ダイアログを開き、パスワードが一致した場合のみ削除します。
- **保存** — 投稿は SQLite3（`board.db`）に保存され、投稿時刻とともに新しい順で一覧表示されます。
- パスワードは初期値 **`kklab`** です。`main.py` 冒頭の `PASSWORD` 定数で変更できます。

> 補足: パスワードは書き込み・消去の「合言葉」として全員共通で使う簡易な仕組みです（投稿ごとの所有者認証ではありません）。

## ファイル構成

| ファイル | 役割 |
| --- | --- |
| `main.py` | flet による UI（入力フォーム・投稿一覧・削除ダイアログ） |
| `db.py` | SQLite3 データ層（テーブル作成、投稿の追加・取得・削除） |
| `pyproject.toml` / `uv.lock` | [uv](https://docs.astral.sh/uv/) による依存管理（flet 0.85.2） |
| `board.db` | 投稿データ（初回起動時に自動生成。リポジトリには含めません） |

## 必要環境

- Python 3.11 以上
- [uv](https://docs.astral.sh/uv/)（パッケージ・仮想環境管理）

## セットアップ

```bash
git clone <このリポジトリ>
cd kklab-flet-board
uv sync          # 依存パッケージ（flet）を仮想環境にインストール
```

## 起動方法

### デスクトップアプリとして起動

```bash
uv run python main.py
```

### ブラウザで起動

```bash
uv run flet run --web main.py
```

`board.db` は初回起動時に自動生成されます。

## 使い方

1. 上部のフォームに「名前」「メッセージ」「パスワード（`kklab`）」を入力し、**投稿する** を押すと書き込まれます。
2. 投稿を消すには、対象カードの🗑️ボタンを押し、ダイアログでパスワード（`kklab`）を入力して **削除** を押します。

## GitHub Pages へのデプロイ

WebAssembly 静的ビルドを `gh-pages` ブランチへ公開する手順です（初回は Flutter SDK が自動でインストールされます）。

1. サブパス配信に合わせて `--base-url` 付きでビルドする:

   ```bash
   uv run flet build web --no-cdn --base-url kklab-flet-board
   ```

2. ビルド成果物（`build/web`）を `gh-pages` ブランチへ push する:

   ```bash
   cd build/web
   touch .nojekyll        # GitHub Pages の Jekyll 処理を無効化
   git init -q && git checkout -b gh-pages
   git add -A && git commit -qm "Deploy flet web build to GitHub Pages"
   git remote add origin https://github.com/katzkawai/kklab-flet-board.git
   git push -f origin gh-pages
   ```

3. リポジトリの **Settings → Pages** で、ソースを `gh-pages` ブランチ・`/`（ルート）に設定する
   （`gh-pages` ブランチを push すると自動で有効化される場合もあります）。

メモ:
- `--no-cdn` で Pyodide・CanvasKit・フォントをすべて同梱するため、外部 CDN なしで動作します。
- カスタムドメイン（`katzkawai.org`）配下でもサブパスは `/kklab-flet-board/` のため、`--base-url` の値は同じです。
- `build/` は `.gitignore` 済みで、`main` ブランチには含めません。

## 更新履歴

### v0.2.0 — 2026-05-30
- `flet build web`（WebAssembly / Pyodide）で静的サイトをビルド。
- GitHub Pages（`gh-pages` ブランチ）へデプロイし、公開デモを開設: https://katzkawai.org/kklab-flet-board/
- README に公開URL・デプロイ手順を追記。

### v0.1.0 — 2026-05-30
- 初版リリース。
- flet + SQLite3 による掲示板の基本機能を実装（投稿一覧表示・書き込み・消去）。
- 書き込みと消去にパスワード認証（`kklab`）を追加。
