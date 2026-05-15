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

    def set_best_individual_selection_type(self, _type:BestIndividualSelectionType):
        self.best_individual_selection_type = _type

    def set_new_generation_type(self, _type):
        self.new_generation_type = _type

    def run(self):
        success = False
        for _ in range(self.n_iterations):
            # las aptitudes son los valores que se obtienen al evaluar la función de aptitud
            aptitudes = [evaluate_aptitude(self.evaluation_type, individual, self.objective) for individual in self.population]
            # el mejor individuo es el que tiene la mejor aptitud
            # (esto se puede elegir como maximo o minimo, depende de como se defina la aptitud)
            best_individual, best_aptitude = select_best_individual(self.best_individual_selection_type, self.population, aptitudes)
            # si el mejor individuo es igual al objetivo, se termina el algoritmo
            if best_individual == self.objective:
                success = True
                print("Objetivo alcanzado:")
                print(f"Generación {self.n_generation}: {best_individual} - Aptitud: {best_aptitude}")
                break
            print(f"Generación {self.n_generation}: {best_individual} - población: {len(self.population)} - Aptitud: {best_aptitude}")

            # la nueva generación se obtiene a partir de la población actual, interactuando entre los individuos
            self.population = generate_new_population(self.new_generation_type, self.population, aptitudes, self.mutation_rate)
            self.n_generation += 1

        if not success:
            print(f"Objetivo no alcanzado en las iteraciones establecidas {self.n_iterations}")


def case_study_1(_objetive):
    # Definición de la población inicial
    population = generate_population(100, len(_objetive))
    mutation_rate = 0.01
    n_iterations = 1000
    ga = GA(population, _objetive, mutation_rate, n_iterations)
    ga.run()

def case_study_2(_objetive):
    population = generate_population(100, len(_objetive))
    mutation_rate = 0.01
    n_iterations = 1000
    ga = GA(population, _objetive, mutation_rate, n_iterations)
    ga.set_evaluation_type(AptitudeType.BY_DISTANCE)
    ga.set_best_individual_selection_type(BestIndividualSelectionType.MIN_DISTANCE)
    ga.set_new_generation_type(NewGenerationType.MIN_DISTANCE)
    ga.run()


if __name__ == "__main__":
    objective = "GA Workshop! USFQ"
    case_study_1(objective)
    # case_study_2(objetive)