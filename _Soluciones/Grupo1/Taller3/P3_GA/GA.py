from Taller3.P3_GA.generalSteps import *
import random
from Taller3.P3_GA.operation import MY_SEED
import random
from Taller3.P3_GA.operation import MY_SEED


class GA:
    def __init__(self, population, objective, mutation_rate, n_iterations):
        self.population = population
        self.n_generation = 0
        self.n_iterations = n_iterations
        self.objective = objective
        self.mutation_rate = mutation_rate
        self.evaluation_type = AptitudeType.DEFAULT
        self.best_individual_selection_type = BestIndividualSelectionType.DEFAULT
        self.new_generation_type = NewGenerationType.DEFAULT

    def set_evaluation_type(self, evaluation_type: AptitudeType):
        self.evaluation_type = evaluation_type

    def set_best_individual_selection_type(self, _type:BestIndividualSelectionType):
        self.best_individual_selection_type = _type

    def set_new_generation_type(self, _type):
        self.new_generation_type = _type

    def run(self, print_interval=50, verbose=True, return_history=False):
        success = False
        best_aptitude_history = []
        generations_to_goal = None
        
        for i in range(self.n_iterations):
            # las aptitudes son los valores que se obtienen al evaluar la función de aptitud
            aptitudes = [evaluate_aptitude(self.evaluation_type, individual, self.objective) for individual in self.population]
            # el mejor individuo es el que tiene la mejor aptitud
            # (esto se puede elegir como maximo o minimo, depende de como se defina la aptitud)
            best_individual, best_aptitude = select_best_individual(self.best_individual_selection_type, self.population, aptitudes)
            
            if return_history:
                best_aptitude_history.append(best_aptitude)
            
            # si el mejor individuo es igual al objetivo, se termina el algoritmo
            if best_individual == self.objective:
                success = True
                generations_to_goal = self.n_generation
                if verbose:
                    print("Objetivo alcanzado:")
                    print(f"Generación {self.n_generation}: {best_individual} - Aptitud: {best_aptitude}")
                break
            if verbose and i % print_interval == 0:  # Print progress every print_interval iterations
                print(f"Generación {self.n_generation}: {best_individual} - población: {len(self.population)} - Aptitud: {best_aptitude}")

            # la nueva generación se obtiene a partir de la población actual, interactuando entre los individuos
            self.population = generate_new_population(self.new_generation_type, self.population, aptitudes, self.mutation_rate)
            self.n_generation += 1

        if verbose and not success:
            print(f"Objetivo no alcanzado en las iteraciones establecidas {self.n_iterations}")
        
        if return_history:
            return success, best_aptitude_history, generations_to_goal


def case_study_1(_objetive):
    population = generate_population(100, len(_objetive))
    mutation_rate = 0.01
    n_iterations = 1000
    ga = GA(population, _objetive, mutation_rate, n_iterations)
    ga.run()

def case_study_2(_objetive):
    population = generate_population(100, len(_objetive))
    mutation_rate = 0.01
    n_iterations = 1000
    _types = [
        NewGenerationType.MIN_DISTANCE, 
        NewGenerationType.TOURNAMENT,
        NewGenerationType.TOURNAMENT_ELITISM
        ]
    for _type in _types:
        print('\n========================================')
        print(f'\nEjecutando caso de estudio 2 con tipo de generación: {_type}')
        random.seed(MY_SEED)
        ga = GA(population, _objetive, mutation_rate, n_iterations)
        ga.set_evaluation_type(AptitudeType.BY_DISTANCE)
        ga.set_best_individual_selection_type(BestIndividualSelectionType.MIN_DISTANCE)
        ga.set_new_generation_type(_type)
        ga.run()

def case_study_3(_objetive):
    # En este caso de estudio se busca encontrar el mejor mutation_rate para el algoritmo genético mediante gridsearch.
    mutation_rates = [0.001, 0.005, 0.01, 0.02, 0.05, 0.1]
    n_runs = 5
    n_iterations = 1000

    best_mutation_rate = None
    best_score = float('inf')
    fastest_mutation_rate = None
    fastest_avg_generations = float('inf')

    for mutation_rate in mutation_rates:
        run_scores = []
        generations_when_found = []
        print('\n========================================')
        print(f'Ejecutando gridsearch con mutation_rate: {mutation_rate}')

        for _ in range(n_runs):
            random.seed(MY_SEED)
            population = generate_population(100, len(_objetive))
            ga = GA(population, _objetive, mutation_rate, n_iterations)
            ga.set_evaluation_type(AptitudeType.BY_DISTANCE)
            ga.set_best_individual_selection_type(BestIndividualSelectionType.MIN_DISTANCE)
            ga.set_new_generation_type(NewGenerationType.TOURNAMENT_ELITISM)

            success, aptitude_history, generations_to_goal = ga.run(verbose=False, return_history=True)
            run_scores.extend(aptitude_history)
            
            if success and generations_to_goal is not None:
                generations_when_found.append(generations_to_goal)

        average_score = sum(run_scores) / len(run_scores) if run_scores else float('inf')
        avg_generations = sum(generations_when_found) / len(generations_when_found) if generations_when_found else float('inf')
        
        print(f'Promedio aptitud: {average_score}')
        print(f'Promedio generaciones para alcanzar objetivo: {avg_generations:.1f} ({len(generations_when_found)}/{n_runs} runs exitosos)')

        if average_score < best_score:
            best_score = average_score
            best_mutation_rate = mutation_rate
        
        if avg_generations < fastest_avg_generations:
            fastest_avg_generations = avg_generations
            fastest_mutation_rate = mutation_rate

    print('\n========================================')
    print(f'Mejor mutation_rate (aptitud): {best_mutation_rate} con aptitud promedio: {best_score}')
    print(f'Más rápido (convergencia): {fastest_mutation_rate} con {fastest_avg_generations:.1f} generaciones en promedio')
