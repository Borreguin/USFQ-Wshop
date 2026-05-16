from random import choice

from Taller3.P3_GA.operation import *
from Taller3.P3_GA.util import word_distance

## from Taller3.P3_GA.GA import GA  # Eliminado para evitar importación circular
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
    from Taller3.P3_GA.GA import GA  # Importación local para evitar ciclo

    population_sizes = [50, 100, 200, 500]
    mutation_rate = 0.01
    n_iterations = 1000
    n_runs = 5
    resumen = []
    output_lines = []
    for pop_size in population_sizes:
        generations_when_found = []
        output_lines.append('\n')
        output_lines.append(f'Ejecutando con tamaño de población: {pop_size}')
        print('\n')
        print(f'Ejecutando con tamaño de población: {pop_size}')
        for run in range(n_runs):
            random.seed(MY_SEED)
            population = generate_population(pop_size, len(_objetive))
            ga = GA(population, _objetive, mutation_rate, n_iterations)
            ga.set_evaluation_type(AptitudeType.BY_DISTANCE)
            ga.set_best_individual_selection_type(BestIndividualSelectionType.MIN_DISTANCE)
            ga.set_new_generation_type(NewGenerationType.TOURNAMENT_ELITISM)
            success, _, generations_to_goal = ga.run(verbose=False, return_history=True)
            if success and generations_to_goal is not None:
                generations_when_found.append(generations_to_goal)
                msg = f"  Run {run+1}: Objetivo alcanzado en {generations_to_goal} generaciones."
            else:
                msg = f"  Run {run+1}: Objetivo NO alcanzado."
            print(msg)
            output_lines.append(msg)
        if generations_when_found:
            avg_generations = sum(generations_when_found) / len(generations_when_found)
            resumen.append((pop_size, avg_generations, len(generations_when_found), n_runs))
            msg = f'Promedio de generaciones para alcanzar el objetivo: {avg_generations:.1f} ({len(generations_when_found)}/{n_runs} runs exitosos)'
            print(msg)
            output_lines.append(msg)
        else:
            resumen.append((pop_size, None, 0, n_runs))
            msg = 'No se alcanzó el objetivo en ningún run.'
            print(msg)
            output_lines.append(msg)
    output_lines.append("\nResumen de resultados por tamaño de población:")
    output_lines.append("Tamaño\tPromedio Generaciones\tRuns Exitosos/Total")
    print("\nResumen de resultados por tamaño de población:")
    print("Tamaño\tPromedio Generaciones\tRuns Exitosos/Total")
    for pop_size, avg_gen, n_success, n_total in resumen:
        if avg_gen is not None:
            line = f"{pop_size}\t{avg_gen:.1f}\t\t{n_success}/{n_total}"
        else:
            line = f"{pop_size}\tNo alcanzado\t{n_success}/{n_total}"
        print(line)
        output_lines.append(line)
    # Guardar resultados en archivo
    with open("case_study_4_resultados.txt", "w", encoding="utf-8") as f:
        for line in output_lines:
            f.write(line + "\n")

            
def case_study_5(_objetive):
    
    print('========== INICIO caso de estudio 5 =========')
    from Taller3.P3_GA.GA import GA  # Importación local para evitar ciclo

    population_sizes = [50, 100, 200, 500]
    mutation_rates = [0.01, 0.05, 0.1]
    n_iterations = 1000
    n_runs = 5
    resumen = []
    output_lines = []
    output_lines.append("Caso de estudio 5: Combinación de lo mejor de los casos anteriores\n")
    for pop_size in population_sizes:
        for mutation_rate in mutation_rates:
            generations_when_found = []
            output_lines.append('\n========================================')
            output_lines.append(f'Población: {pop_size} | Mutación: {mutation_rate}')
            print('\n========================================')
            print(f'Población: {pop_size} | Mutación: {mutation_rate}')
            for run in range(n_runs):
                random.seed(MY_SEED)
                population = generate_population(pop_size, len(_objetive))
                ga = GA(population, _objetive, mutation_rate, n_iterations)
                ga.set_evaluation_type(AptitudeType.BY_DISTANCE)
                ga.set_best_individual_selection_type(BestIndividualSelectionType.MIN_DISTANCE)
                ga.set_new_generation_type(NewGenerationType.TOURNAMENT_ELITISM)
                success, _, generations_to_goal = ga.run(verbose=True, return_history=True)
                if success and generations_to_goal is not None:
                    generations_when_found.append(generations_to_goal)
                    msg = f"  Run {run+1}: Objetivo alcanzado en {generations_to_goal} generaciones."
                else:
                    msg = f"  Run {run+1}: Objetivo NO alcanzado."
                print(msg)
                output_lines.append(msg)
            if generations_when_found:
                avg_generations = sum(generations_when_found) / len(generations_when_found)
                resumen.append((pop_size, mutation_rate, avg_generations, len(generations_when_found), n_runs))
                msg = f'Promedio de generaciones para alcanzar el objetivo: {avg_generations:.1f} ({len(generations_when_found)}/{n_runs} runs exitosos)'
                print(msg)
                output_lines.append(msg)
            else:
                resumen.append((pop_size, mutation_rate, None, 0, n_runs))
                msg = 'No se alcanzó el objetivo en ningún run.'
                print(msg)
                output_lines.append(msg)
    output_lines.append("\nResumen de resultados por tamaño de población y tasa de mutación:")
    output_lines.append("Población\tMutación\tPromedio Generaciones\tRuns Exitosos/Total")
    print("\nResumen de resultados por tamaño de población y tasa de mutación:")
    print("Población\tMutación\tPromedio Generaciones\tRuns Exitosos/Total")
    for pop_size, mutation_rate, avg_gen, n_success, n_total in resumen:
        if avg_gen is not None:
            line = f"{pop_size}\t{mutation_rate}\t{avg_gen:.1f}\t\t{n_success}/{n_total}"
        else:
            line = f"{pop_size}\t{mutation_rate}\tNo alcanzado\t{n_success}/{n_total}"
        print(line)
        output_lines.append(line)
    # Guardar resultados en archivo
    with open("case_study_5_resultados.txt", "w", encoding="utf-8") as f:
        for line in output_lines:
            f.write(line + "\n")
    print('========== FIN caso de estudio 5 =========')
    print('Resultados guardados en case_study_5_resultados.txt')

            