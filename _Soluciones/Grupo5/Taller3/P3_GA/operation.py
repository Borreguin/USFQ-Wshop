import random
from Taller3.P3_GA.constants import *
from Taller3.P3_GA.util import *


def parent_selection(_type: ParentSelectionType, population, aptitudes):
    if _type == ParentSelectionType.DEFAULT:
        # --- SELECCIÓN POR RULETA ---
        # Cada individuo tiene una probabilidad de ser elegido proporcional a su aptitud.
        # Si un individuo tiene aptitud 10 y el total es 100, tiene 10% de probabilidad.
        cumulative = sum(aptitudes)
        selection_probability = [aptitude / cumulative for aptitude in aptitudes]
        # random.choices elige 2 padres con esas probabilidades (con reemplazo)
        parents = random.choices(population, weights=selection_probability, k=2)
        return parents

    if _type == ParentSelectionType.MIN_DISTANCE:
        # Divide la población en dos grupos aleatorios y elige el mejor de cada uno
        partition_size = random.randint(1, len(population) - 1)
        parent1 = choose_best_individual_by_distance(
            population[:partition_size], aptitudes[:partition_size])
        parent2 = choose_best_individual_by_distance(
            population[partition_size:], aptitudes[partition_size:])
        return parent1, parent2

    if _type == ParentSelectionType.NEW:
        # --- SELECCIÓN POR TORNEO (ítem 4) ---
        # Se eligen k individuos al azar y el mejor de ellos es el padre.
        # Ventaja vs ruleta: mayor presión selectiva → converge más rápido.
        # Ventaja vs MIN_DISTANCE: no depende de particiones fijas.
        k = 5  # tamaño del torneo: cuántos candidatos compiten por ser padre
        # Torneo para padre 1: muestra k pares (individuo, aptitud) y elige el de mayor aptitud
        candidates_1 = random.choices(
            list(zip(population, aptitudes)), k=min(k, len(population)))
        parent1 = max(candidates_1, key=lambda x: x[1])[0]
        # Torneo independiente para padre 2
        candidates_2 = random.choices(
            list(zip(population, aptitudes)), k=min(k, len(population)))
        parent2 = max(candidates_2, key=lambda x: x[1])[0]
        return parent1, parent2


def crossover(_type: CrossoverType, parent1, parent2):
    if _type == CrossoverType.DEFAULT:
        # --- CRUCE DE UN PUNTO ---
        # Se elige un punto al azar. El hijo 1 toma la primera parte del padre 1
        # y la segunda del padre 2. El hijo 2 hace lo inverso.
        # Ej: padre1="ABCDE", padre2="VWXYZ", punto=2
        #   hijo1 = "AB" + "XYZ" = "ABXYZ"
        #   hijo2 = "VW" + "CDE" = "VWCDE"
        crossover_point = random.randint(1, len(parent1) - 1)
        child1 = parent1[:crossover_point] + parent2[crossover_point:]
        child2 = parent2[:crossover_point] + parent1[crossover_point:]
        return child1, child2

    if _type == CrossoverType.NEW:
        # --- CRUCE DE DOS PUNTOS (ítem 4) ---
        # Se eligen dos puntos: el hijo 1 toma extremos del padre 1 y el medio del padre 2.
        # Ej: padre1="ABCDE", padre2="VWXYZ", punto1=1, punto2=3
        #   hijo1 = "A" + "WX" + "DE" = "AWXDE"
        #   hijo2 = "V" + "BC" + "YZ" = "VBCYZ"
        # Ventaja: mezcla material genético de AMBOS extremos simultáneamente.
        if len(parent1) < 3:
            # Si la cadena es muy corta no hay espacio para 2 puntos
            return parent1, parent2
        point1 = random.randint(1, len(parent1) - 2)
        point2 = random.randint(point1 + 1, len(parent1) - 1)
        child1 = parent1[:point1] + parent2[point1:point2] + parent1[point2:]
        child2 = parent2[:point1] + parent1[point1:point2] + parent2[point2:]
        return child1, child2


def mutate(_type: MutationType, individual, mutation_rate):
    if _type == MutationType.DEFAULT:
        # --- MUTACIÓN ALEATORIA POR POSICIÓN ---
        # Para cada posición del individuo se lanza un "dado" con probabilidad mutation_rate.
        # Si cae, se reemplaza ese carácter por uno aleatorio del alfabeto.
        # Con mutation_rate=0.01 y 17 caracteres, en promedio mutan ~0.17 caracteres/generación.
        for i in range(len(individual)):
            if random.random() < mutation_rate:
                # Sustituye el carácter i por uno aleatorio del conjunto de genes posibles
                individual = individual[:i] + random.choice(all_possible_gens) + individual[i + 1:]
        return individual

    if _type == MutationType.NEW:
        # --- MUTACIÓN POR INTERCAMBIO (swap mutation) ---
        # En lugar de reemplazar un carácter por uno aleatorio, intercambia dos posiciones.
        # Preserva el "material genético" existente mientras cambia la disposición.
        # Útil cuando el problema tiene estructura posicional.
        mutated = list(individual)
        for i in range(len(mutated)):
            if random.random() < mutation_rate:
                j = random.randint(0, len(mutated) - 1)
                # Intercambia los caracteres en posición i y j
                mutated[i], mutated[j] = mutated[j], mutated[i]
        return ''.join(mutated)
