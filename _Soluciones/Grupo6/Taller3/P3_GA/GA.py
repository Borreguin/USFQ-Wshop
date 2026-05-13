from Taller3.P3_GA.generalSteps import *


class GA:
    """
    Algoritmo Genético configurable.
    Soporta modo consola (imprime en pantalla) y modo GUI (emite callbacks).
    """

    def __init__(self, population, objective, mutation_rate, n_iterations):
        self.population = population
        self.n_generation = 0
        self.n_iterations = n_iterations
        self.objective = objective
        self.mutation_rate = mutation_rate
        self.evaluation_type = AptitudeType.DEFAULT
        self.best_individual_selection_type = BestIndividualSelectionType.DEFAULT
        self.new_generation_type = NewGenerationType.DEFAULT

        self._generation_callbacks = []
        self._complete_callbacks = []
        self._stop_requested = False

    # ── Configuración ────────────────────────────────────────────────────────

    def set_evaluation_type(self, evaluation_type: AptitudeType):
        self.evaluation_type = evaluation_type

    def set_best_individual_selection_type(self, _type: BestIndividualSelectionType):
        self.best_individual_selection_type = _type

    def set_new_generation_type(self, _type: NewGenerationType):
        self.new_generation_type = _type

    # ── API de callbacks (para GUI) ──────────────────────────────────────────

    def on_generation(self, callback):
        """Registra un callback que se llama con un dict de estadísticas por generación."""
        self._generation_callbacks.append(callback)

    def on_complete(self, callback):
        """Registra un callback que se llama con el resultado al finalizar."""
        self._complete_callbacks.append(callback)

    def stop(self):
        """Solicita detener el ciclo evolutivo (usado por la GUI)."""
        self._stop_requested = True

    # ── Ciclo principal ──────────────────────────────────────────────────────

    def run(self):
        self.n_generation = 0
        self._stop_requested = False
        success = False

        for _ in range(self.n_iterations):
            if self._stop_requested:
                break

            aptitudes = [
                evaluate_aptitude(self.evaluation_type, ind, self.objective)
                for ind in self.population
            ]
            best_individual, best_aptitude = select_best_individual(
                self.best_individual_selection_type, self.population, aptitudes
            )

            match_count = sum(a == b for a, b in zip(best_individual, self.objective))
            mean_aptitude = sum(aptitudes) / len(aptitudes)

            stats = {
                'generation': self.n_generation,
                'best_individual': best_individual,
                'best_aptitude': best_aptitude,
                'mean_aptitude': mean_aptitude,
                'match_count': match_count,
                'population_size': len(self.population),
                'objective': self.objective,
                'evaluation_type': self.evaluation_type.value,
            }

            is_success = (best_individual == self.objective)

            if self._generation_callbacks:
                for cb in self._generation_callbacks:
                    cb(stats)
            else:
                if is_success:
                    print("  Objetivo alcanzado:")
                    print(f"    Generación {self.n_generation}: {best_individual!r} "
                          f"- Aptitud: {best_aptitude}")
                else:
                    print(f"  Gen {self.n_generation:5d}: {best_individual!r} "
                          f"| Apt: {best_aptitude:7.1f} "
                          f"| Coinc: {match_count}/{len(self.objective)} "
                          f"| Pob: {len(self.population)}")

            if is_success:
                success = True
                break

            self.population = generate_new_population(
                self.new_generation_type, self.population, aptitudes, self.mutation_rate
            )
            self.n_generation += 1

        if not self._generation_callbacks and not success:
            print(f"  Objetivo no alcanzado en {self.n_iterations} iteraciones.")

        result = {
            'success': success,
            'n_generation': self.n_generation,
            'objective': self.objective,
        }

        for cb in self._complete_callbacks:
            cb(result)

        return result


# ── Casos de estudio ──────────────────────────────────────────────────────────

def _header(titulo: str):
    sep = "=" * 65
    print(f"\n{sep}")
    print(f"  {titulo}")
    print(sep)


def case_study_1(objective):
    """
    Caso 1 — DEFAULT (conteo de coincidencias).
    Función de aptitud: cuenta cuántos caracteres coinciden en la misma posición.
    Selección: ruleta proporcional.  Cruce: un punto.  Mutación: gen aleatorio.
    """
    _header("CASO 1 — Conteo de coincidencias (DEFAULT)")
    population = generate_population(100, len(objective))
    ga = GA(population, objective, mutation_rate=0.01, n_iterations=1000)
    ga.run()


def case_study_2(objective):
    """
    Caso 2 — BY_DISTANCE (distancia de Hamming corregida).
    Ejercicio 2: en la versión original la función distance() acumulaba
    diferencias sin valor absoluto; valores positivos y negativos se
    cancelaban, haciendo que individuos muy distintos tuvieran distancia ~0.
    Ejercicio 3: la corrección aplica abs() en cada par, produciendo una
    distancia de Hamming real que decrece al acercarse al objetivo.
    """
    _header("CASO 2 — Distancia de Hamming (BY_DISTANCE, corregida)")
    population = generate_population(100, len(objective))
    ga = GA(population, objective, mutation_rate=0.01, n_iterations=1000)
    ga.set_evaluation_type(AptitudeType.BY_DISTANCE)
    ga.set_best_individual_selection_type(BestIndividualSelectionType.MIN_DISTANCE)
    ga.set_new_generation_type(NewGenerationType.MIN_DISTANCE)
    ga.run()


def case_study_3(objective):
    """
    Caso 3 — Tasa de mutación alterada (ejercicio 5).
    Se incrementa mutation_rate a 0.05 (5× el valor base).
    Una tasa más alta introduce más diversidad pero puede destruir
    buenas soluciones; existe un rango óptimo que equilibra exploración
    y explotación.
    """
    _header("CASO 3 — Tasa de mutación alterada (mutation_rate=0.05)")
    population = generate_population(100, len(objective))
    ga = GA(population, objective, mutation_rate=0.05, n_iterations=1000)
    ga.run()


def case_study_4(objective):
    """
    Caso 4 — Tamaño de población alterado (ejercicio 6).
    Se duplica la población a 200 individuos.
    Una población mayor mantiene mayor diversidad genética y reduce el
    riesgo de convergencia prematura, aunque cada generación es más costosa.
    """
    _header("CASO 4 — Población duplicada (population_size=200)")
    population = generate_population(200, len(objective))
    ga = GA(population, objective, mutation_rate=0.01, n_iterations=1000)
    ga.run()


def case_study_5(objective):
    """
    Caso 5 — Combinación óptima (ejercicio 7).
    Combina las mejores configuraciones de los ejercicios 4, 5 y 6:
      • Población: 200  (más diversidad)
      • mutation_rate: 0.05  (más exploración)
      • Generación IMPROVED:
          - Elitismo (top 10% pasa intacto)
          - Selección por torneo (k=3)
          - Cruce de dos puntos (mayor recombinación)
    """
    _header("CASO 5 — Combinación óptima (población + mutación + IMPROVED)")
    population = generate_population(200, len(objective))
    ga = GA(population, objective, mutation_rate=0.05, n_iterations=1000)
    ga.set_new_generation_type(NewGenerationType.IMPROVED)
    ga.run()


# ── Punto de entrada ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    objective = "GA Workshop! USFQ"

    #case_study_1(objective)
    #case_study_2(objective)
    #case_study_3(objective)
    #case_study_4(objective)
    case_study_5(objective)
