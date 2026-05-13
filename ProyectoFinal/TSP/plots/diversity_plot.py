import matplotlib.pyplot as plt
import numpy as np
from typing import List, Optional


def plot_diversity(
    diversity: List[float],
    best_fitness: List[float],
    best_dist: List[float],
    save_path: Optional[str] = None,
) -> plt.Figure:
    """
    Grafica la diversidad poblacional y su relacion con la calidad de la solucion.

    Diversidad = porcentaje de individuos unicos en la poblacion.
    Una diversidad alta indica buena exploracion; una baja indica convergencia.
    """
    gens = list(range(len(diversity)))

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle("Diversidad Poblacional — GA TSP", fontsize=12, fontweight="bold")

    # ── Panel 1: diversidad por generacion ──────────────────────────
    ax = axes[0]
    ax.plot(gens, diversity, "m-", lw=1.6, label="Diversidad")
    ax.fill_between(gens, 0, diversity, alpha=0.15, color="m")
    ax.set_xlabel("Generacion")
    ax.set_ylabel("% individuos unicos")
    ax.set_title("Diversidad Poblacional por Generacion")
    ax.set_ylim(0, 1.05)
    ax.grid(alpha=0.25)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.0%}"))

    # Marcar caida brusca (convergencia prematura)
    drop_idx = next(
        (i for i in range(1, len(diversity)) if diversity[i] < 0.3 and diversity[i - 1] >= 0.3),
        None,
    )
    if drop_idx:
        ax.axvline(drop_idx, color="red", lw=0.9, linestyle="--", alpha=0.7)
        ax.text(drop_idx + 5, 0.35, f"Convergencia\ngen {drop_idx}",
                fontsize=8, color="red")

    # ── Panel 2: diversidad vs fitness (ejes duales) ─────────────────
    ax2 = axes[1]
    color_div  = "mediumpurple"
    color_dist = "darkorange"

    l1, = ax2.plot(gens, diversity, "-", color=color_div, lw=1.5, label="Diversidad")
    ax2.set_xlabel("Generacion")
    ax2.set_ylabel("Diversidad", color=color_div)
    ax2.tick_params(axis="y", labelcolor=color_div)
    ax2.set_ylim(0, 1.05)
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.0%}"))

    ax2r = ax2.twinx()
    l2, = ax2r.plot(gens, best_dist, "-", color=color_dist, lw=1.5, label="Mejor distancia")
    ax2r.set_ylabel("Distancia del mejor tour", color=color_dist)
    ax2r.tick_params(axis="y", labelcolor=color_dist)

    ax2.set_title("Diversidad vs Calidad de la Solucion")
    ax2.legend(handles=[l1, l2], loc="upper right", fontsize=9)
    ax2.grid(alpha=0.2)

    # Correlacion
    corr = float(np.corrcoef(diversity, best_dist)[0, 1])
    ax2.text(
        0.03, 0.08,
        f"Correlacion: {corr:+.3f}",
        transform=ax2.transAxes, fontsize=9,
        bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow", alpha=0.8),
    )

    plt.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"  Guardado: {save_path}")
    return fig
