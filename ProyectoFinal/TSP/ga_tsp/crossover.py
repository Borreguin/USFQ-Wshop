import random
from typing import List, Tuple


def ox_crossover(parent1: List[int], parent2: List[int]) -> Tuple[List[int], List[int]]:
    """
    Order Crossover (OX) para permutaciones de ciudades.

    Algoritmo:
      1. Elegir dos puntos de corte aleatorios (start, end).
      2. El hijo hereda el segmento [start..end] del padre 1 en su posicion original.
      3. Las ciudades restantes se copian del padre 2 en el orden en que aparecen,
         comenzando despues del punto 'end', sin repetir ciudades ya incluidas.

    OX preserva el orden relativo de las ciudades de cada padre, lo que es
    especialmente eficaz para TSP porque mantiene subsecuencias de rutas buenas.
    """
    n = len(parent1)
    start, end = sorted(random.sample(range(n), 2))

    def make_child(p_segment: List[int], p_order: List[int]) -> List[int]:
        child = [None] * n
        child[start: end + 1] = p_segment[start: end + 1]
        used = set(child[start: end + 1])
        # Recorrer p_order empezando desde end+1 (circular)
        order = list(range(end + 1, n)) + list(range(end + 1))
        remaining = [c for c in (p_order[i] for i in order) if c not in used]
        fill_positions = [i for i in order if child[i] is None]
        for pos, city in zip(fill_positions, remaining):
            child[pos] = city
        return child

    return make_child(parent1, parent2), make_child(parent2, parent1)
