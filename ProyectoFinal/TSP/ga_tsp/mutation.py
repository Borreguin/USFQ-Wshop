import random
from typing import List


def swap_mutation(tour: List[int], rate: float) -> List[int]:
    """
    Mutacion por intercambio (swap): con probabilidad `rate`,
    elige dos posiciones al azar y las intercambia.
    Preserva la validez de la permutacion.
    """
    tour = tour[:]
    if random.random() < rate:
        i, j = random.sample(range(len(tour)), 2)
        tour[i], tour[j] = tour[j], tour[i]
    return tour


def inversion_mutation(tour: List[int], rate: float) -> List[int]:
    """
    Mutacion por inversion: con probabilidad `rate`,
    elige un segmento aleatorio y lo invierte.
    Equivalente a deshacer un cruce 2-opt, por lo que puede mejorar
    la ruta en espacios Euclidianos.
    """
    tour = tour[:]
    if random.random() < rate:
        i, j = sorted(random.sample(range(len(tour)), 2))
        tour[i: j + 1] = tour[i: j + 1][::-1]
    return tour


def combined_mutation(tour: List[int], rate: float) -> List[int]:
    """
    Aplica primero swap y luego inversion, cada uno con probabilidad `rate`.
    Combina exploracion local (swap) con mejora estructural (inversion).
    """
    tour = swap_mutation(tour, rate)
    tour = inversion_mutation(tour, rate)
    return tour
