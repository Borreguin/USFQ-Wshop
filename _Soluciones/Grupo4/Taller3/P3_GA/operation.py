import random
from _Soluciones.Grupo4.Taller3.P3_GA.constants import *
from _Soluciones.Grupo4.Taller3.P3_GA.util import *


def parent_selection(_type: ParentSelectionType, population, aptitudes):

    if _type == ParentSelectionType.DEFAULT:
        # Selección por ruleta

        cumulative = sum(aptitudes)

        # Caso especial: todos tienen aptitud 0
        if cumulative == 0:
            parents = random.sample(population, 2)
            return parents[0], parents[1]

        selection_probability = [
            aptitude / cumulative
            for aptitude in aptitudes
        ]

        parents = random.choices(
            population,
            weights=selection_probability,
            k=2
        )

        return parents[0], parents[1]

    if _type == ParentSelectionType.MIN_DISTANCE:
        # seleccionando randomicamente dos poblaciones diferentes para cada padre
        # se podria seleccionar de otra manera?
        partition_size = random.randint(1, len(population)-1)
        parent1 = choose_best_individual_by_distance(population[:partition_size], aptitudes[:partition_size])
        parent2 = choose_best_individual_by_distance(population[partition_size:], aptitudes[partition_size:])
        return parent1, parent2

    if _type == ParentSelectionType.NEW:
        tournament_size = max(2, len(population) // 10)

        tournament1 = random.sample(
            range(len(population)),
            tournament_size
        )

        tournament2 = random.sample(
            range(len(population)),
            tournament_size
        )

        best1_idx = max(
            tournament1,
            key=lambda i: aptitudes[i]
        )

        best2_idx = max(
            tournament2,
            key=lambda i: aptitudes[i]
        )

        return (
            population[best1_idx],
            population[best2_idx]
        )


def crossover(_type: CrossoverType, parent1, parent2):
    if _type == CrossoverType.DEFAULT:
        # Cruce de dos padres para producir descendencia
        crossover_point = random.randint(1, len(parent1) - 1)
        child1 = parent1[:crossover_point] + parent2[crossover_point:]
        child2 = parent2[:crossover_point] + parent1[crossover_point:]
        return child1, child2

    if _type == CrossoverType.NEW:
        # Cruce uniforme: cada gen tiene 50% de probabilidad de venir de cada padre
        child1 = ""
        child2 = ""
        for i in range(len(parent1)):
            if random.random() < 0.5:
                child1 += parent1[i]
                child2 += parent2[i]
            else:
                child1 += parent2[i]
                child2 += parent1[i]
        return child1, child2

    # Por defecto
    return parent1, parent2


def mutate(_type: MutationType, individual, mutation_rate):
    if _type == MutationType.DEFAULT:
        # Mutación de un individuo
        for i in range(len(individual)):
            if random.random() < mutation_rate:
                individual = individual[:i] + random.choice(all_possible_gens) + individual[i + 1:]
        return individual

    if _type == MutationType.NEW:
        # Mutación adaptativa: muta con mayor frecuencia al inicio
        for i in range(len(individual)):
            if random.random() < mutation_rate * 2:
                individual = individual[:i] + random.choice(all_possible_gens) + individual[i + 1:]
        return individual

    # Por defecto
    return individual
