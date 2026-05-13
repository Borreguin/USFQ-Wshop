"""Parte 2 - Optimización por Colonia de Hormigas (ACO).

Corre los dos casos de estudio, corrige el problema del caso 2 y agrega Random Search
para ajustar hiperparámetros. El problema original del caso 2 era que el algoritmo
podía escoger como "mejor" una ruta corta incompleta, es decir, una ruta que no llega
al punto final.
"""

from __future__ import annotations

import csv
import math
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

Position = Tuple[int, int]


@dataclass
class ACOResult:
    path: Optional[List[Position]]
    cost: float
    iterations: int
    num_ants: int
    evaporation_rate: float
    alpha: float
    beta: float
    seed: Optional[int]

    @property
    def found(self) -> bool:
        return self.path is not None and len(self.path) > 0

    @property
    def path_nodes(self) -> int:
        return len(self.path or [])


class AntColonyOptimization:
    def __init__(
        self,
        start: Position,
        end: Position,
        obstacles: Sequence[Position],
        grid_size: Tuple[int, int] = (10, 10),
        num_ants: int = 50,
        evaporation_rate: float = 0.2,
        alpha: float = 1.0,
        beta: float = 4.0,
        pheromone_deposit: float = 10.0,
        allow_diagonal: bool = True,
        seed: Optional[int] = None,
    ):
        self.start = start
        self.end = end
        self.obstacles = set(obstacles)
        self.grid_size = grid_size
        self.num_ants = num_ants
        self.evaporation_rate = evaporation_rate
        self.alpha = alpha
        self.beta = beta
        self.pheromone_deposit = pheromone_deposit
        self.allow_diagonal = allow_diagonal
        self.pheromones = np.ones((grid_size[1], grid_size[0]), dtype=float)
        self.best_path: Optional[List[Position]] = None
        self.best_cost = math.inf
        self.history: List[float] = []
        self.rng = np.random.default_rng(seed)
        self.seed = seed

    def _get_neighbors(self, position: Position) -> List[Position]:
        pos_x, pos_y = position
        moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        if self.allow_diagonal:
            moves += [(-1, -1), (-1, 1), (1, -1), (1, 1)]

        neighbors: List[Position] = []
        for dx, dy in moves:
            new_x, new_y = pos_x + dx, pos_y + dy
            candidate = (new_x, new_y)
            if (
                0 <= new_x < self.grid_size[0]
                and 0 <= new_y < self.grid_size[1]
                and candidate not in self.obstacles
            ):
                neighbors.append(candidate)
        return neighbors

    def _select_next_position(self, position: Position, visited: Iterable[Position]) -> Optional[Position]:
        visited_set = set(visited)
        neighbors = [neighbor for neighbor in self._get_neighbors(position) if neighbor not in visited_set]
        if not neighbors:
            return None

        weights = []
        for neighbor in neighbors:
            pheromone = self.pheromones[neighbor[1], neighbor[0]]
            distance_to_end = np.linalg.norm(np.array(neighbor) - np.array(self.end))
            heuristic = 1.0 / (distance_to_end + 0.1)
            weight = (pheromone ** self.alpha) * (heuristic ** self.beta)
            weights.append(weight)

        total = float(np.sum(weights))
        if total <= 0 or np.isnan(total):
            index = self.rng.integers(0, len(neighbors))
            return neighbors[index]

        probabilities = np.array(weights, dtype=float) / total
        index = self.rng.choice(len(neighbors), p=probabilities)
        return neighbors[index]

    def _evaporate_pheromones(self):
        self.pheromones *= (1.0 - self.evaporation_rate)
        # Evita que la feromona desaparezca por completo.
        self.pheromones = np.maximum(self.pheromones, 1e-6)

    @staticmethod
    def _path_cost(path: Sequence[Position]) -> float:
        if len(path) < 2:
            return math.inf
        total = 0.0
        for previous, current in zip(path[:-1], path[1:]):
            total += float(np.linalg.norm(np.array(current) - np.array(previous)))
        return total

    def _path_reaches_end(self, path: Sequence[Position]) -> bool:
        return len(path) > 0 and path[-1] == self.end

    def _deposit_pheromones(self, path: Sequence[Position]):
        if not self._path_reaches_end(path):
            return
        cost = self._path_cost(path)
        amount = self.pheromone_deposit / (cost + 1e-9)
        for position in path:
            self.pheromones[position[1], position[0]] += amount

    def _build_ant_path(self) -> List[Position]:
        current_position = self.start
        path = [current_position]
        max_steps = self.grid_size[0] * self.grid_size[1]

        while current_position != self.end and len(path) < max_steps:
            next_position = self._select_next_position(current_position, path)
            if next_position is None:
                break
            path.append(next_position)
            current_position = next_position
        return path

    def find_best_path(self, num_iterations: int = 150) -> Optional[List[Position]]:
        """Busca la mejor ruta.

        Corrección clave: solo se consideran candidatas las rutas completas que llegan
        a self.end. Luego se selecciona la de menor costo, no solo la de menor número
        de nodos.
        """
        for _ in range(num_iterations):
            all_paths = [self._build_ant_path() for _ in range(self.num_ants)]
            complete_paths = [path for path in all_paths if self._path_reaches_end(path)]

            self._evaporate_pheromones()

            if complete_paths:
                # Se puede reforzar más de una ruta completa, pero se prioriza la mejor.
                iteration_best = min(complete_paths, key=self._path_cost)
                self._deposit_pheromones(iteration_best)
                iteration_cost = self._path_cost(iteration_best)

                if iteration_cost < self.best_cost:
                    self.best_path = list(iteration_best)
                    self.best_cost = iteration_cost
            self.history.append(self.best_cost)

        return self.best_path

    def result(self, iterations: int) -> ACOResult:
        return ACOResult(
            path=self.best_path,
            cost=self.best_cost,
            iterations=iterations,
            num_ants=self.num_ants,
            evaporation_rate=self.evaporation_rate,
            alpha=self.alpha,
            beta=self.beta,
            seed=self.seed,
        )

    def plot(self, save_path: Optional[str] = None, title: str = 'Ant Colony Optimization', show: bool = False):
        cmap = LinearSegmentedColormap.from_list('pheromone', ['white', 'green', 'red'])
        fig, ax = plt.subplots(figsize=(8, 8))
        image = ax.imshow(
            self.pheromones,
            cmap=cmap,
            vmin=np.min(self.pheromones),
            vmax=np.max(self.pheromones),
            origin='upper',
        )
        fig.colorbar(image, ax=ax, label='Pheromone intensity')
        ax.scatter(self.start[0], self.start[1], color='orange', label='Start', s=100)
        ax.scatter(self.end[0], self.end[1], color='magenta', label='End', s=100)
        for obstacle in self.obstacles:
            ax.scatter(obstacle[0], obstacle[1], color='gray', s=900, marker='s')
        if self.best_path:
            path_x, path_y = zip(*self.best_path)
            ax.plot(path_x, path_y, color='blue', label=f'Best Path cost={self.best_cost:.2f}', linewidth=3)
        ax.set_xlabel('Column')
        ax.set_ylabel('Row')
        ax.set_title(title)
        ax.legend()
        ax.grid(True)
        fig.tight_layout()

        if save_path:
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(save_path, dpi=180, bbox_inches='tight')
        if show:
            plt.show()
        plt.close(fig)


def run_case(
    case_name: str,
    start: Position,
    end: Position,
    obstacles: Sequence[Position],
    grid_size: Tuple[int, int] = (10, 10),
    num_ants: int = 60,
    evaporation_rate: float = 0.2,
    alpha: float = 1.0,
    beta: float = 4.0,
    iterations: int = 150,
    seed: Optional[int] = 42,
    save_path: Optional[str] = None,
) -> ACOResult:
    print(f"\nStart of Ant Colony Optimization - {case_name}")
    aco = AntColonyOptimization(
        start=start,
        end=end,
        obstacles=obstacles,
        grid_size=grid_size,
        num_ants=num_ants,
        evaporation_rate=evaporation_rate,
        alpha=alpha,
        beta=beta,
        seed=seed,
    )
    aco.find_best_path(iterations)
    aco.plot(save_path=save_path, title=f"{case_name} - ACO", show=False)
    result = aco.result(iterations)
    print(f"Best path: {result.path}")
    print(f"Found={result.found} | cost={result.cost:.4f} | nodes={result.path_nodes}")
    return result


def study_case_1() -> ACOResult:
    start = (0, 0)
    end = (4, 7)
    obstacles = [(1, 2), (2, 2), (3, 2)]
    return run_case(
        'First Study Case',
        start,
        end,
        obstacles,
        num_ants=35,
        evaporation_rate=0.2,
        alpha=1.0,
        beta=4.0,
        iterations=80,
        seed=42,
        save_path=str(Path(__file__).resolve().parent / 'results' / 'aco_case_1.png'),
    )


def study_case_2() -> ACOResult:
    start = (0, 0)
    end = (4, 7)
    obstacles = [(0, 2), (1, 2), (2, 2), (3, 2)]
    return run_case(
        'Second Study Case Fixed',
        start,
        end,
        obstacles,
        num_ants=45,
        evaporation_rate=0.25,
        alpha=1.0,
        beta=3.0,
        iterations=100,
        seed=7,
        save_path=str(Path(__file__).resolve().parent / 'results' / 'aco_case_2_fixed.png'),
    )


def random_search_parameters(
    start: Position,
    end: Position,
    obstacles: Sequence[Position],
    grid_size: Tuple[int, int] = (10, 10),
    trials: int = 8,
    iterations: int = 60,
    seed: int = 123,
) -> Tuple[ACOResult, List[Dict[str, object]]]:
    """Optimización simple de hiperparámetros con Random Search.

    Es apropiado aquí porque ACO es estocástico y los rangos de alpha, beta y evaporación
    son continuos; Random Search explora más combinaciones útiles con menos ejecuciones
    que una grilla exhaustiva.
    """
    rng = random.Random(seed)
    records: List[Dict[str, object]] = []
    best_result: Optional[ACOResult] = None

    for trial in range(1, trials + 1):
        params = {
            'num_ants': rng.choice([20, 40, 60, 80, 100]),
            'evaporation_rate': rng.uniform(0.05, 0.45),
            'alpha': rng.uniform(0.5, 2.0),
            'beta': rng.uniform(1.0, 6.0),
            'seed': rng.randint(1, 10_000),
        }
        aco = AntColonyOptimization(
            start=start,
            end=end,
            obstacles=obstacles,
            grid_size=grid_size,
            **params,
        )
        aco.find_best_path(iterations)
        result = aco.result(iterations)

        record = {
            'trial': trial,
            'found': result.found,
            'cost': round(result.cost, 5) if result.found else None,
            'path_nodes': result.path_nodes,
            'num_ants': result.num_ants,
            'evaporation_rate': round(result.evaporation_rate, 4),
            'alpha': round(result.alpha, 4),
            'beta': round(result.beta, 4),
            'seed': result.seed,
        }
        records.append(record)

        if result.found and (best_result is None or result.cost < best_result.cost):
            best_result = result

    if best_result is None:
        best_result = ACOResult(None, math.inf, iterations, 0, 0.0, 0.0, 0.0, None)

    return best_result, records


def save_random_search_results(records: List[Dict[str, object]], output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ['trial', 'found', 'cost', 'path_nodes', 'num_ants', 'evaporation_rate', 'alpha', 'beta', 'seed']
    with open(output_path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)


def run_random_search_for_case_2() -> ACOResult:
    start = (0, 0)
    end = (4, 7)
    obstacles = [(0, 2), (1, 2), (2, 2), (3, 2)]
    best_result, records = random_search_parameters(start, end, obstacles, trials=8, iterations=60, seed=123)
    output_dir = Path(__file__).resolve().parent / 'results'
    save_random_search_results(records, output_dir / 'random_search_case_2.csv')

    print("\nRandom Search - mejor configuración encontrada")
    print(best_result)

    if best_result.found:
        aco = AntColonyOptimization(
            start=start,
            end=end,
            obstacles=obstacles,
            num_ants=best_result.num_ants,
            evaporation_rate=best_result.evaporation_rate,
            alpha=best_result.alpha,
            beta=best_result.beta,
            seed=best_result.seed,
        )
        aco.find_best_path(best_result.iterations)
        aco.plot(
            save_path=str(output_dir / 'aco_case_2_random_search_best.png'),
            title='Second Study Case - Random Search Best',
            show=False,
        )
    return best_result


def print_parameter_explanation():
    print("""
Parámetros principales del modelo ACO:
- num_ants: cantidad de hormigas que construyen rutas en cada iteración.
- evaporation_rate: porcentaje de feromona que se evapora; evita convergencia prematura.
- alpha: peso de la feromona; alto alpha hace que las hormigas sigan rutas reforzadas.
- beta: peso de la heurística; alto beta hace que las hormigas sean más codiciosas hacia la meta.
- pheromone_deposit: cantidad base de feromona que se deposita en una ruta exitosa.
- iterations: número de ciclos de búsqueda.
- seed: semilla para reproducibilidad.
""")


def main():
    result_1 = study_case_1()
    result_2 = study_case_2()
    best_random = run_random_search_for_case_2()
    print_parameter_explanation()

    print("Resumen:")
    print(f"Caso 1 -> encontrado={result_1.found}, costo={result_1.cost:.4f}, nodos={result_1.path_nodes}")
    print(f"Caso 2 corregido -> encontrado={result_2.found}, costo={result_2.cost:.4f}, nodos={result_2.path_nodes}")
    print(f"Random Search caso 2 -> encontrado={best_random.found}, costo={best_random.cost:.4f}, nodos={best_random.path_nodes}")


if __name__ == '__main__':
    main()
