from Taller3.P3_GA.generalSteps import *


class GA:
    def __init__(self, population, objective, mutation_rate, n_iterations):
        self.population = population       # lista de strings (los individuos)
        self.n_generation = 0              # contador de generaciones
        self.n_iterations = n_iterations   # número máximo de generaciones a correr
        self.objective = objective         # string objetivo: "GA Workshop! USFQ"
        self.mutation_rate = mutation_rate # probabilidad de mutación por carácter
        # Valores por defecto: evaluación DEFAULT, selección DEFAULT, generación DEFAULT
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
            # Paso 1: Evaluar cada individuo → obtener su aptitud (cuán bueno es)
            aptitudes = [
                evaluate_aptitude(self.evaluation_type, ind, self.objective)
                for ind in self.population
            ]

            # Paso 2: Seleccionar el mejor individuo de esta generación
            best_individual, best_aptitude = select_best_individual(
                self.best_individual_selection_type, self.population, aptitudes)

            # Paso 3: Comprobar si ya llegamos al objetivo
            if best_individual == self.objective:
                success = True
                print("Objetivo alcanzado:")
                print(f"  Generacion {self.n_generation}: '{best_individual}' - Aptitud: {best_aptitude}")
                break

            print(f"  Gen {self.n_generation:4d}: '{best_individual}' | "
                  f"Aptitud: {best_aptitude} | Poblacion: {len(self.population)}")

            # Paso 4: Generar la nueva población a partir de la actual
            self.population = generate_new_population(
                self.new_generation_type, self.population, aptitudes, self.mutation_rate)
            self.n_generation += 1

        if not success:
            print(f"Objetivo NO alcanzado en {self.n_iterations} iteraciones.")


# =============================================================================
# CASO 1 - DEFAULT (ítem 1)
# Evaluación: cuenta coincidencias posición a posición (MAXIMIZAR)
# Selección de padres: ruleta proporcional a aptitud
# Cruce: un punto aleatorio
# Mutación: reemplazo aleatorio con prob=0.01
# Resultado esperado: CONVERGE porque la aptitud 0 nunca ocurre
#   (la ruleta siempre puede elegir padres) y maximizar coincidencias
#   es una señal clara de progreso.
# =============================================================================
def case_study_1(_objetive):
    print("\n" + "="*60)
    print("CASO 1 - DEFAULT (ruleta + cruce 1 punto)")
    print("="*60)
    population = generate_population(100, len(_objetive))
    mutation_rate = 0.01
    n_iterations = 1000
    ga = GA(population, _objetive, mutation_rate, n_iterations)
    ga.run()


# =============================================================================
# CASO 2 - BY_DISTANCE (ítem 1 + ítem 2)
# Evaluación: distancia Manhattan entre individuo y objetivo (MINIMIZAR)
# ANTES del fix: la distancia era casi siempre 0 → todos los individuos
#   parecían igualmente buenos → selección aleatoria → sin convergencia.
# DESPUÉS del fix (abs en util.py): la distancia refleja correctamente
#   cuánto difiere cada individuo → el algoritmo puede converger.
# =============================================================================
def case_study_2(_objetive):
    print("\n" + "="*60)
    print("CASO 2 - BY_DISTANCE (min distancia, con fix en util.py)")
    print("="*60)
    population = generate_population(100, len(_objetive))
    mutation_rate = 0.01
    n_iterations = 1000
    ga = GA(population, _objetive, mutation_rate, n_iterations)
    ga.set_evaluation_type(AptitudeType.BY_DISTANCE)
    ga.set_best_individual_selection_type(BestIndividualSelectionType.MIN_DISTANCE)
    ga.set_new_generation_type(NewGenerationType.MIN_DISTANCE)
    ga.run()


# =============================================================================
# CASO 3 - Variación de mutation_rate (ítem 5)
# Pregunta: ¿alterar mutation_rate beneficia la convergencia?
# Probamos 0.05 (más alto): mayor exploración del espacio de soluciones
#   pero puede deshacer progreso ya alcanzado.
# Conclusión esperada: un mutation_rate muy alto es contraproducente
#   porque muta incluso los caracteres que ya están en su posición correcta.
#   El rango óptimo suele estar entre 0.01 y 0.05.
# =============================================================================
def case_study_3(_objetive):
    print("\n" + "="*60)
    print("CASO 3 - mutation_rate=0.05 (exploración alta)")
    print("="*60)
    population = generate_population(100, len(_objetive))
    mutation_rate = 0.05  # aumentado respecto al caso 1 (era 0.01)
    n_iterations = 1000
    ga = GA(population, _objetive, mutation_rate, n_iterations)
    ga.run()

    print("\n" + "-"*60)
    print("CASO 3b - mutation_rate=0.001 (exploración baja)")
    print("-"*60)
    population = generate_population(100, len(_objetive))
    mutation_rate = 0.001  # muy bajo: casi sin exploración
    n_iterations = 1000
    ga = GA(population, _objetive, mutation_rate, n_iterations)
    ga.run()


# =============================================================================
# CASO 4 - Variación del tamaño de población (ítem 6)
# Pregunta: ¿es beneficioso aumentar la población?
# Mayor población = más diversidad genética = mejor exploración inicial,
#   pero cada generación tarda más en calcularse.
# Menor población = converge más rápido por iteración, pero puede
#   caer en óptimos locales (poca diversidad).
# =============================================================================
def case_study_4(_objetive):
    print("\n" + "="*60)
    print("CASO 4a - Poblacion=500 (grande)")
    print("="*60)
    population = generate_population(500, len(_objetive))
    mutation_rate = 0.01
    n_iterations = 1000
    ga = GA(population, _objetive, mutation_rate, n_iterations)
    ga.run()

    print("\n" + "-"*60)
    print("CASO 4b - Poblacion=20 (pequeña)")
    print("-"*60)
    population = generate_population(20, len(_objetive))
    mutation_rate = 0.01
    n_iterations = 1000
    ga = GA(population, _objetive, mutation_rate, n_iterations)
    ga.run()


# =============================================================================
# CASO 5 - Mejor combinación (ítem 7)
# Combina lo mejor de los ítems 4, 5, 6:
#   - Población = 200 (balance entre diversidad y velocidad)
#   - mutation_rate = 0.03 (ligeramente mayor que default para más exploración)
#   - NewGenerationType.NEW: elitismo (top 2 sobreviven) +
#                             torneo (selección de padres con más presión) +
#                             cruce de dos puntos (mejor mezcla genética)
# Resultado esperado: converge más rápido y con más seguridad que los casos 1-4.
# =============================================================================
def case_study_5(_objetive):
    print("\n" + "="*60)
    print("CASO 5 - Mejor combinacion: elitismo + torneo + 2 puntos")
    print("="*60)
    population = generate_population(200, len(_objetive))
    mutation_rate = 0.03
    n_iterations = 1000
    ga = GA(population, _objetive, mutation_rate, n_iterations)
    # Evaluación DEFAULT (contar coincidencias, maximizar)
    # Selección DEFAULT (el de mayor aptitud es el mejor)
    # Generación NEW: elitismo + torneo + cruce dos puntos
    ga.set_new_generation_type(NewGenerationType.NEW)
    ga.run()


if __name__ == "__main__":
    objective = "GA Workshop! USFQ"

    case_study_1(objective)    # Caso base: converge con ruleta + 1 punto
    case_study_2(objective)    # Distancia: necesita fix en util.py para converger
    case_study_3(objective)    # Explora efecto de mutation_rate alto y bajo
    case_study_4(objective)    # Explora efecto del tamaño de población
    case_study_5(objective)    # Mejor combinación: elitismo + torneo + 2 puntos
