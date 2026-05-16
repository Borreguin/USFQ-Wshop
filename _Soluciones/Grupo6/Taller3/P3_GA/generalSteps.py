import random
from random import choice

from Taller3.P3_GA.operation import *
from Taller3.P3_GA.util import word_distance


def generate_population(population_size, string_length, seed=MY_SEED):
    random.seed(seed)
    return [
        ''.join(choice(all_possible_gens) for _ in range(string_length))
        for _ in range(population_size)
    ]


def evaluate_aptitude(evaluation_type, individual, objective):
    if evaluation_type == AptitudeType.DEFAULT:
        return sum(a == b for a, b in zip(individual, objective))

    if evaluation_type == AptitudeType.BY_DISTANCE:
        return word_distance(individual, objective)

    raise ValueError(f"AptitudeType desconocido: {evaluation_type}")


def select_best_individual(_type: BestIndividualSelectionType, population, aptitudes):
    if _type == BestIndividualSelectionType.DEFAULT:
        best_aptitude = max(aptitudes)
        return population[aptitudes.index(best_aptitude)], best_aptitude

    if _type == BestIndividualSelectionType.MIN_DISTANCE:
        best_aptitude = min(aptitudes)
        return population[aptitudes.index(best_aptitude)], best_aptitude

    raise ValueError(f"BestIndividualSelectionType desconocido: {_type}")


def generate_new_population(_type: NewGenerationType, population, aptitudes, mutation_rate):

    if _type == NewGenerationType.DEFAULT:
        new_population = []
        for _ in range(len(population) // 2):
            p1, p2 = parent_selection(ParentSelectionType.DEFAULT, population, aptitudes)
            c1, c2 = crossover(CrossoverType.DEFAULT, p1, p2)
            new_population.extend([
                mutate(MutationType.DEFAULT, c1, mutation_rate),
                mutate(MutationType.DEFAULT, c2, mutation_rate),
            ])
        return new_population

    if _type == NewGenerationType.MIN_DISTANCE:
        new_population = []
        for _ in range(len(population) // 2):
            p1, p2 = parent_selection(ParentSelectionType.MIN_DISTANCE, population, aptitudes)
            c1, c2 = crossover(CrossoverType.DEFAULT, p1, p2)
            new_population.extend([
                mutate(MutationType.DEFAULT, c1, mutation_rate),
                mutate(MutationType.DEFAULT, c2, mutation_rate),
            ])
        return new_population

    if _type == NewGenerationType.IMPROVED:
        n_elite = max(2, len(population) // 10)
        ranked = sorted(zip(aptitudes, population), reverse=True)
        elite = [ind for _, ind in ranked[:n_elite]]

        new_population = list(elite)
        n_children = len(population) - n_elite

        for _ in range(n_children // 2):
            p1, p2 = parent_selection(ParentSelectionType.TOURNAMENT, population, aptitudes)
            c1, c2 = crossover(CrossoverType.TWO_POINT, p1, p2)
            new_population.extend([
                mutate(MutationType.DEFAULT, c1, mutation_rate),
                mutate(MutationType.DEFAULT, c2, mutation_rate),
            ])

        while len(new_population) < len(population):
            p1, p2 = parent_selection(ParentSelectionType.TOURNAMENT, population, aptitudes)
            c1, _ = crossover(CrossoverType.TWO_POINT, p1, p2)
            new_population.append(mutate(MutationType.DEFAULT, c1, mutation_rate))

        return new_population[:len(population)]

    raise ValueError(f"NewGenerationType desconocido: {_type}")
