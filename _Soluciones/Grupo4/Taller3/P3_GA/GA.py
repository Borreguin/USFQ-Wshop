from _Soluciones.Grupo4.Taller3.P3_GA.generalSteps import *

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
        self.history = []  # Para almacenar historial de generaciones

    def set_evaluation_type(self, evaluation_type: AptitudeType):
        self.evaluation_type = evaluation_type

    def set_best_individual_selection_type(self, _type:BestIndividualSelectionType):
        self.best_individual_selection_type = _type

    def set_new_generation_type(self, _type):
        self.new_generation_type = _type

    def run(self, verbose=True):
        success = False
        for _ in range(self.n_iterations):
            # las aptitudes son los valores que se obtienen al evaluar la función de aptitud
            aptitudes = [evaluate_aptitude(self.evaluation_type, individual, self.objective) for individual in self.population]
            # el mejor individuo es el que tiene la mejor aptitud
            # (esto se puede elegir como maximo o minimo, depende de como se defina la aptitud)
            best_individual, best_aptitude = select_best_individual(self.best_individual_selection_type, self.population, aptitudes)
            # Guardar en historial
            self.history.append((self.n_generation, best_individual, best_aptitude))

            # si el mejor individuo es igual al objetivo, se termina el algoritmo
            if best_individual == self.objective:
                success = True
                if verbose:
                    print("Objetivo alcanzado:")
                    print(f"Generación {self.n_generation}: {best_individual} - Aptitud: {best_aptitude}")
                break
            if verbose:
                print(f"Generación {self.n_generation}: {best_individual} - población: {len(self.population)} - Aptitud: {best_aptitude}")

            self.population = generate_new_population(
                self.new_generation_type,
                self.population,
                aptitudes,
                self.mutation_rate
            )

            self.n_generation += 1

        if not success:
            if verbose:
                print(f"Objetivo no alcanzado en las iteraciones establecidas {self.n_iterations}")

        return success, self.n_generation, self.history


def case_study_1(_objetive):
    """Caso 1: DEFAULT - Cuenta coincidencias"""
    print("\n" + "="*60)
    print("CASO DE ESTUDIO 1: DEFAULT (Coincidencias)")
    print("="*60)
    population = generate_population(100, len(_objetive))
    mutation_rate = 0.01
    n_iterations = 1000
    ga = GA(population, _objetive, mutation_rate, n_iterations)
    success, generations, history = ga.run()
    return ga

def case_study_2(_objetive):
    """Caso 2: BY_DISTANCE - Distancia entre individuos"""
    print("\n" + "="*60)
    print("CASO DE ESTUDIO 2: BY_DISTANCE")
    print("="*60)
    population = generate_population(100, len(_objetive))
    mutation_rate = 0.01
    n_iterations = 1000
    ga = GA(population, _objetive, mutation_rate, n_iterations)
    ga.set_evaluation_type(AptitudeType.BY_DISTANCE)
    ga.set_best_individual_selection_type(BestIndividualSelectionType.MIN_DISTANCE)
    ga.set_new_generation_type(NewGenerationType.MIN_DISTANCE)
    success, generations, history = ga.run()
    return ga

def case_study_3(_objetive):
    """Caso 3: Alterando mutation_rate"""
    print("\n" + "="*60)
    print("CASO DE ESTUDIO 3: Mutation Rate Alterado (0.05)")
    print("="*60)
    population = generate_population(100, len(_objetive))
    mutation_rate = 0.05  # Mayor tasa de mutación
    n_iterations = 1000
    ga = GA(population, _objetive, mutation_rate, n_iterations)
    success, generations, history = ga.run()
    return ga

def case_study_4(_objetive):
    """Caso 4: Alterando tamaño de población"""
    print("\n" + "="*60)
    print("CASO DE ESTUDIO 4: Población Mayor (200)")
    print("="*60)
    population = generate_population(200, len(_objetive))  # Mayor población
    mutation_rate = 0.01
    n_iterations = 1000
    ga = GA(population, _objetive, mutation_rate, n_iterations)
    success, generations, history = ga.run()
    return ga

def case_study_5(_objetive):
    """Caso 5: Definitivo - Mejores características"""
    print("\n" + "="*60)
    print("CASO DE ESTUDIO 5: Definitivo (Optimizado)")
    print("="*60)
    population = generate_population(150, len(_objetive))  # Población balanceada
    mutation_rate = 0.02  # Mutación moderada
    n_iterations = 1000
    ga = GA(population, _objetive, mutation_rate, n_iterations)
    ga.set_evaluation_type(AptitudeType.DEFAULT)
    ga.set_best_individual_selection_type(BestIndividualSelectionType.DEFAULT)
    ga.set_new_generation_type(NewGenerationType.NEW)  # Usa selección por torneo y cruce uniforme
    success, generations, history = ga.run()
    return ga


if __name__ == "__main__":
    objective = "GA Workshop! USFQ"
    #case_study_1(objective)
    # case_study_2(objective)
    case_study_5(objective)
