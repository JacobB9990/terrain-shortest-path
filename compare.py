"""Compare terrain-routing payoff across areas -> plots/compare.png.

Usage: python3 compare.py
"""

import csv
import glob
import os

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import rasterio

import dem


def load_area(path):
    with open(path) as f:
        rows = [{k: float(v) for k, v in r.items()} for r in csv.DictReader(f)]

    col = {k: np.array([r[k] for r in rows]) for k in rows[0]}
    col["percent_time_saved"] = col["time_saved_min"] / col["shortest_time_min"] * 100
    col["gain_avoided_m"] = col["shortest_gain_m"] - col["terrain_gain_m"]

    return col


def relief_of(area):
    with rasterio.open(dem.ensure(area)) as src:
        elevation = src.read(1)

    return float(elevation.max() - elevation.min())


def main_cli():
    paths = sorted(glob.glob("results/*.csv"))
    areas = {os.path.basename(p)[:-4]: load_area(p) for p in paths}

    relief = {a: relief_of(a) for a in areas}
    order = sorted(areas, key=lambda a: relief[a])

    labels = [a.replace("_", " ").title() for a in order]
    pct = [areas[a]["percent_time_saved"] for a in order]
    reliefs = [relief[a] for a in order]
    mean_pct = [p.mean() for p in pct]

    os.makedirs("plots", exist_ok=True)
    fig, axes = plt.subplots(2, 2, figsize=(15, 11))

    # box plot of percent saved, areas ordered by relief
    axes[0][0].boxplot(pct, tick_labels=labels, showmeans=True)
    axes[0][0].set_ylabel("Time saved (%)")
    axes[0][0].set_title("Percent time saved by area (ordered by relief)")
    axes[0][0].tick_params(axis="x", rotation=30)
    axes[0][0].grid(alpha=0.3, axis="y")

    # relief vs mean percent saved
    r = np.corrcoef(reliefs, mean_pct)[0, 1]
    axes[0][1].scatter(reliefs, mean_pct, s=90)

    for x, y, label in zip(reliefs, mean_pct, labels):
        axes[0][1].annotate(
            label, (x, y), fontsize=8, xytext=(5, 5), textcoords="offset points"
        )

    slope, intercept = np.polyfit(reliefs, mean_pct, 1)
    line = np.array([min(reliefs), max(reliefs)])
    axes[0][1].plot(line, slope * line + intercept, color="crimson", linewidth=1.5)
    axes[0][1].set_xlabel("DEM relief (m)")
    axes[0][1].set_ylabel("Mean time saved (%)")
    axes[0][1].set_title(f"Relief vs mean payoff  (r = {r:.3f})")
    axes[0][1].grid(alpha=0.3)

    # pooled climb-avoided vs time-saved, colored by area
    for a, label in zip(order, labels):
        axes[1][0].scatter(
            areas[a]["gain_avoided_m"],
            areas[a]["time_saved_min"],
            s=14,
            alpha=0.6,
            label=label,
        )

    pooled_x = np.concatenate([areas[a]["gain_avoided_m"] for a in order])
    pooled_y = np.concatenate([areas[a]["time_saved_min"] for a in order])
    pooled_r = np.corrcoef(pooled_x, pooled_y)[0, 1]
    pooled_slope, pooled_intercept = np.polyfit(pooled_x, pooled_y, 1)
    line = np.array([pooled_x.min(), pooled_x.max()])
    axes[1][0].plot(
        line, pooled_slope * line + pooled_intercept, color="black", linewidth=1.5
    )
    axes[1][0].set_xlabel("Elevation gain avoided (m)")
    axes[1][0].set_ylabel("Time saved (min)")
    axes[1][0].set_title(
        f"Climb avoided vs time saved, all areas  (r = {pooled_r:.3f})"
    )
    axes[1][0].legend(fontsize=8)
    axes[1][0].grid(alpha=0.3)

    # detour cost paid per area
    detour_pct = [
        (areas[a]["terrain_dist_km"] - areas[a]["shortest_dist_km"])
        / areas[a]["shortest_dist_km"]
        * 100
        for a in order
    ]
    axes[1][1].bar(labels, [d.mean() for d in detour_pct], alpha=0.85)
    axes[1][1].set_ylabel("Extra distance walked (%)")
    axes[1][1].set_title("Detour cost paid for the time saved")
    axes[1][1].tick_params(axis="x", rotation=30)
    axes[1][1].grid(alpha=0.3, axis="y")

    n = sum(len(p) for p in pct)
    fig.suptitle(
        f"Terrain routing across {len(order)} areas, {n} experiments", fontsize=14
    )
    fig.tight_layout()
    fig.savefig("plots/compare.png", dpi=130, bbox_inches="tight")

    print(
        f"{'area':22s} {'relief':>8s} {'mean %':>8s} {'median %':>9s} "
        f"{'max %':>7s} {'detour %':>9s} {'m/min':>7s}"
    )

    for a, label, p, d in zip(order, labels, pct, detour_pct):
        s, _ = np.polyfit(areas[a]["gain_avoided_m"], areas[a]["time_saved_min"], 1)
        print(
            f"{label:22s} {relief[a]:7.0f}m {p.mean():7.1f}% {np.median(p):8.1f}% "
            f"{p.max():6.1f}% {d.mean():8.2f}% {1 / s:6.1f}"
        )

    print(f"\nrelief vs mean payoff      r = {r:.3f}")
    print(f"pooled climb vs time saved r = {pooled_r:.3f}")
    print(f"pooled rate: 1 min saved per {1 / pooled_slope:.1f} m of climb avoided")
    print("\nwrote plots/compare.png")


if __name__ == "__main__":
    main_cli()
