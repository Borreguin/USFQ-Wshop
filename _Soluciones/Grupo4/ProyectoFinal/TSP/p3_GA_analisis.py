"""
=============================================================================
P3 — Análisis Experimental de Parámetros (Punto f)
TSP con Algoritmos Genéticos
=============================================================================

Qué hace este módulo:
    Ejecuta experimentos sistemáticos variando los parámetros del AG
    implementado por el equipo en P1_GA_engine.py, y genera tablas y
    gráficas comparativas.

Qué se reutiliza de los compañeros:
    - run_ga(config)              → motor principal del AG           [P1]
    - load_cities_from_csv()      → carga del dataset                [P1]
    - build_distance_matrix()     → matriz de distancias             [P1]
    - nearest_neighbor_baseline() → heurística de comparación        [P1]
    - PALETTE / _apply_style()    → estilo visual consistente        [P2]
    - detect_convergence()        → generación de convergencia       [P2]

Parámetros analizados (punto f):
    1. Tamaño de población   (n_pop)
    2. Probabilidad de cruce (p_crossover)
    3. Probabilidad de mutación (p_mutation)

Uso:
    python p3_param_analysis.py                        # usa dataset por defecto
    python p3_param_analysis.py dataset/mi_archivo.csv
=============================================================================
"""

import sys
import time
import warnings
import itertools
from typing import List, Dict, Any, Tuple

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import pandas as pd

warnings.filterwarnings("ignore")

# ---------------------------------------------------------------------------
# Importaciones del equipo
# ---------------------------------------------------------------------------
try:
    from P1_GA_engine import (
        run_ga,
        load_cities_from_csv,
        build_distance_matrix,
        nearest_neighbor_baseline,
    )
except ImportError:
    raise ImportError(
        "No se encontró P1_GA_engine.py.\n"
        "Asegúrate de que esté en la misma carpeta que este script."
    )

try:
    from p2_analysis import PALETTE, _apply_style, detect_convergence
except ImportError:
    # Si P2 no está disponible, definimos un estilo básico para no bloquearnos
    PALETTE = {
        "best": "#00C9A7", "avg": "#FFC300", "worst": "#FF5757",
        "diversity": "#A78BFA", "route": "#38BDF8", "city": "#F97316",
        "bg": "#0F172A", "grid": "#1E293B", "text": "#E2E8F0",
    }
    def _apply_style():
        plt.rcParams.update({
            "figure.facecolor": PALETTE["bg"],
            "axes.facecolor":   PALETTE["bg"],
            "axes.edgecolor":   PALETTE["grid"],
            "axes.labelcolor":  PALETTE["text"],
            "axes.titlecolor":  PALETTE["text"],
            "xtick.color":      PALETTE["text"],
            "ytick.color":      PALETTE["text"],
            "grid.color":       PALETTE["grid"],
            "grid.linewidth":   0.6,
            "legend.facecolor": "#1E293B",
            "legend.edgecolor": PALETTE["grid"],
            "legend.labelcolor":PALETTE["text"],
            "font.family":      "monospace",
            "font.size":        10,
        })
    def detect_convergence(fitness_history, window=20, threshold=0.001):
        bests = [g["best"] for g in fitness_history]
        for i in range(window, len(bests)):
            segment = bests[i - window: i]
            delta = abs(segment[0] - segment[-1]) / (segment[0] + 1e-9)
            if delta < threshold:
                return i - window
        return -1

_apply_style()


# ---------------------------------------------------------------------------
# Parámetros base del experimento
# ---------------------------------------------------------------------------

BASE_CONFIG = {
    # Fijos en todos los experimentos salvo el que varía cada parámetro
    "n_pop":       100,
    "n_gen":       200,          # 200 gen para mantener tiempos razonables
    "p_crossover": 0.85,
    "p_mutation":  0.05,
    "seed":        42,
    "greedy_ratio":    0.2,
    "tournament_size": 3,
    "elite_size":      2,
    "mutation_operator": "inversion",
}

# Valores a barrer por experimento
SWEEP = {
    "n_pop":       [30, 60, 100, 150, 200],
    "p_crossover": [0.5, 0.65, 0.75, 0.85, 0.95],
    "p_mutation":  [0.01, 0.05, 0.10, 0.20, 0.30],
}

# Colores por serie (un color por valor dentro de cada barrido)
SERIES_COLORS = ["#00C9A7", "#FFC300", "#FF5757", "#A78BFA", "#38BDF8"]


# ---------------------------------------------------------------------------
# Función central: ejecutar un experimento con un config dado
# ---------------------------------------------------------------------------

def run_experiment(cities, config_overrides: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ejecuta run_ga() de P1 con BASE_CONFIG + overrides, y devuelve
    un diccionario con métricas listas para tabular y graficar.

    Parámetros
    ----------
    cities          : lista de tuplas (x, y) cargadas con load_cities_from_csv
    config_overrides: dict con los parámetros que varían en este experimento

    Retorna
    -------
    dict con:
        params          — parámetros usados
        best_fitness    — mejor distancia encontrada por el AG
        nn_fitness      — distancia de la heurística vecino más cercano
        rel_error_pct   — error relativo AG vs NN en %
        conv_gen        — generación de convergencia (-1 si no converge)
        elapsed_s       — tiempo de ejecución en segundos
        fitness_history — historial completo (para gráficas de curvas)
    """
    config = {**BASE_CONFIG, "cities": cities, **config_overrides}

    t0 = time.perf_counter()
    result = run_ga(config)
    elapsed = time.perf_counter() - t0

    # Baseline NN: usa la función de P1 directamente
    dist_matrix = build_distance_matrix(cities)
    _, nn_fitness = nearest_neighbor_baseline(dist_matrix, start=0)

    ag_fitness = result["best_fitness"]
    rel_error  = (ag_fitness - nn_fitness) / nn_fitness * 100.0

    # Generación de convergencia usando la función de P2
    conv_gen = detect_convergence(result["fitness_history"])

    return {
        "params":         config_overrides,
        "best_fitness":   ag_fitness,
        "nn_fitness":     nn_fitness,
        "rel_error_pct":  rel_error,
        "conv_gen":       conv_gen,
        "elapsed_s":      elapsed,
        "fitness_history": result["fitness_history"],
    }


# ---------------------------------------------------------------------------
# Barrido de un parámetro
# ---------------------------------------------------------------------------

def sweep_parameter(
    cities,
    param_name: str,
    param_values: List[Any],
    verbose: bool = True,
) -> List[Dict[str, Any]]:
    """
    Ejecuta run_experiment() para cada valor de param_name,
    manteniendo todos los demás parámetros en BASE_CONFIG.

    Retorna lista de resultados en el mismo orden que param_values.
    """
    results = []
    for val in param_values:
        if verbose:
            print(f"  [{param_name}={val}] ejecutando...", end=" ", flush=True)
        res = run_experiment(cities, {param_name: val})
        results.append(res)
        if verbose:
            print(f"fitness={res['best_fitness']:,.0f}  "
                  f"error={res['rel_error_pct']:+.1f}%  "
                  f"conv_gen={res['conv_gen']}  "
                  f"t={res['elapsed_s']:.1f}s")
    return results


# ---------------------------------------------------------------------------
# Construcción de tabla de resultados (pandas DataFrame)
# ---------------------------------------------------------------------------

def build_results_table(
    sweep_results: List[Dict[str, Any]],
    param_name: str,
    param_values: List[Any],
) -> pd.DataFrame:
    """
    Convierte los resultados de un barrido en un DataFrame ordenado
    con las columnas que pide el punto f.
    """
    rows = []
    for val, res in zip(param_values, sweep_results):
        rows.append({
            param_name:             val,
            "Fitness AG":           round(res["best_fitness"], 2),
            "Fitness NN (baseline)":round(res["nn_fitness"],   2),
            "Error relativo (%)":   round(res["rel_error_pct"], 2),
            "Gen. convergencia":    res["conv_gen"],
            "Tiempo (s)":           round(res["elapsed_s"], 2),
        })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Gráficas
# ---------------------------------------------------------------------------

def plot_sweep_curves(
    sweep_results: List[Dict[str, Any]],
    param_name: str,
    param_values: List[Any],
    title_prefix: str = "f",
    save_prefix: str = "p3",
):
    """
    Para cada valor del parámetro barrido, grafica la curva de mejor
    fitness por generación. Permite comparar convergencia visualmente.
    """
    fig, ax = plt.subplots(figsize=(13, 5))
    fig.patch.set_facecolor(PALETTE["bg"])

    for i, (val, res) in enumerate(zip(param_values, sweep_results)):
        bests = [g["best"] for g in res["fitness_history"]]
        gens  = list(range(len(bests)))
        color = SERIES_COLORS[i % len(SERIES_COLORS)]
        ax.plot(gens, bests, color=color, lw=1.8,
                label=f"{param_name}={val}")

    ax.set_xlabel("Generación")
    ax.set_ylabel("Mejor fitness (distancia)")
    ax.set_title(
        f"{title_prefix} — Convergencia por {param_name}",
        fontweight="bold"
    )
    ax.legend(fontsize=8, loc="upper right")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    fname = f"{save_prefix}_convergencia_{param_name}.png"
    fig.savefig(fname, dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    print(f"  [guardado] {fname}")
    plt.show()
    return fig


def plot_bar_fitness(
    sweep_results: List[Dict[str, Any]],
    param_name: str,
    param_values: List[Any],
    title_prefix: str = "f",
    save_prefix: str = "p3",
):
    """
    Barras comparativas: fitness AG vs baseline NN para cada valor del
    parámetro. Facilita ver cuánto mejora (o empeora) el AG respecto
    al vecino más cercano al cambiar el parámetro.
    """
    ag_vals = [r["best_fitness"] for r in sweep_results]
    nn_val  = sweep_results[0]["nn_fitness"]   # NN es constante (mismas ciudades)
    x       = np.arange(len(param_values))
    width   = 0.35

    fig, ax = plt.subplots(figsize=(11, 5))
    fig.patch.set_facecolor(PALETTE["bg"])

    bars_ag = ax.bar(x, ag_vals, width, label="AG", color=PALETTE["best"],
                     alpha=0.85)
    ax.axhline(nn_val, color=PALETTE["worst"], lw=1.5, linestyle="--",
               label=f"NN baseline ({nn_val:,.0f})")

    ax.set_xticks(x)
    ax.set_xticklabels([str(v) for v in param_values])
    ax.set_xlabel(param_name)
    ax.set_ylabel("Fitness (distancia total)")
    ax.set_title(f"{title_prefix} — Fitness por {param_name}",
                 fontweight="bold")
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3, axis="y")

    # Etiquetar barras con error relativo
    for bar, res in zip(bars_ag, sweep_results):
        err = res["rel_error_pct"]
        color = PALETTE["best"] if err <= 0 else PALETTE["worst"]
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() * 1.005,
            f"{err:+.1f}%",
            ha="center", va="bottom", fontsize=8, color=color
        )

    plt.tight_layout()
    fname = f"{save_prefix}_fitness_{param_name}.png"
    fig.savefig(fname, dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    print(f"  [guardado] {fname}")
    plt.show()
    return fig


def plot_table_figure(
    df: pd.DataFrame,
    param_name: str,
    title_prefix: str = "f",
    save_prefix: str = "p3",
):
    """
    Renderiza el DataFrame como tabla visual (matplotlib) con el mismo
    estilo oscuro que usan los compañeros en P2.
    """
    fig, ax = plt.subplots(figsize=(12, max(3, len(df) * 0.7 + 1.5)))
    fig.patch.set_facecolor(PALETTE["bg"])
    ax.axis("off")

    col_labels = list(df.columns)
    cell_text  = df.astype(str).values.tolist()

    tbl = ax.table(
        cellText=cell_text,
        colLabels=col_labels,
        cellLoc="center",
        loc="center",
    )
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(9)
    tbl.scale(1, 2.0)

    for (r, c), cell in tbl.get_celld().items():
        if r == 0:
            cell.set_facecolor(PALETTE["grid"])
        else:
            cell.set_facecolor(PALETTE["bg"])
        cell.set_edgecolor(PALETTE["grid"])
        cell.set_text_props(color=PALETTE["text"])

    ax.set_title(
        f"{title_prefix} — Tabla de resultados: variación de {param_name}",
        fontweight="bold", color=PALETTE["text"], pad=16, fontsize=11
    )

    plt.tight_layout()
    fname = f"{save_prefix}_tabla_{param_name}.png"
    fig.savefig(fname, dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    print(f"  [guardado] {fname}")
    plt.show()
    return fig


def plot_summary_dashboard(all_tables: Dict[str, pd.DataFrame], save_prefix: str = "p3"):
    """
    Dashboard resumen: una fila por parámetro analizado.
    Muestra error relativo (%) en función del valor del parámetro.
    Permite comparar el impacto de cada parámetro de un vistazo.
    """
    params = list(all_tables.keys())
    fig, axes = plt.subplots(1, len(params), figsize=(5 * len(params), 5))
    fig.patch.set_facecolor(PALETTE["bg"])

    if len(params) == 1:
        axes = [axes]

    for ax, pname in zip(axes, params):
        df = all_tables[pname]
        x  = df[pname].astype(str)
        y  = df["Error relativo (%)"]
        colors = [PALETTE["best"] if v <= 0 else PALETTE["worst"] for v in y]

        ax.bar(x, y, color=colors, alpha=0.85)
        ax.axhline(0, color=PALETTE["text"], lw=0.8, linestyle="--", alpha=0.5)
        ax.set_xlabel(pname, fontsize=9)
        ax.set_ylabel("Error relativo vs NN (%)", fontsize=9)
        ax.set_title(f"Impacto de {pname}", fontweight="bold", fontsize=10)
        ax.grid(True, alpha=0.3, axis="y")
        ax.tick_params(axis="x", labelsize=8)

    fig.suptitle("f — Resumen: Impacto de parámetros sobre calidad de solución",
                 fontsize=13, fontweight="bold", color=PALETTE["text"])
    plt.tight_layout()
    fname = f"{save_prefix}_dashboard_resumen.png"
    fig.savefig(fname, dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    print(f"  [guardado] {fname}")
    plt.show()
    return fig


# ---------------------------------------------------------------------------
# Pipeline completo
# ---------------------------------------------------------------------------

def run_full_analysis(
    csv_path: str = "dataset/cities_100_101112.csv",
    save_prefix: str = "p3",
    verbose: bool = True,
) -> Dict[str, pd.DataFrame]:
    """
    Ejecuta el análisis experimental completo del punto f.

    Pasos:
        1. Carga ciudades desde CSV usando load_cities_from_csv() de P1.
        2. Para cada parámetro en SWEEP, ejecuta el barrido completo.
        3. Genera tabla, gráfica de curvas y gráfica de barras para cada uno.
        4. Genera dashboard de resumen final.
        5. Retorna dict {param_name: DataFrame} con todos los resultados.

    Parámetros
    ----------
    csv_path   : ruta al CSV con columnas x, y (formato de P1)
    save_prefix: prefijo para los archivos PNG generados
    verbose    : si True imprime progreso en consola
    """
    # 1. Carga de datos usando P1
    print(f"\n{'='*60}")
    print(f"  PUNTO F — Análisis Experimental de Parámetros")
    print(f"{'='*60}")
    print(f"[P3] Cargando ciudades desde: {csv_path}")
    cities = load_cities_from_csv(csv_path)
    print(f"[P3] {len(cities)} ciudades cargadas.\n")

    # Baseline único (mismas ciudades para todos los experimentos)
    dist_matrix = build_distance_matrix(cities)
    _, nn_fitness = nearest_neighbor_baseline(dist_matrix, start=0)
    print(f"[P3] Baseline NN: {nn_fitness:,.2f}\n")

    all_tables: Dict[str, pd.DataFrame] = {}

    # 2. Barrido de cada parámetro
    for param_name, param_values in SWEEP.items():
        print(f"{'─'*60}")
        print(f"[P3] Barrido de {param_name}: {param_values}")
        results = sweep_parameter(cities, param_name, param_values, verbose=verbose)

        # 3. Tabla
        df = build_results_table(results, param_name, param_values)
        all_tables[param_name] = df
        print(f"\n  Tabla de resultados — {param_name}:")
        print(df.to_string(index=False))
        print()

        # 3. Gráficas
        plot_sweep_curves(results, param_name, param_values,
                          save_prefix=save_prefix)
        plot_bar_fitness(results,  param_name, param_values,
                         save_prefix=save_prefix)
        plot_table_figure(df, param_name, save_prefix=save_prefix)

    # 4. Dashboard resumen
    print(f"{'─'*60}")
    print("[P3] Generando dashboard de resumen...")
    plot_summary_dashboard(all_tables, save_prefix=save_prefix)

    print(f"\n{'='*60}")
    print("  Análisis experimental completado.")
    print(f"{'='*60}\n")

    return all_tables


# ---------------------------------------------------------------------------
# Ejecución directa
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    csv = sys.argv[1] if len(sys.argv) > 1 else "dataset/cities_100_101112.csv"
    run_full_analysis(csv_path=csv)
