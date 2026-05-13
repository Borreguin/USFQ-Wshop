import numpy as np
from typing import List, Tuple

from ga_tsp.distances import tour_distance


def nearest_neighbor_tour(dist_matrix: np.ndarray,
                           start: int = 0) -> Tuple[List[int], float]:
    """
    Heuristica Vecino Cercano (Nearest Neighbor) para TSP.

    Algoritmo greedy O(n^2):
      1. Comenzar desde la ciudad `start`.
      2. En cada paso, visitar la ciudad no visitada mas cercana.
      3. Regresar a la ciudad inicial para cerrar el circuito.

    No garantiza la solucion optima, pero produce una ruta razonable
    en tiempo lineal que sirve como linea base de comparacion.
    """
    n = len(dist_matrix)
    visited = [False] * n
    tour = [start]
    visited[start] = True

    for _ in range(n - 1):
        current = tour[-1]
        # Distancias desde current a no visitados
        dists = np.where(visited, np.inf, dist_matrix[current])
        nearest = int(np.argmin(dists))
        tour.append(nearest)
        visited[nearest] = True

    dist = tour_distance(tour, dist_matrix)
    return tour, dist
