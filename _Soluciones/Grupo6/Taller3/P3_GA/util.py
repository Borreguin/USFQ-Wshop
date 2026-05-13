from typing import List


def word_to_array(word: str):
    return [ord(w) for w in word]


def distance(list1: List[int], list2: List[int]):
    """
    Distancia de Hamming entre dos listas de valores ASCII.

    Ejercicio 3 — corrección:
    La versión original usaba (e1 - e2) sin valor absoluto, lo que permitía que
    diferencias positivas y negativas se cancelaran entre sí (e.g., 'abc' vs
    'cba' devolvía 0 aunque son palabras muy distintas).
    La corrección aplica abs() en cada par, garantizando una distancia siempre
    >= 0 que crece a medida que los individuos se alejan del objetivo.
    """
    acc = sum(abs(e1 - e2) for e1, e2 in zip(list1, list2))
    # Penalizar diferencias de longitud con el mayor delta ASCII posible
    acc += abs(len(list1) - len(list2)) * 128
    return acc


def word_distance(word1: str, word2: str):
    return distance(word_to_array(word1), word_to_array(word2))


def choose_best_individual_by_distance(population, aptitudes):
    best_individual = population[0]
    best_aptitude = aptitudes[0]
    for ind, apt in zip(population, aptitudes):
        if apt < best_aptitude:
            best_aptitude = apt
            best_individual = ind
    return best_individual
