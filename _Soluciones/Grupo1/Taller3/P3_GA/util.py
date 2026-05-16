from typing import List

def word_to_array(word: str):
    return [ord(w) for w in word]

def distance_Levenshtein(list1:List[int], list2:List[int]):
    # Levenshtein (edit) distance between two sequences of character codes.
    # Works on lists of ints (character ordinals) and returns the minimal
    # number of insertions/deletions/substitutions to transform list1 -> list2.
    n = len(list1)
    m = len(list2)
    # quick exits
    if n == 0:
        return m
    if m == 0:
        return n
    # initialize DP table with two rows to save memory
    prev = list(range(m + 1))
    cur = [0] * (m + 1)
    for i in range(1, n + 1):
        cur[0] = i
        a = list1[i - 1]
        for j in range(1, m + 1):
            b = list2[j - 1]
            cost = 0 if a == b else 1
            # substitution, insertion, deletion
            cur[j] = min(prev[j - 1] + cost, prev[j] + 1, cur[j - 1] + 1)
        prev, cur = cur, prev
    return prev[m]

#corregido para usar valores absolutos y considerar la diferencia de longitud entre las palabras
def distance(list1:List[int], list2:List[int]):
    acc = 0
    for e1, e2 in zip(list1, list2):
        acc += abs(e1 - e2)
    n_size = min(len(list1), len(list2))
    if n_size == 0:
        return None
    return acc + abs(len(list1) - len(list2))

def word_distance(word1:str, word2:str):
    return distance(word_to_array(word1), word_to_array(word2))

def choose_best_individual_by_distance(population, aptitudes):
    best_individual = population[0]
    best_aptitude = aptitudes[0]
    for ind, apt in zip(population, aptitudes):
        if apt < best_aptitude:
            best_aptitude = apt
            best_individual = ind
    return best_individual
