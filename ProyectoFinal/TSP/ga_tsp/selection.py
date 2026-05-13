import random
from typing import List


def tournament_selection(population: List[List[int]],
                         fitnesses: List[float],
                         k: int = 5) -> List[int]:
    """
    Tournament selection: sample k individuals at random, return a copy
    of the one with the highest fitness.
    """
    indices = random.sample(range(len(population)), min(k, len(population)))
    best = max(indices, key=lambda i: fitnesses[i])
    return population[best][:]
