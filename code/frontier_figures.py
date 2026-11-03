#!/usr/bin/env python3
"""
frontier_figures.py

Produces
  figures/fig_frontier_tangency.pdf : efficient frontier m*(g), Rule-of-40 line, Rule-of-1 and Rule-of-2
                                      iso-score lines with tangency points, dominated region.
  figures/fig_saturation.pdf        : maximal Rule-of-40 score R_1*(s) against s/sbar for several k,
                                      with the saturation limits m0 + (1-k)G marked.

Parameters match the figure captions in sections/model.tex. No titles inside the figures.
Run from anywhere:  python3 frontier_figures.py
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager

ROOT = Path(__file__).resolve().parent.parent
FIG = ROOT / "figures"
FIG.mkdir(parents=True, exist_ok=True)

# Sans-serif font close to Arial/Helvetica, whichever is installed
available = {f.name for f in font_manager.fontManager.ttflist}
family = next((f for f in ["Arial", "Helvetica", "Liberation Sans", "Nimbus Sans", "DejaVu Sans"] if f in available),
              "sans-serif")
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": [family],
    "font.size": 9,
    "axes.labelsize": 9,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "legend.fontsize": 8,
    "axes.linewidth": 0.6,
    "xtick.major.width": 0.6,
    "ytick.major.width": 0.6,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "mathtext.fontset": "custom",
    "mathtext.rm": family,
    "mathtext.it": f"{family}:italic",
    "mathtext.bf": f"{family}:bold",
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.03,
})
BLACK, DARK, MID, LIGHT = "0.0", "0.25", "0.5", "0.88"


def pct(v, _pos=None):
    return f"{100 * v:.0f}%"


def optimum(m0, G, k, X, ell, alpha):
    """Closed form of Proposition 2: (g*, m*, R*)."""
    y = X - k
    if y <= 0:
        return G, m0 - k * G, m0 + y * G
    D = ell ** (1 / (1 - alpha)) * (alpha * y) ** (alpha / (1 - alpha))
    sig = alpha * y * D
    g = G + D
    m = m0 - k * g - sig
    return g, m, X * g + m


# ------------------------------------------------------------------------------------------------
# Figure 1: frontier and tangency
# ------------------------------------------------------------------------------------------------
m0, G, k, alpha, ell = 0.45, 0.10, 0.10, 0.30, 0.60
beta, kappa = 1 / alpha, ell ** (-1 / alpha)
frontier = lambda g: m0 - k * g - kappa * np.clip(g - G, 0, None) ** beta

g_max = 0.72
gg = np.linspace(G, g_max, 1200)
mm = frontier(gg)

fig, ax = plt.subplots(figsize=(5.2, 3.6))
y_lo, y_hi = -0.32, 0.50
x_lo, x_hi = 0.0, g_max

# dominated (feasible, inefficient) region: below frontier, g >= G
ax.fill_between(gg, y_lo, mm, color=LIGHT, lw=0, zorder=0, label="Feasible, dominated")
ax.text(0.285, 0.245, "Feasible but\ndominated", fontsize=7.5, color=DARK, ha="center", va="center")
ax.text(0.62, 0.36, "Infeasible", fontsize=7.5, color=DARK, ha="center")

# Rule of 40 line g + m = 0.40
xs = np.linspace(x_lo, x_hi, 2)
ax.plot(xs, 0.40 - xs, color=MID, lw=0.9, ls=(0, (1, 1.6)), zorder=1, label="Rule of 40: $g+m=40\\%$")

# iso-score lines and tangency points
first = True
for X, mk in [(1.0, "o"), (2.0, "s")]:
    g_s, m_s, R_s = optimum(m0, G, k, X, ell, alpha)
    ax.plot(xs, R_s - X * xs, color=DARK, lw=0.9, ls=(0, (4, 2)), zorder=2,
            label="Iso-score lines, slope $-X$" if first else None)
    first = False
    ax.plot([g_s], [m_s], marker=mk, ms=5.5, mfc="white", mec=BLACK, mew=1.0, zorder=4, ls="none")
    ax.annotate(f"Rule-of-{X:.0f} optimum ($X={X:.0f}$)\n$g^*={100 * g_s:.0f}\\%$, $m={100 * m_s:.0f}\\%$, "
                f"$R_{X:.0f}^*={100 * R_s:.0f}$",
                xy=(g_s, m_s), xytext=(g_s + 0.018, m_s + (0.07 if X == 1 else 0.035)), fontsize=7.2,
                color=BLACK, ha="left", va="bottom",
                arrowprops=dict(arrowstyle="-", lw=0.5, color=DARK, shrinkA=0, shrinkB=3))

# frontier
ax.plot(gg, mm, color=BLACK, lw=1.6, zorder=3, label="Efficient frontier $m^*(g)$")
ax.plot([G], [m0 - k * G], marker="o", ms=3, color=BLACK, zorder=4)
ax.text(G + 0.012, m0 - k * G - 0.035, "$m^*(G)=m_0-kG$", fontsize=7.2, va="top", ha="left")

ax.axvline(G, color=MID, lw=0.5, ls="-", zorder=0)
ax.text(G + 0.005, 0.475, "$G$", fontsize=8, color=DARK)
ax.axhline(0, color=MID, lw=0.4, zorder=0)
handles, labels = ax.get_legend_handles_labels()
order = [labels.index(l) for l in ["Efficient frontier $m^*(g)$", "Iso-score lines, slope $-X$",
                                   "Rule of 40: $g+m=40\\%$", "Feasible, dominated"]]
ax.legend([handles[i] for i in order], [labels[i] for i in order], loc="lower left", frameon=True,
          framealpha=1.0, edgecolor="0.7", fancybox=False, handlelength=2.4, borderpad=0.5)

ax.set_xlim(x_lo, x_hi)
ax.set_ylim(y_lo, y_hi)
ax.xaxis.set_major_formatter(pct)
ax.yaxis.set_major_formatter(pct)
ax.set_xlabel("Revenue growth $g$")
ax.set_ylabel("FCF margin $m$")
fig.savefig(FIG / "fig_frontier_tangency.pdf")
plt.close(fig)

# ------------------------------------------------------------------------------------------------
# Figure 2: saturation
# ------------------------------------------------------------------------------------------------
m0, G, lam, alpha = 0.50, 0.20, 1.2, 0.30
C = (1 - alpha) * alpha ** (alpha / (1 - alpha))
u = np.linspace(0, 1, 801)  # s / sbar
styles = {0.0: ("-", 1.5), 0.3: ((0, (5, 2)), 1.3), 0.6: ((0, (1.2, 1.4)), 1.5)}

fig, ax = plt.subplots(figsize=(5.2, 3.4))
for kk, (ls, lw) in styles.items():
    y = 1.0 - kk
    R = m0 + y * G + C * (lam * (1 - u) * y) ** (1 / (1 - alpha))
    ax.plot(u, R, color=BLACK, ls=ls, lw=lw, label=f"$k={kk:.1f}$")
    lim = m0 + y * G
    ax.plot([0.965, 1.0], [lim, lim], color=BLACK, lw=1.0)
    ax.text(1.012, lim, f"{100 * lim:.0f}", fontsize=7.5, va="center", ha="left")
ax.text(1.012, m0 + G + 0.075, "Limit\n$m_0+(1-k)G$", fontsize=7.2, va="bottom", ha="left", color=DARK)
ax.axhline(0.40, color=MID, lw=0.8, ls=(0, (1, 1.6)))
ax.text(0.02, 0.41, "Rule of 40", fontsize=7.5, color=DARK, va="bottom")

ax.set_xlim(0, 1)
ax.set_ylim(0.30, 1.35)
ax.yaxis.set_major_formatter(lambda v, _p: f"{100 * v:.0f}")
ax.xaxis.set_major_formatter(lambda v, _p: f"{v:.1f}")
ax.set_xlabel("Relative market share $s/\\bar{s}$")
ax.set_ylabel("Maximal Rule-of-40 score $R_1^*$ (points)")
ax.legend(frameon=False, loc="upper right", handlelength=2.6)
fig.savefig(FIG / "fig_saturation.pdf")
plt.close(fig)

print(f"font family: {family}")
for f in ["fig_frontier_tangency.pdf", "fig_saturation.pdf"]:
    print(f"wrote {FIG / f} ({(FIG / f).stat().st_size} bytes)")
