# Lemmata templates

The templates offered in [Lemmata](https://github.com/NilsBriggen/lemmata)'s New project gallery, beyond the six basic ones the app ships with. The app reads `index.json` from this repository, shows the templates with their previews, and downloads the one you pick (checking every file against its SHA-256).

This is a small, curated collection: 20 to 30 templates that are actually good, not every class on CTAN. A template belongs here when it

- builds without errors or warnings with a current TeX Live, using only packages from TeX Live;
- is the starting point people really need: the publisher's class and settings, sensible structure, no lorem-ipsum padding beyond what shows the layout;
- explains its non-obvious choices in short comments, in plain language;
- stays small (no fonts or large images: each file under 5 MB, ideally far less).

## Linking to a template

`lemmata://new?template=<id>` opens Lemmata's New project gallery with that template chosen, for example `lemmata://new?template=ieee`. Use it for "Open in Lemmata" links on a website or in a README. Nothing is created until the user confirms.

## A template

One folder in `templates/`, named by its id (lowercase, dashes):

```
templates/ieee/
  template.toml   # how the gallery shows it
  lemmata.toml    # the project settings a new project starts with
  main.tex        # and any other files: chapters, refs.bib, figures
  preview.png     # page 1, made by scripts/build.py --previews
```

`template.toml`:

```toml
name = "IEEE conference"
description = "A two-column paper with IEEEtran, for IEEE conferences."
# Papers, School, Theses & reports, Presentations, Posters, Letters & CV,
# or Journals & conferences (publisher templates, shown in their own folder)
category = "Journals & conferences"
tags = ["ieee", "conference", "two-column"]
order = 1                 # optional: position within the category
```

`template.toml` and `preview.png` are not copied into new projects; everything else is.

## Adding or changing a template

```sh
python3 scripts/build.py ieee --previews   # build it and write its preview
python3 scripts/build-index.py             # update index.json
```

Commit the template, its `preview.png` and `index.json` together. If it needs TeX Live packages that aren't in `.github/tex-packages.txt` yet, add them: CI builds every template with exactly that list.

`scripts/build.py` without names builds all templates; CI runs it on every push and checks that `index.json` is up to date.

## License

[CC0 1.0](LICENSE): the templates are dedicated to the public domain. Use, change and share them for anything, with no attribution needed; what you write with them is entirely yours. The document classes they use (IEEEtran, acmart and others) come from TeX Live under their own licenses and are not part of this repository.
