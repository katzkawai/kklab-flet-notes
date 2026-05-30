# Repository Guidelines

## Project Structure & Module Organization

This repository contains a small Python/Flet note-taking app backed by SQLite:

- `main.py`: Flet UI, form validation, note rendering, and delete dialog.
- `db.py`: SQLite data access layer. It owns table creation and note add/read/delete operations.
- `assets/index.html`: Local web app HTML template.
- `assets/manifest.json`: PWA manifest used by the local web app.
- `assets/icons/`: Generated PWA icon PNGs.
- `scripts/generate_pwa_icons.py`: Regenerates PWA icons without third-party image libraries.
- `pyproject.toml` and `uv.lock`: Python 3.11+ metadata and locked dependencies.
- `README.md`: Setup, usage, and release notes.
- `notes.db`: Local runtime database created on first launch. Do not commit it.

Keep UI changes in `main.py` and persistence changes in `db.py` unless the app grows enough for new modules.

## Build, Test, and Development Commands

- `uv sync`: Create/update the virtual environment from `pyproject.toml` and `uv.lock`.
- `uv run python main.py`: Run the desktop Flet app locally.
- `uv run flet run --web main.py`: Run the app as a local web app in a browser.
- `uv run python scripts/generate_pwa_icons.py`: Regenerate PWA icon assets.
- `git diff --check`: Check for whitespace errors before committing.

There is no separate build step at present.

## Coding Style & Naming Conventions

Use standard Python style: 4-space indentation, clear function names, and type hints for public helpers. Follow the existing module pattern: constants, helper functions, then UI callback logic.

Names should be descriptive and snake_case, for example `refresh_notes`, `delete_note`, and `password_field`. Keep user-visible text in Japanese. Add comments only for non-obvious behavior.

## Testing Guidelines

No automated test suite is configured. For each change, perform a manual smoke test:

1. Run `uv run python main.py`.
2. Add a note with the correct password (`kklab` unless changed).
3. Confirm empty title and empty body inputs are rejected.
4. Delete a note and verify it disappears.
5. Restart the app and confirm persisted notes load from `notes.db`.

If tests are added later, prefer `pytest` files named `test_*.py`, and isolate database tests with a temporary SQLite path.

## Commit & Pull Request Guidelines

Recent history uses concise imperative commits, sometimes with Conventional Commit prefixes such as `fix(deploy): ...`, `docs: ...`, and `refactor: ...`. Use one focused change per commit.

Pull requests should include a short summary, manual test results, and screenshots or recordings for UI changes. Link related issues when available. Call out database schema or password behavior changes explicitly.

## Security & Configuration Tips

This is a personal local app, not a hosted multi-user service. Do not add external exposure or sync behavior without documenting the storage and security impact. Never commit `notes.db`, secrets, or local environment files.
