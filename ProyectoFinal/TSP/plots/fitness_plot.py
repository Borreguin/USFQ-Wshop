import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
from typing import List, Optional


def plot_fitness_evolution(
    best_fitness: List[float],
    avg_fitness: List[float],
    worst_fitness: List[float],
    best_dist: List[float],
    title: str = "GA-TSP: Evolucion del Fitness",
    save_path: Optional[str] = None,
) -> plt.Figure:
    """
    Grafica la evolucion del fitness (mejor, promedio, peor) y la distancia
    del mejor individuo por generacion.
    """
    gens = list(range(len(best_fitness)))

    fig = plt.figure(figsize=(14, 10))
    gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.38, wspace=0.32)

    # ── Panel 1: fitness (mejor / promedio / peor) ──────────────────
    ax1 = fig.add_subplot(gs[0, :])
    ax1.plot(gens, best_fitness, "g-",  lw=1.8, label="Mejor fitness")
    ax1.plot(gens, avg_fitness,  "b--", lw=1.3, alpha=0.8, label="Fitness promedio")
    ax1.plot(gens, worst_fitness,"r:",  lw=1.0, alpha=0.6, label="Peor fitness")
    ax1.fill_between(gens, worst_fitness, best_fitness, alpha=0.08, color="blue")
    ax1.set_xlabel("Generacion")
    ax1.set_ylabel("Fitness  (1 / distancia)")
    ax1.set_title(title, fontsize=12, fontweight="bold")
    ax1.legend(fontsize=9)
    ax1.grid(alpha=0.25)

    # ── Panel 2: distancia del mejor individuo ───────────────────────
    ax2 = fig.add_subplot(gs[1, 0])
    ax2.plot(gens, best_dist, "g-", lw=1.6)
    ax2.set_xlabel("Generacion")
    ax2.set_ylabel("Distancia total")
    ax2.set_title("Distancia del Mejor Individuo", fontsize=10)
    ax2.grid(alpha=0.25)
    # Marca el minimo
    min_idx = int(np.argmin(best_dist))
    ax2.axvline(min_idx, color="red", lw=0.8, linestyle="--", alpha=0.6)
    ax2.annotate(
        f"min={best_dist[min_idx]:.1f}\n@gen {min_idx}",
        xy=(min_idx, best_dist[min_idx]),
        xytext=(min_idx + len(gens) * 0.05, best_dist[min_idx] * 1.02),
        fontsize=8, color="red",
        arrowprops=dict(arrowstyle="->", color="red", lw=0.8),
    )

    # ── Panel 3: mejora relativa ─────────────────────────────────────
    ax3 = fig.add_subplot(gs[1, 1])
    initial_dist = best_dist[0]
    pct_improve = [(initial_dist - d) / initial_dist * 100 for d in best_dist]
    ax3.plot(gens, pct_improve, "purple", lw=1.6)
    ax3.set_xlabel("Generacion")
    ax3.set_ylabel("Mejora acumulada (%)")
    ax3.set_title("Mejora Relativa vs Generacion 0", fontsize=10)
    ax3.grid(alpha=0.25)
    ax3.axhline(max(pct_improve), color="purple", lw=0.8, linestyle="--", alpha=0.5)
    ax3.text(
        len(gens) * 0.6, max(pct_improve) * 0.95,
        f"Max: {max(pct_improve):.1f}%",
        fontsize=8, color="purple",
    )

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"  Guardado: {save_path}")
    return fig
