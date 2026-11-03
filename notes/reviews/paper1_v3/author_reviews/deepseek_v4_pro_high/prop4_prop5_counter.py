"""
Independent verification of Proposition 4 (Cournot free entry) and Proposition 5 (accountability floor),
plus counterexample stress-tests: k<0 frontier, X<=k corner, Prop 1 with Gi<G (Remark S1(b)).
Not the author's script.
"""
import numpy as np

print("="*70)
print("PROPOSITION 4: Cournot free entry")
print("="*70)
A, B, G, r = 2.0, 1.0, 0.05, 0.10
u, ku, ac = 0.4, 0.5, 0.6
chat = u + r*(ku+ac)          # full unit cost
print(f"chat = u + r(ku+ac) = {u} + {r}*({ku}+{ac}) = {chat:.4f}")

# (a) n-firm symmetric equilibrium
for n in [1, 2, 3]:
    Pn = (A + n*chat)/(n+1)
    xn_flow = (A-chat)/(B*(n+1))          # output flow coefficient (before e^{Gt})
    pin = (A-chat)**2/(B*(n+1)**2)        # flow profit coefficient
    Ln = (Pn-chat)/Pn
    kn, kan = ku/Pn, ac/Pn
    mop = Ln + r*kn + (r-G)*kan
    m = (r-G)*(kn+kan) + Ln
    print(f"  n={n}: P={Pn:.4f}, pi_n={pin:.4f}, Lerner={Ln:.4f}, "
          f"mop={mop:.4f}, FCF m={m:.4f}, score R_X (X=1)={G+m:.4f}")

# (b) free entry: n* = floor(NF)-1
for F in [0.1, 0.02, 0.001, 1e-5]:
    Fhat = (r-G)*F
    NF = (A-chat)/np.sqrt(B*Fhat)
    nstar = int(np.floor(NF))-1
    Ln = (A-chat)/(A + nstar*chat)
    Pn = (A + nstar*chat)/(nstar+1)
    score = G + (r-G)*(ku+ac)/Pn + Ln
    print(f"  F={F:>7}: NF={NF:.2f}, n*={nstar}, L={Ln:.4f}, P={Pn:.4f}, "
          f"RX->XG+(r-G)(ku+ac)/chat = {G+(r-G)*(ku+ac)/chat:.4f} (limit)")

print(f"\n  F->0 limit score = XG + (r-G)(ku+ac)/chat = {G + (r-G)*(ku+ac)/chat:.4f}")
print(f"  For X=1: G(1-khat)+r*khat with khat=(ku+ac)/chat = {G*(1-(ku+ac)/chat)+r*(ku+ac)/chat:.4f}")

# (c) scarce input
Z = 0.2   # must satisfy Z < (A-chat)/(2B) = (2-0.5)/2 = 0.75
print(f"\n  Scarce input Z={Z}, check Z < (A-chat)/(2B)={(A-chat)/(2*B):.3f}: {Z < (A-chat)/(2*B)}")
P = A - B*Z
for n in [1, 2, 3]:
    wn = A - chat - B*Z*(n+1)/n
    Lnet = B*Z/(n*P)
    rhon = wn/P
    k, ka = ku/P, ac/P
    owner_mop = r*k + (r-G)*ka + rhon + Lnet
    buyer_mop = r*k + (r-G)*ka + Lnet
    print(f"    n={n}: w={wn:.4f}, P={P:.4f}, rho={rhon:.4f}, Lnet={Lnet:.4f}, "
          f"owner mop={owner_mop:.4f}, buyer mop={buyer_mop:.4f}")
rho_lim = 1 - chat/(A-B*Z)
print(f"    F->0 limit rho = 1 - chat/(A-BZ) = {rho_lim:.4f}")
print(f"    owner limit score = XG+(r-G)(k+ka)+rho = {G+(r-G)*(ku+ac)/P + rho_lim:.4f}")

# (d) full-cost bound
cc_, f_, amin_, cfull_ = 0.05, 0.02, 0.03, 0.06
# u/P >= cc+f+amin+cfull needed
print(f"\n  (d) full-cost: u/P={u/P:.4f} vs cc+f+amin+cfull={cc_+f_+amin_+cfull_:.4f}")
rho_bound = 1 - cc_ - f_ - amin_ - cfull_ - r*(k+ka)
print(f"  rho <= 1-cc-f-amin-cfull-r(k+ka) = {rho_bound:.4f}")
print(f"  owner score <= 1-cc-f-amin-cfull + XG - G(k+ka) = "
      f"{1-cc_-f_-amin_-cfull_ + G - G*(ku+ac)/P:.4f}")

print()
print("="*70)
print("PROPOSITION 5: accountability floor probability")
print("="*70)
pcc = 0.02
# two types: people (j=1) and AI on provider A (j=2)
pcm = {1: 0.10, 2: 0.20}
p   = {1: 0.05, 2: 0.08}
def Po(n):
    return pcc + (1-pcc)*np.prod([pcm[j] + (1-pcm[j])*p[j]**n[j] for j in n])

for design in [{1:1,2:0}, {1:2,2:0}, {1:0,2:1}, {1:0,2:3}, {1:0,2:100}, {1:1,2:1}]:
    Pv = Po(design)
    print(f"  design {design}: Po(D) = {Pv:.5f}")

# admissibility: pi_o <= pibar  <=>  Po <= 1-(1-pibar)^(1/No)
No, pibar = 100, 0.05
Pbar = 1 - (1-pibar)**(1/No)
print(f"\n  No={No}, pibar={pibar}: Pbar = 1-(1-pibar)^(1/No) = {Pbar:.5f}")
print(f"  pi_o = 1-(1-Po)^No ;  check equivalence Po<=Pbar <=> pi_o<=pibar:")
for Pv in [0.0003, Pbar, 0.001]:
    pio = 1-(1-Pv)**No
    print(f"    Po={Pv:.5f}: pi_o={pio:.5f}, Po<=Pbar={Pv<=Pbar}, pi_o<=pibar={pio<=pibar}")

# all-AI single provider inadmissible when pcc + (1-pcc)pcm_j >= Pbar
j = 2
floor = pcc + (1-pcc)*pcm[j]
print(f"\n  all-AI provider {j}: pcc+(1-pcc)pcm_j = {floor:.5f} vs Pbar={Pbar:.5f}")
print(f"  inadmissible if floor >= Pbar: {floor >= Pbar}")
# depth does not help: Po -> floor from above
for depth in [1, 2, 10, 1000]:
    Pv = pcc + (1-pcc)*(pcm[j] + (1-pcm[j])*p[j]**depth)
    print(f"    depth={depth}: Po={Pv:.8f} (limit {floor:.8f})")

print()
print("="*70)
print("COUNTEREXAMPLE / STRESS TESTS")
print("="*70)
# (ii) Lemma 2 with X <= k: corner solution
print("\n(ii) X <= k corner: y=X-k <= 0 -> S(Delta)=y*Delta - kappa Delta^beta <= 0 = S(0)")
m0_, G_, k_, alpha_, ell_ = 0.4, 0.1, 0.3, 0.3, 0.5
for X_ in [0.2, 0.3, 0.31]:
    y_ = X_ - k_
    Ds = np.linspace(0, 2, 100000)
    S_ = y_*Ds - ell_**(-1/alpha_)*Ds**(1/alpha_)
    i = np.argmax(S_)
    print(f"  X={X_}: y={y_:.2f}, argmax Delta*={Ds[i]:.5f} (expect 0 if X<=k, interior if X>k), "
          f"max S={S_[i]:.5f}")

# (iv) k < 0 (deferred revenue): concavity survives, monotonicity fails
print("\n(iv) k < 0 frontier: m*(g)=m0 - k g - kappa(g-G)^beta")
for k_ in [0.0, -0.3]:
    m0_, G_, alpha_, ell_ = 0.4, 0.1, 0.3, 0.5
    beta_ = 1/alpha_
    kappa_ = ell_**(-beta_)
    Ds = np.linspace(0, 1.0, 100000)
    mstar = m0_ - k_*(G_+Ds) - kappa_*Ds**beta_
    # slope and curvature
    d1 = -k_ - beta_*kappa_*Ds**(beta_-1)
    d2 = -beta_*(beta_-1)*kappa_*Ds**(beta_-2)
    # Delta0 where slope = 0 (for k<0)
    if k_ < 0:
        Delta0 = ((-k_)/(beta_*kappa_))**(1/(beta_-1))
    else:
        Delta0 = 0.0
    # is m* increasing near G for k<0?
    increasing_near_G = d1[100] > 0
    print(f"  k={k_}: m*'(g) near G = {d1[100]:+.4f} (increasing near G: {increasing_near_G}), "
          f"Delta0={Delta0:.4f}")
    print(f"     m*''(g) for g>G all negative (strictly concave)? {np.all(d2[100:] < 0)}")
    # dominance: for k<0, point (G, m*(G)) is dominated by (G+Delta0, m*(G+Delta0))
    if k_ < 0:
        mG = m0_ - k_*G_ - kappa_*0
        mD0 = m0_ - k_*(G_+Delta0) - kappa_*Delta0**beta_
        print(f"     m*(G)={mG:.4f} < m*(G+Delta0)={mD0:.4f} (point at G dominated): {mG < mD0}")

# (i) Prop 1 with Gi < G (Remark S1(b)): budget no longer finite
print("\n(i) Prop 1 with zero-spend growth Gi < G (share decays without spend):")
print("  bound becomes (X-k)[ln(s(T)/s0) + (G-Gi)T] -> grows linearly in T => budget NOT finite")
Gi_ = 0.02
G_ = 0.05
X_, k_ = 1.0, 0.0
for T_ in [1, 10, 100]:
    b = (X_-k_)*(np.log(50) + (G_-Gi_)*T_)   # ln(sbar/s0)=ln(50) for s0=1%, sbar=50%
    print(f"    T={T_}: budget bound = {b:.2f} (unbounded as T grows)")
