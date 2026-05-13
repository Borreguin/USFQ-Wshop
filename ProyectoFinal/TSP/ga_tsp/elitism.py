from typing import List, Tuple


def apply_elitism(population: List[List[int]],
                  fitnesses: List[float],
                  n_elite: int = 2) -> List[List[int]]:
    """
    Elitismo: los `n_elite` mejores individuos pasan intactos a la siguiente
    generacion sin cruce ni mutacion.

    Garantiza que la mejor solucion encontrada nunca se pierde, lo que hace
    que el fitness del mejor individuo sea monotonamente no decreciente.
    """
    sorted_pairs = sorted(zip(fitnesses, population), reverse=True)
    return [ind[:] for _, ind in sorted_pairs[:n_elite]]


def best_individual(population: List[List[int]],
                    fitnesses: List[float]) -> Tuple[List[int], float]:
    """Retorna (tour, fitness) del mejor individuo de la poblacion."""
    best_idx = max(range(len(fitnesses)), key=lambda i: fitnesses[i])
    return population[best_idx][:], fitnesses[best_idx]
