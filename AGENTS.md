# hackupc2023

HackUPC 2023 hackathon project: a PyQt5 desktop app that recommends houses by learning user preferences from pairwise image comparisons and ranking listings via Gower distance over mixed categorical/numerical features.

## Architecture
- `pol/interface.py` — entry point; `ImageChooser` PyQt5 widget that shows two random houses and records user picks, importing `from Tati.HouseMatch import *`.
- `Tati/HouseMatch.py` — feature extraction (`extract_features`), `gower_distance`, and `euler_distance` over the property dataset.
- `Pablesky/` — exploratory Jupyter notebooks (`Untitled.ipynb`, `Testing.ipynb`).
- `restbai/hackupc2023_restbai__dataset.zip` — Restbai property dataset (zipped, not auto-extracted).

## Build and Test
No `requirements.txt`. Install manually: `pip install PyQt5 gower numpy pandas requests`. Run from repo root so the `Tati` package resolves: `python pol/interface.py`. No automated tests.

## Pitfalls
- Hackathon code, frozen — expect rough edges, unused imports, and incomplete functions (e.g. `extract_features` returns `None`).
- PyQt5 needs a desktop Qt runtime; will not run headless / in CI without a virtual display.
- `pol/interface.py` uses `from Tati.HouseMatch import *`, so it must be launched from the repo root (not from inside `pol/`).
- Dataset ships as a zip in `restbai/`; extract before any data-loading code will work.

See [README.md](README.md) for full setup.
