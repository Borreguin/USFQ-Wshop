from typing import List


def word_to_array(word: str):
    return [ord(w) for w in word]

# Algo no está bien con esta función de distancia
def distance(list1:List[int], list2:List[int]):
    # sum of absolute differences per position; treat missing positions as 0
    if not list1 and not list2:
        return 0
    acc = 0
    n = max(len(list1), len(list2))
    for i in range(n):
        v1 = list1[i] if i < len(list1) else 0
        v2 = list2[i] if i < len(list2) else 0
        acc += abs(v1 - v2)
    return acc

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



# print(word_distance("abc", "abc"))
# print(word_distance("abc", "abd"))
# print(word_distance("abc", "abz"))
# print(word_distance("abc", "cba"))
# print(word_distance("abc", "cbad"))