import json, numpy as np
from scipy import stats
J = json.load(open('/home/claude/paper/notes/empirics_organic.json'))
H = J['headline']
rows = []
for k, v in H.items():
    if 'E1_minus_E2' not in v: continue
    if k in ('weight_lo', 'weight_hi'): continue            # deterministic transforms of spend_ratio
    d = v['E1_minus_E2']; se = d['se']; est = d['est']; lo, hi = d['ci90']
    z = est / se if se else np.nan; p = 2 * (1 - stats.norm.cdf(abs(z)))
    rows.append((k, est, se, lo, hi, (lo > 0) or (hi < 0), p))
rows.sort(key=lambda r: r[-1])
m = len(rows)
print('paired E1-E2 statistics in the headline block:', m, '; 90% intervals excluding zero:', sum(r[5] for r in rows))
print('binomial P(at least that many | 10% each, independent):', 1 - stats.binom.cdf(sum(r[5] for r in rows) - 1, m, 0.10))
# Holm and Benjamini-Hochberg on normal-approximation p-values
ps = np.array([r[-1] for r in rows])
holm = np.minimum.accumulate(np.maximum.accumulate((m - np.arange(m)) * ps)[::-1])[::-1]
holm = np.maximum.accumulate(np.minimum(1, (m - np.arange(m)) * ps))
bh = np.minimum.accumulate((ps * m / (np.arange(m) + 1))[::-1])[::-1]
for r, h, b in zip(rows, holm, bh):
    print('%-26s est %+.4f se %.4f ci90 [%+.4f, %+.4f] excl0=%d p=%.3f holm=%.3f bh=%.3f' % (r[0], r[1], r[2], r[3], r[4], r[5], r[6], h, b))
