#!/usr/bin/env python3
"""Writes index.json: every template's details and files, each with its
SHA-256, so the app can show the gallery and check what it downloads.

    python3 scripts/build-index.py          # write index.json
    python3 scripts/build-index.py --check  # fail if index.json is out of date (CI)
"""
import hashlib
import json
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / "templates"
REQUIRED = ("name", "description", "category")
# Not part of a new project: the gallery shows the preview, template.toml describes it.
NOT_COPIED = {"template.toml", "preview.png"}
MAX_FILE = 5 * 1024 * 1024


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def entry(folder: Path) -> dict:
    meta = tomllib.loads((folder / "template.toml").read_text(encoding="utf-8"))
    missing = [k for k in REQUIRED if not meta.get(k)]
    if missing:
        sys.exit(f"{folder.name}/template.toml lacks {', '.join(missing)}")
    if not (folder / "main.tex").is_file():
        sys.exit(f"{folder.name} has no main.tex")
    if not (folder / "preview.png").is_file():
        sys.exit(f"{folder.name} has no preview.png (scripts/previews.sh makes it)")
    files = []
    for f in sorted(folder.rglob("*")):
        rel = f.relative_to(folder).as_posix()
        if f.is_dir() or rel in NOT_COPIED or any(p.startswith(".") for p in f.relative_to(folder).parts):
            continue
        if f.stat().st_size > MAX_FILE:
            sys.exit(f"{folder.name}/{rel} is over {MAX_FILE // 1024 // 1024} MB")
        files.append({"path": rel, "size": f.stat().st_size, "sha256": sha256(f)})
    preview = folder / "preview.png"
    return {
        "id": folder.name,
        "name": meta["name"],
        "description": meta["description"],
        "category": meta["category"],
        "tags": meta.get("tags", []),
        "order": meta.get("order", 100),
        "preview": {"path": "preview.png", "size": preview.stat().st_size, "sha256": sha256(preview)},
        "files": files,
    }


def build() -> str:
    folders = sorted(p for p in TEMPLATES.iterdir() if (p / "template.toml").is_file())
    templates = [entry(f) for f in folders]
    templates.sort(key=lambda t: (t["category"], t["order"], t["name"]))
    return json.dumps({"version": 1, "templates": templates}, indent=2, ensure_ascii=False) + "\n"


def main() -> None:
    text = build()
    out = ROOT / "index.json"
    if "--check" in sys.argv:
        if not out.is_file() or out.read_text(encoding="utf-8") != text:
            sys.exit("index.json is out of date: run python3 scripts/build-index.py and commit it")
        print("index.json is up to date")
        return
    out.write_text(text, encoding="utf-8")
    print(f"index.json: {text.count('\"id\"')} templates")


if __name__ == "__main__":
    main()
