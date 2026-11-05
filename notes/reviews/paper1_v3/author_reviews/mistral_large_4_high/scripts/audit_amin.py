"""Independent check of Prop amin illustrative example (sections/appendix_proofs.tex, rem:amin-values)
and Prop amin(a) formula. Example: S=$1e9, one objective, N_o=24 opportunities/yr.
Human layer: p=0.05, cm=0.002, cost 500k/yr. AI layer on one provider: p=0.02, cm=0.005, cost 50k/yr,
ITGC cost 204,672/yr. p^cc=0. P_o(D) = p^cc + (1-p^cc) prod_j [p^cm_j + (1-p^cm_j) p_j^{n_j}].
pi = 1-(1-P)^N. Thresholds: pi_bar in {5%, 1%} per year (AminEpsCen, AminEpsSens)."""
import numpy as np, json, itertools
def P_o(p_j, pcm_j, n):
    pcc = 0.0
    prod = 1.0
    for p, pcm, nj in zip(p_j, pcm_j, n):
        if nj >= 1:
            prod *= (pcm + (1-pcm)*p**nj)
    return pcc + (1-pcc)*prod
def pi(P, N=24): return 1-(1-P)**N
# all-human designs
out = {}
for nh in range(0, 8):
    P = P_o([0.05],[0.002],[nh]) if nh>=1 else 1.0
    out[f'human_{nh}'] = dict(P=P, pi=pi(P), cost=nh*500_000)
print('all-human: pi at 0 layers:', pi(1.0))
for nh in range(1,4):
    P = P_o([0.05],[0.002],[nh]); print(f'human {nh}: P={P:.6f} pi={pi(P)*100:.4f}% cost=${out[f"human_{nh}"]["cost"]:,}')
# all-AI on one provider
for na in range(1, 6):
    P = P_o([0.02],[0.005],[na]); print(f'AI {na}: P={P:.6f} pi={pi(P)*100:.4f}% cost=${na*50_000+204_672:,}')
# mixed: n_h human + n_a ai
for bar in [0.05, 0.01]:
    Pbar = 1-(1-bar)**(1/24)
    adm = []
    for nh in range(0,4):
        for na in range(0,4):
            if nh+na==0: continue
            P = P_o([0.05,0.02],[0.002,0.005],[nh,na])
            cost = nh*500_000 + na*50_000 + (204_672 if na>=1 else 0)
            if P <= Pbar: adm.append((cost, nh, na, pi(P)))
    adm.sort()
    print(f'threshold {bar*100}%: Pbar={Pbar:.6f}; cheapest admissible: {adm[:3]}')
# paper claims: all-human leaves >= 1-0.998^24 ~ 4.7% (AminHumLim); 3 human layers pass at 5% "by a hair" (AminHumanProb); AI-only min pi = 1-0.995^24 ~ AminAiLim; cheapest at 5% = 1 human + 1 AI (AminCenProb, $AminCenCost); at 1% = 1 human + 2 AI.
print('1-0.998^24 =', 1-0.998**24)
print('1-0.995^24 =', 1-0.995**24)
P31 = P_o([0.05,0.02],[0.002,0.005],[3,0]); P11 = P_o([0.05,0.02],[0.002,0.005],[1,1]); P12 = P_o([0.05,0.02],[0.002,0.005],[1,2])
print('pi(3 human)=', pi(P31), 'pi(1h1a)=', pi(P11), 'pi(1h2a)=', pi(P12))
print('Pbar(5%)=', 1-(1-0.05)**(1/24), 'Pbar(1%)=', 1-(1-0.01)**(1/24))
# Prop amin(a) general formula sanity vs direct simulation
def sim(p_j, pcm_j, n, pcc, Nsim=200000, seed=1):
    rng = np.random.default_rng(seed)
    nj = len(n)
    miss = np.zeros(Nsim, bool)
    cc = rng.random(Nsim) < pcc
    for j in range(nj):
        if n[j] >= 1:
            cm = rng.random(Nsim) < pcm_j[j]
            ind = np.ones(Nsim, bool)
            for _ in range(n[j]):
                ind &= rng.random(Nsim) >= p_j[j]
            layer_miss = cm | ind
        else:
            layer_miss = np.ones(Nsim, bool)
        miss |= layer_miss
    miss = cc | miss
    return miss.mean()
for pcc in [0.0, 0.01]:
    est = sim([0.05,0.02],[0.002,0.005],[2,1],pcc)
    exact = P_o([0.05,0.02],[0.002,0.005],[2,1])*(1-pcc)+pcc
    print(f'sim vs exact P_o (pcc={pcc}): {est:.5f} vs {exact:.5f}')
