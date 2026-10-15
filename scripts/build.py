#!/usr/bin/env python3
"""Compiles every template the way Lemmata does (latexmk with the engine and
bibliography tool from its lemmata.toml), so nothing broken is published.

    python3 scripts/build.py                  # build all, report each
    python3 scripts/build.py --previews       # also write templates/<id>/preview.png
    python3 scripts/build.py ieee poster      # only these

Needs latexmk and the TeX packages of every template; --previews also needs
pdftoppm (poppler). The preview is page 1, at most 420 px on its longer side.
"""
import shutil
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / "templates"
ENGINES = {"pdflatex": "-pdf", "xelatex": "-xelatex", "lualatex": "-lualatex"}
MAX_PREVIEW = 60 * 1024


def build(folder: Path, work: Path, previews: bool) -> str | None:
    """Returns why the template failed, or None."""
    config = tomllib.loads((folder / "lemmata.toml").read_text(encoding="utf-8")) if (folder / "lemmata.toml").is_file() else {}
    engine = config.get("engine", "pdflatex")
    if engine not in ENGINES:
        return f"engine {engine!r} is not one Lemmata offers for templates"
    main = config.get("main", "main.tex")
    copy = work / folder.name
    shutil.copytree(folder, copy)
    # \include writes chapters/x.aux into the output folder; TeX can't create the subfolder (Lemmata does).
    for sub in [d for d in copy.rglob("*") if d.is_dir() and d.name != "build"]:
        (copy / "build" / sub.relative_to(copy)).mkdir(parents=True, exist_ok=True)
    cmd = ["latexmk", ENGINES[engine], "-interaction=nonstopmode", "-halt-on-error", "-file-line-error", "-outdir=build", main]
    run = subprocess.run(cmd, cwd=copy, capture_output=True, text=True, errors="replace", timeout=600)
    pdf = copy / "build" / (Path(main).stem + ".pdf")
    if run.returncode != 0 or not pdf.is_file():
        errors = [l for l in run.stdout.splitlines() if ":" in l and (" error" in l.lower() or l.startswith("!"))]
        return "\n    ".join(errors[:6] or run.stdout.splitlines()[-12:])
    if previews:
        out = folder / "preview"
        subprocess.run(["pdftoppm", "-png", "-f", "1", "-l", "1", "-scale-to", "420", "-singlefile", str(pdf), str(out)], check=True)
        size = (folder / "preview.png").stat().st_size
        if size > MAX_PREVIEW:
            return f"preview.png is {size // 1024} KB, over {MAX_PREVIEW // 1024} KB"
    return None


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    previews = "--previews" in sys.argv
    folders = sorted(p for p in TEMPLATES.iterdir() if (p / "template.toml").is_file() and (not args or p.name in args))
    failed = 0
    with tempfile.TemporaryDirectory() as work:
        for folder in folders:
            why = build(folder, Path(work), previews)
            print(f"{'ok  ' if why is None else 'FAIL'} {folder.name}" + (f"\n    {why}" if why else ""), flush=True)
            failed += why is not None
    if failed:
        sys.exit(f"{failed} of {len(folders)} templates failed")


if __name__ == "__main__":
    main()
