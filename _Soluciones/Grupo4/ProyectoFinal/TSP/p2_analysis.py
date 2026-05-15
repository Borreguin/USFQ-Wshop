"""
=============================================================================
P2 - Analisis y simulación
TSP con Algoritmos Genéticos — Secciones c, d, e
=============================================================================
Integración con P1:
    Se requiere importar run_ga y load_cities_from_csv desde P1_GA_engine.py
    Nota: El archivo P1_GA_engine.py debe estar en la misma carpeta.

Estructura de carpetas esperada:
    proyecto/
    ├── dataset/
    │   └── cities_100_101112.csv
    │   └── ...
    ├── P1_GA_engine.py
    └── p2_analysis.py

Uso en P1:
    from p2_analysis import run_p2
    run_p2("dataset/cities_100_101112.csv")

Uso manual:
    from p2_analysis import P2Analyzer
    from P1_GA_engine import load_cities_from_csv, run_ga
    cities  = load_cities_from_csv("dataset/cities_100_101112.csv")
    results = run_ga({"cities": cities, "n_pop": 100, "n_gen": 300,
                      "p_crossover": 0.9, "p_mutation": 0.05}) #parametros P1
    analyzer = P2Analyzer(results, cities=cities)
    analyzer.run_all()
=============================================================================
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.colors import LinearSegmentedColormap
from typing import Optional
import warnings
warnings.filterwarnings("ignore")



# Estilo de graficas
# ---------------------------------------------------------------------------
PALETTE = {
    "best":      "#00C9A7",   # verde agua
    "avg":       "#FFC300",   # amarillo
    "worst":     "#FF5757",   # rojo
    "diversity": "#A78BFA",   # violeta
    "route":     "#38BDF8",   # celeste
    "city":      "#F97316",   # naranja
    "bg":        "#0F172A",   # fondo oscuro
    "grid":      "#1E293B",   # grid suave
    "text":      "#E2E8F0",   # texto claro
}

def _apply_style():
    plt.rcParams.update({
        "figure.facecolor":  PALETTE["bg"],
        "axes.facecolor":    PALETTE["bg"],
        "axes.edgecolor":    PALETTE["grid"],
        "axes.labelcolor":   PALETTE["text"],
        "axes.titlecolor":   PALETTE["text"],
        "xtick.color":       PALETTE["text"],
        "ytick.color":       PALETTE["text"],
        "grid.color":        PALETTE["grid"],
        "grid.linewidth":    0.6,
        "legend.facecolor":  "#1E293B",
        "legend.edgecolor":  PALETTE["grid"],
        "legend.labelcolor": PALETTE["text"],
        "font.family":       "monospace",
        "font.size":         10,
    })

_apply_style()



# Datos simulados — trabajo paralelo a P1
# ---------------------------------------------------------------------------

def generate_mock_results(n_cities: int = 130, n_gen: int = 300,
                           n_pop: int = 100, seed: int = 42) -> dict:
    """
    Genera un dict con la misma estructura que run_ga() de P1.
    Útil para desarrollo y pruebas de P2 sin necesitar P1.
    """
    rng = np.random.default_rng(seed)

    # Ciudades aleatorias
    cities = [(float(rng.integers(0, 1000)),
               float(rng.integers(0, 1000))) for _ in range(n_cities)]

    # Simular convergencia realista
    start, end = 18000.0, 9500.0
    decay = np.exp(-np.linspace(0, 5, n_gen))
    noise = rng.normal(0, 80, n_gen)

    best_curve  = end + (start - end) * decay + np.abs(noise) * 0.3
    avg_curve   = best_curve * rng.uniform(1.05, 1.15, n_gen)
    worst_curve = avg_curve  * rng.uniform(1.08, 1.20, n_gen)

    fitness_history = [
        {"best": float(b), "avg": float(a), "worst": float(w)}
        for b, a, w in zip(best_curve, avg_curve, worst_curve)
    ]

    # Diversidad: alta al inicio, decae con el fitness
    div_start = rng.uniform(0.85, 0.95)
    div_end   = rng.uniform(0.10, 0.20)
    div_curve = div_end + (div_start - div_end) * decay + rng.normal(0, 0.015, n_gen)
    div_curve = np.clip(div_curve, 0, 1)
    diversity_history = div_curve.tolist()

    # Población final mock
    final_population = [
        list(rng.permutation(n_cities)) for _ in range(n_pop)
    ]

    best_route = list(rng.permutation(n_cities))

    return {
        "best_route":        best_route,
        "best_fitness":      float(best_curve[-1]),
        "fitness_history":   fitness_history,
        "diversity_history": diversity_history,
        "final_population":  final_population,
        "_cities_mock":      cities,   # solo en mock; en P1 viene de config
    }



# Funciones de análisis
# ---------------------------------------------------------------------------

def detect_convergence(fitness_history: list[dict],
                        window: int = 20,
                        threshold: float = 0.001) -> int:
    """
    Detecta la generación donde el algoritmo converge.
    Criterio: mejora relativa promedio en ventana < threshold.
    Retorna el índice de generación (o -1 si no converge).
    """
    bests = [g["best"] for g in fitness_history]
    for i in range(window, len(bests)):
        segment = bests[i - window: i]
        delta = abs(segment[0] - segment[-1]) / (segment[0] + 1e-9)
        if delta < threshold:
            return i - window
    return -1


def detect_stagnation(fitness_history: list[dict],
                       window: int = 30,
                       threshold: float = 0.0005) -> list[tuple]:
    """
    Detecta bloques de estancamiento (tramos donde el mejor fitness
    casi no cambia). Retorna lista de (gen_inicio, gen_fin).
    """
    bests = [g["best"] for g in fitness_history]
    stagnation_blocks = []
    in_stagnation = False
    start_idx = 0

    for i in range(1, len(bests)):
        delta = abs(bests[i] - bests[i - 1]) / (bests[i - 1] + 1e-9)
        if delta < threshold:
            if not in_stagnation:
                in_stagnation = True
                start_idx = i - 1
        else:
            if in_stagnation:
                if i - start_idx >= window // 2:
                    stagnation_blocks.append((start_idx, i))
                in_stagnation = False

    if in_stagnation and len(bests) - start_idx >= window // 2:
        stagnation_blocks.append((start_idx, len(bests) - 1))

    return stagnation_blocks


def compute_route_distance(route: list[int], cities: list[tuple]) -> float:
    """Calcula la distancia total de una ruta."""
    total = 0.0
    n = len(route)
    for i in range(n):
        c1 = cities[route[i]]
        c2 = cities[route[(i + 1) % n]]
        total += np.hypot(c1[0] - c2[0], c1[1] - c2[1])
    return total


def nearest_neighbor_heuristic(cities: list[tuple],
                                 start: int = 0) -> tuple[list[int], float]:
    """
    Heurística del vecino más cercano (baseline para comparación en e).
    Retorna (ruta, distancia_total).
    """
    n = len(cities)
    visited = [False] * n
    route = [start]
    visited[start] = True

    for _ in range(n - 1):
        current = route[-1]
        cx, cy = cities[current]
        best_dist = float("inf")
        best_next = -1
        for j in range(n):
            if not visited[j]:
                dx = cities[j][0] - cx
                dy = cities[j][1] - cy
                d = np.hypot(dx, dy)
                if d < best_dist:
                    best_dist = d
                    best_next = j
        route.append(best_next)
        visited[best_next] = True

    dist = compute_route_distance(route, cities)
    return route, dist


def relative_error(ag_fitness: float, baseline_fitness: float) -> float:
    """Error relativo del AG respecto al baseline (en %)."""
    return (ag_fitness - baseline_fitness) / baseline_fitness * 100.0


def population_diversity_pct_unique(population: list[list[int]]) -> float:
    """Porcentaje de individuos únicos en la población."""
    unique = len(set(tuple(ind) for ind in population))
    return unique / len(population) * 100.0


# Clase principal P2Analyzer
# ---------------------------------------------------------------------------

class P2Analyzer:
    """
    Clase principal de análisis y visualización para P2.

    Parámetros
    ----------
    results : dict
        Diccionario retornado por run_ga() de P1.
    cities  : list[tuple]
        Lista de coordenadas (x, y) de las ciudades.
        Si results contiene '_cities_mock' (modo mock), se usa ese.
    nn_result : tuple[list[int], float] | None
        Resultado de la heurística NN precalculado por P1.
        Si es None, P2 lo calcula internamente.
    save_figures : bool
        Si True, guarda cada figura como PNG.
    fig_prefix : str
        Prefijo para los nombres de archivo de las figuras.
    """

    def __init__(self,
                 results: dict,
                 cities: Optional[list] = None,
                 nn_result: Optional[tuple] = None,
                 save_figures: bool = True,
                 fig_prefix: str = "p2"):

        self.results   = results
        self.cities    = cities or results.get("_cities_mock", [])
        self.save_figs = save_figures
        self.prefix    = fig_prefix

        self.fitness_history   = results["fitness_history"]
        self.diversity_history = results["diversity_history"]
        self.best_route        = results["best_route"]
        self.best_fitness      = results["best_fitness"]
        self.final_population  = results["final_population"]
        self.generations       = list(range(len(self.fitness_history)))

        # Baseline nearest-neighbor
        if nn_result is not None:
            self.nn_route, self.nn_fitness = nn_result
        elif self.cities:
            print("[P2] Calculando baseline nearest-neighbor...")
            self.nn_route, self.nn_fitness = nearest_neighbor_heuristic(self.cities)
        else:
            self.nn_route, self.nn_fitness = None, None

        # Análisis previos
        self.conv_gen        = detect_convergence(self.fitness_history)
        self.stagnation_blks = detect_stagnation(self.fitness_history)

  
    # Literal c — Evolución del Fitness
    # ------------------------------------------------------------------

    def plot_fitness_evolution(self):
        """
        Gráfica principal de evolución del fitness (c).
        Incluye las 3 curvas + marcador de convergencia + regiones de
        estancamiento.
        """
        fig, ax = plt.subplots(figsize=(12, 5))
        fig.patch.set_facecolor(PALETTE["bg"])

        bests  = [g["best"]  for g in self.fitness_history]
        avgs   = [g["avg"]   for g in self.fitness_history]
        worsts = [g["worst"] for g in self.fitness_history]
        gens   = self.generations

        # Área entre mejor y peor
        ax.fill_between(gens, bests, worsts,
                        alpha=0.08, color=PALETTE["avg"])

        ax.plot(gens, worsts, color=PALETTE["worst"],  lw=1.2,
                alpha=0.7, label="Peor fitness",    linestyle="--")
        ax.plot(gens, avgs,   color=PALETTE["avg"],    lw=1.5,
                alpha=0.9, label="Fitness promedio")
        ax.plot(gens, bests,  color=PALETTE["best"],   lw=2.0,
                label="Mejor fitness")

        # Marcador de convergencia
        if self.conv_gen >= 0:
            ax.axvline(self.conv_gen, color=PALETTE["route"],
                       lw=1.4, linestyle=":", alpha=0.9,
                       label=f"Convergencia (gen {self.conv_gen})")
            ax.annotate(f"conv.\ngen {self.conv_gen}",
                        xy=(self.conv_gen, bests[self.conv_gen]),
                        xytext=(self.conv_gen + len(gens)*0.03,
                                bests[self.conv_gen] * 1.04),
                        color=PALETTE["route"], fontsize=8,
                        arrowprops=dict(arrowstyle="->",
                                        color=PALETTE["route"],
                                        lw=0.8))

        # Regiones de estancamiento
        for (s, e) in self.stagnation_blks:
            ax.axvspan(s, e, alpha=0.10, color=PALETTE["worst"],
                       label="_stagnation")

        # Dummy para leyenda de estancamiento
        if self.stagnation_blks:
            from matplotlib.patches import Patch
            ax.legend(handles=ax.get_legend_handles_labels()[0] + [
                Patch(facecolor=PALETTE["worst"], alpha=0.3,
                      label=f"Estancamiento ({len(self.stagnation_blks)} bloque/s)")
            ], loc="upper right", fontsize=8)
        else:
            ax.legend(loc="upper right", fontsize=8)

        ax.set_xlabel("Generación")
        ax.set_ylabel("Fitness (distancia total)")
        ax.set_title("c — Evolución del Fitness por Generación", fontweight="bold")
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        self._save(fig, "fitness_evolution")
        plt.show()
        return fig

   
    # Literal d — Diversidad Poblacional
    # ------------------------------------------------------------------

    def plot_diversity(self):
        """
        Gráfica de diversidad a lo largo de las generaciones (d).
        """
        fig, ax = plt.subplots(figsize=(12, 4))
        fig.patch.set_facecolor(PALETTE["bg"])

        ax.fill_between(self.generations, self.diversity_history,
                        alpha=0.15, color=PALETTE["diversity"])
        ax.plot(self.generations, self.diversity_history,
                color=PALETTE["diversity"], lw=2.0,
                label="Diversidad (% únicos o dist. promedio)")

        if self.conv_gen >= 0:
            ax.axvline(self.conv_gen, color=PALETTE["route"],
                       lw=1.3, linestyle=":", alpha=0.8,
                       label=f"Convergencia (gen {self.conv_gen})")

        ax.set_xlabel("Generación")
        ax.set_ylabel("Diversidad")
        ax.set_title("d — Diversidad Poblacional por Generación", fontweight="bold")
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        self._save(fig, "diversity")
        plt.show()
        return fig

    def plot_diversity_vs_fitness(self):
        """
        Gráfica doble eje: diversidad vs mejor fitness (d).
        Permite ver la correlación entre ambas métricas.
        """
        fig, ax1 = plt.subplots(figsize=(12, 5))
        fig.patch.set_facecolor(PALETTE["bg"])
        ax2 = ax1.twinx()

        bests = [g["best"] for g in self.fitness_history]

        ax1.plot(self.generations, bests,
                 color=PALETTE["best"], lw=2.0, label="Mejor fitness")
        ax1.set_ylabel("Fitness (distancia)", color=PALETTE["best"])
        ax1.tick_params(axis="y", labelcolor=PALETTE["best"])

        ax2.plot(self.generations, self.diversity_history,
                 color=PALETTE["diversity"], lw=1.8, linestyle="--",
                 alpha=0.85, label="Diversidad")
        ax2.set_ylabel("Diversidad", color=PALETTE["diversity"])
        ax2.tick_params(axis="y", labelcolor=PALETTE["diversity"])

        if self.conv_gen >= 0:
            ax1.axvline(self.conv_gen, color=PALETTE["route"],
                        lw=1.2, linestyle=":", alpha=0.8)

        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2,
                   loc="upper right", fontsize=8)

        ax1.set_xlabel("Generación")
        ax1.set_title("d — Diversidad vs Calidad de Solución", fontweight="bold")
        ax1.grid(True, alpha=0.3)

        plt.tight_layout()
        self._save(fig, "diversity_vs_fitness")
        plt.show()
        return fig


    # Literal e — Mapa de ruta + comparación con baseline (vecino mas cercano)
    # ------------------------------------------------------------------

    def plot_route_map(self):
        """
        Dibuja el mapa de ciudades con la mejor ruta del AG (e).
        """
        if not self.cities:
            print("[P2] No hay coordenadas de ciudades disponibles.")
            return None

        xs = [c[0] for c in self.cities]
        ys = [c[1] for c in self.cities]

        fig, ax = plt.subplots(figsize=(10, 8))
        fig.patch.set_facecolor(PALETTE["bg"])

        # Ruta
        route_closed = self.best_route + [self.best_route[0]]
        rx = [xs[i] for i in route_closed]
        ry = [ys[i] for i in route_closed]
        ax.plot(rx, ry, color=PALETTE["route"], lw=1.2,
                alpha=0.7, zorder=1)

        # Ciudades
        ax.scatter(xs, ys, color=PALETTE["city"],
                   s=20, zorder=2, linewidths=0)

        # Ciudad inicial
        start = self.best_route[0]
        ax.scatter([xs[start]], [ys[start]],
                   color=PALETTE["best"], s=80, zorder=3,
                   marker="*", label=f"Inicio (ciudad {start})")

        ax.set_title(
            f"e — Mejor Ruta AG   |   Distancia: {self.best_fitness:,.1f}",
            fontweight="bold")
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.2)

        plt.tight_layout()
        self._save(fig, "route_map")
        plt.show()
        return fig

    def plot_comparison_table(self) -> dict:
        """
        Imprime y grafica la tabla comparativa AG vs Nearest Neighbor (e).
        Retorna dict con los valores para incluir en el reporte.
        """
        if self.nn_fitness is None:
            print("[P2] No hay baseline NN disponible para comparar.")
            return {}

        err = relative_error(self.best_fitness, self.nn_fitness)
        pct_unique = population_diversity_pct_unique(self.final_population)

        summary = {
            "ag_fitness":     self.best_fitness,
            "nn_fitness":     self.nn_fitness,
            "relative_error": err,
            "pct_unique_final": pct_unique,
            "convergence_gen":  self.conv_gen,
            "stagnation_blocks": len(self.stagnation_blks),
        }

        # Tabla visual
        fig, ax = plt.subplots(figsize=(9, 3))
        fig.patch.set_facecolor(PALETTE["bg"])
        ax.axis("off")

        col_labels = ["Método", "Fitness (distancia)", "Error relativo vs NN"]
        rows = [
            ["Nearest Neighbor (baseline)", f"{self.nn_fitness:,.2f}", "—"],
            ["Algoritmo Genético (AG)",     f"{self.best_fitness:,.2f}",
             f"{err:+.2f}%"],
        ]

        tbl = ax.table(
            cellText=rows,
            colLabels=col_labels,
            cellLoc="center",
            loc="center",
        )
        tbl.auto_set_font_size(False)
        tbl.set_fontsize(11)
        tbl.scale(1, 2.2)

        # Estilo celdas
        for (r, c), cell in tbl.get_celld().items():
            cell.set_facecolor(PALETTE["grid"] if r == 0 else PALETTE["bg"])
            cell.set_edgecolor(PALETTE["grid"])
            cell.set_text_props(color=PALETTE["text"])

        # Color error
        err_cell = tbl[2, 2]
        err_cell.get_text().set_color(
            PALETTE["best"] if err <= 0 else PALETTE["worst"])

        ax.set_title("e — Comparación AG vs Heurística Nearest Neighbor",
                     fontweight="bold", color=PALETTE["text"], pad=14)

        plt.tight_layout()
        self._save(fig, "comparison_table")
        plt.show()

        # Imprimir resumen en consola
        print("\n" + "="*55)
        print("  RESUMEN P2 — Análisis de Calidad")
        print("="*55)
        print(f"  Fitness AG          : {self.best_fitness:>12,.2f}")
        print(f"  Fitness NN baseline : {self.nn_fitness:>12,.2f}")
        print(f"  Error relativo      : {err:>+11.2f} %")
        print(f"  Convergencia en gen : {self.conv_gen}")
        print(f"  Bloques estancado   : {len(self.stagnation_blks)}")
        print(f"  % únicos (final)    : {pct_unique:.1f} %")
        print("="*55 + "\n")

        return summary


    # Dashboard de gráficas
    # ------------------------------------------------------------------

    def plot_dashboard(self):
        """
        Genera un dashboard de 4 paneles con todos los análisis en una
        sola figura.
        """
        fig = plt.figure(figsize=(16, 12))
        fig.patch.set_facecolor(PALETTE["bg"])
        gs = gridspec.GridSpec(2, 2, figure=fig,
                               hspace=0.40, wspace=0.32)

        # Panel 1: Fitness evolution
        ax1 = fig.add_subplot(gs[0, 0])
        bests  = [g["best"]  for g in self.fitness_history]
        avgs   = [g["avg"]   for g in self.fitness_history]
        worsts = [g["worst"] for g in self.fitness_history]
        ax1.fill_between(self.generations, bests, worsts,
                         alpha=0.07, color=PALETTE["avg"])
        ax1.plot(self.generations, worsts, color=PALETTE["worst"],
                 lw=1.0, alpha=0.7, linestyle="--", label="Peor")
        ax1.plot(self.generations, avgs,   color=PALETTE["avg"],
                 lw=1.3, label="Promedio")
        ax1.plot(self.generations, bests,  color=PALETTE["best"],
                 lw=2.0, label="Mejor")
        if self.conv_gen >= 0:
            ax1.axvline(self.conv_gen, color=PALETTE["route"],
                        lw=1.2, linestyle=":", alpha=0.8)
        for (s, e) in self.stagnation_blks:
            ax1.axvspan(s, e, alpha=0.10, color=PALETTE["worst"])
        ax1.set_title("c — Evolución Fitness", fontsize=10, fontweight="bold")
        ax1.set_xlabel("Generación", fontsize=8)
        ax1.set_ylabel("Fitness", fontsize=8)
        ax1.legend(fontsize=7)
        ax1.grid(True, alpha=0.25)

        # Panel 2: Diversity
        ax2 = fig.add_subplot(gs[0, 1])
        ax2.fill_between(self.generations, self.diversity_history,
                         alpha=0.15, color=PALETTE["diversity"])
        ax2.plot(self.generations, self.diversity_history,
                 color=PALETTE["diversity"], lw=1.8, label="Diversidad")
        if self.conv_gen >= 0:
            ax2.axvline(self.conv_gen, color=PALETTE["route"],
                        lw=1.2, linestyle=":", alpha=0.8,
                        label=f"Conv. gen {self.conv_gen}")
        ax2.set_title("d — Diversidad Poblacional", fontsize=10, fontweight="bold")
        ax2.set_xlabel("Generación", fontsize=8)
        ax2.set_ylabel("Diversidad", fontsize=8)
        ax2.legend(fontsize=7)
        ax2.grid(True, alpha=0.25)

        # Panel 3: Diversity vs Fitness (doble eje)
        ax3 = fig.add_subplot(gs[1, 0])
        ax3b = ax3.twinx()
        ax3.plot(self.generations, bests,
                 color=PALETTE["best"], lw=1.8, label="Mejor fitness")
        ax3b.plot(self.generations, self.diversity_history,
                  color=PALETTE["diversity"], lw=1.5,
                  linestyle="--", alpha=0.85, label="Diversidad")
        ax3.set_ylabel("Fitness", color=PALETTE["best"], fontsize=8)
        ax3b.set_ylabel("Diversidad", color=PALETTE["diversity"], fontsize=8)
        ax3.tick_params(axis="y", labelcolor=PALETTE["best"])
        ax3b.tick_params(axis="y", labelcolor=PALETTE["diversity"])
        ax3.set_title("d — Diversidad vs Calidad", fontsize=10, fontweight="bold")
        ax3.set_xlabel("Generación", fontsize=8)
        ax3.grid(True, alpha=0.25)

        # Panel 4: Mapa de ruta
        ax4 = fig.add_subplot(gs[1, 1])
        if self.cities:
            xs = [c[0] for c in self.cities]
            ys = [c[1] for c in self.cities]
            route_closed = self.best_route + [self.best_route[0]]
            rx = [xs[i] for i in route_closed]
            ry = [ys[i] for i in route_closed]
            ax4.plot(rx, ry, color=PALETTE["route"], lw=0.9, alpha=0.6)
            ax4.scatter(xs, ys, color=PALETTE["city"], s=8, zorder=2)
            start = self.best_route[0]
            ax4.scatter([xs[start]], [ys[start]],
                        color=PALETTE["best"], s=60, zorder=3, marker="*")
        ax4.set_title(
            f"e — Mejor Ruta  ({self.best_fitness:,.0f})",
            fontsize=10, fontweight="bold")
        ax4.set_xlabel("X", fontsize=8)
        ax4.set_ylabel("Y", fontsize=8)
        ax4.grid(True, alpha=0.20)

        fig.suptitle("P2 — Análisis y Visualización · TSP con AG",
                     fontsize=14, fontweight="bold",
                     color=PALETTE["text"], y=1.01)

        plt.tight_layout()
        self._save(fig, "dashboard")
        plt.show()
        return fig

 
    # Funcion 'run_all' — ejecuta el pipeline completo
    # ------------------------------------------------------------------

    def run_all(self):
        """
        Genera todas las figuras y el resumen de análisis.
        Orden: dashboard → fitness → diversidad → diversidad_vs_fitness
               → mapa → tabla comparativa
        """
        print("[P2] Generando dashboard completo...")
        self.plot_dashboard()

        print("[P2] Figura c — Evolución del Fitness...")
        self.plot_fitness_evolution()

        print("[P2] Figura d — Diversidad...")
        self.plot_diversity()

        print("[P2] Figura d — Diversidad vs Fitness...")
        self.plot_diversity_vs_fitness()

        print("[P2] Figura e — Mapa de ruta...")
        self.plot_route_map()

        print("[P2] Tabla e — Comparación AG vs NN...")
        summary = self.plot_comparison_table()

        return summary


    # Guardar figuras generadas
    # ------------------------------------------------------------------

    def _save(self, fig, name: str):
        if self.save_figs:
            path = f"{self.prefix}_{name}.png"
            fig.savefig(path, dpi=150, bbox_inches="tight",
                        facecolor=fig.get_facecolor())
            print(f"  [guardado] {path}")



# Función principal de integración con P1
# ---------------------------------------------------------------------------

def run_p2(
    csv_path: str = "dataset/cities_100_101112.csv",
    n_pop: int = 100,
    n_gen: int = 300,
    p_crossover: float = 0.9,
    p_mutation: float = 0.05,
    seed: int = 42,
    save_figures: bool = True,
    fig_prefix: str = "p2",
) -> dict:
    """
    Función para ejecutar P2 con el motor real de P1.

    Parámetros
    ----------
    csv_path     : ruta al archivo CSV con columnas city, x, y
    n_pop        : tamaño de la población
    n_gen        : número de generaciones
    p_crossover  : probabilidad de cruce (0.0 a 1.0)
    p_mutation   : probabilidad de mutación (0.0 a 1.0)
    seed         : semilla para reproducibilidad
    save_figures : si True guarda los PNGs en el directorio actual
    fig_prefix   : prefijo de los archivos de figura

    Retorna
    -------
    dict con métricas finales: fitness AG, fitness NN, error relativo, etc.
    """
    # Importar P1
    try:
        from P1_GA_engine import load_cities_from_csv, run_ga, nearest_neighbor_baseline, build_distance_matrix
    except ImportError:
        raise ImportError(
            "No se encontró P1_GA_engine.py. "
            "Asegúrate de que esté en la misma carpeta que p2_analysis.py."
        )

    # Cargar ciudades desde CSV 
    print(f"[P2] Cargando ciudades desde: {csv_path}")
    cities = load_cities_from_csv(csv_path)
    print(f"[P2] {len(cities)} ciudades cargadas correctamente.")

    # Configurar y correr el AG de P1 
    config = {
        "cities":      cities,
        "n_pop":       n_pop,
        "n_gen":       n_gen,
        "p_crossover": p_crossover,
        "p_mutation":  p_mutation,
        "seed":        seed,
    }

    print(f"[P2] Ejecutando AG  |  n_pop={n_pop}  n_gen={n_gen}  "
          f"p_cx={p_crossover}  p_mut={p_mutation}")
    results = run_ga(config)
    print(f"[P2] AG finalizado  |  Mejor fitness: {results['best_fitness']:,.2f}")

    #  Calcular baseline NN desde P1 (para no duplicar código) 
    distance_matrix = build_distance_matrix(cities)
    nn_route, nn_fitness = nearest_neighbor_baseline(distance_matrix, start=0)
    print(f"[P2] Baseline NN    |  Fitness NN: {nn_fitness:,.2f}")

    # Crear analizador y generar todas las figuras 
    analyzer = P2Analyzer(
        results     = results,
        cities      = cities,
        nn_result   = (nn_route, nn_fitness),   # pasa el NN ya calculado
        save_figures = save_figures,
        fig_prefix   = fig_prefix,
    )

    summary = analyzer.run_all()
    return summary



# Ejecución desde consola: python p2_analysis.py
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    # Si se pasa un CSV como argumento: python p2_analysis.py dataset/otro.csv
    csv = sys.argv[1] if len(sys.argv) > 1 else "dataset/cities_100_101112.csv"

    summary = run_p2(
        csv_path    = csv,
        n_pop       = 100,
        n_gen       = 300,
        p_crossover = 0.9,
        p_mutation  = 0.05,
        seed        = 42,
    )
