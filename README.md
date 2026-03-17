# HackUPC 2023

Hackathon project from HackUPC 2023 — a house preference matching application that helps users find their ideal property using similarity-based comparison.

## Overview

The app presents the user with property images through a PyQt5 interface and uses Gower distance to compute similarity between houses based on multiple attributes, matching user preferences to available listings.

## Structure

```
├── pol/
│   ├── interface.py          # PyQt5 GUI (ImageChooser interface)
│   └── obsolete/             # Earlier interface versions
├── Tati/
│   └── HouseMatch.py         # Gower distance-based house matching
└── Pablesky/
    ├── Untitled.ipynb         # Exploratory notebook
    └── Testing.ipynb          # Testing notebook
```

## Tech Stack

- **Python** with PyQt5, NumPy, pandas
- **Gower** distance for mixed-type similarity
- **Jupyter Notebooks** for prototyping
