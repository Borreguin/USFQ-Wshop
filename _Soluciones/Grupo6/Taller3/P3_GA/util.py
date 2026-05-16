from typing import List


def word_to_array(word: str):
    return [ord(w) for w in word]


def distance(list1: List[int], list2: List[int]):
    acc = sum(abs(e1 - e2) for e1, e2 in zip(list1, list2))
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
