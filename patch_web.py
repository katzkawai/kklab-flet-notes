"""flet build web の生成物に GitHub Pages 用パッチを当てるスクリプト。

GitHub Pages は COOP/COEP ヘッダーを送れないため、Pyodide が必要とする
SharedArrayBuffer が使えず、アプリがローディングで固まる。これを回避するため:

1) coi-serviceworker（Service Worker でクロスオリジン分離を有効化）を index.html の
   先頭で読み込む。
2) Flutter 自身の Service Worker 登録を無効化する（同一スコープで coi と競合し、
   クロスオリジン分離が壊れるのを防ぐ）。

`flet build web` を実行するたびに index.html / flutter_bootstrap.js は再生成される
ため、ビルド後に本スクリプトを実行する（deploy.sh から呼ばれる）。冪等。
"""

import re
import shutil
import sys
from pathlib import Path

WEB_DIR = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("build/web")
COI_SRC = Path("web/coi-serviceworker.min.js")
COI_NAME = "coi-serviceworker.min.js"


def patch_index_html(path: Path) -> None:
    html = path.read_text(encoding="utf-8")
    if COI_NAME in html:
        print("  index.html: 既にパッチ済み")
        return
    snippet = (
        '\n  <!-- GitHub Pages 用: Service Worker でクロスオリジン分離を有効化し '
        "SharedArrayBuffer を使えるようにする（最初に読み込む） -->\n"
        f'  <script src="{COI_NAME}"></script>'
    )
    # <base ...> の直後に挿入（無ければ <head> の直後）
    if "<base " in html:
        html = re.sub(r"(<base [^>]*>)", r"\1" + snippet, html, count=1)
    else:
        html = re.sub(r"(<head>)", r"\1" + snippet, html, count=1)
    path.write_text(html, encoding="utf-8")
    print("  index.html: coi-serviceworker を注入")


def patch_bootstrap(path: Path) -> None:
    js = path.read_text(encoding="utf-8")
    # _flutter.loader.load({...}) に渡す serviceWorkerSettings: {...}, を除去
    new = re.sub(
        r"\n\s*serviceWorkerSettings:\s*\{.*?\},",
        "\n    // Flutter の Service Worker は無効化（coi-serviceworker と競合するため）",
        js,
        count=1,
        flags=re.DOTALL,
    )
    if new == js:
        print("  flutter_bootstrap.js: serviceWorkerSettings 無し（パッチ不要）")
    else:
        path.write_text(new, encoding="utf-8")
        print("  flutter_bootstrap.js: Flutter SW 登録を無効化")


def main() -> None:
    if not WEB_DIR.exists():
        sys.exit(f"ビルド出力が見つかりません: {WEB_DIR}")
    shutil.copy(COI_SRC, WEB_DIR / COI_NAME)
    print(f"  {COI_NAME} を {WEB_DIR} へコピー")
    (WEB_DIR / ".nojekyll").touch()  # GitHub Pages の Jekyll 処理を無効化
    patch_index_html(WEB_DIR / "index.html")
    patch_bootstrap(WEB_DIR / "flutter_bootstrap.js")
    print("パッチ完了 ✅")


if __name__ == "__main__":
    main()
