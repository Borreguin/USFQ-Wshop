"""
TSP – Travelling Salesman Problem | Diseño Orientado a Objetos
Clases: City, DistanceMatrix, Route, NearestNeighborSolver,
        TwoOptSolver, AntColonyOptimizer, TSPVisualizer, TSPSolver
"""

from __future__ import annotations
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import time
from dataclasses import dataclass
from itertools import combinations
from typing import List, Tuple, Optional


# ── Entidades del dominio ────────────────────────────────────────────────────

@dataclass
class City:
    """Representa una ciudad con nombre y coordenadas geograficas."""
    name: str
    lon: float
    lat: float

    def distance_to(self, other: City) -> float:
        dx = (self.lon - other.lon) * np.cos(np.radians(self.lat)) * 111.32
        dy = (self.lat - other.lat) * 110.57
        return np.sqrt(dx**2 + dy**2)

    def __repr__(self) -> str:
        return f"City({self.name})"


class DistanceMatrix:
    """Matriz de distancias entre todas las ciudades (km)."""

    def __init__(self, cities: List[City]):
        self.cities = cities
        self.n = len(cities)
        self._matrix = self._build()

    def _build(self) -> np.ndarray:
        m = np.zeros((self.n, self.n))
        for i in range(self.n):
            for j in range(self.n):
                if i != j:
                    m[i][j] = self.cities[i].distance_to(self.cities[j])
        return m

    def __getitem__(self, idx: Tuple[int, int]) -> float:
        return self._matrix[idx[0], idx[1]]

    @property
    def matrix(self) -> np.ndarray:
        return self._matrix

    @property
    def names(self) -> List[str]:
        return [c.name for c in self.cities]

    @property
    def coords(self) -> np.ndarray:
        return np.array([[c.lon, c.lat] for c in self.cities])


class Route:
    """Ruta como secuencia de indices de ciudades con calculo de costo."""

    def __init__(self, indices: List[int], dist_matrix: DistanceMatrix):
        self.indices = indices
        self._dm = dist_matrix

    @property
    def cost(self) -> float:
        return sum(
            self._dm[self.indices[i], self.indices[i + 1]]
            for i in range(len(self.indices) - 1)
        )

    @property
    def city_names(self) -> List[str]:
        return [self._dm.cities[i].name for i in self.indices]

    def __repr__(self) -> str:
        return f"Route(cost={self.cost:.2f} km, path={' -> '.join(self.city_names)})"


# ── Algoritmos de optimizacion ───────────────────────────────────────────────

class NearestNeighborSolver:
    """Heuristica greedy: siempre ir a la ciudad mas cercana no visitada."""

    def __init__(self, dist_matrix: DistanceMatrix):
        self._dm = dist_matrix

    def solve(self, start: int = 0) -> Route:
        n = self._dm.n
        visited = [False] * n
        path = [start]
        visited[start] = True
        for _ in range(n - 1):
            last = path[-1]
            nearest = min(
                (j for j in range(n) if not visited[j]),
                key=lambda j: self._dm[last, j],
            )
            path.append(nearest)
            visited[nearest] = True
        path.append(start)
        return Route(path, self._dm)


class TwoOptSolver:
    """Mejora local: invierte segmentos de la ruta hasta convergencia."""

    def __init__(self, route: Route):
        self._route = route
        self._dm = route._dm

    def solve(self) -> Tuple[Route, List[float]]:
        best = self._route.indices[:]
        best_cost = Route(best, self._dm).cost
        history = [best_cost]
        improved = True
        while improved:
            improved = False
            for i, j in combinations(range(1, len(best) - 1), 2):
                if j - i == 1:
                    continue
                candidate = best[:i] + best[i:j][::-1] + best[j:]
                cost = Route(candidate, self._dm).cost
                if cost < best_cost - 1e-10:
                    best, best_cost = candidate, cost
                    history.append(best_cost)
                    improved = True
        return Route(best, self._dm), history


class AntColonyOptimizer:
    """
    Ant Colony Optimization para TSP.
    p(i->j) = [tau^alpha * eta^beta] / sum[tau^alpha * eta^beta]
    Evaporacion: tau *= (1 - rho)
    Deposito elite: refuerza la mejor ruta global extra veces.
    """

    def __init__(self, dist_matrix: DistanceMatrix,
                 n_ants: int = 25, n_iter: int = 150,
                 alpha: float = 1.2, beta: float = 2.5,
                 rho: float = 0.15, Q: float = 500.0, elite: int = 3):
        self._dm    = dist_matrix
        self.n_ants = n_ants
        self.n_iter = n_iter
        self.alpha  = alpha
        self.beta   = beta
        self.rho    = rho
        self.Q      = Q
        self.elite  = elite
        self.n      = dist_matrix.n

        with np.errstate(divide="ignore"):
            self._eta = np.where(dist_matrix.matrix > 0,
                                 1.0 / dist_matrix.matrix, 0.0)
        tau0 = 1.0 / (self.n * np.mean(
            dist_matrix.matrix[dist_matrix.matrix > 0]))
        self._tau = np.ones((self.n, self.n)) * tau0

    def _build_route(self) -> List[int]:
        start = np.random.randint(self.n)
        visited = np.zeros(self.n, dtype=bool)
        visited[start] = True
        path = [start]
        for _ in range(self.n - 1):
            curr = path[-1]
            probs = (self._tau[curr] ** self.alpha) * (self._eta[curr] ** self.beta)
            probs[visited] = 0.0
            total = probs.sum()
            nxt = int(np.random.choice(self.n, p=probs / total) if total > 0
                      else np.random.choice(np.where(~visited)[0]))
            path.append(nxt)
            visited[nxt] = True
        path.append(start)
        return path

    def _update_pheromones(self, paths: List[List[int]], best: List[int]):
        self._tau *= (1 - self.rho)
        for path in paths:
            delta = self.Q / Route(path, self._dm).cost
            for i in range(len(path) - 1):
                self._tau[path[i]][path[i+1]] += delta
                self._tau[path[i+1]][path[i]] += delta
        delta_e = self.elite * self.Q / Route(best, self._dm).cost
        for i in range(len(best) - 1):
            a, b = best[i], best[i+1]
            self._tau[a][b] += delta_e
            self._tau[b][a] += delta_e

    def run(self, verbose: bool = False):
        best_path, best_cost = None, np.inf
        cost_history, avg_history, snapshots = [], [], []
        for it in range(self.n_iter):
            paths = [self._build_route() for _ in range(self.n_ants)]
            costs = [Route(p, self._dm).cost for p in paths]
            idx = int(np.argmin(costs))
            if costs[idx] < best_cost:
                best_cost = costs[idx]
                best_path = paths[idx][:]
            self._update_pheromones(paths, best_path)
            cost_history.append(best_cost)
            avg_history.append(float(np.mean(costs)))
            if it % 10 == 0:
                snapshots.append((it, self._tau.copy()))
            if verbose and it % 25 == 0:
                print(f"  Iter {it:4d} | mejor: {best_cost:.2f} km | "
                      f"promedio: {np.mean(costs):.2f} km")
        return Route(best_path, self._dm), cost_history, avg_history, snapshots


# ── Visualizador ─────────────────────────────────────────────────────────────

class TSPVisualizer:
    """Genera todas las figuras del TSP."""

    def __init__(self, dist_matrix: DistanceMatrix):
        self._dm     = dist_matrix
        self._coords = dist_matrix.coords
        self._names  = dist_matrix.names

    def _draw_route(self, ax, route: Route, title: str, color: str):
        ax.clear()
        xs = [self._coords[i][0] for i in route.indices]
        ys = [self._coords[i][1] for i in route.indices]
        ax.plot(xs, ys, "-", color=color, linewidth=1.6, alpha=0.85, zorder=2)
        ax.scatter(self._coords[:, 0], self._coords[:, 1],
                   s=60, color=color, zorder=3,
                   edgecolors="white", linewidths=0.8)
        ax.scatter(self._coords[route.indices[0]][0],
                   self._coords[route.indices[0]][1],
                   s=160, color="gold", zorder=4,
                   edgecolors="black", linewidths=1.2, marker="*")
        for i, name in enumerate(self._names):
            ax.annotate(name, (self._coords[i][0], self._coords[i][1]),
                        textcoords="offset points", xytext=(5, 4), fontsize=7.5)
        ax.set_title(title, fontsize=10, fontweight="bold")
        ax.set_xlabel("Longitud"); ax.set_ylabel("Latitud")
        ax.grid(True, alpha=0.25, linestyle="--")

    def plot_comparison(self, routes, labels, palette) -> plt.Figure:
        fig, axes = plt.subplots(1, len(routes), figsize=(6*len(routes), 5))
        fig.suptitle("TSP Ecuador – Comparativa de Algoritmos",
                     fontsize=14, fontweight="bold")
        for ax, route, label, color in zip(axes, routes, labels, palette):
            self._draw_route(ax, route, f"{label}\n{route.cost:.1f} km", color)
        mejora = (routes[0].cost - routes[-1].cost) / routes[0].cost * 100
        fig.text(0.5, 0.01, f"Mejora: {mejora:.1f}% sobre Nearest Neighbor",
                 ha="center", fontsize=10, color="darkgreen", fontweight="bold")
        plt.tight_layout(rect=[0, 0.04, 1, 1])
        return fig

    def plot_convergence(self, cost_history, avg_history,
                         nn_cost, best_cost) -> plt.Figure:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
        fig.suptitle("ACO – Convergencia", fontsize=13, fontweight="bold")
        iters = range(len(cost_history))
        ax1.plot(iters, cost_history, color="steelblue", linewidth=2,
                 label="Mejor global")
        ax1.plot(iters, avg_history, color="orange", linewidth=1.2,
                 linestyle="--", alpha=0.8, label="Promedio iteracion")
        ax1.axhline(nn_cost, color="tomato", linestyle=":",
                    label=f"Nearest Neighbor ({nn_cost:.0f} km)")
        ax1.axhline(best_cost, color="seagreen", linestyle=":",
                    label=f"ACO+2opt ({best_cost:.0f} km)")
        ax1.fill_between(iters, cost_history, best_cost, alpha=0.08, color="steelblue")
        ax1.set_xlabel("Iteracion"); ax1.set_ylabel("Costo (km)")
        ax1.set_title("Evolucion del costo"); ax1.legend(fontsize=9)
        ax1.grid(True, alpha=0.3)
        delta = -np.diff(cost_history)
        ax2.bar(range(len(delta)), delta,
                color=np.where(delta > 0, "seagreen", "lightgrey"),
                edgecolor="none")
        ax2.set_xlabel("Iteracion"); ax2.set_ylabel("Reduccion (km)")
        ax2.set_title("Mejoras por iteracion"); ax2.grid(True, alpha=0.3, axis="y")
        plt.tight_layout()
        return fig

    def plot_pheromones(self, snapshots) -> plt.Figure:
        n_snaps = min(len(snapshots), 4)
        fig, axes = plt.subplots(1, n_snaps, figsize=(4.5*n_snaps, 4.5))
        fig.suptitle("Evolucion de Feromonas ACO", fontsize=13, fontweight="bold")
        if n_snaps == 1:
            axes = [axes]
        for idx in range(n_snaps):
            k = idx * (len(snapshots)-1) // max(n_snaps-1, 1)
            it, tau = snapshots[k]
            im = axes[idx].imshow(tau, cmap="YlOrRd", aspect="auto",
                                  norm=mcolors.LogNorm(
                                      vmin=tau[tau>0].min(), vmax=tau.max()))
            n = self._dm.n
            axes[idx].set_xticks(range(n)); axes[idx].set_yticks(range(n))
            axes[idx].set_xticklabels(self._names, rotation=45,
                                       ha="right", fontsize=7)
            axes[idx].set_yticklabels(self._names, fontsize=7)
            axes[idx].set_title(f"Iteracion {it}", fontsize=10)
            plt.colorbar(im, ax=axes[idx], shrink=0.8)
        plt.tight_layout()
        return fig

    def plot_statistics(self, results: np.ndarray, nn_cost: float) -> plt.Figure:
        fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
        fig.suptitle(f"Analisis Estadistico – {len(results)} ejecuciones",
                     fontsize=13, fontweight="bold")
        axes[0].hist(results, bins=10, color="steelblue",
                     edgecolor="white", alpha=0.85, density=True)
        axes[0].axvline(results.mean(), color="orange", linewidth=2,
                        label=f"Media: {results.mean():.1f}")
        axes[0].axvline(results.min(), color="seagreen", linewidth=2,
                        label=f"Min: {results.min():.1f}")
        axes[0].set_title("Distribucion"); axes[0].legend(fontsize=9)
        axes[0].grid(True, alpha=0.3)
        bp = axes[1].boxplot(results, patch_artist=True, widths=0.5)
        bp["boxes"][0].set_facecolor("steelblue"); bp["boxes"][0].set_alpha(0.7)
        axes[1].axhline(nn_cost, color="tomato", linestyle="--",
                        label=f"NN: {nn_cost:.1f} km")
        axes[1].set_title("Dispersion"); axes[1].legend(fontsize=9)
        axes[1].grid(True, alpha=0.3, axis="y")
        data = [["Minimo", f"{results.min():.2f} km"],
                ["Maximo", f"{results.max():.2f} km"],
                ["Media",  f"{results.mean():.2f} km"],
                ["Std",    f"{results.std():.2f} km"],
                ["Mejora vs NN", f"{(nn_cost-results.mean())/nn_cost*100:.1f}%"]]
        axes[2].axis("off")
        tbl = axes[2].table(cellText=data, colLabels=["Metrica","Valor"],
                             loc="center", cellLoc="left")
        tbl.auto_set_font_size(False); tbl.set_fontsize(10); tbl.scale(1.2, 1.8)
        for (r,c), cell in tbl.get_celld().items():
            if r == 0:
                cell.set_facecolor("#283593")
                cell.set_text_props(color="white", fontweight="bold")
            elif r % 2 == 0:
                cell.set_facecolor("#e8eaf6")
        axes[2].set_title("Estadisticas", fontweight="bold")
        plt.tight_layout()
        return fig

    def plot_heatmap(self) -> plt.Figure:
        n, dist = self._dm.n, self._dm.matrix
        size = max(8, n * 0.4)
        fig, ax = plt.subplots(figsize=(size, size * 0.85))
        im = ax.imshow(dist, cmap="YlOrRd", aspect="auto")
        fs = max(5, 9 - n // 5)
        ax.set_xticks(range(n)); ax.set_yticks(range(n))
        ax.set_xticklabels(self._names, rotation=45, ha="right", fontsize=fs)
        ax.set_yticklabels(self._names, fontsize=fs)
        plt.colorbar(im, ax=ax, label="Distancia (km)")
        if n <= 15:  # solo mostrar valores numericos para instancias pequenas
            for i in range(n):
                for j in range(n):
                    ax.text(j, i, f"{dist[i][j]:.0f}", ha="center", va="center",
                            fontsize=5.5,
                            color="black" if dist[i][j] < dist.max()*0.6 else "white")
        ax.set_title(f"Mapa de Calor – Distancias entre {n} ciudades (km)",
                     fontweight="bold")
        plt.tight_layout()
        return fig

    def save_all(self, figs, names, save_dir):
        import os
        os.makedirs(save_dir, exist_ok=True)
        for fig, name in zip(figs, names):
            fig.savefig(os.path.join(save_dir, name), dpi=150, bbox_inches="tight")
        plt.close("all")
        print(f"  TSP: {len(figs)} imagenes -> {save_dir}/")


# ── Orquestador ──────────────────────────────────────────────────────────────

class TSPSolver:
    """
    Punto de entrada: instancia todo, ejecuta algoritmos y visualiza.
    Soporta n ciudades arbitrarias via parametro cities_data.
    Por defecto usa las 24 capitales de provincia del Ecuador.
    """

    # 24 capitales de provincia del Ecuador (lon, lat)
    CITIES_DATA = {
        "Quito":          (-78.5249, -0.2295),
        "Guayaquil":      (-79.9000, -2.1894),
        "Cuenca":         (-79.0059, -2.9001),
        "Manta":          (-80.7089, -0.9677),
        "Ambato":         (-78.6197, -1.2491),
        "Loja":           (-79.2045, -3.9931),
        "Esmeraldas":     (-79.7000,  0.9592),
        "Riobamba":       (-78.6464, -1.6635),
        "Ibarra":         (-78.1228,  0.3517),
        "Latacunga":      (-78.6165, -0.9319),
        "Machala":        (-79.9605, -3.2581),
        "Portoviejo":     (-80.4549, -1.0546),
        "Sto. Domingo":   (-79.1719, -0.2543),
        "Babahoyo":       (-79.5347, -1.8017),
        "Tulcan":         (-77.7176,  0.8117),
        "Guaranda":       (-78.9954, -1.5933),
        "Azogues":        (-78.8465, -2.7391),
        "Macas":          (-78.1158, -2.3069),
        "Zamora":         (-78.9582, -4.0671),
        "Tena":           (-77.8153, -0.9943),
        "Puyo":           (-77.9997, -1.4888),
        "Nueva Loja":     (-76.9972,  0.0839),
        "Puerto F. de Orellana": (-76.9868, -0.4642),
        "Santa Rosa":     (-79.9613, -3.4493),
    }

    def __init__(self, cities_data: Optional[dict] = None, n_runs: int = 20):
        data            = cities_data if cities_data is not None else self.CITIES_DATA
        self.cities     = [City(n, lo, la) for n, (lo, la) in data.items()]
        self.dm         = DistanceMatrix(self.cities)
        self.visualizer = TSPVisualizer(self.dm)
        self.n_runs     = n_runs

    def run(self, save_dir: Optional[str] = None) -> Route:
        print("=" * 60)
        print("  TSP Ecuador – OOP  (ACO + 2-opt)")
        print("=" * 60)

        nn_route = NearestNeighborSolver(self.dm).solve()
        print(f"\n[1] Nearest Neighbor: {nn_route.cost:.2f} km")

        print("\n[2] ACO...")
        aco_route, cost_hist, avg_hist, snaps = AntColonyOptimizer(
            self.dm, n_ants=25, n_iter=150).run(verbose=True)

        best_route, _ = TwoOptSolver(aco_route).solve()
        print(f"    ACO + 2-opt: {best_route.cost:.2f} km  "
              f"| Mejora: {(nn_route.cost-best_route.cost)/nn_route.cost*100:.1f}%")
        print(f"\n  {best_route}")

        print(f"\n[3] Multi-corrida ({self.n_runs} runs)...")
        results = np.array([TwoOptSolver(
            AntColonyOptimizer(self.dm, n_ants=20, n_iter=100).run()[0]
        ).solve()[0].cost for _ in range(self.n_runs)])
        print(f"    Media: {results.mean():.2f} +/- {results.std():.2f} km")

        figs = [
            self.visualizer.plot_comparison(
                [nn_route, aco_route, best_route],
                ["Nearest Neighbor", "ACO", "ACO + 2-opt"],
                ["tomato", "steelblue", "seagreen"]),
            self.visualizer.plot_convergence(
                cost_hist, avg_hist, nn_route.cost, best_route.cost),
            self.visualizer.plot_pheromones(snaps),
            self.visualizer.plot_statistics(results, nn_route.cost),
            self.visualizer.plot_heatmap(),
        ]
        img_names = ["tsp_01_comparativa_rutas.png", "tsp_02_convergencia.png",
                     "tsp_03_feromonas.png", "tsp_04_estadisticas.png",
                     "tsp_05_heatmap_distancias.png"]

        if save_dir:
            self.visualizer.save_all(figs, img_names, save_dir)
        else:
            plt.show()
        return best_route
