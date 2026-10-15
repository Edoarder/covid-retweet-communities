#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from rw_common import load_config, load_weighted_edgelist, render_template, resolve_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Plot non-cumulative log-log degree/strength distributions on global LWCC directed weighted network."
    )
    parser.add_argument("--config", default="core_pipeline/configs/config.yaml")
    return parser.parse_args()


def _build_log_bins(max_value: int) -> np.ndarray:
    if max_value <= 1:
        return np.array([1.0, 2.0], dtype=float)
    if max_value <= 2:
        return np.array([1.0, 2.0, 3.0], dtype=float)

    tail = np.logspace(np.log10(2.0), np.log10(float(max_value) + 1.0), num=30)
    edges = np.unique(np.concatenate([np.array([1.0, 2.0]), tail, np.array([float(max_value) + 1.0])]))
    edges = np.sort(edges)
    if edges.size < 2:
        edges = np.array([1.0, float(max_value) + 1.0], dtype=float)
    return edges


def _plot_distribution(
    values: pd.Series,
    title: str,
    x_label: str,
    out_path: Path,
) -> None:
    arr = pd.to_numeric(values, errors="coerce").fillna(0).to_numpy(dtype=np.int64)
    arr = arr[arr >= 0]

    zero_count = int(np.sum(arr == 0))
    positive = arr[arr > 0]
    max_val = int(np.max(arr)) if arr.size else 1
    bar_color = "#4C72B0"

    fig, ax = plt.subplots(figsize=(8, 5), dpi=220)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    # Zero-count bar shown separately at x=0.8 so it is visible on log-scale x-axis.
    if zero_count > 0:
        ax.bar(
            [0.8],
            [zero_count],
            width=0.14,
            color=bar_color,
            alpha=0.85,
            edgecolor="black",
            linewidth=0.4,
        )

    if positive.size > 0:
        bins = _build_log_bins(int(np.max(positive)))
        counts, edges = np.histogram(positive, bins=bins)
        centers = np.sqrt(edges[:-1] * edges[1:])
        widths = (edges[1:] - edges[:-1]) * 0.95
        mask = counts > 0
        if np.any(mask):
            ax.bar(
                centers[mask],
                counts[mask],
                width=widths[mask],
                align="center",
                color=bar_color,
                alpha=0.85,
                edgecolor="black",
                linewidth=0.4,
            )

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(left=0.7)
    ax.set_xlabel(x_label)
    ax.set_ylabel("Number of nodes")
    ax.set_title(title)

    tick_vals = [0.8, 1.0]
    tick_lbls = ["0", "1"]
    if max_val >= 10:
        pmin = 1
        pmax = int(np.floor(np.log10(max_val)))
        for p in range(pmin, pmax + 1):
            v = float(10 ** p)
            if v not in tick_vals:
                tick_vals.append(v)
                tick_lbls.append(str(int(v)))
    ax.set_xticks(tick_vals)
    ax.set_xticklabels(tick_lbls)

    fig.tight_layout()
    fig.savefig(out_path, dpi=300, facecolor="white", bbox_inches="tight")
    plt.close(fig)


def main() -> int:
    args = parse_args()
    config_path = Path(args.config).expanduser().resolve()
    if not config_path.exists():
        print(f"[ERROR] missing config: {config_path}")
        return 1

    cfg = load_config(config_path)
    project_root = config_path.parents[2]

    run_label = str(cfg.get("run", {}).get("label", "default"))
    variant = str(cfg.get("community", {}).get("main_variant", "")).strip()
    paths_cfg = cfg.get("paths", {}) if isinstance(cfg.get("paths", {}), dict) else {}

    lwcc_raw = str(
        paths_cfg.get(
            "edgelist_weighted_lwcc_csv",
            "core_pipeline/outputs/runs/{run.label}/01_data/edgelist_weighted_lwcc.csv",
        )
    )
    lwcc_path = resolve_path(project_root, render_template(lwcc_raw, run_label, variant))
    if not lwcc_path.exists():
        print(f"[ERROR] LWCC weighted edgelist not found: {lwcc_path}")
        return 1

    df = load_weighted_edgelist(lwcc_path)
    if df.empty:
        print(f"[ERROR] empty LWCC weighted edgelist: {lwcc_path}")
        return 1

    nodes = pd.Index(sorted(set(df["source"]).union(set(df["target"]))), dtype="object")

    edge_pairs = df[["source", "target"]].drop_duplicates()

    out_degree = edge_pairs.groupby("source").size().reindex(nodes, fill_value=0).astype(np.int64)
    in_degree = edge_pairs.groupby("target").size().reindex(nodes, fill_value=0).astype(np.int64)

    out_strength = df.groupby("source")["weight"].sum().reindex(nodes, fill_value=0).astype(np.int64)
    in_strength = df.groupby("target")["weight"].sum().reindex(nodes, fill_value=0).astype(np.int64)

    n_nodes = int(len(nodes))
    zero_in_degree = int((in_degree == 0).sum())
    zero_out_degree = int((out_degree == 0).sum())

    out_dir = project_root / "core_pipeline" / "figures" / "global_distributions"
    out_dir.mkdir(parents=True, exist_ok=True)

    files: Dict[str, Path] = {
        "in_degree": out_dir / "lwcc_in_degree_distribution.png",
        "out_degree": out_dir / "lwcc_out_degree_distribution.png",
        "in_strength": out_dir / "lwcc_in_strength_distribution.png",
        "out_strength": out_dir / "lwcc_out_strength_distribution.png",
    }

    _plot_distribution(
        values=in_degree,
        title="LWCC In-Degree Distribution (Directed Global Retweet Network)",
        x_label="Degree",
        out_path=files["in_degree"],
    )
    _plot_distribution(
        values=out_degree,
        title="LWCC Out-Degree Distribution (Directed Global Retweet Network)",
        x_label="Degree",
        out_path=files["out_degree"],
    )
    _plot_distribution(
        values=in_strength,
        title="LWCC In-Strength Distribution (Directed Global Retweet Network)",
        x_label="Strength",
        out_path=files["in_strength"],
    )
    _plot_distribution(
        values=out_strength,
        title="LWCC Out-Strength Distribution (Directed Global Retweet Network)",
        x_label="Strength",
        out_path=files["out_strength"],
    )

    print(f"lwcc_nodes={n_nodes}")
    print(f"max_in_degree={int(in_degree.max())}")
    print(f"max_out_degree={int(out_degree.max())}")
    print(f"max_in_strength={int(in_strength.max())}")
    print(f"max_out_strength={int(out_strength.max())}")
    print(f"zero_in_degree_nodes={zero_in_degree}")
    print(f"zero_out_degree_nodes={zero_out_degree}")
    print("saved_figures:")
    for p in files.values():
        print(str(p.resolve()))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
