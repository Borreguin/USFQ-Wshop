from random import choice

from operation import *
from util import word_distance


# Generar población
def generate_population(population_size, string_length, seed=MY_SEED):
    random.seed(seed)
    population = []
    for _ in range(population_size):
        # crear un individuo aleatorio de tamaño string_length
        individual = ''.join(choice(all_possible_gens) for _ in range(string_length))
        population.append(individual)
    return population


# Función de evaluación de aptitud
def evaluate_aptitude(evaluation_type, individual, objetive):
    if evaluation_type == AptitudeType.DEFAULT:
        aptitude = 0
        for i in range(len(individual)):
            if individual[i] == objetive[i]:
                aptitude += 1
        return aptitude

    if evaluation_type == AptitudeType.BY_DISTANCE:
        return word_distance(individual, objetive)

    if evaluation_type == AptitudeType.NEW:
        print("implement here the new evaluation")
        return 0

# Selección del mejor individuo
def select_best_individual(_type: BestIndividualSelectionType, population, aptitudes):
    if _type == BestIndividualSelectionType.DEFAULT:
        best_aptitude = max(aptitudes)
        return population[aptitudes.index(best_aptitude)], best_aptitude

    if _type == BestIndividualSelectionType.MIN_DISTANCE:
        best_aptitude = min(aptitudes)
        return population[aptitudes.index(best_aptitude)], best_aptitude

    if _type == BestIndividualSelectionType.NEW:
        print("implement here the new best individual selection")
        return None, None

def generate_new_population(_type: NewGenerationType, population, aptitudes, mutation_rate):
    if _type == NewGenerationType.DEFAULT:
        new_population = []
        # se generara 2 hijos con cada par de padres, se interactúa con la mitad de poplación para mantener el mismo
        # numero de individuos en la siguiente generación
        for _ in range(len(population) // 2):
            parent1, parent2 = parent_selection(ParentSelectionType.DEFAULT, population, aptitudes)
            child1, child2 = crossover(CrossoverType.DEFAULT, parent1, parent2)
            child1 = mutate(MutationType.DEFAULT, child1, mutation_rate)
            child2 = mutate(MutationType.DEFAULT, child2, mutation_rate)
            new_population.extend([child1, child2])
        return new_population
    if _type == NewGenerationType.MIN_DISTANCE:
        new_population = []
        for _ in range(len(population)//2):
            parent1, parent2 = parent_selection(ParentSelectionType.MIN_DISTANCE, population, aptitudes)
            child1, child2 = crossover(CrossoverType.DEFAULT, parent1, parent2)
            child1 = mutate(MutationType.DEFAULT, child1, mutation_rate)
            child2 = mutate(MutationType.DEFAULT, child2, mutation_rate)
            new_population.extend([child1, child2])
        return new_population

    if _type == NewGenerationType.NEW:
        # Elitismo: conservar el top 10% directamente, luego rellenar con torneo + cruce uniforme
        elite_count = max(1, len(population) // 10)
        sorted_indices = sorted(range(len(aptitudes)), key=lambda i: aptitudes[i], reverse=True)
        new_population = [population[i] for i in sorted_indices[:elite_count]]
        while len(new_population) < len(population):
            parent1, parent2 = parent_selection(ParentSelectionType.NEW, population, aptitudes)
            child1, child2 = crossover(CrossoverType.NEW, parent1, parent2)
            child1 = mutate(MutationType.DEFAULT, child1, mutation_rate)
            child2 = mutate(MutationType.DEFAULT, child2, mutation_rate)
            new_population.extend([child1, child2])
        return new_population[:len(population)]

    if _type == NewGenerationType.DEFINITIVE:
        # Elitismo 20% + torneo k=10 + cruce uniforme
        elite_count = max(1, len(population) // 5)
        sorted_indices = sorted(range(len(aptitudes)), key=lambda i: aptitudes[i], reverse=True)
        new_population = [population[i] for i in sorted_indices[:elite_count]]
        indices = list(range(len(population)))
        k = 10
        while len(new_population) < len(population):
            c1 = random.sample(indices, k)
            c2 = random.sample(indices, k)
            parent1 = population[max(c1, key=lambda i: aptitudes[i])]
            parent2 = population[max(c2, key=lambda i: aptitudes[i])]
            child1, child2 = crossover(CrossoverType.NEW, parent1, parent2)
            child1 = mutate(MutationType.DEFAULT, child1, mutation_rate)
            child2 = mutate(MutationType.DEFAULT, child2, mutation_rate)
            new_population.extend([child1, child2])
        return new_population[:len(population)]