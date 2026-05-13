import numpy as np
import random
import itertools
import time
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap


# =============================================================================
# CLASE ACO — Caso 2 con fix aplicado
# =============================================================================
class AntColonyOptimization:
    def __init__(self, start, end, obstacles, grid_size=(10, 10),
                 num_ants=20, evaporation_rate=0.3, alpha=1.0, beta=5.0):
        self.start = start
        self.end = end
        self.obstacles = set(obstacles)
        self.grid_size = grid_size
        self.num_ants = num_ants
        self.evaporation_rate = evaporation_rate
        self.alpha = alpha
        self.beta = beta
        self.pheromones = np.ones(grid_size)
        self.best_path = None

    def _get_neighbors(self, position):
        px, py = position
        neighbors = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                nx, ny = px + i, py + j
                if (0 <= nx < self.grid_size[0] and
                        0 <= ny < self.grid_size[1] and
                        (nx, ny) != position and
                        (nx, ny) not in self.obstacles):
                    neighbors.append((nx, ny))
        return neighbors

    def _select_next_position(self, position, visited):
        neighbors = self._get_neighbors(position)
        candidates = []
        total = 0.0
        for nb in neighbors:
            if nb not in visited:
                pheromone = self.pheromones[nb[1], nb[0]]
                heuristic = 1.0 / (np.linalg.norm(np.array(nb) - np.array(self.end)) + 0.1)
                score = (pheromone ** self.alpha) * (heuristic ** self.beta)
                candidates.append((nb, score))
                total += score
        if not candidates:
            return None
        candidates = [(pos, s / total) for pos, s in candidates]
        idx = np.random.choice(len(candidates), p=[s for _, s in candidates])
        return candidates[idx][0]

    def _evaporate_pheromones(self):
        self.pheromones *= (1 - self.evaporation_rate)
        self.pheromones = np.clip(self.pheromones, 0.01, None)

    def _deposit_pheromones(self, path):
        deposit = 100.0 / len(path)
        for position in path:
            self.pheromones[position[1], position[0]] += deposit

    def find_best_path(self, num_iterations=15):
        for _ in range(num_iterations):
            all_paths = []
            for _ in range(self.num_ants):
                current = self.start
                path = [current]
                visited = {current}
                for _ in range(150):
                    if current == self.end:
                        break
                    next_pos = self._select_next_position(current, visited)
                    if next_pos is None:
                        break
                    path.append(next_pos)
                    visited.add(next_pos)
                    current = next_pos
                all_paths.append(path)

            # Fix: solo caminos que llegaron al destino
            valid_paths = [p for p in all_paths if p[-1] == self.end]
            self._evaporate_pheromones()
            if not valid_paths:
                continue
            valid_paths.sort(key=len)
            for path in valid_paths:
                self._deposit_pheromones(path)
            if self.best_path is None or len(valid_paths[0]) < len(self.best_path):
                self.best_path = valid_paths[0]

        return self.best_path


# =============================================================================
# FUNCIÓN DE EVALUACIÓN
# Corre ACO n_runs veces y retorna la longitud promedio del mejor camino.
# El promedio reduce el efecto de la aleatoriedad del algoritmo.
# Retorna 999 como penalización si no encontró ningún camino válido.
# =============================================================================
def evaluate_params(num_ants, evaporation_rate, alpha, beta, n_runs=2):
    start     = (0, 0)
    end       = (4, 7)
    obstacles = [(0, 2), (1, 2), (2, 2), (3, 2)]

    lengths = []
    for _ in range(n_runs):
        aco = AntColonyOptimization(
            start, end, obstacles,
            num_ants=num_ants,
            evaporation_rate=evaporation_rate,
            alpha=alpha,
            beta=beta
        )
        path = aco.find_best_path(num_iterations=15)
        if path is not None and path[-1] == end:
            lengths.append(len(path))
        else:
            lengths.append(999)

    return float(np.mean(lengths))


# =============================================================================
# MÉTODO 1: GRID SEARCH — Búsqueda exhaustiva
# Prueba TODAS las combinaciones posibles del espacio discretizado.
# Con 3 valores por cada uno de los 4 parámetros => 3^4 = 81 combinaciones.
# =============================================================================
def grid_search():
    print("=" * 55)
    print("MÉTODO 1: GRID SEARCH (Búsqueda Exhaustiva)")
    print("=" * 55)

    param_grid = {
        'num_ants':         [10, 20, 30],
        'evaporation_rate': [0.1, 0.3, 0.5],
        'alpha':            [0.5, 1.0, 2.0],
        'beta':             [3.0, 5.0, 8.0],
    }

    keys   = list(param_grid.keys())
    combos = list(itertools.product(*param_grid.values()))
    print(f"Total de combinaciones: {len(combos)}")

    results  = []
    t_inicio = time.time()

    for i, combo in enumerate(combos):
        # Convierte la tupla de valores en un diccionario de parámetros
        params = dict(zip(keys, combo))
        score  = evaluate_params(**params)
        results.append((params, score))

        if (i + 1) % 20 == 0:
            mejor = min(r[1] for r in results)
            print(f"  Progreso: {i+1}/{len(combos)} | mejor hasta ahora: {mejor:.1f}")

    results.sort(key=lambda x: x[1])
    t_total = time.time() - t_inicio

    print(f"\nTiempo total: {t_total:.1f}s")
    print("\nTop 5 mejores configuraciones:")
    print(f"  {'num_ants':>8} {'evap':>6} {'alpha':>6} {'beta':>6} {'score':>8}")
    print("  " + "-" * 40)
    for params, score in results[:5]:
        print(f"  {params['num_ants']:>8} {params['evaporation_rate']:>6.2f} "
              f"{params['alpha']:>6.2f} {params['beta']:>6.2f} {score:>8.1f}")

    print(f"\n✅ Mejor: score={results[0][1]:.1f} | params={results[0][0]}")
    return results, t_total


# =============================================================================
# MÉTODO 2: RANDOM SEARCH — Búsqueda aleatoria
# Muestrea combinaciones ALEATORIAS del espacio continuo de parámetros.
# Más eficiente que Grid Search con el mismo número de evaluaciones porque
# puede encontrar valores entre los puntos del grid (ej: alpha=1.73, beta=6.4).
# =============================================================================
def random_search(n_iter=20):
    print("\n" + "=" * 55)
    print("MÉTODO 2: RANDOM SEARCH (Búsqueda Aleatoria)")
    print("=" * 55)
    print(f"Evaluando {n_iter} combinaciones aleatorias...")

    # Rangos continuos para cada parámetro
    param_space = {
        'num_ants':         (5,    50),
        'evaporation_rate': (0.05, 0.6),
        'alpha':            (0.1,  3.0),
        'beta':             (1.0,  10.0),
    }

    results      = []
    best_so_far  = []        # curva de convergencia
    current_best = 999.0
    t_inicio     = time.time()

    for i in range(n_iter):
        # Muestreo aleatorio uniforme dentro de cada rango
        params = {
            'num_ants':         random.randint(*param_space['num_ants']),
            'evaporation_rate': round(random.uniform(*param_space['evaporation_rate']), 2),
            'alpha':            round(random.uniform(*param_space['alpha']), 2),
            'beta':             round(random.uniform(*param_space['beta']), 2),
        }
        score        = evaluate_params(**params)
        results.append((params, score))
        current_best = min(current_best, score)
        best_so_far.append(current_best)       # guardar progreso para graficar

        if (i + 1) % 5 == 0:
            print(f"  Iter {i+1:3d}/{n_iter} | mejor hasta ahora: {current_best:.1f}")

    results.sort(key=lambda x: x[1])
    t_total = time.time() - t_inicio

    print(f"\nTiempo total: {t_total:.1f}s")
    print("\nTop 5 mejores configuraciones:")
    print(f"  {'num_ants':>8} {'evap':>6} {'alpha':>6} {'beta':>6} {'score':>8}")
    print("  " + "-" * 40)
    for params, score in results[:5]:
        print(f"  {params['num_ants']:>8} {params['evaporation_rate']:>6.2f} "
              f"{params['alpha']:>6.2f} {params['beta']:>6.2f} {score:>8.1f}")

    print(f"\n✅ Mejor: score={results[0][1]:.1f} | params={results[0][0]}")
    return results, best_so_far, t_total


# =============================================================================
# VISUALIZACIÓN COMPARATIVA
# =============================================================================
def plot_comparison(gs_results, gs_time, rs_results, rs_bsf, rs_time):
    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    cmap      = LinearSegmentedColormap.from_list('ph', ['white', 'green', 'red'])
    obstacles = [(0, 2), (1, 2), (2, 2), (3, 2)]
    best_gs   = gs_results[0][0]
    best_rs   = rs_results[0][0]

    # ── Histograma Grid Search ─────────────────────────────────────────────────
    ax = axes[0, 0]
    gs_scores = [s for _, s in gs_results if s < 900]
    ax.hist(gs_scores, bins=10, color='steelblue', edgecolor='white', alpha=0.85)
    ax.axvline(min(gs_scores), color='red', ls='--', lw=2, label=f'Mejor: {min(gs_scores):.0f}')
    ax.set_title('Grid Search — Distribución de Scores')
    ax.set_xlabel('Longitud del camino')
    ax.set_ylabel('Frecuencia')
    ax.legend()

    # ── Histograma Random Search ───────────────────────────────────────────────
    ax = axes[0, 1]
    rs_scores = [s for _, s in rs_results if s < 900]
    ax.hist(rs_scores, bins=8, color='darkorange', edgecolor='white', alpha=0.85)
    ax.axvline(min(rs_scores), color='red', ls='--', lw=2, label=f'Mejor: {min(rs_scores):.0f}')
    ax.set_title('Random Search — Distribución de Scores')
    ax.set_xlabel('Longitud del camino')
    ax.set_ylabel('Frecuencia')
    ax.legend()

    # ── Curva de convergencia Random Search ───────────────────────────────────
    ax = axes[0, 2]
    ax.plot(rs_bsf, color='green', lw=2, marker='o', ms=4)
    ax.set_title('Random Search — Convergencia del Mejor Score')
    ax.set_xlabel('Iteración')
    ax.set_ylabel('Mejor score acumulado')
    ax.grid(True, alpha=0.4)

    # ── ACO con mejor config Grid Search ──────────────────────────────────────
    ax = axes[1, 0]
    aco_gs = AntColonyOptimization((0, 0), (4, 7), obstacles, **best_gs)
    aco_gs.find_best_path(50)
    ax.imshow(aco_gs.pheromones, cmap=cmap)
    ax.scatter(0, 0, color='orange',  s=150, zorder=5, label='Start')
    ax.scatter(4, 7, color='magenta', s=150, zorder=5, label='End')
    for obs in obstacles:
        ax.scatter(*obs, color='gray', s=400, marker='s', zorder=4)
    if aco_gs.best_path:
        px, py = zip(*aco_gs.best_path)
        ax.plot(px, py, color='blue', lw=3, zorder=6, label=f'{len(aco_gs.best_path)} pasos')
    ax.set_title(f'Grid Search — Mejor config\n'
                 f'ants={best_gs["num_ants"]}, evap={best_gs["evaporation_rate"]}, '
                 f'α={best_gs["alpha"]}, β={best_gs["beta"]}')
    ax.legend(fontsize=7)

    # ── ACO con mejor config Random Search ────────────────────────────────────
    ax = axes[1, 1]
    aco_rs = AntColonyOptimization((0, 0), (4, 7), obstacles, **best_rs)
    aco_rs.find_best_path(50)
    ax.imshow(aco_rs.pheromones, cmap=cmap)
    ax.scatter(0, 0, color='orange',  s=150, zorder=5, label='Start')
    ax.scatter(4, 7, color='magenta', s=150, zorder=5, label='End')
    for obs in obstacles:
        ax.scatter(*obs, color='gray', s=400, marker='s', zorder=4)
    if aco_rs.best_path:
        px, py = zip(*aco_rs.best_path)
        ax.plot(px, py, color='blue', lw=3, zorder=6, label=f'{len(aco_rs.best_path)} pasos')
    ax.set_title(f'Random Search — Mejor config\n'
                 f'ants={best_rs["num_ants"]}, evap={best_rs["evaporation_rate"]}, '
                 f'α={best_rs["alpha"]}, β={best_rs["beta"]}')
    ax.legend(fontsize=7)

    # ── Tabla comparativa ──────────────────────────────────────────────────────
    ax = axes[1, 2]
    ax.axis('off')
    tabla = [
        ['',               'Grid Search',                      'Random Search'],
        ['Combinaciones',   str(len(gs_results)),              '20'],
        ['Tiempo (s)',      f'{gs_time:.1f}',                  f'{rs_time:.1f}'],
        ['Mejor score',     f'{gs_results[0][1]:.1f}',         f'{rs_results[0][1]:.1f}'],
        ['num_ants',        str(best_gs['num_ants']),           str(best_rs['num_ants'])],
        ['evap_rate',       str(best_gs['evaporation_rate']),   str(best_rs['evaporation_rate'])],
        ['alpha',           str(best_gs['alpha']),              str(best_rs['alpha'])],
        ['beta',            str(best_gs['beta']),               str(best_rs['beta'])],
    ]
    t = ax.table(cellText=tabla, loc='center', cellLoc='center')
    t.auto_set_font_size(False)
    t.set_fontsize(9)
    t.scale(1.1, 1.9)
    ax.set_title('Comparativa de Métodos', pad=15)

    plt.suptitle('Optimización de Hiperparámetros — ACO Caso 2',
                 fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig('hyperparam_search.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("\nGráfico guardado como 'hyperparam_search.png'")


# =============================================================================
# MAIN
# =============================================================================
if __name__ == '__main__':

    gs_results, gs_time             = grid_search()
    rs_results, rs_bsf, rs_time     = random_search(n_iter=20)

    plot_comparison(gs_results, gs_time, rs_results, rs_bsf, rs_time)

    print()
    print("=" * 55)
    print("CONCLUSIÓN FINAL")
    print("=" * 55)
    print(f"Grid Search   → score={gs_results[0][1]:.1f} en {gs_time:.1f}s ({len(gs_results)} combinaciones)")
    print(f"Random Search → score={rs_results[0][1]:.1f} en {rs_time:.1f}s (20 combinaciones)")
    if rs_results[0][1] <= gs_results[0][1]:
        print("\nRandom Search igualó o superó a Grid Search usando menos evaluaciones.")
        print("→ Para este problema, Random Search es más eficiente.")
    else:
        print("\nGrid Search encontró una mejor solución al explorar exhaustivamente.")
        print("→ El espacio era suficientemente pequeño para justificar la búsqueda total.")