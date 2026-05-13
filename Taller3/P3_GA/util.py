from typing import List


def word_to_array(word: str):
    # ord() convierte cada carácter a su código ASCII entero
    # Ej: 'A'->65, 'a'->97, ' '->32, '!'->33
    return [ord(w) for w in word]


# =============================================================================
# ANÁLISIS DEL BUG ORIGINAL (ítem 2 del taller)
# =============================================================================
# La función acumulaba (e1 - e2) SIN valor absoluto.
# Ejemplo: distance("cba", "abc")
#   c=99, a=97  → 99-97 = +2
#   b=98, b=98  → 98-98 =  0
#   a=97, c=99  → 97-99 = -2
#   total = 0  ← ¡pero "cba" ≠ "abc"!
# Los errores positivos cancelan los negativos → distancia siempre ≈ 0
# → la ruleta asigna probabilidades iguales a todos → sin convergencia.
#
# FIX: usar abs(e1 - e2) → Distancia Manhattan (norma L1 sobre códigos ASCII).
# =============================================================================


def distance(list1: List[int], list2: List[int]):
    """
    Métrica: Distancia Manhattan (norma L1) sobre códigos ASCII.

    Suma la diferencia absoluta posición a posición.
    Rango: 0 (idénticos) a N * max_delta (donde max_delta ≈ 94 para el alfabeto
    imprimible de ASCII 32–126).

    ¿Por qué Manhattan es mejor que simplemente contar coincidencias?
      - Contar coincidencias es binario: correcto(0 diff) o incorrecto(>0 diff),
        sin distinguir "casi correcto" de "muy incorrecto".
      - Manhattan es continuo: 'A'(65) vs 'B'(66) → distancia 1; 'A' vs 'z'(122)
        → distancia 57. El GA puede guiar la búsqueda hacia caracteres cercanos al
        objetivo antes de alcanzarlos exactamente.

    ¿Por qué no Levenshtein/Jaro-Winkler?
      - Para strings de IGUAL longitud, Levenshtein = Hamming (número de posiciones
        distintas) → mismo gradiente binario que contar coincidencias.
      - Jaro-Winkler está diseñado para comparar nombres propios con transposiciones,
        no para guiar un GA posición a posición.
      → Manhattan gana porque provee señal de gradiente continua y eficiente.
    """
    n_size = min(len(list1), len(list2))
    if n_size == 0:
        return None

    acc = 0
    for e1, e2 in zip(list1, list2):
        acc += abs(e1 - e2)   # abs() garantiza acumulación positiva siempre

    # Penalización por diferencia de longitud:
    # cada carácter extra aporta abs(e) como si el otro tuviera '\0'=0
    for extra in list1[n_size:]:
        acc += abs(extra)
    for extra in list2[n_size:]:
        acc += abs(extra)

    return acc


def word_distance(word1: str, word2: str):
    """Distancia Manhattan entre dos strings (vía sus códigos ASCII)."""
    return distance(word_to_array(word1), word_to_array(word2))


# =============================================================================
# JARO-WINKLER: métrica estándar de similitud entre palabras (referencia NLP)
# =============================================================================
# Jaro-Winkler es la métrica canónica para "similitud entre palabras" en NLP:
# mide coincidencias y transposiciones dentro de una ventana de matching,
# y premia los prefijos comunes. Rango: [0, 1], donde 1 = idénticos.
#
# Para este GA NO se usa como fitness principal porque:
#   1. Es [0,1] → hay que invertirla (1-jw) para obtener una distancia.
#   2. Premia prefijos: favorece strings como "GA" pero no ayuda con el resto.
#   3. No distingue la magnitud de la diferencia carácter a carácter.
# → Se incluye aquí como referencia educativa y comparativa.
# =============================================================================

def jaro_similarity(s1: str, s2: str) -> float:
    """
    Similitud de Jaro entre dos strings. Rango [0, 1], 1 = idénticos.
    Mide: proporción de caracteres coincidentes y número de transposiciones.
    """
    if s1 == s2:
        return 1.0
    len1, len2 = len(s1), len(s2)
    if len1 == 0 or len2 == 0:
        return 0.0

    match_dist = max(len1, len2) // 2 - 1
    s1_flags = [False] * len1
    s2_flags = [False] * len2
    matches = 0

    for i in range(len1):
        start = max(0, i - match_dist)
        end = min(i + match_dist + 1, len2)
        for j in range(start, end):
            if s2_flags[j] or s1[i] != s2[j]:
                continue
            s1_flags[i] = s2_flags[j] = True
            matches += 1
            break

    if matches == 0:
        return 0.0

    transpositions = 0
    k = 0
    for i in range(len1):
        if not s1_flags[i]:
            continue
        while not s2_flags[k]:
            k += 1
        if s1[i] != s2[k]:
            transpositions += 1
        k += 1

    return (matches / len1 + matches / len2 +
            (matches - transpositions / 2) / matches) / 3


def jaro_winkler_similarity(s1: str, s2: str, p: float = 0.1) -> float:
    """
    Similitud Jaro-Winkler: extiende Jaro premiando coincidencias de prefijo.
    p: factor de prefijo (estándar = 0.1, máx recomendado 0.25).
    Rango [0, 1], 1 = idénticos.
    """
    jaro = jaro_similarity(s1, s2)
    prefix_len = 0
    for i in range(min(4, min(len(s1), len(s2)))):
        if s1[i] == s2[i]:
            prefix_len += 1
        else:
            break
    return jaro + prefix_len * p * (1 - jaro)


def jaro_winkler_distance(word1: str, word2: str) -> float:
    """Distancia Jaro-Winkler: 1 - similitud. Rango [0, 1], 0 = idénticos."""
    return 1.0 - jaro_winkler_similarity(word1, word2)


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
