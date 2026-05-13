"""
experiments.py — Experimentos comparativos de parametros del GA-TSP.

Ejecutar:
    python experiments.py

Experimentos:
  1. Variacion del tamano de poblacion (pop_size).
  2. Variacion de la tasa de mutacion (mutation_rate).
  3. Variacion del tipo de mutacion (swap / inversion / combined).
  4. Variacion del tamano del torneo (tournament_k).

Genera tablas CSV y una grafica comparativa en results/experiments/.
"""

import os
import sys
import time
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(__file__))

from ga_tsp.distances import load_cities, compute_distance_matrix
from ga_tsp.ga import GeneticAlgorithmTSP
from ga_tsp.nearest_neighbor import nearest_neighbor_tour

DATASET    = os.path.join(os.path.dirname(__file__), "dataset", "cities_100_123.csv")
OUT_DIR    = os.path.join(os.path.dirname(__file__), "results", "experiments")
N_GEN      = 300        # generaciones por experimento (reducido para velocidad)
BASE_CFG   = dict(
    pop_size=100, mutation_rate=0.02, n_elite=5,
    tournament_k=5, mutation_type="combined",
    n_generations=N_GEN, seed=42, verbose=False,
)


def run_config(dist_matrix, **kwargs) -> dict:
    cfg = {**BASE_CFG, **kwargs}
    t0 = time.time()
    ga = GeneticAlgorithmTSP(dist_matrix=dist_matrix, **cfg)
    _, dist = ga.run()
    elapsed = time.time() - t0
    return {"dist": dist, "time": elapsed, "ga": ga, "cfg": cfg}


def experiments():
    os.makedirs(OUT_DIR, exist_ok=True)

    cities      = load_cities(DATASET)
    dist_matrix = compute_distance_matrix(cities)
    nn_tour, nn_dist = nearest_neighbor_tour(dist_matrix)

    print(f"NN baseline: {nn_dist:.2f}\n")
    all_results = []

    # ── Experimento 1: tamano de poblacion ──────────────────────────
    print("=" * 55)
    print("Exp 1 — Tamano de poblacion (mutation_rate=0.02 fijo)")
    print("=" * 55)
    pop_results = []
    for pop in [50, 100, 150, 200, 300]:
        r = run_config(dist_matrix, pop_size=pop)
        imp = (nn_dist - r["dist"]) / nn_dist * 100
        pop_results.append({
            "experimento": "pop_size",
            "parametro": pop,
            "dist_GA": round(r["dist"], 2),
            "mejora_vs_NN_%": round(imp, 2),
            "tiempo_s": round(r["time"], 1),
        })
        all_results.append({"exp": "pop_size", "label": f"pop={pop}",
                             "history": r["ga"].best_dist_history, "color": None})
        print(f"  pop={pop:3d}: dist={r['dist']:.2f}  mejora={imp:.1f}%  t={r['time']:.1f}s")

    # ── Experimento 2: tasa de mutacion ─────────────────────────────
    print("\n" + "=" * 55)
    print("Exp 2 — Tasa de mutacion (pop_size=100 fijo)")
    print("=" * 55)
    mut_results = []
    for mr in [0.005, 0.01, 0.02, 0.05, 0.10]:
        r = run_config(dist_matrix, mutation_rate=mr)
        imp = (nn_dist - r["dist"]) / nn_dist * 100
        mut_results.append({
            "experimento": "mutation_rate",
            "parametro": mr,
            "dist_GA": round(r["dist"], 2),
            "mejora_vs_NN_%": round(imp, 2),
            "tiempo_s": round(r["time"], 1),
        })
        all_results.append({"exp": "mutation_rate", "label": f"mr={mr}",
                             "history": r["ga"].best_dist_history, "color": None})
        print(f"  mr={mr:.3f}: dist={r['dist']:.2f}  mejora={imp:.1f}%  t={r['time']:.1f}s")

    # ── Experimento 3: tipo de mutacion ─────────────────────────────
    print("\n" + "=" * 55)
    print("Exp 3 — Tipo de mutacion")
    print("=" * 55)
    type_results = []
    for mtype in ["swap", "inversion", "combined"]:
        r = run_config(dist_matrix, mutation_type=mtype)
        imp = (nn_dist - r["dist"]) / nn_dist * 100
        type_results.append({
            "experimento": "mutation_type",
            "parametro": mtype,
            "dist_GA": round(r["dist"], 2),
            "mejora_vs_NN_%": round(imp, 2),
            "tiempo_s": round(r["time"], 1),
        })
        all_results.append({"exp": "mutation_type", "label": mtype,
                             "history": r["ga"].best_dist_history, "color": None})
        print(f"  {mtype:10s}: dist={r['dist']:.2f}  mejora={imp:.1f}%")

    # ── Experimento 4: tamano del torneo ────────────────────────────
    print("\n" + "=" * 55)
    print("Exp 4 — Tamano del torneo (tournament_k)")
    print("=" * 55)
    k_results = []
    for k in [2, 3, 5, 7, 10]:
        r = run_config(dist_matrix, tournament_k=k)
        imp = (nn_dist - r["dist"]) / nn_dist * 100
        k_results.append({
            "experimento": "tournament_k",
            "parametro": k,
            "dist_GA": round(r["dist"], 2),
            "mejora_vs_NN_%": round(imp, 2),
            "tiempo_s": round(r["time"], 1),
        })
        all_results.append({"exp": "tournament_k", "label": f"k={k}",
                             "history": r["ga"].best_dist_history, "color": None})
        print(f"  k={k:2d}: dist={r['dist']:.2f}  mejora={imp:.1f}%")

    # ── Guardar tablas CSV ───────────────────────────────────────────
    all_rows = pop_results + mut_results + type_results + k_results
    df = pd.DataFrame(all_rows)
    csv_path = os.path.join(OUT_DIR, "experiments_results.csv")
    df.to_csv(csv_path, index=False)
    print(f"\nTabla guardada: {csv_path}")

    # ── Grafica comparativa ──────────────────────────────────────────
    _plot_experiments(all_results, nn_dist, OUT_DIR)
    print(f"Grafica guardada en {OUT_DIR}/")


def _plot_experiments(all_results, nn_dist, out_dir):
    groups = ["pop_size", "mutation_rate", "mutation_type", "tournament_k"]
    titles = [
        "Exp 1 — Tamano de poblacion",
        "Exp 2 — Tasa de mutacion",
        "Exp 3 — Tipo de mutacion",
        "Exp 4 — Tamano de torneo",
    ]
    colors_sets = [
        ["#e74c3c", "#e67e22", "#f1c40f", "#2ecc71", "#3498db"],
        ["#8e44ad", "#c0392b", "#e74c3c", "#e67e22", "#f39c12"],
        ["#1abc9c", "#2980b9", "#8e44ad"],
        ["#34495e", "#2c3e50", "#1abc9c", "#16a085", "#27ae60"],
    ]

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("Experimentos GA-TSP: Convergencia por Configuracion",
                 fontsize=12, fontweight="bold")

    for ax, group, title, colors in zip(axes.flat, groups, titles, colors_sets):
        group_results = [r for r in all_results if r["exp"] == group]
        for r, color in zip(group_results, colors):
            ax.plot(r["history"], color=color, lw=1.4, label=r["label"])
        ax.axhline(nn_dist, color="black", lw=1.0, linestyle="--",
                   alpha=0.6, label=f"NN={nn_dist:.0f}")
        ax.set_title(title, fontsize=10)
        ax.set_xlabel("Generacion")
        ax.set_ylabel("Mejor distancia")
        ax.legend(fontsize=8)
        ax.grid(alpha=0.2)

    plt.tight_layout()
    fig.savefig(os.path.join(out_dir, "experiments_comparison.png"),
                dpi=150, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    experiments()
