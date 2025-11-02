# Módulo visualizacao
# Sugestão de imports comuns:
import matplotlib.pyplot as plt

# ==== Trechos do notebook (seção: Visualização — Radar Charts) ====

# Compatibilidade: IPython display opcional
try:
    from IPython.display import display, HTML, clear_output
except ImportError:
    def display(x): print(x)
    def HTML(x): return str(x)
    def clear_output(): pass
import re
import numpy as np
import pandas as pd


def _normalize_pair(a_vals, b_vals):
    out_a, out_b = [], []
    for a, b in zip(a_vals, b_vals):
        a = float(a or 0); b = float(b or 0)
        m = max(a, b)
        out_a.append(a/m if m>0 else 0.0)
        out_b.append(b/m if m>0 else 0.0)
    return out_a, out_b

def _radar_plot(values_a, values_b, labels, name_a, name_b, title):
    angles = np.linspace(0, 2*np.pi, len(labels), endpoint=False).tolist()
    v1 = list(values_a) + [values_a[0]]
    v2 = list(values_b) + [values_b[0]]
    angles += angles[:1]
    fig, ax = plt.subplots(figsize=(8,8), subplot_kw=dict(polar=True))
    ax.fill(angles, v1, alpha=0.25); ax.plot(angles, v1, linewidth=2, label=name_a)
    ax.fill(angles, v2, alpha=0.25); ax.plot(angles, v2, linewidth=2, label=name_b)
    ax.set_yticklabels([]); ax.set_xticks(angles[:-1]); ax.set_xticklabels(labels, size=12)
    plt.title(title, size=16, y=1.08); plt.legend(loc='upper right', bbox_to_anchor=(1.25, 1.08)); plt.show()

def plot_offensive_radar(stats_a, stats_b, name_a, name_b):
    metrics = ['Gls', 'Ast', 'G+A_p90', 'xG', 'xAG']
    labels  = ['Gols', 'Assist.', 'G+A p/90', 'xG', 'xAG']
    a_vals = [stats_a.get(m, 0) for m in metrics]
    b_vals = [stats_b.get(m, 0) for m in metrics]
    na, nb = _normalize_pair(a_vals, b_vals)
    _radar_plot(na, nb, labels, name_a, name_b, 'Comparativo Ofensivo')

def plot_defensive_radar(stats_a, stats_b, name_a, name_b):
    metrics = ['Tkl', 'Int', 'Blocks', 'Clr', 'AerialsWon', 'Pressures']
    labels  = ['Desarmes','Intercep.','Bloqueios','Rebatidas','Aéreos','Pressões']
    a_vals = [stats_a.get(m, 0) for m in metrics]
    b_vals = [stats_b.get(m, 0) for m in metrics]
    na, nb = _normalize_pair(a_vals, b_vals)
    _radar_plot(na, nb, labels, name_a, name_b, 'Comparativo Defensivo')

