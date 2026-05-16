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

        self._generation_callbacks = []
        self._complete_callbacks = []
        self._stop_requested = False

    def set_evaluation_type(self, evaluation_type: AptitudeType):
        self.evaluation_type = evaluation_type

    def set_best_individual_selection_type(self, _type: BestIndividualSelectionType):
        self.best_individual_selection_type = _type

    def set_new_generation_type(self, _type: NewGenerationType):
        self.new_generation_type = _type

    def on_generation(self, callback):
        self._generation_callbacks.append(callback)

    def on_complete(self, callback):
        self._complete_callbacks.append(callback)

    def stop(self):
        self._stop_requested = True

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


def _header(titulo: str):
    sep = "=" * 65
    print(f"\n{sep}")
    print(f"  {titulo}")
    print(sep)


def case_study_1(objective):
    _header("CASO 1 — Conteo de coincidencias (DEFAULT)")
    population = generate_population(100, len(objective))
    ga = GA(population, objective, mutation_rate=0.01, n_iterations=1000)
    ga.run()


def case_study_2(objective):
    _header("CASO 2 — Distancia de Hamming (BY_DISTANCE, corregida)")
    population = generate_population(100, len(objective))
    ga = GA(population, objective, mutation_rate=0.01, n_iterations=1000)
    ga.set_evaluation_type(AptitudeType.BY_DISTANCE)
    ga.set_best_individual_selection_type(BestIndividualSelectionType.MIN_DISTANCE)
    ga.set_new_generation_type(NewGenerationType.MIN_DISTANCE)
    ga.run()


def case_study_3(objective):
    _header("CASO 3 — Tasa de mutación alterada (mutation_rate=0.05)")
    population = generate_population(100, len(objective))
    ga = GA(population, objective, mutation_rate=0.05, n_iterations=1000)
    ga.run()


def case_study_4(objective):
    _header("CASO 4 — Población duplicada (population_size=200)")
    population = generate_population(200, len(objective))
    ga = GA(population, objective, mutation_rate=0.01, n_iterations=1000)
    ga.run()


def case_study_5(objective):
    _header("CASO 5 — Combinación óptima (población + mutación + IMPROVED)")
    population = generate_population(200, len(objective))
    ga = GA(population, objective, mutation_rate=0.05, n_iterations=1000)
    ga.set_new_generation_type(NewGenerationType.IMPROVED)
    ga.run()


if __name__ == "__main__":
    objective = "GA Workshop! USFQ"
    case_study_5(objective)
