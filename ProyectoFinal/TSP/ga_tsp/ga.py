import random
import numpy as np
from typing import List, Tuple, Optional

from ga_tsp.distances import tour_distance
from ga_tsp.selection import tournament_selection
from ga_tsp.crossover import ox_crossover
from ga_tsp.mutation import swap_mutation, inversion_mutation, combined_mutation
from ga_tsp.elitism import apply_elitism, best_individual


class GeneticAlgorithmTSP:
    """
    Algoritmo Genetico para el Problema del Viajante (TSP).

    Representacion: permutacion de indices de ciudades [0..n-1].
    Fitness: 1 / distancia_total (mayor = mejor).
    Seleccion: torneo de tamano k.
    Cruce: Order Crossover (OX).
    Mutacion: swap, inversion o combinada.
    Elitismo: los N mejores individuos sobreviven sin cambios.
    """

    def __init__(
        self,
        dist_matrix: np.ndarray,
        pop_size: int = 150,
        mutation_rate: float = 0.02,
        n_elite: int = 5,
        tournament_k: int = 5,
        mutation_type: str = "combined",   # "swap" | "inversion" | "combined"
        n_generations: int = 500,
        seed: int = 42,
        verbose: bool = True,
    ):
        self.dist_matrix = dist_matrix
        self.n_cities = len(dist_matrix)
        self.pop_size = pop_size
        self.mutation_rate = mutation_rate
        self.n_elite = n_elite
        self.tournament_k = tournament_k
        self.mutation_type = mutation_type
        self.n_generations = n_generations
        self.seed = seed
        self.verbose = verbose

        # Historial por generacion
        self.best_fitness_history: List[float] = []
        self.avg_fitness_history: List[float] = []
        self.worst_fitness_history: List[float] = []
        self.best_dist_history: List[float] = []
        self.diversity_history: List[float] = []

        # Mejor solucion global
        self.best_tour: Optional[List[int]] = None
        self.best_distance: float = float("inf")

    # ------------------------------------------------------------------
    # Helpers internos
    # ------------------------------------------------------------------

    def _fitness(self, tour: List[int]) -> float:
        d = tour_distance(tour, self.dist_matrix)
        return 1.0 / d if d > 0 else float("inf")

    def _random_tour(self) -> List[int]:
        t = list(range(self.n_cities))
        random.shuffle(t)
        return t

    def _mutate(self, tour: List[int]) -> List[int]:
        if self.mutation_type == "swap":
            return swap_mutation(tour, self.mutation_rate)
        if self.mutation_type == "inversion":
            return inversion_mutation(tour, self.mutation_rate)
        return combined_mutation(tour, self.mutation_rate)

    def _diversity(self, population: List[List[int]]) -> float:
        """Porcentaje de tours unicos en la poblacion."""
        return len(set(tuple(t) for t in population)) / len(population)

    # ------------------------------------------------------------------
    # Ejecucion principal
    # ------------------------------------------------------------------

    def run(self) -> Tuple[List[int], float]:
        random.seed(self.seed)
        np.random.seed(self.seed)

        population = [self._random_tour() for _ in range(self.pop_size)]

        for gen in range(self.n_generations):
            fitnesses = [self._fitness(t) for t in population]
            distances = [tour_distance(t, self.dist_matrix) for t in population]

            # Actualizar mejor global
            min_dist_idx = int(np.argmin(distances))
            if distances[min_dist_idx] < self.best_distance:
                self.best_distance = distances[min_dist_idx]
                self.best_tour = population[min_dist_idx][:]

            # Registrar historial
            self.best_fitness_history.append(max(fitnesses))
            self.avg_fitness_history.append(float(np.mean(fitnesses)))
            self.worst_fitness_history.append(min(fitnesses))
            self.best_dist_history.append(self.best_distance)
            self.diversity_history.append(self._diversity(population))

            if self.verbose and gen % 100 == 0:
                print(
                    f"  Gen {gen:4d}: dist={self.best_distance:.2f}  "
                    f"diversidad={self.diversity_history[-1]:.1%}"
                )

            # Elitismo: conservar los mejores
            elite = apply_elitism(population, fitnesses, self.n_elite)

            # Generar nueva poblacion
            new_pop = list(elite)
            while len(new_pop) < self.pop_size:
                p1 = tournament_selection(population, fitnesses, self.tournament_k)
                p2 = tournament_selection(population, fitnesses, self.tournament_k)
                c1, c2 = ox_crossover(p1, p2)
                c1 = self._mutate(c1)
                c2 = self._mutate(c2)
                new_pop.extend([c1, c2])

            population = new_pop[: self.pop_size]

        if self.verbose:
            print(f"  Gen {self.n_generations}: dist={self.best_distance:.2f}  [FINAL]")

        return self.best_tour, self.best_distance
