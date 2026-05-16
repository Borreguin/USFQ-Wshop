from PyQt5.QtCore import QThread, pyqtSignal

from ..GA import GA
from ..generalSteps import generate_population
from ..constants import (
    AptitudeType,
    BestIndividualSelectionType,
    NewGenerationType,
    MY_SEED,
)


class GAWorker(QThread):
    generation_ready = pyqtSignal(object)
    run_complete = pyqtSignal(object)

    def __init__(self, config: dict):
        super().__init__()
        self._config = config
        self._ga = None
        self._history = []

    def run(self):
        cfg = self._config
        self._history = []

        seed = cfg.get('seed', MY_SEED)
        population = generate_population(
            cfg['population_size'],
            len(cfg['objective']),
            seed=seed,
        )

        self._ga = GA(
            population=population,
            objective=cfg['objective'],
            mutation_rate=cfg['mutation_rate'],
            n_iterations=cfg['n_iterations'],
        )
        self._ga.set_evaluation_type(cfg.get('evaluation_type', AptitudeType.DEFAULT))
        self._ga.set_best_individual_selection_type(
            cfg.get('best_individual_type', BestIndividualSelectionType.DEFAULT)
        )
        self._ga.set_new_generation_type(
            cfg.get('new_generation_type', NewGenerationType.DEFAULT)
        )

        def on_gen(stats):
            self._history.append(stats)
            self.generation_ready.emit(stats)

        def on_complete(result):
            result['history'] = self._history
            self.run_complete.emit(result)

        self._ga.on_generation(on_gen)
        self._ga.on_complete(on_complete)
        self._ga.run()

    def stop(self):
        if self._ga:
            self._ga.stop()
