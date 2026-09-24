"""Run N random start/end experiments per area, comparing the terrain-aware
route to the shortest-distance route. Writes results/<area>.csv per area.

Usage: python3 experiments.py [--areas a,b] [--n 100] [--seed 0]
"""

import argparse
import csv
import math
import os
import random
from concurrent.futures import ProcessPoolExecutor

import dem
import main

# fraction of the grid diagonal a start/end pair must span, so routes are
# comparably long relative to each DEM instead of a fixed cell count
MIN_SEPARATION_FRAC = 0.25

FIELDS = [
    "run",
    "start_row",
    "start_col",
    "end_row",
    "end_col",
    "terrain_cells",
    "terrain_dist_km",
    "terrain_time_min",
    "terrain_gain_m",
    "terrain_loss_m",
    "shortest_cells",
    "shortest_dist_km",
    "shortest_time_min",
    "shortest_gain_m",
    "shortest_loss_m",
    "extra_dist_m",
    "time_saved_min",
]


def random_pairs(n, seed, shape):
    rows, cols = shape
    min_separation = MIN_SEPARATION_FRAC * math.hypot(rows, cols)

    rng = random.Random(seed)
    pairs = []

    while len(pairs) < n:
        start = (rng.randrange(rows), rng.randrange(cols))
        end = (rng.randrange(rows), rng.randrange(cols))

        if math.dist(start, end) >= min_separation:
            pairs.append((start, end))

    return pairs


def run_one(args):
    run, start, end = args

    _, terrain_parents = main.compute_dijkstra(start, end, main.get_terrain_cost)
    terrain_path = main.reconstruct_path(terrain_parents, start, end)

    _, distance_parents = main.compute_dijkstra(start, end, main.get_distance_cost)
    distance_path = main.reconstruct_path(distance_parents, start, end)

    if not terrain_path or not distance_path:
        return None

    terrain_gain, terrain_loss = main.elevation_stats(terrain_path)
    shortest_gain, shortest_loss = main.elevation_stats(distance_path)

    terrain_dist = main.total_path_distance(terrain_path)
    shortest_dist = main.total_path_distance(distance_path)
    terrain_time = main.total_path_time(terrain_path) * 60
    shortest_time = main.total_path_time(distance_path) * 60

    return {
        "run": run,
        "start_row": start[0],
        "start_col": start[1],
        "end_row": end[0],
        "end_col": end[1],
        "terrain_cells": len(terrain_path),
        "terrain_dist_km": terrain_dist / 1000,
        "terrain_time_min": terrain_time,
        "terrain_gain_m": float(terrain_gain),
        "terrain_loss_m": float(terrain_loss),
        "shortest_cells": len(distance_path),
        "shortest_dist_km": shortest_dist / 1000,
        "shortest_time_min": shortest_time,
        "shortest_gain_m": float(shortest_gain),
        "shortest_loss_m": float(shortest_loss),
        "extra_dist_m": terrain_dist - shortest_dist,
        "time_saved_min": shortest_time - terrain_time,
    }


def check(rows, area):
    """Dijkstra invariants: each route must be optimal under its own cost."""
    for r in rows:
        assert r["time_saved_min"] >= -1e-6, f"{area} run {r['run']}: terrain slower"
        assert r["extra_dist_m"] >= -1e-6, f"{area} run {r['run']}: distance longer"


def mean(rows, key):
    return sum(r[key] for r in rows) / len(rows)


def run_area(area, n, seed, outdir="results"):
    path = dem.ensure(area)
    elevation = main.load_dem(path)

    jobs = [
        (i + 1, s, e)
        for i, (s, e) in enumerate(random_pairs(n, seed, elevation.shape))
    ]

    # each worker loads the same DEM into its own globals (spawn start method)
    with ProcessPoolExecutor(initializer=main.load_dem, initargs=(path,)) as pool:
        rows = [r for r in pool.map(run_one, jobs) if r]

    check(rows, area)

    os.makedirs(outdir, exist_ok=True)

    with open(f"{outdir}/{area}.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    relief = float(elevation.max() - elevation.min())
    pct = [r["time_saved_min"] / r["shortest_time_min"] * 100 for r in rows]

    print(
        f"{area:22s} {str(elevation.shape):14s} relief {relief:6.0f} m  "
        f"saved {mean(rows, 'time_saved_min'):6.1f} min "
        f"({sum(pct) / len(pct):4.1f}%)  "
        f"detour {mean(rows, 'extra_dist_m'):5.0f} m  "
        f"climb {mean(rows, 'shortest_gain_m'):5.0f}->{mean(rows, 'terrain_gain_m'):4.0f} m"
    )

    return rows


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--areas", default="", help="comma-separated, default all")
    parser.add_argument("--n", type=int, default=100)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    areas = args.areas.split(",") if args.areas else dem.all_areas()

    print(f"{args.n} experiments per area, seed {args.seed}, "
          f"pairs >= {MIN_SEPARATION_FRAC:.0%} of grid diagonal apart\n")

    for area in areas:
        run_area(area, args.n, args.seed)

    print("\nwrote results/<area>.csv")
