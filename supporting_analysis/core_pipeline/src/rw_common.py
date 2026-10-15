#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional, Tuple

import numpy as np
import pandas as pd
import scipy.sparse as sp

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

try:
    import igraph as ig
except ImportError:  # pragma: no cover
    ig = None


def load_config(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if yaml is not None:
        data = yaml.safe_load(text)
    else:
        data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("Config must be a mapping.")
    return data


def resolve_path(project_root: Path, value: str) -> Path:
    p = Path(value).expanduser()
    if p.is_absolute():
        return p
    return project_root / p


def render_template(value: str, run_label: str, variant: str = "") -> str:
    out = str(value).replace("{run.label}", run_label)
    out = out.replace("{variant}", variant)
    return out


def normalize_id(value: object) -> str:
    if value is None:
        return ""
    s = str(value).strip()
    if s in {"", "<NA>", "nan", "NaN", "None"}:
        return ""
    if s.endswith(".0"):
        s = s[:-2]
    return s


def parse_bool(value: object, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    return str(value).strip().lower() in {"1", "true", "t", "yes", "y"}


def detect_edge_cols(columns: Iterable[str]) -> Tuple[str, str]:
    cols = list(columns)
    colset = set(cols)
    preferred = (
        ("source", "target"),
        ("source_id_str", "target_id_str"),
        ("user_id_str", "retweet_author_id"),
        ("verified", "unverified"),
    )
    for a, b in preferred:
        if a in colset and b in colset:
            return a, b
    if len(cols) < 2:
        raise ValueError("Edgelist must contain at least two columns.")
    return cols[0], cols[1]


def load_weighted_edgelist(
    path: Path,
    source_col: str = "",
    target_col: str = "",
    weight_col: str = "weight",
) -> pd.DataFrame:
    header = pd.read_csv(path, nrows=0)
    columns = header.columns.tolist()

    if source_col and target_col and source_col in columns and target_col in columns:
        src_col, tgt_col = source_col, target_col
    else:
        src_col, tgt_col = detect_edge_cols(columns)

    usecols = [src_col, tgt_col]
    if weight_col in columns:
        usecols.append(weight_col)
    elif "weight" in columns and "weight" not in usecols:
        usecols.append("weight")

    df = pd.read_csv(path, usecols=usecols, dtype=str)
    df["source"] = df[src_col].map(normalize_id)
    df["target"] = df[tgt_col].map(normalize_id)

    active_weight_col = weight_col if weight_col in df.columns else ("weight" if "weight" in df.columns else "")
    if active_weight_col:
        df["weight"] = pd.to_numeric(df[active_weight_col], errors="coerce").fillna(0).astype("int64")
    else:
        df["weight"] = 1

    df = df[(df["source"] != "") & (df["target"] != "") & (df["weight"] > 0)].copy()
    return df[["source", "target", "weight"]]


def compute_lwcc_nodes_from_weighted(df_weighted: pd.DataFrame) -> List[str]:
    if ig is None:
        raise RuntimeError("igraph is required to compute LWCC from weighted edgelist.")
    vertices = sorted(set(df_weighted["source"]).union(set(df_weighted["target"])))
    idx = {v: i for i, v in enumerate(vertices)}
    edges = [(idx[s], idx[t]) for s, t in df_weighted[["source", "target"]].itertuples(index=False, name=None)]
    g = ig.Graph(n=len(vertices), directed=True)
    g.vs["name"] = vertices
    g.add_edges(edges)
    giant = g.components(mode="weak").giant()
    return sorted(str(v) for v in giant.vs["name"])


def ensure_lwcc_weighted_edgelist(
    full_weighted_path: Path,
    lwcc_weighted_path: Path,
    source_col: str = "",
    target_col: str = "",
    weight_col: str = "weight",
    lwcc_nodes_hint_path: Optional[Path] = None,
) -> Tuple[pd.DataFrame, Path]:
    if lwcc_weighted_path.exists():
        df = load_weighted_edgelist(
            lwcc_weighted_path,
            source_col=source_col,
            target_col=target_col,
            weight_col=weight_col,
        )
        return df, lwcc_weighted_path

    full_df = load_weighted_edgelist(
        full_weighted_path,
        source_col=source_col,
        target_col=target_col,
        weight_col=weight_col,
    )

    if lwcc_nodes_hint_path is not None and lwcc_nodes_hint_path.exists():
        hint = pd.read_csv(lwcc_nodes_hint_path, dtype=str)
        col = hint.columns[0]
        lwcc_nodes = sorted(hint[col].map(normalize_id).dropna().astype(str).tolist())
    else:
        lwcc_nodes = compute_lwcc_nodes_from_weighted(full_df)

    lwcc_set = set(lwcc_nodes)
    lwcc_df = full_df[full_df["source"].isin(lwcc_set) & full_df["target"].isin(lwcc_set)].copy()
    lwcc_df = lwcc_df.sort_values(["source", "target"], kind="mergesort").reset_index(drop=True)
    lwcc_weighted_path.parent.mkdir(parents=True, exist_ok=True)
    lwcc_df.to_csv(lwcc_weighted_path, index=False)
    return lwcc_df, lwcc_weighted_path


def file_hash_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def file_fingerprint(path: Path) -> Dict[str, object]:
    stat = path.stat()
    return {
        "path": str(path),
        "size_bytes": int(stat.st_size),
        "mtime": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
        "sha256": file_hash_sha256(path),
    }


def is_sparse(A) -> bool:
    return sp.issparse(A)


def as_float64_dense(A):
    return np.array(A, dtype=np.float64, copy=True)


def sum_axis(A, axis: int):
    if is_sparse(A):
        return np.asarray(A.sum(axis=axis)).ravel().astype(np.float64, copy=False)
    return np.sum(A, axis=axis, dtype=np.float64)


def to_csr_float64(A):
    if is_sparse(A):
        if hasattr(A, "asfptype"):
            A = A.asfptype()
        else:
            A = A.astype(np.float64)
        return A.tocsr()
    return sp.csr_matrix(A, dtype=np.float64)


def normalize_transition_matrix(F):
    if is_sparse(F):
        F = to_csr_float64(F)
        Dim, Col = F.shape
    else:
        F = as_float64_dense(F)
        Dim, Col = F.shape
    if Dim != Col:
        raise ValueError("F must be square")

    sout = sum_axis(F, axis=1)
    sin = sum_axis(F, axis=0)
    Norm = sout + np.maximum(sin - sout, 0.0)

    if is_sparse(F):
        scales = np.divide(1.0, Norm, out=np.zeros_like(Norm), where=(Norm != 0))
        D = sp.diags(scales, offsets=0, format="csr")
        M = (D @ F).tocsr()
    else:
        M = F.copy()
        mask = Norm != 0
        M[mask, :] = M[mask, :] / Norm[mask][:, None]
        M[~mask, :] = 0.0
    return M, Norm


def _triple_sum(M):
    if is_sparse(M):
        Mcsr = M.tocsr()
        MM = Mcsr.multiply(Mcsr)
        MT = Mcsr.transpose().tocsr()
        return MM.multiply(MT).sum()
    return np.sum(M * M * M.T, dtype=np.float64)


def theo_prob(W):
    """
    Legacy theoretical motif probabilities (Motif 1..8), matching script_0index_correct.py.
    Returns a float64 numpy array of length 8.
    """
    if is_sparse(W):
        W = to_csr_float64(W)
        Dim, Col = W.shape
    else:
        W = as_float64_dense(W)
        Dim, Col = W.shape
    if Dim != Col:
        raise ValueError("W must be square")

    M, _ = normalize_transition_matrix(W)

    sout = sum_axis(W, axis=1)
    sin = sum_axis(W, axis=0)
    sin = np.nan_to_num(sin, nan=0.0)

    temp = sin - sout
    temp = (temp > 0).astype(np.float64) * temp
    sink = np.divide(temp, sin, out=np.zeros_like(sin), where=(sin != 0))
    sink = np.nan_to_num(sink, nan=0.0)

    if is_sparse(M):
        M2 = (M @ M).tocsr()
        M3 = (M2 @ M).tocsr()
    else:
        M2 = M @ M
        M3 = M2 @ M

    P = np.zeros(8, dtype=np.float64)

    v1 = M @ sink
    P[0] = v1.sum() / Dim

    diagM2 = M2.diagonal() if is_sparse(M2) else np.diag(M2)
    P[1] = np.dot(diagM2, sink) / Dim

    v2 = M2 @ sink
    P[2] = v2.sum() / Dim - P[1]

    triple = _triple_sum(M)
    P[3] = triple / Dim

    diagM3 = M3.diagonal() if is_sparse(M3) else np.diag(M3)
    P[4] = diagM3.sum() / Dim

    row_sums_M = sum_axis(M, axis=1)
    col_sums_M = sum_axis(M, axis=0)
    P[5] = (np.dot(diagM2, row_sums_M) - triple) / Dim
    P[6] = (np.dot(diagM2, col_sums_M) - triple) / Dim

    total_M3 = M3.sum() if is_sparse(M3) else np.sum(M3, dtype=np.float64)
    offdiag_sum = total_M3 - diagM3.sum()
    P[7] = offdiag_sum / Dim - P[3] - P[5] - P[6]

    return P


def _build_row_cdfs(M_csr):
    M_csr = M_csr.tocsr()
    indptr = M_csr.indptr
    indices = M_csr.indices
    data = M_csr.data

    cdf = np.empty_like(data, dtype=np.float64)
    Dim = M_csr.shape[0]
    for i in range(Dim):
        s, e = indptr[i], indptr[i + 1]
        if e > s:
            np.cumsum(data[s:e], out=cdf[s:e])
    return cdf, indptr, indices


def _choose_from_row_cdf(i_row0: int, u: float, cdf, indptr, indices, Dim: int) -> int:
    s, e = indptr[i_row0], indptr[i_row0 + 1]
    if e <= s:
        return Dim
    last = cdf[e - 1]
    if u > last:
        return Dim
    off = np.searchsorted(cdf[s:e], u, side="right")
    return int(indices[s + off])


def _sample_uniform_starts(Dim: int, Iter: int, rng: np.random.Generator, batch_size: int = 200_000) -> Iterator[np.ndarray]:
    remaining = Iter
    while remaining > 0:
        b = min(batch_size, remaining)
        remaining -= b
        yield rng.integers(0, Dim, size=b, dtype=np.int32)


def generate_paths_uniform_stream(
    F,
    Iter: int,
    Num: int,
    seed: int,
    batch_size: int = 200_000,
    discard_immediate_sink: bool = True,
) -> Iterator[Tuple[np.ndarray, int]]:
    if not is_sparse(F):
        F = sp.csr_matrix(F, dtype=np.float64)

    M, _ = normalize_transition_matrix(F)
    M = M.tocsr()
    Dim = M.shape[0]
    SINK = Dim
    cdf, indptr, indices = _build_row_cdfs(M)
    rng = np.random.default_rng(seed)

    for starts in _sample_uniform_starts(Dim, Iter, rng, batch_size=batch_size):
        b = len(starts)
        paths = np.empty((b, Num + 1), dtype=np.int32)
        paths[:, 0] = starts
        alive = np.ones(b, dtype=bool)

        for j in range(1, Num + 1):
            idx = np.where(alive)[0]
            if idx.size == 0:
                paths[:, j:] = SINK
                break

            u = rng.random(idx.size)
            nxt = np.empty(idx.size, dtype=np.int32)
            for k, r in enumerate(idx):
                i0 = int(paths[r, j - 1])
                nxt[k] = _choose_from_row_cdf(i0, u[k], cdf, indptr, indices, Dim)
            paths[idx, j] = nxt
            alive[idx] = nxt != SINK
            dead = ~alive
            if np.any(dead):
                paths[dead, j] = SINK

        sink_counts = np.sum(paths[:, 1:] == SINK, axis=1)
        immediate_sink = sink_counts == Num
        discarded = int(np.sum(immediate_sink))

        if discard_immediate_sink:
            yield paths[~immediate_sink], discarded
        else:
            yield paths, 0


def classify_paths(Paths: np.ndarray, Dim: int) -> np.ndarray:
    sink = Dim
    n, C = Paths.shape
    motifs = np.zeros(n, dtype=np.int32)

    if C == 3:
        t = (Paths == sink).sum(axis=1)
        motifs[t == 1] = 1
        keep = t != 1
        motifs[keep & (Paths[:, 0] == Paths[:, 2])] = 2
        motifs[keep & (Paths[:, 0] != Paths[:, 2])] = 3
        return motifs

    t = (Paths == sink).sum(axis=1)
    motifs[t == (C - 2)] = 1

    mask2 = t == (C - 3)
    motifs[mask2 & (Paths[:, 0] == Paths[:, 2])] = 2
    motifs[mask2 & (Paths[:, 0] != Paths[:, 2])] = 3

    mask3 = motifs == 0
    if np.any(mask3):
        P3 = Paths[mask3]
        idx = np.where(mask3)[0]

        m4 = (P3[:, 1] == P3[:, 3]) & (P3[:, 0] == P3[:, 2])
        motifs[idx[m4]] = 4

        keep = ~m4
        P5 = P3[keep]
        idx5 = idx[keep]
        m5 = P5[:, 0] == P5[:, 3]
        motifs[idx5[m5]] = 5

        keep2 = ~m5
        P6 = P5[keep2]
        idx6 = idx5[keep2]
        m6 = (P6[:, 0] == P6[:, 2]) & (P6[:, 1] != P6[:, 3])
        motifs[idx6[m6]] = 6

        keep3 = ~m6
        P7 = P6[keep3]
        idx7 = idx6[keep3]
        m7 = (P7[:, 1] == P7[:, 3]) & (P7[:, 0] != P7[:, 2])
        motifs[idx7[m7]] = 7
        motifs[idx7[~m7]] = 8

    return motifs


def build_rw_matrix(
    weighted_lwcc_df: pd.DataFrame,
    node_to_comm: Dict[str, int],
    reverse_edges: bool,
) -> Tuple[sp.csr_matrix, List[str], np.ndarray, int]:
    df = weighted_lwcc_df.copy()
    if reverse_edges:
        df[["source", "target"]] = df[["target", "source"]]

    nodes = sorted(set(df["source"]).union(set(df["target"])))
    idx = {node: i for i, node in enumerate(nodes)}

    rows = df["source"].map(idx).astype(int).to_numpy()
    cols = df["target"].map(idx).astype(int).to_numpy()
    data = df["weight"].astype(np.int64).to_numpy()

    Dim = len(nodes)
    W = sp.coo_matrix((data, (rows, cols)), shape=(Dim, Dim), dtype=np.int64).tocsr()
    W.setdiag(0)
    W.eliminate_zeros()

    missing_comm = 0
    comm_arr = np.full(Dim + 1, "", dtype=object)
    for i, node in enumerate(nodes):
        comm = node_to_comm.get(node)
        if comm is None:
            missing_comm += 1
            comm_arr[i] = ""
        else:
            comm_arr[i] = str(int(comm))
    comm_arr[Dim] = "-1"

    return W, nodes, comm_arr, missing_comm


def parse_rw_config(cfg: dict) -> Dict[str, object]:
    rw = cfg.get("random_walk", {}) if isinstance(cfg.get("random_walk", {}), dict) else {}
    return {
        "L": int(rw.get("L", 3)),
        "n_trials": int(rw.get("n_trials", 100000)),
        "seed_base": int(rw.get("seed_base", 123)),
        "discard_immediate_sink": parse_bool(rw.get("discard_immediate_sink", True), True),
        "include_sink": parse_bool(rw.get("include_sink", True), True),
        "weight_col": str(rw.get("weight_col", "weight")),
        "source_col": str(rw.get("source_col", "")),
        "target_col": str(rw.get("target_col", "")),
        "top_k": int(rw.get("top_k", 10)),
        "rw_inputs_dir": str(rw.get("rw_inputs_dir", "outputs/runs/{run.label}/07_rw_inputs/top10/")),
        "out_dir": str(rw.get("out_dir", "outputs/runs/{run.label}/08_random_walks/top10/")),
    }


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()
