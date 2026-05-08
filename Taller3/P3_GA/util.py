from typing import List


def word_to_array(word: str):
    # ord() convierte cada carácter a su código ASCII entero
    # Ej: 'A'->65, 'a'->97, ' '->32, '!'->33
    return [ord(w) for w in word]


# PROBLEMA ORIGINAL (ítem 2 del taller):
# La función acumulaba (e1 - e2) SIN valor absoluto.
# Ejemplo: distance("cba", "abc")
#   c=99, a=97  → 99-97 = +2
#   b=98, b=98  → 98-98 =  0
#   a=97, c=99  → 97-99 = -2
#   total = 0  ← ¡pero "cba" ≠ "abc"!
# Los errores positivos cancelan los negativos → distancia siempre ≈ 0
# → el algoritmo no puede ordenar cuál individuo está más cerca del objetivo.

def distance(list1: List[int], list2: List[int]):
    """
    Distancia Manhattan entre dos listas de códigos ASCII.
    Mide cuánto difieren posición a posición, sin cancelaciones.
    Menor distancia = individuo más parecido al objetivo.
    """
    n_size = min(len(list1), len(list2))
    if n_size == 0:
        return None

    acc = 0
    for e1, e2 in zip(list1, list2):
        acc += abs(e1 - e2)   # abs() garantiza acumulación positiva siempre

    # Penalización por diferencia de longitud:
    # cada carácter extra en list1 aporta abs(e) porque list2 tiene implícito 0
    for extra in list1[n_size:]:
        acc += abs(extra)
    for extra in list2[n_size:]:
        acc += abs(extra)

    return acc


def word_distance(word1: str, word2: str):
    # Convierte las palabras a listas de ASCII y calcula su distancia
    return distance(word_to_array(word1), word_to_array(word2))


def choose_best_individual_by_distance(population, aptitudes):
    # Busca el individuo cuya aptitud (distancia) sea la MENOR
    # porque menor distancia = más parecido al objetivo
    best_individual = population[0]
    best_aptitude = aptitudes[0]
    for ind, apt in zip(population, aptitudes):
        if apt < best_aptitude:
            best_aptitude = apt
            best_individual = ind
    return best_individual
