# HackUPC 2023 House Match

This restored HackUPC 2023 desktop demo learns a house preference profile from
pairwise choices, then ranks the next comparisons by mixed-feature similarity.

## Run the demo

Use Python 3.10 through 3.13. Python 3.12 is provided by the devcontainer and
Python 3.13 is covered by the desktop test suite.

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python -m house_match.interface
```

On macOS or Linux, replace `.venv\Scripts\python` with `.venv/bin/python`.
The root-level launch command reads the 100-listing sample JSON directly from
`restbai/hackupc2023_restbai__dataset.zip`; do not extract the approximately
1.36 GB full dataset. Listing images are optional live HTTP downloads. A
timeout, invalid response, or unavailable URL produces an in-application
fallback instead of stopping the comparison.

## Recommendation policy

Each listing has five categorical features: city, neighborhood, region, image
style, and property type. It also has eight numerical features: price, area,
bedrooms, bathrooms, and four visual scores for the property, kitchen,
bathroom, and interior.

Missing categorical values become `Unknown`. Missing numerical values use the
sample median for that feature, then every numerical feature is min-max
normalized to `[0, 1]`; constant features map to `0.5`. Similarity uses an
equal-weight Gower-style distance: categorical values contribute `0` when they
match and `1` otherwise, while normalized numerical values contribute their
absolute difference. A vote adds the chosen listing to the preference profile
and presents the closest unused pair that does not contain either listing from
the preceding comparison when enough candidates remain.

The `house_match/` package contains the supported recommendation core, image
loader, and desktop interface, and performs no work at import. The notebooks
in `notebooks/` and assets and interface under `legacy/` are historical
hackathon artifacts and are not part of the supported demo.

## Test

```powershell
$env:QT_QPA_PLATFORM = "offscreen"
.venv\Scripts\python -m unittest -v
```

The tests are hermetic: dataset fixtures use temporary ZIPs, HTTP is replaced
with local doubles, and the GUI runs offscreen.

## Desktop smoke test

1. Launch `.venv\Scripts\python -m house_match.interface` from the repository
   root.
2. Confirm two different houses show details and either an image or a visible
   image-unavailable message.
3. For a house with multiple images, use **Previous image** and **Next image**
   and confirm the displayed image changes.
4. Vote for either house at least three times. Confirm the vote count advances
   and each vote presents two different houses without immediately reusing the
   preceding pair.
