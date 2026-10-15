#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import dendrogram, leaves_list, linkage
from scipy.spatial.distance import jensenshannon, squareform

from rw_common import load_config, parse_rw_config, render_template, resolve_path

AXIS_LABEL_FONTSIZE = 16
TICK_LABEL_FONTSIZE = 14


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def resolve_input_path(project_root: Path, cfg: dict, top_k: int) -> Path:
    run_label = str(cfg.get("run", {}).get("label", "default"))
    candidate = (
        project_root
        / "core_pipeline"
        / "outputs"
        / "runs"
        / run_label
        / "09_aggregations"
        / f"top{top_k}"
        / f"motifs_by_start_comm_attention_top{top_k}.csv"
    )
    if candidate.exists():
        return candidate

    fallback = (
        project_root
        / "core_pipeline"
        / "outputs"
        / "runs"
        / "2prat"
        / "09_aggregations"
        / "top10"
        / "motifs_by_start_comm_attention_top10.csv"
    )
    return fallback


def upright_vertical_text(v: object) -> str:
    s = str(v)
    if len(s) > 1:
        return s
    return "\n".join(list(s))


def main() -> int:
    config_path = Path("core_pipeline/configs/config.yaml").resolve()
    if not config_path.exists():
        print(f"[ERROR] missing config: {config_path}")
        return 1

    cfg = load_config(config_path)
    project_root = config_path.parents[2]
    run_label = str(cfg.get("run", {}).get("label", "default"))
    rw_cfg = parse_rw_config(cfg)
    top_k = int(rw_cfg.get("top_k", 10))

    input_csv = resolve_input_path(project_root, cfg, top_k)
    if not input_csv.exists():
        print(f"[ERROR] input CSV not found: {input_csv}")
        return 1

    df = pd.read_csv(input_csv)
    motif_cols = [f"Motif {i}" for i in range(1, 9)]
    missing_cols = [c for c in (["start_comm"] + motif_cols) if c not in df.columns]
    if missing_cols:
        print(f"[ERROR] missing required columns: {missing_cols}")
        return 1

    start_comm = pd.to_numeric(df["start_comm"], errors="coerce")
    if start_comm.isna().any():
        print("[ERROR] start_comm contains non-numeric values.")
        return 1

    df = df.copy()
    df["start_comm"] = start_comm.astype(int)
    df = df.sort_values("start_comm", kind="mergesort").reset_index(drop=True)

    P = df[motif_cols].apply(pd.to_numeric, errors="coerce").fillna(0.0).astype(float)
    row_sums = P.sum(axis=1)
    if (row_sums <= 0).any():
        bad = int((row_sums <= 0).sum())
        print(f"[ERROR] found {bad} rows with non-positive motif mass.")
        return 1
    P = P.div(row_sums, axis=0)

    labels: List[int] = df["start_comm"].astype(int).tolist()
    n = len(labels)

    dist = np.zeros((n, n), dtype=np.float64)
    for i in range(n):
        pi = P.iloc[i].to_numpy(dtype=np.float64)
        for j in range(i + 1, n):
            pj = P.iloc[j].to_numpy(dtype=np.float64)
            d = float(jensenshannon(pi, pj, base=2.0))
            dist[i, j] = d
            dist[j, i] = d

    agg_dir = (
        project_root
        / "core_pipeline"
        / "outputs"
        / "runs"
        / run_label
        / "09_aggregations"
        / f"top{top_k}"
    )
    agg_dir.mkdir(parents=True, exist_ok=True)

    matrix_path = agg_dir / f"js_distance_matrix_attention_top{top_k}.csv"
    long_path = agg_dir / f"js_distance_long_attention_top{top_k}.csv"

    dist_df = pd.DataFrame(dist, index=labels, columns=labels)
    dist_df.to_csv(matrix_path, float_format="%.10f")

    long_rows = []
    for i, ci in enumerate(labels):
        for j, cj in enumerate(labels):
            long_rows.append({"comm_i": int(ci), "comm_j": int(cj), "jsd": float(dist[i, j])})
    pd.DataFrame(long_rows).to_csv(long_path, index=False, float_format="%.10f")

    condensed = squareform(dist, checks=False)
    Z = linkage(condensed, method="average")
    order_idx = leaves_list(Z).tolist()
    order_labels = [labels[i] for i in order_idx]
    ordered_dist = dist[np.ix_(order_idx, order_idx)]

    fig_dir = project_root / "core_pipeline" / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)
    dendro_path = fig_dir / f"js_dendrogram_attention_top{top_k}.png"
    heatmap_path = fig_dir / f"js_heatmap_attention_top{top_k}.png"

    fig, ax = plt.subplots(figsize=(9, 5), dpi=220)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    dendrogram(Z, labels=[str(x) for x in labels], leaf_rotation=0, ax=ax)
    dendro_xlabs = [tick.get_text() for tick in ax.get_xticklabels()]
    ax.set_xticklabels(
        [upright_vertical_text(x) for x in dendro_xlabs],
        rotation=0,
        fontsize=TICK_LABEL_FONTSIZE,
    )
    ax.tick_params(axis="y", labelsize=TICK_LABEL_FONTSIZE)
    ax.set_xlabel("starting community", fontsize=AXIS_LABEL_FONTSIZE)
    ax.set_ylabel("Jensen-Shannon distance", fontsize=AXIS_LABEL_FONTSIZE)
    fig.tight_layout()
    fig.savefig(dendro_path, facecolor="white", bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 6), dpi=220)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    im = ax.imshow(ordered_dist, cmap="viridis", interpolation="nearest", aspect="equal")
    ax.set_xticks(np.arange(n))
    ax.set_yticks(np.arange(n))
    ax.set_xticklabels(
        [upright_vertical_text(x) for x in order_labels],
        rotation=0,
        fontsize=TICK_LABEL_FONTSIZE,
    )
    ax.set_yticklabels([str(x) for x in order_labels], fontsize=TICK_LABEL_FONTSIZE)
    ax.set_xlabel("community (cluster order)", fontsize=AXIS_LABEL_FONTSIZE)
    ax.set_ylabel("community (cluster order)", fontsize=AXIS_LABEL_FONTSIZE)
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("Jensen-Shannon distance", fontsize=AXIS_LABEL_FONTSIZE)
    cbar.ax.tick_params(labelsize=TICK_LABEL_FONTSIZE)
    fig.tight_layout()
    fig.savefig(heatmap_path, facecolor="white", bbox_inches="tight")
    plt.close(fig)

    manifest = {
        "timestamp": now_utc(),
        "run_label": run_label,
        "input_path": str(input_csv),
        "distance_definition": "scipy.spatial.distance.jensenshannon, base=2 (distance)",
        "linkage_method": "average",
        "included_communities": [int(x) for x in labels],
        "cluster_order_communities": [int(x) for x in order_labels],
        "outputs": {
            "js_distance_matrix_csv": str(matrix_path),
            "js_distance_long_csv": str(long_path),
            "dendrogram_png": str(dendro_path),
            "heatmap_png": str(heatmap_path),
        },
    }
    manifest_path = agg_dir / f"js_motif_profiles_attention_top{top_k}_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    tri = dist[np.triu_indices(n, k=1)]
    min_jsd = float(np.min(tri)) if tri.size else 0.0
    max_jsd = float(np.max(tri)) if tri.size else 0.0

    print(f"n_communities={n}")
    print(f"jsd_min={min_jsd:.10f}")
    print(f"jsd_max={max_jsd:.10f}")
    print(f"cluster_order={order_labels}")
    print(f"[SAVE] {matrix_path}")
    print(f"[SAVE] {long_path}")
    print(f"[SAVE] {dendro_path}")
    print(f"[SAVE] {heatmap_path}")
    print(f"[SAVE] {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
