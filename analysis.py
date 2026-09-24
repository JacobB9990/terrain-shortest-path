"""Cross-experiment plots over experiments.csv -> plots/analysis.png.

Usage: python3 analysis.py
"""

import csv
import os

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np


def load(path="experiments.csv"):
    with open(path) as f:
        rows = [{k: float(v) for k, v in r.items()} for r in csv.DictReader(f)]

    col = {k: np.array([r[k] for r in rows]) for k in rows[0]}

    col["gain_avoided_m"] = col["shortest_gain_m"] - col["terrain_gain_m"]
    col["percent_time_saved"] = col["time_saved_min"] / col["shortest_time_min"] * 100

    return col


def scatter(ax, x, y, xlabel, ylabel, title, fit=True):
    r = np.corrcoef(x, y)[0, 1]

    ax.scatter(x, y, s=22, alpha=0.7, edgecolor="none")

    if fit:
        slope, intercept = np.polyfit(x, y, 1)
        line = np.array([x.min(), x.max()])
        ax.plot(line, slope * line + intercept, linewidth=1.5, color="crimson")

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(f"{title}  (r = {r:.3f})")
    ax.grid(alpha=0.3)

    return r


def main_cli():
    col = load()
    os.makedirs("plots", exist_ok=True)

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    scatter(
        axes[0][0],
        col["gain_avoided_m"],
        col["time_saved_min"],
        "Elevation gain avoided (m)",
        "Time saved (min)",
        "Climb avoided vs time saved",
    )

    scatter(
        axes[0][1],
        col["extra_dist_m"],
        col["time_saved_min"],
        "Extra distance walked (m)",
        "Time saved (min)",
        "Detour length vs time saved",
    )

    pct = col["percent_time_saved"]
    axes[1][0].hist(pct, bins=20, edgecolor="white")
    axes[1][0].axvline(
        pct.mean(), color="crimson", linestyle="--", label=f"mean {pct.mean():.1f}%"
    )
    axes[1][0].axvline(
        np.median(pct),
        color="darkorange",
        linestyle=":",
        label=f"median {np.median(pct):.1f}%",
    )
    axes[1][0].set_xlabel("Time saved (%)")
    axes[1][0].set_ylabel("Experiments")
    axes[1][0].set_title("Distribution of percent time saved")
    axes[1][0].legend()
    axes[1][0].grid(alpha=0.3)

    scatter(
        axes[1][1],
        col["shortest_dist_km"],
        pct,
        "Shortest-route distance (km)",
        "Time saved (%)",
        "Route length vs percent time saved",
    )

    fig.suptitle(
        f"Terrain-aware vs shortest-distance routing, {len(pct)} random pairs",
        fontsize=14,
    )
    fig.tight_layout()
    fig.savefig("plots/analysis.png", dpi=130, bbox_inches="tight")

    def r_of(a, b):
        return np.corrcoef(col[a], b)[0, 1]

    slope, _ = np.polyfit(col["gain_avoided_m"], col["time_saved_min"], 1)

    print(f"gain_avoided  vs time_saved   r = {r_of('gain_avoided_m', col['time_saved_min']):.3f}")
    print(f"extra_dist    vs time_saved   r = {r_of('extra_dist_m', col['time_saved_min']):.3f}")
    print(f"shortest_dist vs percent      r = {r_of('shortest_dist_km', pct):.3f}")
    print(f"\nfit: 1 minute saved per {1 / slope:.1f} m of climb avoided")
    print(f"percent saved: mean {pct.mean():.1f}%  median {np.median(pct):.1f}%  range {pct.min():.1f}-{pct.max():.1f}%")
    print("\nwrote plots/analysis.png")


if __name__ == "__main__":
    main_cli()
