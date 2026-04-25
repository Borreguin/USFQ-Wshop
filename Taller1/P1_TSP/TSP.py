"""
TSP – Travelling Salesman Problem
Enfoque: Ant Colony Optimization (ACO) + 2-opt local search
Comparativa: Greedy Nearest Neighbor vs ACO vs ACO+2opt
Análisis: convergencia, feromonas, estadísticas multi-corrida
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.animation as animation
from itertools import combinations
import time

# ── Ciudades ecuatorianas (lon, lat) ────────────────────────────────────────
CITIES = {
    "Quito":       (-78.5249, -0.2295),
    "Guayaquil":   (-79.9000, -2.1894),
    "Cuenca":      (-79.0059, -2.9001),
    "Manta":       (-80.7089, -0.9677),
    "Ambato":      (-78.6197, -1.2491),
    "Loja":        (-79.2045, -3.9931),
    "Esmeraldas":  (-79.7000,  0.9592),
    "Riobamba":    (-78.6464, -1.6635),
    "Ibarra":      (-78.1228,  0.3517),
    "Latacunga":   (-78.6165, -0.9319),
}

# ── Utilidades de distancia y rutas ─────────────────────────────────────────

def build_distance_matrix(cities: dict):
    names = list(cities.keys())
    n = len(names)
    coords = np.array([cities[c] for c in names])
    dist = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i != j:
                dx = (coords[i][0] - coords[j][0]) * np.cos(np.radians(coords[i][1])) * 111.32
                dy = (coords[i][1] - coords[j][1]) * 110.57
                dist[i][j] = np.sqrt(dx**2 + dy**2)
    return dist, names, coords


def route_cost(route: list, dist: np.ndarray) -> float:
    return sum(dist[route[i]][route[i + 1]] for i in range(len(route) - 1))


# ── Algoritmo 1: Nearest Neighbor (baseline greedy) ─────────────────────────

def nearest_neighbor(dist: np.ndarray, start: int = 0) -> list:
    n = len(dist)
    visited = [False] * n
    route = [start]
    visited[start] = True
    for _ in range(n - 1):
        last = route[-1]
        nearest = min((j for j in range(n) if not visited[j]), key=lambda j: dist[last][j])
        route.append(nearest)
        visited[nearest] = True
    route.append(start)
    return route


# ── Algoritmo 2: 2-opt local search ─────────────────────────────────────────

def two_opt(route: list, dist: np.ndarray):
    best = route[:]
    best_cost = route_cost(best, dist)
    history = [best_cost]
    improved = True
    while improved:
        improved = False
        for i, j in combinations(range(1, len(best) - 1), 2):
            if j - i == 1:
                continue
            candidate = best[:i] + best[i:j][::-1] + best[j:]
            cost = route_cost(candidate, dist)
            if cost < best_cost - 1e-10:
                best, best_cost = candidate, cost
                history.append(best_cost)
                improved = True
    return best, history


# ── Algoritmo 3: Ant Colony Optimization (ACO) ──────────────────────────────
#
#  Cada hormiga construye una ruta completa eligiendo el siguiente nodo con
#  probabilidad proporcional a:
#      p(i→j) = [τ(i,j)^α · η(i,j)^β] / Σ [τ(i,k)^α · η(i,k)^β]
#  donde τ=feromonas, η=1/dist (heurística), α controla explotación, β exploración.
#  Tras cada iteración se evapora feromona: τ ← (1-ρ)·τ  y se deposita en las
#  mejores rutas: Δτ = Q / costo_ruta.

class ACO:
    def __init__(
        self,
        dist: np.ndarray,
        n_ants: int = 20,
        n_iter: int = 150,
        alpha: float = 1.2,   # peso de feromonas
        beta: float  = 2.5,   # peso de heurística de distancia
        rho: float   = 0.15,  # tasa de evaporación
        Q: float     = 500.0, # constante de depósito de feromona
        elite: int   = 3,     # hormigas élite que refuerzan la mejor global
    ):
        self.dist    = dist
        self.n       = len(dist)
        self.n_ants  = n_ants
        self.n_iter  = n_iter
        self.alpha   = alpha
        self.beta    = beta
        self.rho     = rho
        self.Q       = Q
        self.elite   = elite

        # heurística η = 1/dist (evitar div/0)
        with np.errstate(divide="ignore"):
            self.eta = np.where(dist > 0, 1.0 / dist, 0.0)

        # feromonas iniciales = pequeño valor uniforme
        self.tau = np.ones((self.n, self.n)) * (1.0 / (self.n * np.mean(dist[dist > 0])))

    def _build_route(self) -> list:
        start = np.random.randint(self.n)
        visited = np.zeros(self.n, dtype=bool)
        visited[start] = True
        route = [start]
        for _ in range(self.n - 1):
            current = route[-1]
            # probabilidades de transición
            pheromone = self.tau[current] ** self.alpha
            heuristic = self.eta[current] ** self.beta
            probs = pheromone * heuristic
            probs[visited] = 0.0
            total = probs.sum()
            if total == 0:
                # todos los vecinos iguales, elige aleatorio
                unvisited = np.where(~visited)[0]
                nxt = np.random.choice(unvisited)
            else:
                probs /= total
                nxt = np.random.choice(self.n, p=probs)
            route.append(nxt)
            visited[nxt] = True
        route.append(start)
        return route

    def _update_pheromones(self, all_routes: list, best_route_global: list):
        # Evaporación
        self.tau *= (1 - self.rho)
        # Depósito por todas las hormigas de esta iteración
        for route in all_routes:
            cost = route_cost(route, self.dist)
            delta = self.Q / cost
            for i in range(len(route) - 1):
                self.tau[route[i]][route[i + 1]] += delta
                self.tau[route[i + 1]][route[i]] += delta
        # Refuerzo élite: la mejor ruta global deposita extra veces
        best_cost = route_cost(best_route_global, self.dist)
        delta_elite = self.elite * self.Q / best_cost
        for i in range(len(best_route_global) - 1):
            a, b = best_route_global[i], best_route_global[i + 1]
            self.tau[a][b] += delta_elite
            self.tau[b][a] += delta_elite

    def run(self, verbose: bool = False):
        best_route = None
        best_cost  = np.inf
        cost_history     = []   # mejor costo por iteración
        avg_cost_history = []   # costo promedio por iteración
        tau_snapshots    = []   # instantáneas de feromonas cada 10 iter

        for iteration in range(self.n_iter):
            routes = [self._build_route() for _ in range(self.n_ants)]
            costs  = [route_cost(r, self.dist) for r in routes]

            iter_best_idx  = int(np.argmin(costs))
            iter_best_cost = costs[iter_best_idx]

            if iter_best_cost < best_cost:
                best_cost  = iter_best_cost
                best_route = routes[iter_best_idx][:]

            self._update_pheromones(routes, best_route)

            cost_history.append(best_cost)
            avg_cost_history.append(float(np.mean(costs)))

            if iteration % 10 == 0:
                tau_snapshots.append((iteration, self.tau.copy()))

            if verbose and iteration % 25 == 0:
                print(f"  Iter {iteration:4d} | mejor: {best_cost:.2f} km | promedio: {np.mean(costs):.2f} km")

        return best_route, best_cost, cost_history, avg_cost_history, tau_snapshots


# ── Análisis multi-corrida ───────────────────────────────────────────────────

def multi_run_analysis(dist: np.ndarray, n_runs: int = 20):
    """Ejecuta ACO+2opt varias veces y recolecta estadísticas."""
    results = []
    for _ in range(n_runs):
        aco = ACO(dist, n_ants=20, n_iter=100)
        route, cost, *_ = aco.run()
        opt_route, opt_hist = two_opt(route, dist)
        results.append(opt_hist[-1])
    return np.array(results)


# ── Visualizaciones ──────────────────────────────────────────────────────────

def plot_route_on_ax(ax, route, coords, names, title, color="steelblue",
                     highlight_start=True):
    xs = [coords[i][0] for i in route]
    ys = [coords[i][1] for i in route]
    ax.plot(xs, ys, "-", color=color, linewidth=1.6, alpha=0.8, zorder=2)
    ax.scatter([c[0] for c in coords], [c[1] for c in coords],
               s=60, color=color, zorder=3, edgecolors="white", linewidths=0.8)
    if highlight_start:
        ax.scatter(coords[route[0]][0], coords[route[0]][1],
                   s=160, color="gold", zorder=4, edgecolors="black", linewidths=1.2,
                   marker="*")
    for i, name in enumerate(names):
        ax.annotate(name, (coords[i][0], coords[i][1]),
                    textcoords="offset points", xytext=(5, 4), fontsize=7.5)
    ax.set_title(title, fontsize=10, fontweight="bold")
    ax.set_xlabel("Longitud (°)")
    ax.set_ylabel("Latitud (°)")
    ax.grid(True, alpha=0.25, linestyle="--")


def figure_algorithm_comparison(nn_route, nn_cost, aco_route, aco_cost,
                                  aco2_route, aco2_cost, coords, names):
    fig, axes = plt.subplots(1, 3, figsize=(17, 5))
    fig.suptitle("TSP Ecuador – Comparativa de Algoritmos", fontsize=14, fontweight="bold")

    plot_route_on_ax(axes[0], nn_route, coords, names,
                     f"Nearest Neighbor\n{nn_cost:.1f} km", color="tomato")
    plot_route_on_ax(axes[1], aco_route, coords, names,
                     f"ACO (sin post-proceso)\n{aco_cost:.1f} km", color="steelblue")
    plot_route_on_ax(axes[2], aco2_route, coords, names,
                     f"ACO + 2-opt\n{aco2_cost:.1f} km", color="seagreen")

    mejora_nn  = (nn_cost - aco2_cost) / nn_cost * 100
    fig.text(0.5, 0.01,
             f"Mejora ACO+2opt vs Nearest Neighbor: {mejora_nn:.1f}%",
             ha="center", fontsize=10, color="darkgreen", fontweight="bold")
    plt.tight_layout(rect=[0, 0.04, 1, 1])
    return fig


def figure_convergence(cost_history, avg_history, nn_cost, aco2_cost):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("ACO – Convergencia", fontsize=13, fontweight="bold")

    iters = range(len(cost_history))
    ax1.plot(iters, cost_history, color="steelblue", linewidth=2, label="Mejor global")
    ax1.plot(iters, avg_history, color="orange", linewidth=1.2, linestyle="--",
             alpha=0.8, label="Promedio iteración")
    ax1.axhline(nn_cost, color="tomato", linestyle=":", linewidth=1.5,
                label=f"Nearest Neighbor ({nn_cost:.0f} km)")
    ax1.axhline(aco2_cost, color="seagreen", linestyle=":", linewidth=1.5,
                label=f"ACO+2opt ({aco2_cost:.0f} km)")
    ax1.fill_between(iters, cost_history, aco2_cost, alpha=0.08, color="steelblue")
    ax1.set_xlabel("Iteración")
    ax1.set_ylabel("Costo (km)")
    ax1.set_title("Evolución del costo por iteración")
    ax1.legend(fontsize=9)
    ax1.grid(True, alpha=0.3)

    # Velocidad de mejora (derivada discreta)
    delta = -np.diff(cost_history)
    ax2.bar(range(len(delta)), delta, color=np.where(delta > 0, "seagreen", "lightgrey"),
            edgecolor="none")
    ax2.set_xlabel("Iteración")
    ax2.set_ylabel("Reducción de costo (km)")
    ax2.set_title("Mejoras por iteración (Δ costo)")
    ax2.grid(True, alpha=0.3, axis="y")

    plt.tight_layout()
    return fig


def figure_pheromone_heatmap(tau_snapshots, names):
    n_snaps = min(len(tau_snapshots), 4)
    fig, axes = plt.subplots(1, n_snaps, figsize=(4.5 * n_snaps, 4.5))
    fig.suptitle("Evolución de Feromonas τ(i,j) a lo largo de ACO",
                 fontsize=13, fontweight="bold")
    if n_snaps == 1:
        axes = [axes]

    for idx in range(n_snaps):
        iteration, tau = tau_snapshots[idx * (len(tau_snapshots) - 1) // max(n_snaps - 1, 1)]
        n = len(names)
        im = axes[idx].imshow(tau, cmap="YlOrRd", aspect="auto",
                               norm=mcolors.LogNorm(vmin=tau[tau > 0].min(), vmax=tau.max()))
        axes[idx].set_xticks(range(n))
        axes[idx].set_yticks(range(n))
        axes[idx].set_xticklabels(names, rotation=45, ha="right", fontsize=7)
        axes[idx].set_yticklabels(names, fontsize=7)
        axes[idx].set_title(f"Iteración {iteration}", fontsize=10)
        plt.colorbar(im, ax=axes[idx], shrink=0.8)

    plt.tight_layout()
    return fig


def figure_statistical_analysis(multi_results, aco2_cost, nn_cost):
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
    fig.suptitle(f"Análisis Estadístico – {len(multi_results)} ejecuciones de ACO+2opt",
                 fontsize=13, fontweight="bold")

    # Histograma
    axes[0].hist(multi_results, bins=10, color="steelblue", edgecolor="white",
                 alpha=0.85, density=True)
    axes[0].axvline(multi_results.mean(), color="orange", linewidth=2,
                    label=f"Media: {multi_results.mean():.1f} km")
    axes[0].axvline(multi_results.min(), color="seagreen", linewidth=2,
                    label=f"Mínimo: {multi_results.min():.1f} km")
    axes[0].set_xlabel("Costo (km)")
    axes[0].set_ylabel("Densidad")
    axes[0].set_title("Distribución de costos")
    axes[0].legend(fontsize=9)
    axes[0].grid(True, alpha=0.3)

    # Boxplot
    bp = axes[1].boxplot(multi_results, patch_artist=True, vert=True,
                          widths=0.5)
    bp["boxes"][0].set_facecolor("steelblue")
    bp["boxes"][0].set_alpha(0.7)
    axes[1].axhline(nn_cost, color="tomato", linestyle="--", linewidth=1.5,
                    label=f"Nearest Neighbor: {nn_cost:.1f} km")
    axes[1].set_xticks([])
    axes[1].set_ylabel("Costo (km)")
    axes[1].set_title("Dispersión de resultados")
    axes[1].legend(fontsize=9)
    axes[1].grid(True, alpha=0.3, axis="y")

    # Tabla de métricas
    stats = {
        "Mínimo":          f"{multi_results.min():.2f} km",
        "Máximo":          f"{multi_results.max():.2f} km",
        "Media":           f"{multi_results.mean():.2f} km",
        "Desv. estándar":  f"{multi_results.std():.2f} km",
        "Mediana":         f"{np.median(multi_results):.2f} km",
        "Nearest Neighbor":f"{nn_cost:.2f} km",
        "Mejora media vs NN": f"{(nn_cost - multi_results.mean()) / nn_cost * 100:.1f}%",
        "Mejora máx vs NN":   f"{(nn_cost - multi_results.min()) / nn_cost * 100:.1f}%",
    }
    axes[2].axis("off")
    table_data = [[k, v] for k, v in stats.items()]
    tbl = axes[2].table(cellText=table_data, colLabels=["Métrica", "Valor"],
                         loc="center", cellLoc="left")
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(10)
    tbl.scale(1.2, 1.8)
    for (row, col), cell in tbl.get_celld().items():
        if row == 0:
            cell.set_facecolor("#283593")
            cell.set_text_props(color="white", fontweight="bold")
        elif row % 2 == 0:
            cell.set_facecolor("#e8eaf6")
    axes[2].set_title("Estadísticas descriptivas", fontweight="bold", fontsize=10)

    plt.tight_layout()
    return fig


def figure_distance_heatmap(dist, names):
    n = len(names)
    fig, ax = plt.subplots(figsize=(8, 6.5))
    im = ax.imshow(dist, cmap="YlOrRd", aspect="auto")
    ax.set_xticks(range(n)); ax.set_yticks(range(n))
    ax.set_xticklabels(names, rotation=45, ha="right", fontsize=8)
    ax.set_yticklabels(names, fontsize=8)
    plt.colorbar(im, ax=ax, label="Distancia (km)")
    for i in range(n):
        for j in range(n):
            ax.text(j, i, f"{dist[i][j]:.0f}", ha="center", va="center",
                    fontsize=6.5, color="black" if dist[i][j] < dist.max() * 0.6 else "white")
    ax.set_title("Mapa de Calor – Distancias entre Ciudades (km)", fontweight="bold")
    plt.tight_layout()
    return fig


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    dist, names, coords = build_distance_matrix(CITIES)
    n = len(names)

    print("=" * 60)
    print("  TSP Ecuador – ACO + 2-opt")
    print("=" * 60)

    # 1. Baseline: Nearest Neighbor
    t0 = time.time()
    nn_route = nearest_neighbor(dist, start=0)
    nn_cost  = route_cost(nn_route, dist)
    print(f"\n[1] Nearest Neighbor:  {nn_cost:.2f} km  ({time.time()-t0:.3f}s)")

    # 2. ACO
    print("\n[2] ACO en progreso…")
    t0 = time.time()
    aco = ACO(dist, n_ants=25, n_iter=150, alpha=1.2, beta=2.5, rho=0.15, Q=500, elite=3)
    aco_route, aco_cost, cost_hist, avg_hist, tau_snaps = aco.run(verbose=True)
    print(f"    ACO puro:          {aco_cost:.2f} km  ({time.time()-t0:.3f}s)")

    # 3. ACO + 2-opt refinement
    t0 = time.time()
    aco2_route, aco2_hist = two_opt(aco_route, dist)
    aco2_cost = aco2_hist[-1]
    print(f"    ACO + 2-opt:       {aco2_cost:.2f} km  ({time.time()-t0:.3f}s)")

    mejora = (nn_cost - aco2_cost) / nn_cost * 100
    print(f"\n  Mejora sobre NN:     {mejora:.1f}%")
    print("\n  Ruta óptima encontrada:")
    print("  " + " → ".join(names[i] for i in aco2_route))

    # 4. Análisis multi-corrida (estadísticas)
    print("\n[3] Análisis estadístico (20 corridas ACO+2opt)…")
    t0 = time.time()
    multi_results = multi_run_analysis(dist, n_runs=20)
    print(f"    Completado en {time.time()-t0:.1f}s")
    print(f"    Media: {multi_results.mean():.2f} ± {multi_results.std():.2f} km")
    print(f"    Rango: [{multi_results.min():.2f}, {multi_results.max():.2f}] km")

    # ── Figuras ──────────────────────────────────────────────────────────────
    fig1 = figure_algorithm_comparison(nn_route, nn_cost, aco_route, aco_cost,
                                        aco2_route, aco2_cost, coords, names)
    fig2 = figure_convergence(cost_hist, avg_hist, nn_cost, aco2_cost)
    fig3 = figure_pheromone_heatmap(tau_snaps, names)
    fig4 = figure_statistical_analysis(multi_results, aco2_cost, nn_cost)
    fig5 = figure_distance_heatmap(dist, names)

    plt.show()


if __name__ == "__main__":
    main()
