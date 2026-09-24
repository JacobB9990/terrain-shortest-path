"""Run N random start/end experiments comparing the terrain-aware route to the
shortest-distance route. Writes results to experiments.csv and prints a summary.

Usage: python3 experiments.py [n] [seed]
"""

import csv
import math
import random
import sys
from concurrent.futures import ProcessPoolExecutor

import main

ROWS, COLS = main.elevation.shape
MIN_SEPARATION = 150  # cells, so each pair is a route worth comparing

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


def random_pairs(n, seed):
    rng = random.Random(seed)
    pairs = []

    while len(pairs) < n:
        start = (rng.randrange(ROWS), rng.randrange(COLS))
        end = (rng.randrange(ROWS), rng.randrange(COLS))

        if math.dist(start, end) >= MIN_SEPARATION:
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


def check(rows):
    """Dijkstra invariants: each route must be optimal under its own cost."""
    for r in rows:
        assert r["time_saved_min"] >= -1e-6, f"run {r['run']}: terrain route slower"
        assert r["extra_dist_m"] >= -1e-6, f"run {r['run']}: distance route longer"


def mean(rows, key):
    return sum(r[key] for r in rows) / len(rows)


def main_cli():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 0

    jobs = [(i + 1, s, e) for i, (s, e) in enumerate(random_pairs(n, seed))]

    with ProcessPoolExecutor() as pool:
        rows = [r for r in pool.map(run_one, jobs) if r]

    check(rows)

    with open("experiments.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    saved = [r["time_saved_min"] for r in rows]
    detour = [r["extra_dist_m"] for r in rows]

    print(f"\n--- {len(rows)} EXPERIMENTS (seed {seed}) ---")
    print(f"pairs kept at >= {MIN_SEPARATION} cells straight-line separation")
    print(f"mean shortest-route distance:  {mean(rows, 'shortest_dist_km'):.2f} km")
    print(f"mean terrain-route distance:   {mean(rows, 'terrain_dist_km'):.2f} km")
    print(f"mean detour:                   {mean(rows, 'extra_dist_m'):.0f} m")
    print(f"mean shortest-route time:      {mean(rows, 'shortest_time_min'):.1f} min")
    print(f"mean terrain-route time:       {mean(rows, 'terrain_time_min'):.1f} min")
    print(f"mean time saved:               {mean(rows, 'time_saved_min'):.1f} min")
    print(f"median time saved:             {sorted(saved)[len(saved) // 2]:.1f} min")
    print(f"max time saved:                {max(saved):.1f} min")
    print(f"min time saved:                {min(saved):.1f} min")
    print(f"max detour:                    {max(detour):.0f} m")
    print(f"mean elevation gain, terrain:  {mean(rows, 'terrain_gain_m'):.0f} m")
    print(f"mean elevation gain, shortest: {mean(rows, 'shortest_gain_m'):.0f} m")
    print("\nwrote experiments.csv")


if __name__ == "__main__":
    main_cli()
