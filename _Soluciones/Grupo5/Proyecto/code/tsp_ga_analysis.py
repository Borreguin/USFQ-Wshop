import os, glob, json, math, random, time
from pathlib import Path
from dataclasses import dataclass
from typing import List, Tuple, Dict, Callable
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path('/mnt/data/tsp_ga_project')
FIG = ROOT / 'figures'
RES = ROOT / 'results'
CODE = ROOT / 'code'
for p in [ROOT, FIG, RES, CODE]:
    p.mkdir(parents=True, exist_ok=True)

CSV_FILES = sorted(glob.glob('/mnt/data/cities_*.csv'))
MASTER_SEED = 20260512
np.random.seed(MASTER_SEED)
random.seed(MASTER_SEED)


def read_dataset(path: str):
    df = pd.read_csv(path)
    # normalize headers
    df = df.rename(columns={c: c.strip().lower() for c in df.columns})
    required = {'city','x','y'}
    if not required.issubset(df.columns):
        raise ValueError(f'{path} missing columns {required}')
    # ensure unique city labels; if duplicates, append row number (but keep original name separately)
    df['city'] = df['city'].astype(str)
    if df['city'].duplicated().any():
        counts = {}
        new_names = []
        for c in df['city']:
            counts[c] = counts.get(c, 0) + 1
            new_names.append(f'{c}_{counts[c]}' if counts[c] > 1 else c)
        df['city'] = new_names
    coords = df[['x','y']].astype(float).to_numpy()
    names = df['city'].tolist()
    return names, coords, df


def distance_matrix(coords: np.ndarray):
    diff = coords[:, None, :] - coords[None, :, :]
    return np.sqrt((diff * diff).sum(axis=2))


def route_length(route: np.ndarray, D: np.ndarray) -> float:
    return float(D[route, np.roll(route, -1)].sum())


def population_lengths(pop: np.ndarray, D: np.ndarray) -> np.ndarray:
    return D[pop, np.roll(pop, -1, axis=1)].sum(axis=1)


def nearest_neighbor_best(D: np.ndarray) -> Tuple[np.ndarray, float]:
    n = D.shape[0]
    best_route, best_len = None, float('inf')
    for start in range(n):
        unvisited = set(range(n))
        route = [start]
        unvisited.remove(start)
        current = start
        while unvisited:
            nxt = min(unvisited, key=lambda j: D[current, j])
            route.append(nxt)
            unvisited.remove(nxt)
            current = nxt
        route = np.array(route, dtype=np.int32)
        L = route_length(route, D)
        if L < best_len:
            best_len, best_route = L, route
    return best_route, best_len


def two_opt(route: np.ndarray, D: np.ndarray, max_passes: int = 50) -> Tuple[np.ndarray, float]:
    # First improvement 2-opt, bounded to avoid long runtime.
    n = len(route)
    best = route.copy()
    best_len = route_length(best, D)
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
                if delta < -1e-9:
                    best[i:k+1] = best[i:k+1][::-1]
                    best_len += float(delta)
                    improved = True
                    break
            if improved:
                break
    return best, best_len


def is_valid(route: np.ndarray, n: int) -> bool:
    return len(route) == n and len(set(route.tolist())) == n and set(route.tolist()) == set(range(n))


def init_population(n: int, pop_size: int, seed_route=None, rng=None) -> np.ndarray:
    rng = rng or np.random.default_rng()
    pop = np.empty((pop_size, n), dtype=np.int32)
    start = 0
    if seed_route is not None:
        pop[0] = seed_route
        start = 1
    for i in range(start, pop_size):
        pop[i] = rng.permutation(n)
    return pop


def ox_crossover(p1: np.ndarray, p2: np.ndarray, rng) -> np.ndarray:
    n = len(p1)
    a, b = sorted(rng.choice(n, size=2, replace=False))
    child = np.full(n, -1, dtype=np.int32)
    child[a:b+1] = p1[a:b+1]
    used = set(child[a:b+1].tolist())
    pos = (b + 1) % n
    for gene in np.concatenate([p2[b+1:], p2[:b+1]]):
        if int(gene) not in used:
            child[pos] = gene
            used.add(int(gene))
            pos = (pos + 1) % n
    return child


def pmx_crossover(p1: np.ndarray, p2: np.ndarray, rng) -> np.ndarray:
    n = len(p1)
    a, b = sorted(rng.choice(n, size=2, replace=False))
    child = np.full(n, -1, dtype=np.int32)
    child[a:b+1] = p1[a:b+1]
    # Map genes from p2 segment into child positions according to PMX
    for i in range(a, b+1):
        gene = int(p2[i])
        if gene not in child:
            pos = i
            while True:
                mapped = int(p1[pos])
                pos_arr = np.where(p2 == mapped)[0]
                pos = int(pos_arr[0])
                if child[pos] == -1:
                    child[pos] = gene
                    break
    for i in range(n):
        if child[i] == -1:
            child[i] = p2[i]
    return child


def mutate_inversion(route: np.ndarray, pm: float, rng) -> np.ndarray:
    r = route.copy()
    if rng.random() < pm:
        a, b = sorted(rng.choice(len(r), size=2, replace=False))
        r[a:b+1] = r[a:b+1][::-1]
    return r


def mutate_swap(route: np.ndarray, pm: float, rng) -> np.ndarray:
    r = route.copy()
    if rng.random() < pm:
        a, b = rng.choice(len(r), size=2, replace=False)
        r[a], r[b] = r[b], r[a]
    return r


def tournament_select(pop: np.ndarray, lengths: np.ndarray, k: int, rng) -> np.ndarray:
    idx = rng.choice(len(pop), size=k, replace=False)
    return pop[idx[np.argmin(lengths[idx])]]


def diversity_metrics(pop: np.ndarray, rng, pair_samples: int = 80) -> Tuple[float, float]:
    # % unique and normalized average Hamming distance sampled among pairs
    unique_pct = len({tuple(row.tolist()) for row in pop}) / len(pop) * 100.0
    m, n = pop.shape
    if m < 2:
        return unique_pct, 0.0
    num_pairs = min(pair_samples, m * (m - 1) // 2)
    total = 0.0
    for _ in range(num_pairs):
        i, j = rng.choice(m, size=2, replace=False)
        total += np.mean(pop[i] != pop[j])
    return unique_pct, total / num_pairs


def run_ga(D: np.ndarray,
           names=None,
           pop_size: int = 120,
           generations: int = 350,
           crossover: str = 'OX',
           mutation: str = 'inversion',
           mutation_prob: float = 0.15,
           crossover_prob: float = 0.90,
           elitism: int = 2,
           tournament_k: int = 3,
           seed: int = 0,
           seed_route=None,
           diversity_every: int = 1) -> Dict:
    rng = np.random.default_rng(seed)
    n = D.shape[0]
    pop = init_population(n, pop_size, seed_route=seed_route, rng=rng)
    # Choose operators
    cx_fn = ox_crossover if crossover.upper() == 'OX' else pmx_crossover
    mut_fn = mutate_inversion if mutation == 'inversion' else mutate_swap
    hist = []
    best_route = None
    best_len = float('inf')
    no_improve = 0
    best_generation = 0
    for g in range(generations + 1):
        lengths = population_lengths(pop, D)
        order = np.argsort(lengths)
        gen_best = float(lengths[order[0]])
        gen_avg = float(lengths.mean())
        gen_worst = float(lengths.max())
        if gen_best < best_len - 1e-9:
            best_len = gen_best
            best_route = pop[order[0]].copy()
            no_improve = 0
            best_generation = g
        else:
            no_improve += 1
        unique_pct, hamming = diversity_metrics(pop, rng) if g % diversity_every == 0 else (np.nan, np.nan)
        hist.append({
            'generation': g,
            'best_distance': best_len,
            'generation_best_distance': gen_best,
            'avg_distance': gen_avg,
            'worst_distance': gen_worst,
            'unique_pct': unique_pct,
            'hamming_avg': hamming,
            'no_improve': no_improve,
        })
        if g == generations:
            break
        # create next generation
        new_pop = np.empty_like(pop)
        # elitism: copy best current individuals
        elite_count = min(elitism, pop_size)
        new_pop[:elite_count] = pop[order[:elite_count]]
        fill = elite_count
        while fill < pop_size:
            p1 = tournament_select(pop, lengths, tournament_k, rng)
            p2 = tournament_select(pop, lengths, tournament_k, rng)
            if rng.random() < crossover_prob:
                child = cx_fn(p1, p2, rng)
            else:
                child = p1.copy()
            child = mut_fn(child, mutation_prob, rng)
            # Safety repair if ever needed (should not occur)
            if not is_valid(child, n):
                missing = [i for i in range(n) if i not in set(child.tolist())]
                seen = set()
                mi = 0
                for idx, val in enumerate(child):
                    if int(val) in seen or int(val) < 0:
                        child[idx] = missing[mi]
                        mi += 1
                    else:
                        seen.add(int(val))
            new_pop[fill] = child
            fill += 1
        pop = new_pop
    return {
        'best_route': best_route,
        'best_distance': float(best_len),
        'history': pd.DataFrame(hist),
        'best_generation': int(best_generation),
        'valid': is_valid(best_route, D.shape[0])
    }


def plot_convergence(hist: pd.DataFrame, title: str, outpath: Path):
    plt.figure(figsize=(8, 4.8), dpi=160)
    plt.plot(hist['generation'], hist['best_distance'], label='Mejor fitness (distancia)')
    plt.plot(hist['generation'], hist['avg_distance'], label='Fitness promedio')
    plt.plot(hist['generation'], hist['worst_distance'], label='Peor fitness')
    plt.xlabel('Generación')
    plt.ylabel('Distancia total del tour')
    plt.title(title)
    plt.legend()
    plt.grid(True, alpha=0.25)
    plt.tight_layout()
    plt.savefig(outpath)
    plt.close()


def plot_diversity(hist: pd.DataFrame, title: str, outpath: Path):
    plt.figure(figsize=(8, 4.8), dpi=160)
    plt.plot(hist['generation'], hist['unique_pct'], label='% individuos únicos')
    plt.plot(hist['generation'], hist['hamming_avg'] * 100, label='Distancia Hamming promedio (%)')
    plt.xlabel('Generación')
    plt.ylabel('Diversidad poblacional')
    plt.title(title)
    plt.legend()
    plt.grid(True, alpha=0.25)
    plt.tight_layout()
    plt.savefig(outpath)
    plt.close()


def plot_route(coords: np.ndarray, route: np.ndarray, names: list, title: str, outpath: Path):
    ordered = coords[route]
    closed = np.vstack([ordered, ordered[0]])
    plt.figure(figsize=(6.2, 6.2), dpi=160)
    plt.scatter(coords[:, 0], coords[:, 1], s=12)
    plt.plot(closed[:, 0], closed[:, 1], linewidth=1.1)
    # label only first 12 to avoid unreadability
    for idx in route[:12]:
        plt.text(coords[idx,0], coords[idx,1], names[idx], fontsize=6)
    plt.xlabel('x')
    plt.ylabel('y')
    plt.title(title)
    plt.grid(True, alpha=0.2)
    plt.tight_layout()
    plt.savefig(outpath)
    plt.close()


def stagnation_analysis(hist: pd.DataFrame, patience: int = 50) -> str:
    # Consider stagnation if no improvement in last patience generations.
    final_no_improve = int(hist['no_improve'].iloc[-1])
    improvement_ratio = (hist['best_distance'].iloc[0] - hist['best_distance'].iloc[-1]) / hist['best_distance'].iloc[0]
    if final_no_improve >= patience:
        return f'Estancamiento final: {final_no_improve} generaciones sin mejora; mejora acumulada {improvement_ratio*100:.2f}%.'
    return f'Convergencia activa: mejora reciente dentro de las ultimas {patience} generaciones; mejora acumulada {improvement_ratio*100:.2f}%.'


all_rows = []
summary_rows = []
start_time = time.time()
main_params = dict(pop_size=90, generations=140, crossover='OX', mutation='inversion', mutation_prob=0.15, crossover_prob=0.90, elitism=3, tournament_k=3)

for ds_i, path in enumerate(CSV_FILES):
    dataset = Path(path).stem.replace('(1)','')
    names, coords, df = read_dataset(path)
    D = distance_matrix(coords)
    nn_route, nn_len = nearest_neighbor_best(D)
    nn2_route, nn2_len = two_opt(nn_route, D, max_passes=100)
    # Use NN route as one seed to accelerate; GA is still stochastic and maintains random population.
    seed = MASTER_SEED + ds_i * 100
    result = run_ga(D, names, seed=seed, seed_route=nn_route, **main_params)
    ga2_route, ga2_len = two_opt(result['best_route'], D, max_passes=100)
    hist = result['history']
    hist.to_csv(RES / f'{dataset}_history.csv', index=False)
    route_df = pd.DataFrame({
        'order': np.arange(1, len(ga2_route)+1),
        'city': [names[i] for i in ga2_route],
        'x': coords[ga2_route,0],
        'y': coords[ga2_route,1]
    })
    route_df.to_csv(RES / f'{dataset}_best_route.csv', index=False)
    # Plots
    plot_convergence(hist, f'Evolucion del fitness - {dataset}', FIG / f'{dataset}_convergencia.png')
    plot_diversity(hist, f'Diversidad poblacional - {dataset}', FIG / f'{dataset}_diversidad.png')
    plot_route(coords, ga2_route, names, f'Mejor ruta GA + 2-opt - {dataset}', FIG / f'{dataset}_ruta.png')
    rel_vs_nn = (ga2_len - nn_len) / nn_len * 100.0
    rel_vs_nn2 = (ga2_len - nn2_len) / nn2_len * 100.0
    diversity_end = float(hist['unique_pct'].iloc[-1])
    hamming_end = float(hist['hamming_avg'].iloc[-1])
    summary_rows.append({
        'dataset': dataset,
        'n_ciudades': len(names),
        'nn_distance': nn_len,
        'nn_2opt_distance': nn2_len,
        'ga_distance': result['best_distance'],
        'ga_2opt_distance': ga2_len,
        'gap_vs_nn_pct': rel_vs_nn,
        'gap_vs_nn2_pct': rel_vs_nn2,
        'best_generation': result['best_generation'],
        'unique_pct_final': diversity_end,
        'hamming_pct_final': hamming_end*100,
        'valid_solution': result['valid'],
        'stagnation': stagnation_analysis(hist)
    })

summary = pd.DataFrame(summary_rows)
summary.to_csv(RES / 'summary_all_datasets.csv', index=False)

# Experimental analysis on the largest dataset (largest n, tie first by sort order)
largest_row_idx = summary['n_ciudades'].idxmax()
largest_dataset = summary.loc[largest_row_idx, 'dataset']
largest_path = [p for p in CSV_FILES if Path(p).stem.replace('(1)','') == largest_dataset][0]
names, coords, df = read_dataset(largest_path)
D = distance_matrix(coords)
nn_route, nn_len = nearest_neighbor_best(D)

param_grid = []
for pop_size in [60, 100, 140]:
    for crossover in ['OX', 'PMX']:
        for mutation_prob in [0.05, 0.15, 0.30]:
            param_grid.append((pop_size, crossover, mutation_prob))

exp_rows = []
for idx, (pop_size, crossover, pm) in enumerate(param_grid):
    seed = 880000 + idx
    res = run_ga(D, names, pop_size=pop_size, generations=140, crossover=crossover, mutation='inversion', mutation_prob=pm, crossover_prob=0.90, elitism=3, tournament_k=3, seed=seed, seed_route=nn_route)
    ga2_route, ga2_len = two_opt(res['best_route'], D, max_passes=80)
    hist = res['history']
    exp_rows.append({
        'dataset': largest_dataset,
        'n_ciudades': len(names),
        'pop_size': pop_size,
        'crossover': crossover,
        'crossover_prob': 0.90,
        'mutation': 'inversion',
        'mutation_prob': pm,
        'generations': 140,
        'best_distance_ga': res['best_distance'],
        'best_distance_ga_2opt': ga2_len,
        'best_generation': res['best_generation'],
        'unique_pct_final': float(hist['unique_pct'].iloc[-1]),
        'hamming_pct_final': float(hist['hamming_avg'].iloc[-1]*100),
        'gap_vs_nn_pct': (ga2_len - nn_len) / nn_len * 100.0,
        'valid_solution': res['valid']
    })

exp = pd.DataFrame(exp_rows).sort_values('best_distance_ga_2opt')
exp.to_csv(RES / 'parameter_experiment_largest_dataset.csv', index=False)

# Aggregated parameter plots
for metric, ylabel, outfile in [
    ('best_distance_ga_2opt', 'Distancia final GA + 2-opt', 'parametros_distancia.png'),
    ('unique_pct_final', '% individuos unicos final', 'parametros_diversidad_unica.png'),
]:
    plt.figure(figsize=(9, 5), dpi=160)
    labels = []
    vals = []
    for _, row in exp.iterrows():
        labels.append(f"P{int(row['pop_size'])}-{row['crossover']}-m{row['mutation_prob']}")
        vals.append(row[metric])
    plt.bar(range(len(vals)), vals)
    plt.xticks(range(len(vals)), labels, rotation=75, ha='right', fontsize=7)
    plt.ylabel(ylabel)
    plt.title(f'Analisis experimental de parametros - {largest_dataset}')
    plt.grid(True, axis='y', alpha=0.2)
    plt.tight_layout()
    plt.savefig(FIG / outfile)
    plt.close()

# Save a compact JSON metadata file
metadata = {
    'master_seed': MASTER_SEED,
    'main_params': main_params,
    'datasets': summary_rows,
    'largest_dataset_for_param_exp': largest_dataset,
    'runtime_seconds': time.time() - start_time
}
with open(RES / 'metadata.json', 'w', encoding='utf-8') as f:
    json.dump(metadata, f, indent=2, ensure_ascii=False)

# Copy this script as project code
import shutil
shutil.copy('/mnt/data/run_tsp_ga_project.py', CODE / 'tsp_ga_analysis.py')
print('DONE')
print(summary.to_string(index=False, formatters={
    'nn_distance': '{:.2f}'.format,
    'nn_2opt_distance': '{:.2f}'.format,
    'ga_distance': '{:.2f}'.format,
    'ga_2opt_distance': '{:.2f}'.format,
    'gap_vs_nn_pct': '{:.2f}'.format,
    'gap_vs_nn2_pct': '{:.2f}'.format,
    'unique_pct_final': '{:.1f}'.format,
    'hamming_pct_final': '{:.1f}'.format,
}))
print('\nEXPERIMENT BEST:')
print(exp.head(8).to_string(index=False, formatters={
    'best_distance_ga': '{:.2f}'.format,
    'best_distance_ga_2opt': '{:.2f}'.format,
    'unique_pct_final': '{:.1f}'.format,
    'hamming_pct_final': '{:.1f}'.format,
    'gap_vs_nn_pct': '{:.2f}'.format,
}))
