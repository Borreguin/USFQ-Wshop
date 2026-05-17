import random
from Taller3.P3_GA.constants import *
from Taller3.P3_GA.util import *


def parent_selection(_type: ParentSelectionType, population, aptitudes):
    if _type == ParentSelectionType.DEFAULT:
        # Selección de padres por ruleta
        cumulative = sum(aptitudes)
        selection_probability = [aptitude / cumulative for aptitude in aptitudes]
        parents = random.choices(population, weights=selection_probability, k=2)
        return parents
    if _type == ParentSelectionType.MIN_DISTANCE:
        # seleccionando randomicamente dos poblaciones diferentes para cada padre
        # se podria seleccionar de otra manera?
        partition_size = random.randint(1, len(population)-1)
        parent1 = choose_best_individual_by_distance(population[:partition_size], aptitudes[:partition_size])
        parent2 = choose_best_individual_by_distance(population[partition_size:], aptitudes[partition_size:])
        return parent1, parent2

    if _type == ParentSelectionType.NEW:
        # Selección por torneo: k candidatos aleatorios, gana el de mayor aptitud
        k = 5
        indices = list(range(len(population)))
        candidates1 = random.sample(indices, k)
        candidates2 = random.sample(indices, k)
        parent1 = population[max(candidates1, key=lambda i: aptitudes[i])]
        parent2 = population[max(candidates2, key=lambda i: aptitudes[i])]
        return parent1, parent2


def crossover(_type: CrossoverType, parent1, parent2):
    if _type == CrossoverType.DEFAULT:
        # Cruce de dos padres para producir descendencia
        crossover_point = random.randint(1, len(parent1) - 1)
        child1 = parent1[:crossover_point] + parent2[crossover_point:]
        child2 = parent2[:crossover_point] + parent1[crossover_point:]
        return child1, child2
    if _type == CrossoverType.NEW:
        # Cruce uniforme: cada posición se toma independientemente de un padre o del otro
        child1 = ''
        child2 = ''
        for g1, g2 in zip(parent1, parent2):
            if random.random() < 0.5:
                child1 += g1
                child2 += g2
            else:
                child1 += g2
                child2 += g1
        return child1, child2


def mutate(_type: MutationType, individual, mutation_rate):
    if _type == MutationType.DEFAULT:
        # Mutación de un individuo
        for i in range(len(individual)):
            if random.random() < mutation_rate:
                individual = individual[:i] + random.choice(all_possible_gens) + individual[i + 1:]
        return individual
    if _type == MutationType.NEW:
        print("implement here the new mutation")
        return None