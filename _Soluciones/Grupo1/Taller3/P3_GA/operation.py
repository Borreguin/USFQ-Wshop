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
        # Tournament selection (prefer individuals with smaller distance)
        def tournament(k=5):
            # sample k distinct indices
            k = min(k, len(population))
            indices = random.sample(range(len(population)), k)
            best_idx = indices[0]
            best_apt = aptitudes[best_idx]
            for idx in indices[1:]:
                if aptitudes[idx] < best_apt:
                    best_idx = idx
                    best_apt = aptitudes[idx]
            return population[best_idx]

        parent1 = tournament()
        parent2 = tournament()
        # ensure two distinct parents
        attempts = 0
        while parent2 == parent1 and attempts < 5:
            parent2 = tournament()
            attempts += 1
        return parent1, parent2

    if _type == ParentSelectionType.NEW:
        print("implement here the new parent selection")
        return None


def crossover(_type: CrossoverType, parent1, parent2):
    if _type == CrossoverType.DEFAULT:
        # Cruce de dos padres para producir descendencia
        crossover_point = random.randint(1, len(parent1) - 1)
        child1 = parent1[:crossover_point] + parent2[crossover_point:]
        child2 = parent2[:crossover_point] + parent1[crossover_point:]
        return child1, child2
    if _type == CrossoverType.NEW:
        print("implement here the new crossover")
        return None


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