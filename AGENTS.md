# hackupc2023

HackUPC 2023 house-preference demo. The supported PyQt5 app learns from
pairwise choices and ranks listings with a mixed categorical/numerical
distance.

## Architecture

- `pol/interface.py`: desktop entry point and asynchronous image presentation.
- `pol/image_loader.py`: bounded HTTP image loading with validation and safe
	errors.
- `Tati/recommender.py`: side-effect-free sample loading, feature processing,
	ranking, and pair progression.
- `Tati/HouseMatch.py`: compatibility exports for the recommendation core.
- `restbai/hackupc2023_restbai__dataset.zip`: tracked sample and full Restbai
	property data; supported code reads only the nested sample member.
- `Pablesky/` and `pol/obsolete/`: historical artifacts, outside the supported
	runtime.

## Build and test

Use Python 3.10 through 3.13; the devcontainer supplies Python 3.12.

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
$env:QT_QPA_PLATFORM = "offscreen"
.venv\Scripts\python -m unittest -v
.venv\Scripts\python -m pol.interface
```

Tests must remain hermetic: use temporary archives, injected HTTP doubles, and
the Qt offscreen platform. Recommendation imports must never write files,
access the network, or execute the demo.

## Scope

The original hackathon material is frozen unless the user explicitly
authorizes an issue. Keep authorized work narrowly scoped, preserve the
pairwise desktop concept, and do not rewrite exploratory notebooks.
