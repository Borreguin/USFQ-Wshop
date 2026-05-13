import numpy as np
from typing import List

from ga_tsp.distances import tour_distance


def two_opt(tour: List[int], dist_matrix: np.ndarray) -> List[int]:
    """
    Mejora local 2-opt: elimina cruces de aristas invirtiendo segmentos.

    Complejidad O(n^2) por iteracion. Se aplica como post-procesamiento
    sobre la mejor solucion del GA para refinar el resultado final.
    Garantiza que no existan dos aristas que se crucen en el plano Euclideo.
    """
    best = tour[:]
    n = len(best)
    best_dist = tour_distance(best, dist_matrix)
    improved = True
    while improved:
        improved = False
        for i in range(n - 1):
            for j in range(i + 2, n):
                if i == 0 and j == n - 1:
                    continue
                new_tour = best[:i+1] + best[i+1:j+1][::-1] + best[j+1:]
                new_dist = tour_distance(new_tour, dist_matrix)
                if new_dist < best_dist - 1e-10:
                    best = new_tour
                    best_dist = new_dist
                    improved = True
    return best


def nn_with_perturbation(dist_matrix: np.ndarray, start: int) -> List[int]:
    """Vecino Cercano desde un nodo de inicio distinto (para diversificar poblacion inicial)."""
    from ga_tsp.nearest_neighbor import nearest_neighbor_tour
    tour, _ = nearest_neighbor_tour(dist_matrix, start=start)
    return tour
