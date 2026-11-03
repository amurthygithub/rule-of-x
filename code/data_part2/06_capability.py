"""Capability path H(t) = H0 * 2^((t - t0)/T_d) refitted from METR Time Horizon 1.1 run data.

Source: github.com/METR/eval-analysis-public (reports/time-horizon-1-1/data/raw/runs.jsonl, release dates in
data/external/release_dates.yaml). Method follows METR's code in that repository:
- per agent, weighted logistic regression of score_binarized on log2(human_minutes), weights invsqrt_task_weight
  (1 / (runs in task * sqrt(tasks in family)), normalised), sklearn LogisticRegression with C = 1/1e-5;
- p-horizon h_p = 2^((logit(p) - intercept)/coef) minutes;
- SOTA agents = agents whose p50 is >= every p50 released on or before their date; trend = OLS of ln(p50) on date;
- doubling time T_d = ln 2 / slope (days). 95% CI by cluster bootstrap over task families (B draws; METR's own
  bootstrap is hierarchical over families, tasks and runs, so CIs differ slightly).
Also reports the logistic slope, which converts a 50% horizon into a horizon at reliability r:
  h_r / h_50 = 2^(-logit(r)/|coef|), the chi(r) of spec Section 6, and the cost of agent runs relative to human
  baseline cost where METR recorded generation cost.
"""
import sys
sys.path.insert(0, '/home/claude/paper/code/data_part2')
import json
import numpy as np
import pandas as pd
import yaml
from sklearn.linear_model import LogisticRegression
from common import METR, write_csv, save_meta

B = 200
rng = np.random.default_rng(20261029)
runs = pd.read_json(f'{METR}/reports/time-horizon-1-1/data/raw/runs.jsonl', lines=True)
dates = yaml.safe_load(open(f'{METR}/data/external/release_dates.yaml'))['date']
runs = runs[runs.alias != 'human'].copy()


def weights(df):
    n_run = df.groupby('task_id').run_id.transform('count')
    fam = df.groupby('task_family').task_id.transform('nunique')
    w = 1 / (n_run * np.sqrt(fam))
    return (w / w.sum()).values


def fit(df):
    x = np.log2(df.human_minutes.values).reshape(-1, 1)
    y = df.score_binarized.values.astype(float)
    if y.min() == y.max():
        return np.nan, np.nan
    m = LogisticRegression(C=1 / 1e-5, max_iter=1000).fit(x, y, sample_weight=weights(df))
    return float(m.coef_[0][0]), float(m.intercept_[0])


def horizon(coef, icpt, p):
    return 2 ** ((np.log(p / (1 - p)) - icpt) / coef)


def sota(tab):
    t = tab.sort_values('release_date')
    out, best = [], -np.inf
    for d, g in t.groupby('release_date', sort=True):
        best = max(best, g.p50.max())
        out += g.loc[g.p50 >= best, 'agent'].tolist()
    return out


def trend(tab, after):
    t = tab[(tab.release_date >= pd.Timestamp(after)) & tab.agent.isin(sota(tab[tab.release_date >= pd.Timestamp(after)]))]
    t = t[np.isfinite(t.p50) & (t.p50 > 1e-3)]
    x = (t.release_date - pd.Timestamp('2019-01-01')).dt.days.values
    b, a = np.polyfit(x, np.log(t.p50.values), 1)
    return np.log(2) / b, a, b, t.agent.tolist()


def table(df):
    rows = []
    for ag, g in df.groupby('alias'):
        c, i = fit(g)
        rows.append(dict(agent=ag, release_date=pd.Timestamp(dates[ag]), coef=c, intercept=i,
                         p50=horizon(c, i, .5), p80=horizon(c, i, .8), n_runs=len(g)))
    return pd.DataFrame(rows)


tab = table(runs)
periods = {'2019-01-01': None, '2023-01-01': None, '2024-01-01': None}
res = {}
for after in periods:
    td, a, b, ag = trend(tab, after)
    res[after] = dict(doubling_days=td, sota_agents=ag, ln_p50_at_2019=a, slope_per_day=b)

# cluster bootstrap over task families
fams = runs.task_family.unique()
boot = {k: [] for k in periods}
for _ in range(B):
    pick = rng.choice(fams, size=len(fams), replace=True)
    parts = [runs[runs.task_family == f].assign(task_family=f'{f}#{j}', task_id=lambda d, j=j: d.task_id + f'#{j}')
             for j, f in enumerate(pick)]
    tb = table(pd.concat(parts, ignore_index=True))
    for after in periods:
        try:
            boot[after].append(trend(tb, after)[0])
        except Exception:
            pass
for after in periods:
    v = np.array([x for x in boot[after] if np.isfinite(x) and x > 0])
    res[after].update(ci95=[float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))], n_boot=int(len(v)),
                      median_boot=float(np.median(v)))

# frontier point (latest SOTA agent) and reliability conversion
s = tab[tab.agent.isin(sota(tab))].sort_values('release_date')
front = s.iloc[-1]
recent = tab[tab.release_date >= pd.Timestamp('2025-01-01')]
slope_med = float(np.median(np.abs(recent.coef)))
chi = {str(r): float(2 ** (np.log(r / (1 - r)) / slope_med)) for r in [0.5, 0.8, 0.9, 0.95, 0.99, 0.999]}

# cost of AI runs relative to human baseline (only runs with recorded generation cost)
c = runs[(runs.generation_cost > 0) & (runs.human_cost > 0) & (runs.score_binarized == 1)]
cost_ratio = dict(n_runs=int(len(c)), agents=sorted(c.alias.unique().tolist()),
                  median_ratio=float((c.generation_cost / c.human_cost).median()) if len(c) else None,
                  p90_ratio=float((c.generation_cost / c.human_cost).quantile(.9)) if len(c) else None,
                  human_cost_per_hour_median=float((runs.human_cost / (runs.human_minutes / 60)).median()))

# Time Horizon 1.0 run data (covers 2019-2025 models) for comparison with the published 207-day estimate
r10 = pd.read_json(f'{METR}/reports/time-horizon-1-0/data/raw/runs.jsonl', lines=True)
r10 = r10[(r10.alias != 'human') & r10.alias.isin(dates.keys())]
tab10 = table(r10)
th10 = {after: dict(zip(['doubling_days', 'ln_p50_at_2019', 'slope_per_day', 'sota_agents'], trend(tab10, after)))
        for after in ['2019-01-01', '2024-01-01']}

out = tab.assign(p50_hours=tab.p50 / 60, p80_hours=tab.p80 / 60, is_sota=tab.agent.isin(sota(tab)).astype(int))
write_csv(out.sort_values('release_date'), 'capability_metr_th11.csv')
meta = dict(source='METR eval-analysis-public, reports/time-horizon-1-1 (commit in source log)', n_runs=int(len(runs)),
            trend=res, frontier=dict(agent=front.agent, release_date=str(front.release_date.date()),
                                     p50_hours=float(front.p50 / 60), p80_hours=float(front.p80 / 60)),
            logistic_slope_median_2025plus=slope_med, chi_reliability_factor=chi, cost=cost_ratio, bootstrap_draws=B,
            th10_point_estimates=th10, th10_n_runs=int(len(r10)))
save_meta('capability', meta)
print(json.dumps(meta, indent=1, default=float)[:3000])
