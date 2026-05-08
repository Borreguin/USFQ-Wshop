from random import choice

from Taller3.P3_GA.operation import *
from Taller3.P3_GA.util import word_distance


def generate_population(population_size, string_length, seed=MY_SEED):
    # Fijamos la semilla para que la población inicial sea reproducible
    random.seed(seed)
    population = []
    for _ in range(population_size):
        # choice() elige un carácter al azar del alfabeto definido en constants.py
        # ''.join() une los caracteres en un string de longitud string_length
        individual = ''.join(choice(all_possible_gens) for _ in range(string_length))
        population.append(individual)
    return population


def evaluate_aptitude(evaluation_type, individual, objetive):
    if evaluation_type == AptitudeType.DEFAULT:
        # Cuenta cuántos caracteres coinciden posición a posición
        # Rango: 0 (ninguna coincidencia) a len(objective) (individuo = objetivo)
        # El algoritmo busca MAXIMIZAR este valor
        aptitude = 0
        for i in range(len(individual)):
            if individual[i] == objetive[i]:
                aptitude += 1
        return aptitude

    if evaluation_type == AptitudeType.BY_DISTANCE:
        # Usa la distancia Manhattan entre el individuo y el objetivo
        # El algoritmo busca MINIMIZAR este valor (0 = igual al objetivo)
        # ANTES del fix de util.py, esta distancia era siempre ~0 → no servía
        return word_distance(individual, objetive)

    if evaluation_type == AptitudeType.NEW:
        print("implement here the new evaluation")
        return 0


def select_best_individual(_type: BestIndividualSelectionType, population, aptitudes):
    if _type == BestIndividualSelectionType.DEFAULT:
        # MAX: el mejor individuo es el que más caracteres coincide con el objetivo
        best_aptitude = max(aptitudes)
        return population[aptitudes.index(best_aptitude)], best_aptitude

    if _type == BestIndividualSelectionType.MIN_DISTANCE:
        # MIN: el mejor individuo es el de menor distancia al objetivo
        best_aptitude = min(aptitudes)
        return population[aptitudes.index(best_aptitude)], best_aptitude

    if _type == BestIndividualSelectionType.NEW:
        print("implement here the new best individual selection")
        return None, None


def generate_new_population(_type: NewGenerationType, population, aptitudes, mutation_rate):
    if _type == NewGenerationType.DEFAULT:
        new_population = []
        # Se generan 2 hijos por cada par de padres.
        # Con len(population)//2 iteraciones mantenemos el mismo número de individuos.
        for _ in range(len(population) // 2):
            parent1, parent2 = parent_selection(ParentSelectionType.DEFAULT, population, aptitudes)
            child1, child2 = crossover(CrossoverType.DEFAULT, parent1, parent2)
            child1 = mutate(MutationType.DEFAULT, child1, mutation_rate)
            child2 = mutate(MutationType.DEFAULT, child2, mutation_rate)
            new_population.extend([child1, child2])
        return new_population

    if _type == NewGenerationType.MIN_DISTANCE:
        new_population = []
        for _ in range(len(population) // 2):
            parent1, parent2 = parent_selection(ParentSelectionType.MIN_DISTANCE, population, aptitudes)
            child1, child2 = crossover(CrossoverType.DEFAULT, parent1, parent2)
            child1 = mutate(MutationType.DEFAULT, child1, mutation_rate)
            child2 = mutate(MutationType.DEFAULT, child2, mutation_rate)
            new_population.extend([child1, child2])
        return new_population

    if _type == NewGenerationType.NEW:
        # --- GENERACIÓN CON ELITISMO + TORNEO + CRUCE DOS PUNTOS (ítem 4) ---
        #
        # ELITISMO: los N mejores individuos de la generación actual pasan
        # directamente a la siguiente sin modificación. Esto evita perder
        # la mejor solución encontrada hasta el momento.
        #
        n_elite = 2  # número de individuos élite que sobreviven sin cambios
        # Ordenamos de mayor a menor aptitud y tomamos los primeros n_elite
        sorted_pairs = sorted(zip(aptitudes, population), reverse=True)
        elite = [ind for _, ind in sorted_pairs[:n_elite]]

        # El resto de la población se genera con torneo + cruce de dos puntos
        new_population = list(elite)
        while len(new_population) < len(population):
            # Torneo: selecciona el mejor de un subconjunto aleatorio
            parent1, parent2 = parent_selection(ParentSelectionType.NEW, population, aptitudes)
            # Cruce de dos puntos: mayor mezcla genética
            child1, child2 = crossover(CrossoverType.NEW, parent1, parent2)
            # Mutación estándar sobre los hijos
            child1 = mutate(MutationType.DEFAULT, child1, mutation_rate)
            child2 = mutate(MutationType.DEFAULT, child2, mutation_rate)
            new_population.extend([child1, child2])

        # Recortamos al tamaño exacto de la población original
        return new_population[:len(population)]
