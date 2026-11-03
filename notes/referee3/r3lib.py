"""Referee 3 helper library: fast numpy versions of the paper's frontier estimators plus alternatives."""
import numpy as np
import pandas as pd

BASE = '/home/claude/paper'
PERIODS = ['2010-15', '2016-19', '2020-22', '2023-25']
GRID = np.round(np.arange(0.0, 1.01, 0.05), 2)


def load():
    return pd.read_csv(f'{BASE}/data/panel.csv')


def order_alpha(gv, mv, alpha=0.95, min_n=30, grid=GRID):
    out = np.full(len(grid), np.nan)
    for k, g0 in enumerate(grid):
        s = mv[gv >= g0]
        if len(s) >= min_n:
            out[k] = np.quantile(s, alpha)
    return out


def frontier_score(gv, mv, alpha=0.95, min_n=30, grid=GRID):
    phi = order_alpha(gv, mv, alpha, min_n, grid)
    v = grid + phi
    if np.all(np.isnan(v)):
        return np.nan, np.nan, np.nan
    k = int(np.nanargmax(v))
    edge = float(grid[~np.isnan(phi)].max())
    return float(v[k]), float(grid[k]), edge


def fixed_threshold_score(gv, mv, g0, alpha=0.95):
    s = mv[gv >= g0]
    return g0 + np.quantile(s, alpha) if len(s) else np.nan


def top_share_score(gv, mv, share=0.05, alpha=0.95):
    """Edge defined by a fixed share of the period's firm-years (sample-size invariant)."""
    g0 = np.quantile(gv, 1 - share)
    s = mv[gv >= g0]
    return g0 + np.quantile(s, alpha)


def cluster_index(cik):
    firms, inv = np.unique(cik, return_inverse=True)
    idx = [np.where(inv == j)[0] for j in range(len(firms))]
    return idx


def cluster_draw(idx, rng):
    draw = rng.integers(0, len(idx), size=len(idx))
    return np.concatenate([idx[j] for j in draw])


def boot(d, stat, B=500, seed=1, cols=None):
    """Firm-cluster percentile bootstrap of stat(sub_df)."""
    rng = np.random.default_rng(seed)
    idx = cluster_index(d['cik'].values)
    vals = []
    for _ in range(B):
        ii = cluster_draw(idx, rng)
        vals.append(stat(d.iloc[ii]))
    return np.array(vals, dtype=float)


def ci(a, lo=0.05, hi=0.95):
    return float(np.nanquantile(a, lo)), float(np.nanquantile(a, hi))
