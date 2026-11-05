"""Independent re-derivation of Prop entry (a)-(b): Cournot with n firms, linear demand P=A-BQ e^{-Gt},
full cost chat = u + r(k_u+a_c), sunk F, entry at date 0 only."""
import numpy as np, json
A,B,u,ku,ac,r,G,F = 10.0, 1.0, 2.0, 0.5, 0.3, 0.10, 0.05, 0.5
chat = u + r*(ku+ac)
def cournot(n):
    x = (A-chat)/(B*(n+1))  # per-firm flow output coefficient (x_n e^{Gt})
    P = (A+n*chat)/(n+1)
    pi = (A-chat)**2/(B*(n+1)**2)
    L = (P-chat)/P
    k_n = ku/P; k_a = ac/P
    m_op = r*k_n + (r-G)*k_a + L
    m = (r-G)*(k_n+k_a) + L
    R = 1*G + m   # X=1
    npv = pi/(r-G) - F
    return dict(P=P, pi=pi, L=L, k_n=k_n, k_a=k_a, m=m, R=R, npv_entrant=npv)
for n in [1,2,3,5,10]:
    c = cournot(n)
    print('n=%d: P=%.3f L=%.4f m=%.4f R=%.4f entrant NPV=%.4f' % (n, c['P'], c['L'], c['m'], c['R'], c['npv_entrant']))
NF = (A-chat)/np.sqrt(B*(r-G)*F)
import math
n_star = math.floor(NF)-1
print('N_F=%.3f n*=%d' % (NF, n_star))
# limit F->0
for F2 in [0.05, 0.005, 0.0005]:
    NF2 = (A-chat)/np.sqrt(B*(r-G)*F2); n2 = math.floor(NF2)-1
    c = cournot(n2)
    print('F=%.4f: n*=%d L=%.5f R=%.5f (limit XG+(r-G)(ku+ac)/chat = %.5f)' % (F2, n2, c['L'], c['R'], G+(r-G)*(ku+ac)/chat))
# scarce input case (c): Z, w_n = A-chat-B Z (n+1)/n, P=A-BZ
Z = 0.5
for n in [2,5,20]:
    w = A - chat - B*Z*(n+1)/n
    P = A - B*Z
    rho = w/P
    Lnet = B*Z/(n*P)
    k = ku/P; ka = ac/P
    R_owner = 1*G + (r-G)*(k+ka) + rho + Lnet
    print('input n=%d: w=%.3f rho=%.4f R_owner=%.4f' % (n, w, rho, R_owner))
ZF = Z*np.sqrt(B/((r-G)*F))
print('n* input = floor(%.3f) = %d' % (ZF, math.floor(ZF)))
