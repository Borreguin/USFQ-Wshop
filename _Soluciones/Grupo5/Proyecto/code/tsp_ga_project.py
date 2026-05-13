"""
Proyecto final de IA - Resolucion del TSP mediante Algoritmos Geneticos
Grupo 5

Este script ejecuta un Algoritmo Genetico Elitista con representacion por permutaciones,
cruce OX, mutacion por inversion y refinamiento final 2-opt sobre todos los datasets CSV.
Tambien compara contra Nearest Neighbor y ejecuta un analisis experimental de parametros.

Estructura de entrada esperada: data/*.csv con columnas city, x, y
Salidas: results/*.csv y figures/*.png
"""
from __future__ import annotations

import glob
import json
import math
import random
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"
for p in [RESULTS, FIGURES]:
    p.mkdir(parents=True, exist_ok=True)

MASTER_SEED = 20260513
EPS = 1e-12

# Parametros base defendidos en el informe.
BASE_CONFIG = {
    "population_size": 100,
    "generations": 250,
    "crossover": "OX",
    "crossover_probability": 0.90,
    "mutation": "inversion",
    "mutation_probability": 0.15,
    "elitism": 2,
    "tournament_k": 3,
    "diversity_pair_samples": 40,
    "final_two_opt_passes": 60,
}


def dataset_stem(path: str | Path) -> str:
    """Normaliza nombres como cities_100_123(1).csv -> cities_100_123."""
    return Path(path).stem.replace("(1)", "")


def read_dataset(path: str | Path) -> Tuple[List[str], np.ndarray, pd.DataFrame]:
    df = pd.read_csv(path)
    df = df.rename(columns={c: c.strip().lower() for c in df.columns})
    required = {"city", "x", "y"}
    if not required.issubset(df.columns):
        raise ValueError(f"El archivo {path} debe contener columnas {required}.")

    df = df[["city", "x", "y"]].copy()
    df["city"] = df["city"].astype(str)
    df["x"] = pd.to_numeric(df["x"], errors="raise")
    df["y"] = pd.to_numeric(df["y"], errors="raise")

    # Si hubiera etiquetas de ciudad repetidas, se diferencian sin cambiar coordenadas.
    if df["city"].duplicated().any():
        counts = {}
        corrected = []
        for city in df["city"]:
            counts[city] = counts.get(city, 0) + 1
            corrected.append(city if counts[city] == 1 else f"{city}_{counts[city]}")
        df["city"] = corrected

    names = df["city"].tolist()
    coords = df[["x", "y"]].to_numpy(dtype=float)
    return names, coords, df


def distance_matrix(coords: np.ndarray) -> np.ndarray:
    """Matriz simetrica de distancias euclidianas."""
    diff = coords[:, None, :] - coords[None, :, :]
    return np.sqrt(np.sum(diff * diff, axis=2))


def route_length(route: np.ndarray, D: np.ndarray) -> float:
    """Distancia total de una ruta cerrada: ultima ciudad regresa a la primera."""
    return float(D[route, np.roll(route, -1)].sum())


def population_lengths(population: np.ndarray, D: np.ndarray) -> np.ndarray:
    return D[population, np.roll(population, -1, axis=1)].sum(axis=1)


def fitness_from_distance(distance: np.ndarray | float) -> np.ndarray | float:
    """El fitness se define como inverso de distancia; mayor fitness = mejor ruta."""
    return 1.0 / (distance + EPS)


def is_valid_permutation(route: np.ndarray, n: int) -> bool:
    """Valida: longitud n, sin repetidas y sin faltantes."""
    if len(route) != n:
        return False
    values = route.tolist()
    return len(set(values)) == n and set(values) == set(range(n))


def validate_population(population: np.ndarray, n: int) -> bool:
    return all(is_valid_permutation(ind, n) for ind in population)


def nearest_neighbor_best(D: np.ndarray) -> Tuple[np.ndarray, float]:
    """Heuristica greedy: se prueba cada ciudad como inicio y se conserva la mejor ruta."""
    n = D.shape[0]
    best_route = None
    best_len = math.inf
    for start in range(n):
        unvisited = set(range(n))
        route = [start]
        unvisited.remove(start)
        current = start
        while unvisited:
            next_city = min(unvisited, key=lambda j: D[current, j])
            route.append(next_city)
            unvisited.remove(next_city)
            current = next_city
        route_np = np.array(route, dtype=np.int32)
        length = route_length(route_np, D)
        if length < best_len:
            best_len = length
            best_route = route_np
    return best_route, best_len


def two_opt(route: np.ndarray, D: np.ndarray, max_passes: int = 60) -> Tuple[np.ndarray, float, int]:
    """Mejora local 2-opt: invierte segmentos si reduce la distancia total."""
    best = route.copy()
    best_len = route_length(best, D)
    n = len(best)
    improvements = 0

    improved = True
    passes = 0
    while improved and passes < max_passes:
        improved = False
        passes += 1
        for i in range(1, n - 2):
            a, b = best[i - 1], best[i]
            for k in range(i + 1, n - 1):
                c, d = best[k], best[(k + 1) % n]
                delta = (D[a, c] + D[b, d]) - (D[a, b] + D[c, d])
                if delta < -1e-10:
                    best[i:k + 1] = best[i:k + 1][::-1]
                    best_len += float(delta)
                    improvements += 1
                    improved = True
                    break
            if improved:
                break
    return best, float(best_len), improvements


def init_population(n: int, pop_size: int, rng: np.random.Generator, seed_route: Optional[np.ndarray] = None) -> np.ndarray:
    """Inicializacion valida: cada individuo es una permutacion completa de 0..n-1."""
    population = np.empty((pop_size, n), dtype=np.int32)
    start = 0
    if seed_route is not None:
        population[0] = seed_route
        start = 1
    for i in range(start, pop_size):
        population[i] = rng.permutation(n)
    return population


def ox_crossover(parent1: np.ndarray, parent2: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Order Crossover (OX): preserva un segmento del padre 1 y completa en el orden del padre 2."""
    n = len(parent1)
    a, b = sorted(rng.choice(n, size=2, replace=False))
    child = np.full(n, -1, dtype=np.int32)
    child[a:b + 1] = parent1[a:b + 1]
    used = set(child[a:b + 1].tolist())
    pos = (b + 1) % n
    for gene in np.concatenate([parent2[b + 1:], parent2[:b + 1]]):
        if int(gene) not in used:
            child[pos] = int(gene)
            used.add(int(gene))
            pos = (pos + 1) % n
    return child


def pmx_crossover(parent1: np.ndarray, parent2: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Partially Mapped Crossover (PMX), usado solo en el analisis experimental."""
    n = len(parent1)
    a, b = sorted(rng.choice(n, size=2, replace=False))
    child = np.full(n, -1, dtype=np.int32)
    child[a:b + 1] = parent1[a:b + 1]
    for i in range(a, b + 1):
        gene = int(parent2[i])
        if gene not in child:
            pos = i
            while True:
                mapped = int(parent1[pos])
                pos = int(np.where(parent2 == mapped)[0][0])
                if child[pos] == -1:
                    child[pos] = gene
                    break
    for i in range(n):
        if child[i] == -1:
            child[i] = parent2[i]
    return child


def mutate_inversion(route: np.ndarray, mutation_probability: float, rng: np.random.Generator) -> np.ndarray:
    """Mutacion por inversion: invierte un segmento; conserva todos los genes."""
    child = route.copy()
    if rng.random() < mutation_probability:
        a, b = sorted(rng.choice(len(child), size=2, replace=False))
        child[a:b + 1] = child[a:b + 1][::-1]
    return child


def mutate_swap(route: np.ndarray, mutation_probability: float, rng: np.random.Generator) -> np.ndarray:
    """Mutacion swap, incluida como alternativa de codigo."""
    child = route.copy()
    if rng.random() < mutation_probability:
        a, b = rng.choice(len(child), size=2, replace=False)
        child[a], child[b] = child[b], child[a]
    return child


def repair_permutation(route: np.ndarray, n: int) -> np.ndarray:
    """Mecanismo defensivo: corrige repetidos reemplazandolos por faltantes. No deberia activarse con OX+inversion."""
    repaired = route.copy()
    counts = {i: 0 for i in range(n)}
    for gene in repaired:
        if 0 <= int(gene) < n:
            counts[int(gene)] += 1
    missing = [i for i in range(n) if counts[i] == 0]
    seen = set()
    miss_idx = 0
    for idx, gene in enumerate(repaired):
        gene_int = int(gene)
        if gene_int in seen or gene_int < 0 or gene_int >= n:
            repaired[idx] = missing[miss_idx]
            miss_idx += 1
        else:
            seen.add(gene_int)
    return repaired


def tournament_select(population: np.ndarray, distances: np.ndarray, k: int, rng: np.random.Generator) -> np.ndarray:
    """Seleccion por torneo; gana la ruta de menor distancia entre k candidatos."""
    idx = rng.choice(len(population), size=k, replace=False)
    winner = idx[np.argmin(distances[idx])]
    return population[winner]


def diversity_metrics(population: np.ndarray, rng: np.random.Generator, pair_samples: int = 40) -> Tuple[float, float]:
    """Porcentaje de individuos unicos y distancia Hamming promedio normalizada (%)."""
    pop_size, n = population.shape
    unique_pct = len({tuple(row.tolist()) for row in population}) / pop_size * 100.0
    if pop_size < 2:
        return unique_pct, 0.0
    max_pairs = pop_size * (pop_size - 1) // 2
    samples = min(pair_samples, max_pairs)
    i_idx = rng.integers(0, pop_size, size=samples)
    j_idx = rng.integers(0, pop_size - 1, size=samples)
    j_idx = np.where(j_idx >= i_idx, j_idx + 1, j_idx)
    hamming_pct = float(np.mean(population[i_idx] != population[j_idx]) * 100.0)
    return float(unique_pct), hamming_pct

def classify_stagnation(history: pd.DataFrame, generations: int) -> str:
    """Diagnostico simple y explicable de convergencia/estancamiento."""
    final_no_improve = int(history["no_improve"].iloc[-1])
    unique_final = float(history["unique_pct"].iloc[-1])
    hamming_final = float(history["hamming_pct"].iloc[-1])
    window = max(40, int(generations * 0.20))

    if final_no_improve >= window and unique_final < 20 and hamming_final < 15:
        return "Posible convergencia prematura: largo periodo sin mejora y diversidad final baja."
    if final_no_improve >= window:
        return "Estancamiento final: no hubo mejora en el tramo final, aunque la poblacion aun conserva diversidad parcial."
    return "Convergencia activa: se observaron mejoras dentro del tramo final del algoritmo."


def run_ga(
    D: np.ndarray,
    pop_size: int = 120,
    generations: int = 350,
    crossover: str = "OX",
    crossover_probability: float = 0.90,
    mutation: str = "inversion",
    mutation_probability: float = 0.15,
    elitism: int = 2,
    tournament_k: int = 3,
    seed: int = 0,
    seed_route: Optional[np.ndarray] = None,
    diversity_pair_samples: int = 100,
) -> Dict:
    rng = np.random.default_rng(seed)
    n = D.shape[0]
    population = init_population(n, pop_size, rng, seed_route=seed_route)
    if not validate_population(population, n):
        raise RuntimeError("La poblacion inicial contiene soluciones invalidas.")

    cx_fn = ox_crossover if crossover.upper() == "OX" else pmx_crossover
    mut_fn = mutate_inversion if mutation == "inversion" else mutate_swap

    history = []
    best_route = None
    best_distance = math.inf
    best_generation = 0
    no_improve = 0
    invalid_children = 0
    repaired_children = 0
    invalid_population_generations = 0

    for generation in range(generations + 1):
        distances = population_lengths(population, D)
        fitness_values = fitness_from_distance(distances)
        order = np.argsort(distances)

        generation_best_distance = float(distances[order[0]])
        if generation_best_distance < best_distance - 1e-10:
            best_distance = generation_best_distance
            best_route = population[order[0]].copy()
            best_generation = generation
            no_improve = 0
        else:
            no_improve += 1

        unique_pct, hamming_pct = diversity_metrics(population, rng, diversity_pair_samples)
        history.append({
            "generation": generation,
            "best_distance_so_far": float(best_distance),
            "generation_best_distance": generation_best_distance,
            "avg_distance": float(np.mean(distances)),
            "worst_distance": float(np.max(distances)),
            "best_fitness": float(np.max(fitness_values)),
            "avg_fitness": float(np.mean(fitness_values)),
            "worst_fitness": float(np.min(fitness_values)),
            "unique_pct": unique_pct,
            "hamming_pct": hamming_pct,
            "no_improve": int(no_improve),
        })

        if generation == generations:
            break

        new_population = np.empty_like(population)
        elite_count = min(elitism, pop_size)
        new_population[:elite_count] = population[order[:elite_count]]
        fill = elite_count
        while fill < pop_size:
            parent1 = tournament_select(population, distances, tournament_k, rng)
            parent2 = tournament_select(population, distances, tournament_k, rng)
            if rng.random() < crossover_probability:
                child = cx_fn(parent1, parent2, rng)
            else:
                child = parent1.copy()
            child = mut_fn(child, mutation_probability, rng)
            if not is_valid_permutation(child, n):
                invalid_children += 1
                child = repair_permutation(child, n)
                repaired_children += 1
            new_population[fill] = child
            fill += 1

        if not validate_population(new_population, n):
            invalid_population_generations += 1
        population = new_population

    history_df = pd.DataFrame(history)
    return {
        "best_route": best_route,
        "best_distance": float(best_distance),
        "best_generation": int(best_generation),
        "history": history_df,
        "valid_solution": is_valid_permutation(best_route, n),
        "invalid_children": int(invalid_children),
        "repaired_children": int(repaired_children),
        "invalid_population_generations": int(invalid_population_generations),
        "stagnation": classify_stagnation(history_df, generations),
    }


def save_route_csv(route: np.ndarray, names: List[str], coords: np.ndarray, path: Path):
    rows = []
    for order, idx in enumerate(route, start=1):
        rows.append({"visit_order": order, "city": names[int(idx)], "x": coords[int(idx), 0], "y": coords[int(idx), 1]})
    # cierre de ruta para dejar claro el retorno al origen
    first = int(route[0])
    rows.append({"visit_order": len(route) + 1, "city": names[first] + " (retorno)", "x": coords[first, 0], "y": coords[first, 1]})
    pd.DataFrame(rows).to_csv(path, index=False)


def plot_fitness(history: pd.DataFrame, dataset: str, path: Path):
    plt.figure(figsize=(9, 5.2))
    plt.plot(history["generation"], history["best_fitness"], label="Mejor fitness")
    plt.plot(history["generation"], history["avg_fitness"], label="Fitness promedio")
    plt.plot(history["generation"], history["worst_fitness"], label="Peor fitness")
    plt.xlabel("Generacion")
    plt.ylabel("Fitness = 1 / distancia")
    plt.title(f"Evolucion del fitness - {dataset}")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(path, dpi=180)
    plt.close()


def plot_distance(history: pd.DataFrame, dataset: str, path: Path):
    plt.figure(figsize=(9, 5.2))
    plt.plot(history["generation"], history["best_distance_so_far"], label="Mejor distancia acumulada")
    plt.plot(history["generation"], history["avg_distance"], label="Distancia promedio")
    plt.plot(history["generation"], history["worst_distance"], label="Peor distancia")
    plt.xlabel("Generacion")
    plt.ylabel("Distancia total")
    plt.title(f"Convergencia por distancia - {dataset}")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(path, dpi=180)
    plt.close()


def plot_diversity(history: pd.DataFrame, dataset: str, path: Path):
    plt.figure(figsize=(9, 5.2))
    plt.plot(history["generation"], history["unique_pct"], label="Individuos unicos (%)")
    plt.plot(history["generation"], history["hamming_pct"], label="Distancia Hamming promedio (%)")
    plt.xlabel("Generacion")
    plt.ylabel("Diversidad poblacional (%)")
    plt.title(f"Diversidad poblacional - {dataset}")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(path, dpi=180)
    plt.close()


def plot_route(route: np.ndarray, names: List[str], coords: np.ndarray, dataset: str, path: Path):
    closed = np.append(route, route[0])
    plt.figure(figsize=(7.2, 6.5))
    plt.plot(coords[closed, 0], coords[closed, 1], marker="o", markersize=3, linewidth=1.0)
    plt.scatter(coords[route[0], 0], coords[route[0], 1], marker="s", s=70, label="Inicio/fin")
    plt.xlabel("x")
    plt.ylabel("y")
    plt.title(f"Mejor ruta encontrada - {dataset}")
    plt.grid(True, alpha=0.25)
    plt.legend()
    plt.tight_layout()
    plt.savefig(path, dpi=180)
    plt.close()


def panel_from_histories(histories: Dict[str, pd.DataFrame], metric_cols: List[str], labels: List[str], ylabel: str, title: str, path: Path):
    datasets = list(histories.keys())
    n = len(datasets)
    cols = 2
    rows = math.ceil(n / cols)
    fig, axes = plt.subplots(rows, cols, figsize=(13, rows * 3.2))
    axes = np.array(axes).reshape(-1)
    for ax, ds in zip(axes, datasets):
        hist = histories[ds]
        for col, label in zip(metric_cols, labels):
            ax.plot(hist["generation"], hist[col], label=label, linewidth=1.2)
        ax.set_title(ds, fontsize=9)
        ax.grid(True, alpha=0.25)
        ax.set_xlabel("Gen.")
        ax.set_ylabel(ylabel)
    for ax in axes[n:]:
        ax.axis("off")
    handles, leg_labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, leg_labels, loc="upper center", ncol=len(labels), bbox_to_anchor=(0.5, 0.995))
    fig.suptitle(title, y=1.025, fontsize=13)
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def create_aggregate_plots(summary: pd.DataFrame, param_df: pd.DataFrame):
    # Comparacion NN vs GA+2opt
    x = np.arange(len(summary))
    labels = summary["dataset"].tolist()
    plt.figure(figsize=(12, 5.8))
    width = 0.36
    plt.bar(x - width / 2, summary["nn_distance"], width, label="Nearest Neighbor")
    plt.bar(x + width / 2, summary["ga_2opt_distance"], width, label="AG elitista + 2-opt")
    plt.xticks(x, labels, rotation=50, ha="right")
    plt.ylabel("Distancia total")
    plt.title("Comparacion de calidad: heuristica NN vs AG elitista + 2-opt")
    plt.grid(axis="y", alpha=0.25)
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURES / "comparacion_nn_vs_ag2opt.png", dpi=180)
    plt.close()

    plt.figure(figsize=(11, 5.5))
    plt.bar(summary["dataset"], summary["gap_vs_nn_pct"])
    plt.axhline(0, linewidth=1)
    plt.xticks(rotation=50, ha="right")
    plt.ylabel("Gap relativo vs NN (%)")
    plt.title("Error relativo respecto a la heuristica NN (negativo = mejora)")
    plt.grid(axis="y", alpha=0.25)
    plt.tight_layout()
    plt.savefig(FIGURES / "gap_relativo_vs_nn.png", dpi=180)
    plt.close()

    plt.figure(figsize=(11, 5.5))
    plt.bar(summary["dataset"], summary["unique_pct_final"], label="Individuos unicos finales (%)")
    plt.xticks(rotation=50, ha="right")
    plt.ylabel("Diversidad final (%)")
    plt.title("Diversidad final por dataset")
    plt.grid(axis="y", alpha=0.25)
    plt.tight_layout()
    plt.savefig(FIGURES / "diversidad_final_por_dataset.png", dpi=180)
    plt.close()

    # Parametros: se guardan vistas resumidas.
    param_sorted = param_df.sort_values("best_distance_ga_2opt", ascending=True).reset_index(drop=True)
    top = param_sorted.head(20).copy()
    top["config"] = top.apply(lambda r: f"P{int(r.pop_size)}-{r.crossover}-pc{r.crossover_prob}-pm{r.mutation_prob}", axis=1)
    plt.figure(figsize=(13, 6))
    plt.bar(top["config"], top["best_distance_ga_2opt"])
    plt.xticks(rotation=60, ha="right")
    plt.ylabel("Distancia AG + 2-opt")
    plt.title("Analisis experimental: mejores configuraciones de parametros")
    plt.grid(axis="y", alpha=0.25)
    plt.tight_layout()
    plt.savefig(FIGURES / "parametros_top_configuraciones.png", dpi=180)
    plt.close()

    pop_summary = param_df.groupby("pop_size", as_index=False).agg(
        avg_distance=("best_distance_ga_2opt", "mean"), avg_unique=("unique_pct_final", "mean"), avg_hamming=("hamming_pct_final", "mean")
    )
    plt.figure(figsize=(8.5, 5))
    plt.plot(pop_summary["pop_size"], pop_summary["avg_distance"], marker="o", label="Distancia promedio")
    plt.xlabel("Tamano de poblacion")
    plt.ylabel("Distancia promedio AG + 2-opt")
    plt.title("Efecto del tamano de poblacion")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(FIGURES / "parametros_poblacion_distancia.png", dpi=180)
    plt.close()

    mut_summary = param_df.groupby("mutation_prob", as_index=False).agg(
        avg_distance=("best_distance_ga_2opt", "mean"), avg_unique=("unique_pct_final", "mean"), avg_hamming=("hamming_pct_final", "mean")
    )
    plt.figure(figsize=(8.5, 5))
    plt.plot(mut_summary["mutation_prob"], mut_summary["avg_distance"], marker="o", label="Distancia promedio")
    plt.xlabel("Probabilidad de mutacion")
    plt.ylabel("Distancia promedio AG + 2-opt")
    plt.title("Efecto de la probabilidad de mutacion")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(FIGURES / "parametros_mutacion_distancia.png", dpi=180)
    plt.close()

    cx_summary = param_df.groupby(["crossover", "crossover_prob"], as_index=False).agg(
        avg_distance=("best_distance_ga_2opt", "mean"), avg_unique=("unique_pct_final", "mean")
    )
    cx_summary["config"] = cx_summary.apply(lambda r: f"{r.crossover} pc={r.crossover_prob}", axis=1)
    plt.figure(figsize=(8.5, 5))
    plt.bar(cx_summary["config"], cx_summary["avg_distance"])
    plt.ylabel("Distancia promedio AG + 2-opt")
    plt.title("Efecto de la parametrizacion del crossover")
    plt.grid(axis="y", alpha=0.25)
    plt.tight_layout()
    plt.savefig(FIGURES / "parametros_crossover_distancia.png", dpi=180)
    plt.close()


def run_parameter_experiment(largest_dataset_path: Path) -> pd.DataFrame:
    names, coords, _ = read_dataset(largest_dataset_path)
    D = distance_matrix(coords)
    nn_route, nn_len = nearest_neighbor_best(D)
    nn_2opt_route, nn_2opt_len, _ = two_opt(nn_route, D, max_passes=BASE_CONFIG["final_two_opt_passes"])

    rows = []
    pop_sizes = [60, 100, 140]
    crossovers = ["OX", "PMX"]
    crossover_probs = [0.80, 0.90]
    mutation_probs = [0.05, 0.20]
    exp_generations = 40
    seed_base = MASTER_SEED + 7000
    experiment_id = 0
    for pop_size in pop_sizes:
        for crossover in crossovers:
            for pc in crossover_probs:
                for pm in mutation_probs:
                    experiment_id += 1
                    result = run_ga(
                        D,
                        pop_size=pop_size,
                        generations=exp_generations,
                        crossover=crossover,
                        crossover_probability=pc,
                        mutation="inversion",
                        mutation_probability=pm,
                        elitism=2,
                        tournament_k=3,
                        seed=seed_base + experiment_id,
                        seed_route=nn_route,
                        diversity_pair_samples=20,
                    )
                    final_route, final_len, improvements = two_opt(result["best_route"], D, max_passes=15)
                    hist = result["history"]
                    rows.append({
                        "dataset": dataset_stem(largest_dataset_path),
                        "n_ciudades": len(names),
                        "pop_size": pop_size,
                        "crossover": crossover,
                        "crossover_prob": pc,
                        "mutation": "inversion",
                        "mutation_prob": pm,
                        "generations": exp_generations,
                        "nn_distance": nn_len,
                        "nn_2opt_distance": nn_2opt_len,
                        "best_distance_ga": result["best_distance"],
                        "best_distance_ga_2opt": final_len,
                        "two_opt_improvements": improvements,
                        "best_generation": result["best_generation"],
                        "final_no_improve": int(hist["no_improve"].iloc[-1]),
                        "unique_pct_final": float(hist["unique_pct"].iloc[-1]),
                        "hamming_pct_final": float(hist["hamming_pct"].iloc[-1]),
                        "gap_vs_nn_pct": ((final_len - nn_len) / nn_len) * 100.0,
                        "gap_vs_nn2_pct": ((final_len - nn_2opt_len) / nn_2opt_len) * 100.0,
                        "valid_solution": is_valid_permutation(final_route, len(names)),
                    })
    return pd.DataFrame(rows).sort_values("best_distance_ga_2opt", ascending=True).reset_index(drop=True)


def main():
    np.random.seed(MASTER_SEED)
    random.seed(MASTER_SEED)
    csv_files = sorted(DATA.glob("cities_*.csv"), key=lambda p: dataset_stem(p))
    if not csv_files:
        raise FileNotFoundError(f"No se encontraron archivos CSV en {DATA}")

    histories: Dict[str, pd.DataFrame] = {}
    summary_rows = []
    validation_rows = []
    start_time = time.time()

    for i, path in enumerate(csv_files, start=1):
        name = dataset_stem(path)
        names, coords, df = read_dataset(path)
        n = len(names)
        D = distance_matrix(coords)

        nn_route, nn_len = nearest_neighbor_best(D)
        nn_2opt_route, nn_2opt_len, nn_2opt_improvements = two_opt(nn_route, D, max_passes=BASE_CONFIG["final_two_opt_passes"])

        result = run_ga(
            D,
            pop_size=BASE_CONFIG["population_size"],
            generations=BASE_CONFIG["generations"],
            crossover=BASE_CONFIG["crossover"],
            crossover_probability=BASE_CONFIG["crossover_probability"],
            mutation=BASE_CONFIG["mutation"],
            mutation_probability=BASE_CONFIG["mutation_probability"],
            elitism=BASE_CONFIG["elitism"],
            tournament_k=BASE_CONFIG["tournament_k"],
            seed=MASTER_SEED + i,
            seed_route=nn_route,
            diversity_pair_samples=BASE_CONFIG["diversity_pair_samples"],
        )
        ga_2opt_route, ga_2opt_len, ga_2opt_improvements = two_opt(
            result["best_route"], D, max_passes=BASE_CONFIG["final_two_opt_passes"]
        )
        hist = result["history"]
        histories[name] = hist
        hist.to_csv(RESULTS / f"{name}_history.csv", index=False)
        save_route_csv(ga_2opt_route, names, coords, RESULTS / f"{name}_best_route.csv")

        plot_fitness(hist, name, FIGURES / f"{name}_fitness.png")
        plot_distance(hist, name, FIGURES / f"{name}_distancia_convergencia.png")
        plot_diversity(hist, name, FIGURES / f"{name}_diversidad.png")
        plot_route(ga_2opt_route, names, coords, name, FIGURES / f"{name}_ruta.png")

        # Correlaciones para analizar relacion diversidad-calidad/convergencia.
        corr_unique_distance = hist["unique_pct"].corr(hist["best_distance_so_far"])
        corr_hamming_distance = hist["hamming_pct"].corr(hist["best_distance_so_far"])
        corr_unique_no_improve = hist["unique_pct"].corr(hist["no_improve"])

        summary_rows.append({
            "dataset": name,
            "n_ciudades": n,
            "nn_distance": nn_len,
            "nn_2opt_distance": nn_2opt_len,
            "ga_distance": result["best_distance"],
            "ga_2opt_distance": ga_2opt_len,
            "gap_vs_nn_pct": ((ga_2opt_len - nn_len) / nn_len) * 100.0,
            "gap_vs_nn2_pct": ((ga_2opt_len - nn_2opt_len) / nn_2opt_len) * 100.0,
            "best_generation": result["best_generation"],
            "final_no_improve": int(hist["no_improve"].iloc[-1]),
            "unique_pct_final": float(hist["unique_pct"].iloc[-1]),
            "hamming_pct_final": float(hist["hamming_pct"].iloc[-1]),
            "corr_unique_vs_best_distance": corr_unique_distance,
            "corr_hamming_vs_best_distance": corr_hamming_distance,
            "corr_unique_vs_no_improve": corr_unique_no_improve,
            "valid_solution": bool(is_valid_permutation(ga_2opt_route, n)),
            "invalid_children": result["invalid_children"],
            "repaired_children": result["repaired_children"],
            "invalid_population_generations": result["invalid_population_generations"],
            "stagnation": result["stagnation"],
        })
        validation_rows.append({
            "dataset": name,
            "n_ciudades": n,
            "ciudades_duplicadas_en_entrada": int(df["city"].duplicated().sum()),
            "ruta_nn_valida": is_valid_permutation(nn_route, n),
            "ruta_nn_2opt_valida": is_valid_permutation(nn_2opt_route, n),
            "ruta_ag_valida": is_valid_permutation(result["best_route"], n),
            "ruta_ag_2opt_valida": is_valid_permutation(ga_2opt_route, n),
            "hijos_invalidos_generados": result["invalid_children"],
            "hijos_reparados": result["repaired_children"],
            "generaciones_con_poblacion_invalida": result["invalid_population_generations"],
            "sin_ciudades_repetidas": is_valid_permutation(ga_2opt_route, n),
            "sin_ciudades_faltantes": is_valid_permutation(ga_2opt_route, n),
        })

    summary = pd.DataFrame(summary_rows).sort_values("dataset").reset_index(drop=True)
    validation = pd.DataFrame(validation_rows).sort_values("dataset").reset_index(drop=True)
    summary.to_csv(RESULTS / "summary_all_datasets.csv", index=False)
    validation.to_csv(RESULTS / "validacion_permutaciones.csv", index=False)

    panel_from_histories(
        histories,
        metric_cols=["best_fitness", "avg_fitness", "worst_fitness"],
        labels=["Mejor", "Promedio", "Peor"],
        ylabel="Fitness",
        title="Evolucion del fitness por dataset",
        path=FIGURES / "panel_fitness_all_datasets.png",
    )
    panel_from_histories(
        histories,
        metric_cols=["unique_pct", "hamming_pct"],
        labels=["Unicos (%)", "Hamming (%)"],
        ylabel="Diversidad (%)",
        title="Evolucion de la diversidad por dataset",
        path=FIGURES / "panel_diversidad_all_datasets.png",
    )

    # Experimento de parametros sobre el dataset con mayor numero de ciudades.
    largest_path = max(csv_files, key=lambda p: len(read_dataset(p)[0]))
    param_df = run_parameter_experiment(largest_path)
    param_df.to_csv(RESULTS / "parameter_experiment_largest_dataset.csv", index=False)
    create_aggregate_plots(summary, param_df)

    config = {
        "master_seed": MASTER_SEED,
        "base_config": BASE_CONFIG,
        "n_datasets": len(csv_files),
        "datasets": [dataset_stem(p) for p in csv_files],
        "runtime_seconds": round(time.time() - start_time, 3),
        "fitness_definition": "fitness = 1 / total_route_distance",
        "distance_definition": "Euclidean closed tour distance including return to origin",
        "main_algorithm": "Algoritmo Genetico Generacional Elitista con representacion por permutaciones, OX, inversion y refinamiento final 2-opt",
    }
    with open(RESULTS / "run_config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    print("Ejecucion completada.")
    print(summary[["dataset", "n_ciudades", "nn_distance", "ga_2opt_distance", "gap_vs_nn_pct", "valid_solution"]].to_string(index=False))
    print(f"Resultados guardados en: {RESULTS}")
    print(f"Graficas guardadas en: {FIGURES}")


if __name__ == "__main__":
    main()
