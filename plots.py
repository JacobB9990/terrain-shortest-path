"""Re-run the most interesting experiments per area and save route plots.

Picks one run per "interesting" criterion from results/<area>.csv, recomputes
both routes, and writes plots/<area>/run<N>_{map,profile}.png.

Usage: python3 plots.py [--areas a,b]
"""

import argparse
import csv
import os

import matplotlib

matplotlib.use("Agg")

import dem
import main

# what makes a run worth looking at
CRITERIA = {
    "max absolute saving": lambda r: r["time_saved_min"],
    "max relative saving": lambda r: r["shortest_time_min"] / r["terrain_time_min"],
    "max detour": lambda r: r["extra_dist_m"],
    "max climb avoided": lambda r: r["shortest_gain_m"] - r["terrain_gain_m"],
    "cheapest detour": lambda r: r["time_saved_min"] / max(r["extra_dist_m"], 1),
}


def load(path):
    with open(path) as f:
        return [{k: float(v) for k, v in row.items()} for row in csv.DictReader(f)]


def pick(rows):
    """One winner per criterion, deduped, keeping the reason it was picked."""
    picked = {}

    for label, key in CRITERIA.items():
        run = int(max(rows, key=key)["run"])
        picked.setdefault(run, []).append(label)

    return picked


def plot_run(row, labels, outdir):
    start = (int(row["start_row"]), int(row["start_col"]))
    end = (int(row["end_row"]), int(row["end_col"]))
    run = int(row["run"])

    _, terrain_parents = main.compute_dijkstra(start, end, main.get_terrain_cost)
    terrain_path = main.reconstruct_path(terrain_parents, start, end)

    _, distance_parents = main.compute_dijkstra(start, end, main.get_distance_cost)
    distance_path = main.reconstruct_path(distance_parents, start, end)

    main.plot_comparison(
        terrain_path, distance_path, start, end, save=f"{outdir}/run{run}_map.png"
    )
    main.plot_elevation_profiles(
        terrain_path, distance_path, save=f"{outdir}/run{run}_profile.png"
    )

    print(
        f"  run {run:3d}  {', '.join(labels)}\n"
        f"           {start} -> {end}\n"
        f"           terrain  {row['terrain_dist_km']:5.2f} km  "
        f"{row['terrain_time_min']:6.1f} min  +{row['terrain_gain_m']:.0f} m climb\n"
        f"           shortest {row['shortest_dist_km']:5.2f} km  "
        f"{row['shortest_time_min']:6.1f} min  +{row['shortest_gain_m']:.0f} m climb\n"
        f"           saved {row['time_saved_min']:.1f} min "
        f"({row['time_saved_min'] / row['shortest_time_min'] * 100:.0f}%) for "
        f"{row['extra_dist_m']:.0f} m extra\n"
    )


def plot_area(area):
    csv_path = f"results/{area}.csv"

    if not os.path.exists(csv_path):
        print(f"{area}: no {csv_path}, skipping\n")
        return

    main.load_dem(dem.ensure(area))

    outdir = f"plots/{area}"
    os.makedirs(outdir, exist_ok=True)

    rows = load(csv_path)
    by_run = {int(r["run"]): r for r in rows}

    print(f"{area}")

    for run, labels in pick(rows).items():
        plot_run(by_run[run], labels, outdir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--areas", default="", help="comma-separated, default all")
    args = parser.parse_args()

    for area in args.areas.split(",") if args.areas else dem.all_areas():
        plot_area(area)

    print("wrote plots/<area>/run<N>_{map,profile}.png")
