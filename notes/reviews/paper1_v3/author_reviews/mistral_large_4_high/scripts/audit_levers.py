"""Check Prop levers-position (b): switch weight X0 = k + a^{1-alpha}/(alpha*l).
Derive: growth-engine gain x*sigma* vs cut line x*a: sigma* > a iff (a l y)^{1/(1-a)} > a
iff a l y > a^{1-a} iff y > a^{-a}/l... check: (a l y)^{1/(1-a)} > a  <=> a l y > a^{1-a} <=> y > a^{1-a}/(a l) = a^{-a}/l.
Paper says X0 = k + a^{1-alpha}/(alpha l). y > a^{1-alpha}/(alpha l) = a^{-a}/l? a^{1-alpha}/alpha vs a^{-a}: a^{1-a}/a = a^{-a}. Yes equal. OK."""
import numpy as np
rng = np.random.default_rng(3)
maxerr = 0
for _ in range(2000):
    a = rng.uniform(0.1, 0.9); k = rng.uniform(0, 1); X = rng.uniform(k+0.01, 10)
    l = rng.uniform(0.05, 3); a_line = rng.uniform(0.01, 0.5)
    y = X - k
    sig = (a*l*y)**(1/(1-a))
    X0 = k + a_line**(1-a)/(a*l)
    # condition sigma* > a_line iff X > X0
    lhs = sig > a_line; rhs = X > X0
    if lhs != rhs: maxerr += 1
print('switch-weight mismatches:', maxerr, '/2000')
# demand-pull gain x*sig/a > x*a iff sig/a > a iff a l y > (a a)^{1-a} iff y > (a a)^{1-a}/(a l); paper: X > k + (a a)^{1-a}/(a l)
maxerr2 = 0
for _ in range(2000):
    a = rng.uniform(0.1, 0.9); k = rng.uniform(0, 1); X = rng.uniform(k+0.01, 10)
    l = rng.uniform(0.05, 3); al = rng.uniform(0.01, 0.5)
    y = X - k; sig = (a*l*y)**(1/(1-a))
    lhs = sig/a > al; rhs = X > k + (a*al)**(1-a)/(a*l)
    if lhs != rhs: maxerr2 += 1
print('demand-pull switch mismatches:', maxerr2, '/2000')
