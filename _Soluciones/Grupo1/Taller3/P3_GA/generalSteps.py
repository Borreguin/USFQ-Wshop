from random import choice

from Taller3.P3_GA.operation import *
from Taller3.P3_GA.util import word_distance

from Taller3.P3_GA.GA import GA
from Taller3.P3_GA.constants import MY_SEED


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
    if _type == NewGenerationType.TOURNAMENT:
        new_population = []
        for _ in range(len(population)//2):
            parent1, parent2 = parent_selection(ParentSelectionType.TOURNAMENT, population, aptitudes)
            child1, child2 = crossover(CrossoverType.DEFAULT, parent1, parent2)
            child1 = mutate(MutationType.DEFAULT, child1, mutation_rate)
            child2 = mutate(MutationType.DEFAULT, child2, mutation_rate)
            new_population.extend([child1, child2])
        return new_population
    if _type == NewGenerationType.TOURNAMENT_ELITISM:
        # elitism: keep the best individual (smallest distance)
        new_population = []
        best_idx = aptitudes.index(min(aptitudes))
        new_population.append(population[best_idx])
        target_size = len(population)
        # generate children until we reach the target size
        while len(new_population) < target_size:
            parent1, parent2 = parent_selection(ParentSelectionType.TOURNAMENT, population, aptitudes)
            child1, child2 = crossover(CrossoverType.DEFAULT, parent1, parent2)
            child1 = mutate(MutationType.DEFAULT, child1, mutation_rate)
            child2 = mutate(MutationType.DEFAULT, child2, mutation_rate)
            new_population.extend([child1, child2])
        # trim if we exceeded target_size
        return new_population[:target_size]

    if _type == NewGenerationType.NEW:
        print("implement here the new generation")


def case_study_4(_objetive):

    population_sizes = [50, 100, 200, 500]
    mutation_rate = 0.01
    n_iterations = 1000
    n_runs = 5
    for pop_size in population_sizes:
        generations_when_found = []
        print('\n========================================')
        print(f'Ejecutando con tamaño de población: {pop_size}')
        for _ in range(n_runs):
            random.seed(MY_SEED)
            population = generate_population(pop_size, len(_objetive))
            ga = GA(population, _objetive, mutation_rate, n_iterations)
            ga.set_evaluation_type(AptitudeType.BY_DISTANCE)
            ga.set_best_individual_selection_type(BestIndividualSelectionType.MIN_DISTANCE)
            ga.set_new_generation_type(NewGenerationType.TOURNAMENT_ELITISM)
            success, _, generations_to_goal = ga.run(verbose=False, return_history=True)
            if success and generations_to_goal is not None:
                generations_when_found.append(generations_to_goal)
        if generations_when_found:
            avg_generations = sum(generations_when_found) / len(generations_when_found)
            print(f'Promedio de generaciones para alcanzar el objetivo: {avg_generations:.1f} ({len(generations_when_found)}/{n_runs} runs exitosos)')
        else:
            print('No se alcanzó el objetivo en ningún run.')