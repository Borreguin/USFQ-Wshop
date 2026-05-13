"""
main.py — Punto de entrada principal del proyecto GA-TSP.

Ejecutar desde la carpeta ProyectoFinal/TSP/:
    python main.py

El script:
  1. Carga el dataset de ciudades (>= 100 ciudades).
  2. Calcula la heuristica Vecino Cercano (baseline).
  3. Ejecuta el Algoritmo Genetico.
  4. Compara ambas soluciones.
  5. Genera graficas de fitness, diversidad y rutas.
  6. Imprime tabla de resultados.
"""

import os
import sys
import time
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")          # sin ventana interactiva
import matplotlib.pyplot as plt

# ── rutas de importacion ────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(__file__))

from ga_tsp.distances import load_cities, compute_distance_matrix, tour_distance
from ga_tsp.ga import GeneticAlgorithmTSP
from ga_tsp.nearest_neighbor import nearest_neighbor_tour
from ga_tsp.local_search import two_opt
from plots.fitness_plot import plot_fitness_evolution
from plots.diversity_plot import plot_diversity
from plots.route_plot import plot_comparison

# ── configuracion ───────────────────────────────────────────────────
DATASET    = os.path.join(os.path.dirname(__file__), "dataset", "cities_100_123.csv")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "results")

GA_CONFIG = dict(
    pop_size      = 150,
    mutation_rate = 0.02,
    n_elite       = 5,
    tournament_k  = 5,
    mutation_type = "combined",
    n_generations = 1000,
    seed          = 42,
    verbose       = True,
)


# ── helpers ─────────────────────────────────────────────────────────

def separator(char="=", n=60):
    print(char * n)


# ── main ─────────────────────────────────────────────────────────────

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    separator()
    print("  GA-TSP  |  Proyecto Final MSDS 6004 — USFQ")
    print("  Grupo 5: Kevin Vitery, Raquel Pacheco,")
    print("           Gustavo Baru, Nancy Altamirano")
    separator()

    # 1. Cargar dataset
    print(f"\n[1/5] Cargando dataset: {os.path.basename(DATASET)}")
    cities = load_cities(DATASET)
    n = len(cities)
    print(f"  {n} ciudades cargadas")
    dist_matrix = compute_distance_matrix(cities)

    # 2. Heuristica Vecino Cercano (baseline)
    print("\n[2/5] Heuristica Vecino Cercano (baseline)...")
    t0 = time.time()
    nn_tour, nn_dist = nearest_neighbor_tour(dist_matrix, start=0)
    nn_time = time.time() - t0
    print(f"  NN distancia : {nn_dist:.2f}")
    print(f"  NN tiempo    : {nn_time:.3f} s")

    # 3. Algoritmo Genetico
    print("\n[3/5] Algoritmo Genetico...")
    print(f"  Config: pop={GA_CONFIG['pop_size']} | "
          f"mut={GA_CONFIG['mutation_rate']} | "
          f"elite={GA_CONFIG['n_elite']} | "
          f"torneo k={GA_CONFIG['tournament_k']} | "
          f"generaciones={GA_CONFIG['n_generations']}")
    t0 = time.time()
    ga = GeneticAlgorithmTSP(dist_matrix=dist_matrix, **GA_CONFIG)
    ga_tour, ga_dist = ga.run()
    ga_time = time.time() - t0
    print(f"\n  GA distancia : {ga_dist:.2f}")
    print(f"  GA tiempo    : {ga_time:.1f} s")

    # Pos-procesamiento: 2-opt sobre la mejor solucion del GA
    print("\n[3b/5] Post-procesamiento 2-opt sobre mejor tour GA...")
    t0 = time.time()
    ga_tour_2opt = two_opt(ga_tour, dist_matrix)
    ga_dist_2opt = tour_distance(ga_tour_2opt, dist_matrix)
    opt_time = time.time() - t0
    print(f"  GA+2opt dist : {ga_dist_2opt:.2f}  (t={opt_time:.1f}s)")

    improvement_ga   = (nn_dist - ga_dist) / nn_dist * 100
    improvement_2opt = (nn_dist - ga_dist_2opt) / nn_dist * 100

    # 4. Tabla de resultados
    separator("-")
    print(f"{'Metodo':<26} {'Distancia':>12} {'Tiempo':>10} {'Mejora vs NN':>14}")
    separator("-")
    print(f"{'Vecino Cercano (NN)':<26} {nn_dist:>12.2f} {nn_time:>9.3f}s {'—':>14}")
    print(f"{'Algoritmo Genetico':<26} {ga_dist:>12.2f} {ga_time:>9.1f}s {improvement_ga:>13.2f}%")
    print(f"{'GA + 2-opt':<26} {ga_dist_2opt:>12.2f} {opt_time:>9.1f}s {improvement_2opt:>13.2f}%")
    separator("-")

    # 5. Graficas
    print("\n[4/5] Generando graficas...")

    plot_fitness_evolution(
        ga.best_fitness_history,
        ga.avg_fitness_history,
        ga.worst_fitness_history,
        ga.best_dist_history,
        title=f"GA-TSP ({n} ciudades) — Evolucion del Fitness",
        save_path=os.path.join(OUTPUT_DIR, "fitness_evolution.png"),
    )
    plot_diversity(
        ga.diversity_history,
        ga.best_fitness_history,
        ga.best_dist_history,
        save_path=os.path.join(OUTPUT_DIR, "diversity.png"),
    )
    plot_comparison(
        cities, nn_tour, ga_tour_2opt, nn_dist, ga_dist_2opt,
        save_path=os.path.join(OUTPUT_DIR, "route_comparison.png"),
    )
    plt.close("all")

    # 6. Guardar resumen en CSV
    summary = pd.DataFrame([
        {"metodo": "Vecino Cercano",    "distancia": nn_dist,      "tiempo_s": round(nn_time, 3),  "mejora_pct": 0.0},
        {"metodo": "Algoritmo Genetico","distancia": ga_dist,      "tiempo_s": round(ga_time, 1),  "mejora_pct": round(improvement_ga, 2)},
        {"metodo": "GA + 2-opt",        "distancia": ga_dist_2opt, "tiempo_s": round(opt_time, 1), "mejora_pct": round(improvement_2opt, 2)},
    ])
    summary.to_csv(os.path.join(OUTPUT_DIR, "summary.csv"), index=False)

    print(f"\n[5/5] Resultados guardados en: {OUTPUT_DIR}/")
    separator()
    print("  Listo.")
    separator()


if __name__ == "__main__":
    main()
