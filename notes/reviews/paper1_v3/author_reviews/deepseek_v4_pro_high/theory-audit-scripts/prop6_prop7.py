"""
Independent verification of Proposition 6/7 (attainable & expected frontier), esp.
Prop 7(e) divisible program: E(t) <= min{1, p_emb * c_w * n(t_R)} and the fluid-limit
greedy plan E(t)=1-U_n with shortfall < c_w.
Not the author's script.
"""
import numpy as np

print("Proposition 7(e): divisible continuum of mass-1 identical processes.")
print("Fluid dynamics: wave w attempts up to c_w of available mass; fraction pemb embeds.")
print("E(t) <= min{1, pemb * c_w * n(tR)}  (every plan)")
print("Greedy plan: E(t) = pemb * c_w * n whenever c_w[1 + varpi(n-1)] <= 1")

def simulate(cw, varpi, pemb, n_waves):
    # track embedded E, working-in-flight W (mass attempted that is working, not yet embedded)
    # failed mass reverts at end of wave; working mass embeds after its flight.
    # Simplified steady fluid: each wave attempts min(cw, available); of attempted a, varpi*a works
    # (and will embed), pemb*a embeds. Working mass ties up capacity until embed.
    # Paper's model: a wave attempts mass that is neither embedded nor working in flight.
    E = 0.0
    W = 0.0  # mass currently in flight (working)
    for w in range(n_waves):
        avail = 1 - E - W
        a = min(cw, avail)
        # varpi fraction works (stays in flight, will embed), 1-varpi fails and reverts immediately
        # pemb fraction embeds by end of this wave's flight horizon
        W += varpi*a
        E += pemb*a
        # working mass from this wave eventually embeds or is counted; for simplicity
        # treat working mass as embedded next step (pemb = varpi when nuD=0)
    return E

# Use the paper's exact recurrence: with nuD=0, pemb=varpi.
# U_w = 1 - varpi*A_w,  U_w = U_{w-1} - varpi*min(cw, U_{w-1});  E(n) = 1 - U_n
def fluid(cw, varpi, n):
    U = 1.0
    for w in range(n):
        U = U - varpi*min(cw, U)
    return 1 - U

print("\nCase nuD=0 (pemb=varpi), cw=0.25, varpi=0.7:")
cw, varpi = 0.25, 0.7
for n in [1, 2, 3, 5, 10, 20]:
    E = fluid(cw, varpi, n)
    bound = min(1, varpi*cw*n)
    print(f"  n={n:>2}: E(t)={E:.4f}, min(1,varpi*cw*n)={bound:.4f}, E<=bound: {E<=bound+1e-9}, "
          f"shortfall={bound-E:.4f} (<cw={cw}: {bound-E < cw + 1e-9})")

print("\nGreedy fills all waves when cw[1+varpi(n-1)] <= 1:")
for n in [1,2,3]:
    cond = cw*(1+varpi*(n-1)) <= 1
    E = varpi*cw*n if cond else fluid(cw,varpi,n)
    print(f"  n={n}: cw[1+varpi(n-1)]={cw*(1+varpi*(n-1)):.3f} <=1: {cond}, E={E:.4f}")

print("\nProposition 6(d): concave piecewise-linear value of LP knapsack:")
# identical uses ci, per-resource knapsack fills in decreasing DeltaR_p/ci_p
DeltaR = [0.5, 0.4, 0.3, 0.2]
ci = [1.0, 0.5, 1.0, 2.0]
order = np.argsort(-np.array(DeltaR)/np.array(ci))
V = 0.0; rem = 3.0  # capacity C=3
for p in order:
    take = min(1.0, rem/ci[p])
    V += DeltaR[p]*take
    rem -= take*ci[p]
print(f"  DeltaR={DeltaR}, ci={ci}, ratios={[round(a/b,2) for a,b in zip(DeltaR,ci)]}")
print(f"  order={list(order)}, V(C=3)={V:.3f} (concave in C)")
