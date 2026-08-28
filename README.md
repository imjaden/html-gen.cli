<p align="center">
  <a href="README.zh.md">🇨🇳</a> · <a href="README.md">🇬🇧</a>
</p>

<h1 align="center">html-gen</h1>

<p align="center">
  <a href="https://github.com/imjaden/html-gen.cli"><img src="https://github.com/favicon.ico" width="16" height="16" alt="GitHub"> GitHub</a>
  <span> · </span>
  <a href="https://pypi.org/project/html-gen-cli"><img src="https://pypi.org/static/images/favicon.35549fe8.ico" width="16" height="16" alt="PyPI"> PyPI</a>
</p>

> Markdown / JSON → self-contained single-file HTML. Zero dependencies.
>
> Dark theme, Chinese-first. Four template types: B-doc (TOC sidebar), A-table (search / sort / paginate), C-knowledge (tabs + sections), D-slide (h2 pages).
>
> html-gen is an independent tool — unrelated to the npm package "html-gen".

- [x] **Zero External Dependencies** — Python stdlib only; output is a self-contained single HTML file (CSS inlined)
- [x] **Four Template Types** — doc / table / knowledge / slide (`html-gen doc|table|knowledge|slide`)
- [x] **Rich Data Table** — search / multi-sort / pagination / column visibility / CSV export / batch ops / split preview / videos column
- [x] **Knowledge Base** — top tabs + sidebar sections + iframe/inline content, URL sync & state restore
- [x] **AI Agent Integration** — `html-gen prompt` ships project skills (usage docs for AI agents)
- [x] **Privacy by Default** — generated HTML carries no personal links unless you opt in (`--github-url` / `--home-url`)

## Installation

```bash
pip install html-gen-cli        # installs the `html-gen` command
```

Or run from source (no install):

```bash
git clone https://github.com/imjaden/html-gen.cli
cd html-gen.cli
python3 html-gen.py version     # html-gen v3.3 (2026-08-28)
```

## Quick Start

```bash
# B — Markdown → document (TOC sidebar + reading)
html-gen doc -i report.md -o report.html

# D — Markdown → slide (h2 pages + keyboard nav)
html-gen slide -i slides.md -o slides.html

# A — JSON → data table
html-gen table -d data.json -o index.html

# C — JSON → knowledge base (top tabs + sidebar sections)
html-gen knowledge -d kb.json -g groups.json -o kb.html
```

## Commands

| Command | Description |
|:--|:--|
| `html-gen doc` | Markdown → B-type document |
| `html-gen slide` | Markdown → D-type slide |
| `html-gen table` | JSON → A-type data table |
| `html-gen knowledge` | JSON → C-type knowledge base |
| `html-gen version` | Show version (vX.Y + release date) |
| `html-gen help [topic]` | Overview + topic help (doc/slide/table/knowledge/prompt/demo) |
| `html-gen prompt [skill]` | Output project skills (AI-facing docs) |
| `html-gen demo list` | Demo index & registry |

## AI Interchange

```bash
html-gen prompt                   # list all skills (name + description)
html-gen prompt html-gen-table    # full usage guide for one skill
html-gen prompt html-gen-table --brief
html-gen prompt --json            # machine-readable envelope
```

## Data Directory

- `data/*.json` — source data (tables / knowledge bases)
- `demos/*.html` — generated artifacts (never hand-edit; regenerate from data)
- `layout-*.html` / `style-guide.css` — Layer-2 templates / Layer-1 CSS base

## Local Development

```bash
# preview (root landing page + demos)
python3 -m http.server 8089

# run tests (pytest-xdist, ~36s)
python3 -m pytest tests/ -q -n 4
```

## Testing

- Selenium headless Chrome regression suite (`tests/test_*.py`, 214+ cases)
- Every test asserts zero JS errors on page load
