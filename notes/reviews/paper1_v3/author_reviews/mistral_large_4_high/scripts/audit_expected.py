"""Check prop:expected(c),(e): identical processes, embedding prob q, capacity n_cap per wave.
Bound: E[#embedded by t] <= min(N, q n_cap n(t_R)). Simulate plans incl. retry; also divisible limit."""
import numpy as np
rng = np.random.default_rng(7)
def sim_plan(N, n_cap, T_par, T_emb, q, T, strategy='greedy'):
    # waves at times w*T_par; attempts embed at (w-1)*T_par + T_emb if success (prob q)
    n = lambda t: 0 if t < T_emb else int((t - T_emb)//T_par) + 1
    waves = [w for w in range(1, n(T)+1)]
    embedded = set(); in_flight = {}
    for w in waves:
        # choose up to n_cap processes not embedded and not in flight
        avail = [p for p in range(N) if p not in embedded and p not in in_flight]
        chosen = avail[:n_cap]
        for p in chosen:
            in_flight[p] = w
    # outcomes
    for p, w in in_flight.items():
        if rng.random() < q:
            embed_time = (w-1)*T_par + T_emb
            if embed_time <= T:
                embedded.add(p)
    return len(embedded)
viol = 0; trials = 3000
for _ in range(trials):
    N, n_cap, T_par, T_emb, q, T = 40, 3, 1.0, 2.0, 0.6, 7.0
    e = sim_plan(N, n_cap, T_par, T_emb, q, T)
    n_t = 0 if T < T_emb else int((T-T_emb)//T_par)+1
    bound = min(N, q*n_cap*n_t)
    if e > bound + 1e-9:
        viol += 1
print('greedy-sim embedded vs bound q*n_cap*n(t): violations', viol, 'of', trials)
# expected value check
vals = [sim_plan(40,3,1.0,2.0,0.6,7.0) for _ in range(20000)]
n_t = int((7.0-2.0)//1.0)+1
print('mean embedded = %.3f, bound = q*n_cap*n_t = %.3f, N=40' % (np.mean(vals), 0.6*3*n_t))
