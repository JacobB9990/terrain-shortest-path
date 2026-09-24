# Three Presentations on Geographical Analysis and Modeling: Non- Isotropic Geographic Modeling; Speculations on the Geometry of Geography; and Global Spatial Analysis (93-1)
## Tobler, Waldo

Read the [Report](Report.md).

Shortest-path routing over real terrain, comparing a Tobler hiking-function
cost against plain distance across six areas of the northeast US.

## Running it

```bash
pip install -r requirements.txt
python3 main.py
```

DEMs are not in the repo (~32 MB). Any script downloads the one it needs on
first use via `py3dep`, so there is no setup step — `python3 dem.py` pre-fetches
all six if you would rather wait once.

| command | what it does |
| --- | --- |
| `python3 main.py` | route one pair, show the map and elevation profiles |
| `python3 experiments.py` | 100 random pairs per area → `results/<area>.csv` |
| `python3 plots.py` | map + profile for the standout runs → `plots/<area>/` |
| `python3 analysis.py [csv]` | within-area relationships → `plots/analysis_<area>.png` |
| `python3 compare.py` | across-area comparison → `plots/compare.png` |
| `python3 view.py` | raw DEM preview |

`experiments.py` takes `--areas`, `--n` and `--seed`; it runs the pairs in
parallel across cores and asserts each route is optimal under its own cost.

## Areas

`ricketts_glen`, `delaware_water_gap`, `lehigh_gorge`, `catskills`,
`adirondacks`, `mount_washington` — bounding boxes in `dem.py`.