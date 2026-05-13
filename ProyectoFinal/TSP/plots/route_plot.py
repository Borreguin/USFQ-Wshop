import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from typing import List, Optional


def plot_route(
    cities: pd.DataFrame,
    tour: List[int],
    title: str = "Ruta TSP",
    color: str = "steelblue",
    save_path: Optional[str] = None,
) -> plt.Figure:
    """Grafica la ruta sobre un mapa de coordenadas."""
    coords = cities[["x", "y"]].values
    names  = cities["city"].values if "city" in cities.columns else [str(i) for i in range(len(cities))]

    # Cerrar el circuito
    route_idx = tour + [tour[0]]

    fig, ax = plt.subplots(figsize=(8, 7))
    xs = [coords[i][0] for i in route_idx]
    ys = [coords[i][1] for i in route_idx]

    ax.plot(xs, ys, "-o", color=color, lw=1.2, markersize=5, alpha=0.85)
    ax.scatter(coords[:, 0], coords[:, 1], color="red", s=20, zorder=5)

    # Anotar solo las primeras y ultimas ciudades para no saturar
    for idx in [tour[0], tour[len(tour)//4], tour[len(tour)//2], tour[3*len(tour)//4]]:
        ax.annotate(names[idx],
                    (coords[idx][0], coords[idx][1]),
                    textcoords="offset points", xytext=(4, 4),
                    fontsize=7, color="darkred")

    ax.set_title(title, fontsize=11, fontweight="bold")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.grid(alpha=0.2)
    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"  Guardado: {save_path}")
    return fig


def plot_comparison(
    cities: pd.DataFrame,
    nn_tour: List[int],
    ga_tour: List[int],
    nn_dist: float,
    ga_dist: float,
    save_path: Optional[str] = None,
) -> plt.Figure:
    """Comparacion visual: ruta NN (izq.) vs ruta GA (der.)."""
    coords = cities[["x", "y"]].values
    improvement = (nn_dist - ga_dist) / nn_dist * 100

    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    fig.suptitle(
        f"Comparacion NN vs GA-TSP  |  Mejora GA: {improvement:.1f}%",
        fontsize=12, fontweight="bold",
    )

    for ax, tour, dist, label, color in [
        (axes[0], nn_tour, nn_dist, "Vecino Cercano (NN)", "coral"),
        (axes[1], ga_tour, ga_dist, "Algoritmo Genetico (GA)", "steelblue"),
    ]:
        route = tour + [tour[0]]
        xs = [coords[i][0] for i in route]
        ys = [coords[i][1] for i in route]
        ax.plot(xs, ys, "-", color=color, lw=1.2, alpha=0.8)
        ax.scatter(coords[:, 0], coords[:, 1], color="black", s=15, zorder=5)
        ax.set_title(f"{label}\nDistancia: {dist:.2f}", fontsize=10)
        ax.set_xlabel("X"); ax.set_ylabel("Y")
        ax.grid(alpha=0.2)

    plt.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"  Guardado: {save_path}")
    return fig
