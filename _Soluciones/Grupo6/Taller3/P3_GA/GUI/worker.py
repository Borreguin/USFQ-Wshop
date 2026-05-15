from PyQt5.QtCore import QThread, pyqtSignal

from ..engine.ga import GAConfig, GeneticAlgorithm
from ..models.ga_stats import GAHistory, GenerationStats
from ..operators.base import CrossoverOperator, FitnessEvaluator, MutationOperator, SelectionOperator


class GAWorker(QThread):
    """Runs GeneticAlgorithm in a background thread and emits Qt signals."""

    generation_ready = pyqtSignal(object)   # GenerationStats
    run_complete = pyqtSignal(object)        # GAHistory

    def __init__(
        self,
        objective: str,
        config: GAConfig,
        fitness: FitnessEvaluator,
        selection: SelectionOperator,
        crossover: CrossoverOperator,
        mutation: MutationOperator,
    ):
        super().__init__()
        self._ga = GeneticAlgorithm(
            objective=objective,
            config=config,
            fitness=fitness,
            selection=selection,
            crossover=crossover,
            mutation=mutation,
        )
        self._ga.on_generation(self.generation_ready.emit)
        self._ga.on_complete(self.run_complete.emit)

    def run(self):
        self._ga.run()

    def stop(self):
        self._ga.stop()
