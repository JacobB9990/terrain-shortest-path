"""Where the DEMs live, and fetching them when they aren't on disk.

The .tif files are gitignored (~32 MB), so a fresh clone has none. Anything
that needs one calls ensure(area) and gets a path back, downloading first if
required.

Usage: python3 dem.py [area ...]   # pre-fetch, default all
"""

import os
import sys

# (west, south, east, north) in EPSG:4326
AREAS = {
    "ricketts_glen": (-76.36, 41.27, -76.20, 41.40),
    "delaware_water_gap": (-75.25, 40.90, -75.05, 41.05),
    "lehigh_gorge": (-75.85, 40.82, -75.60, 41.00),
    "catskills": (-74.35, 42.05, -74.10, 42.22),
    "adirondacks": (-73.95, 44.05, -73.65, 44.25),
    "mount_washington": (-71.42, 44.20, -71.15, 44.38),
}

RESOLUTION = 30

# absolute, so scripts work from any working directory
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def all_areas():
    return list(AREAS)


def path(area):
    return os.path.join(DATA_DIR, f"{area}_dem.tif")


def download(area):
    import py3dep  # only needed the first time, keeps startup cheap

    os.makedirs(DATA_DIR, exist_ok=True)
    target = path(area)

    print(f"downloading {area} DEM ({RESOLUTION} m)...", flush=True)

    py3dep.get_dem(AREAS[area], resolution=RESOLUTION, crs=4326).rio.to_raster(target)

    print(f"saved {target}", flush=True)

    return target


def ensure(area):
    """Path to this area's DEM, downloading it if missing."""
    if area not in AREAS:
        raise KeyError(f"unknown area {area!r}; known: {', '.join(AREAS)}")

    target = path(area)

    return target if os.path.exists(target) else download(area)


if __name__ == "__main__":
    for area in sys.argv[1:] or all_areas():
        ensure(area)
