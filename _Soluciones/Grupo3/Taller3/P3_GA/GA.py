from Taller3.P3_GA.generalSteps import *


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

    def set_best_individual_selection_type(self, _type: BestIndividualSelectionType):
        self.best_individual_selection_type = _type

    def set_new_generation_type(self, _type):
        self.new_generation_type = _type

    def run(self):
        success = False
        for _ in range(self.n_iterations):
            aptitudes = [evaluate_aptitude(self.evaluation_type, individual, self.objective) for individual in self.population]
            best_individual, best_aptitude = select_best_individual(self.best_individual_selection_type, self.population, aptitudes)
            if best_individual == self.objective:
                success = True
                print("Objetivo alcanzado:")
                print(f"Generación {self.n_generation}: {best_individual} - Aptitud: {best_aptitude}")
                break
            print(f"Generación {self.n_generation}: {best_individual} - población: {len(self.population)} - Aptitud: {best_aptitude}")
            self.population = generate_new_population(self.new_generation_type, self.population, aptitudes, self.mutation_rate)
            self.n_generation += 1

        if not success:
            print(f"Objetivo no alcanzado en las iteraciones establecidas {self.n_iterations}")


def case_study_1(_objetive):
    print("\n=== CASO 1: DEFAULT ===")
    population = generate_population(100, len(_objetive))
    mutation_rate = 0.01
    n_iterations = 1000
    ga = GA(population, _objetive, mutation_rate, n_iterations)
    ga.run()


def case_study_2(_objetive):
    print("\n=== CASO 2: BY DISTANCE ===")
    population = generate_population(100, len(_objetive))
    mutation_rate = 0.01
    n_iterations = 1000
    ga = GA(population, _objetive, mutation_rate, n_iterations)
    ga.set_evaluation_type(AptitudeType.BY_DISTANCE)
    ga.set_best_individual_selection_type(BestIndividualSelectionType.MIN_DISTANCE)
    ga.set_new_generation_type(NewGenerationType.NEW)
    ga.run()


def case_study_improved(_objetive):
    print("\n=== CASO MEJORADO (ítem 4): Torneo + Cruce 2 puntos ===")
    population = generate_population(100, len(_objetive))
    mutation_rate = 0.01
    n_iterations = 1000
    ga = GA(population, _objetive, mutation_rate, n_iterations)
    ga.set_evaluation_type(AptitudeType.BY_DISTANCE)
    ga.set_best_individual_selection_type(BestIndividualSelectionType.MIN_DISTANCE)
    ga.set_new_generation_type(NewGenerationType.NEW)
    ga.run()


def case_study_3(_objetive):
    print("\n=== CASO 3 (ítem 5): Variando mutation_rate ===")
    for rate in [0.001, 0.01, 0.05, 0.1, 0.3]:
        print(f"\n--- mutation_rate = {rate} ---")
        population = generate_population(100, len(_objetive))
        ga = GA(population, _objetive, rate, 1000)
        ga.set_evaluation_type(AptitudeType.BY_DISTANCE)
        ga.set_best_individual_selection_type(BestIndividualSelectionType.MIN_DISTANCE)
        ga.set_new_generation_type(NewGenerationType.NEW)
        ga.run()


def case_study_4(_objetive):
    print("\n=== CASO 4 (ítem 6): Variando tamaño de población ===")
    for pop_size in [20, 50, 100, 200, 500]:
        print(f"\n--- Población = {pop_size} ---")
        population = generate_population(pop_size, len(_objetive))
        ga = GA(population, _objetive, 0.01, 1000)
        ga.set_evaluation_type(AptitudeType.BY_DISTANCE)
        ga.set_best_individual_selection_type(BestIndividualSelectionType.MIN_DISTANCE)
        ga.set_new_generation_type(NewGenerationType.NEW)
        ga.run()


def case_study_5(_objetive):
    print("\n=== CASO 5 (ítem 7): Configuración definitiva ===")
    population = generate_population(200, len(_objetive))
    mutation_rate = 0.02
    n_iterations = 1000
    ga = GA(population, _objetive, mutation_rate, n_iterations)
    ga.set_evaluation_type(AptitudeType.BY_DISTANCE)
    ga.set_best_individual_selection_type(BestIndividualSelectionType.MIN_DISTANCE)
    ga.set_new_generation_type(NewGenerationType.NEW)
    ga.run()


if __name__ == "__main__":
    objective = "GA Workshop! USFQ"
    case_study_1(objective)
    case_study_2(objective)
    case_study_improved(objective)
    case_study_3(objective)
    case_study_4(objective)
    case_study_5(objective)