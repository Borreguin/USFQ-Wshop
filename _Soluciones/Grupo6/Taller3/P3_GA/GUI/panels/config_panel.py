from PyQt5.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from ...engine.ga import GAConfig
from ...operators.crossover import SinglePoint, TwoPoint, Uniform
from ...operators.fitness import HammingDistance, MatchCount
from ...operators.mutation import RandomGene, SwapGene
from ...operators.selection import Elitist, RouletteWheel, Tournament

_FITNESS_OPS = [MatchCount(), HammingDistance()]
_SELECTION_OPS = [RouletteWheel(), Tournament(k=3), Elitist(top_fraction=0.3)]
_CROSSOVER_OPS = [SinglePoint(), TwoPoint(), Uniform()]
_MUTATION_OPS = [RandomGene(), SwapGene()]


class ConfigPanel(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("Configuration", parent)
        self._build_ui()

    def _build_ui(self):
        form = QFormLayout()

        self.target_edit = QLineEdit("GA Workshop! USFQ")
        form.addRow("Target expression:", self.target_edit)

        self.pop_spin = QSpinBox()
        self.pop_spin.setRange(10, 5000)
        self.pop_spin.setValue(100)
        form.addRow("Population size:", self.pop_spin)

        self.mut_spin = QDoubleSpinBox()
        self.mut_spin.setRange(0.001, 1.0)
        self.mut_spin.setSingleStep(0.005)
        self.mut_spin.setDecimals(3)
        self.mut_spin.setValue(0.01)
        form.addRow("Mutation rate:", self.mut_spin)

        self.iter_spin = QSpinBox()
        self.iter_spin.setRange(10, 50000)
        self.iter_spin.setValue(1000)
        form.addRow("Max iterations:", self.iter_spin)

        self.seed_edit = QLineEdit("42")
        self.seed_edit.setPlaceholderText("blank = no seed")
        form.addRow("Random seed:", self.seed_edit)

        self.fitness_combo = QComboBox()
        for op in _FITNESS_OPS:
            self.fitness_combo.addItem(op.label)
        form.addRow("Fitness:", self.fitness_combo)

        self.selection_combo = QComboBox()
        for op in _SELECTION_OPS:
            self.selection_combo.addItem(op.label)
        form.addRow("Selection:", self.selection_combo)

        self.crossover_combo = QComboBox()
        for op in _CROSSOVER_OPS:
            self.crossover_combo.addItem(op.label)
        form.addRow("Crossover:", self.crossover_combo)

        self.mutation_combo = QComboBox()
        for op in _MUTATION_OPS:
            self.mutation_combo.addItem(op.label)
        form.addRow("Mutation:", self.mutation_combo)

        self.run_btn = QPushButton("Run GA")
        self.run_btn.setStyleSheet("font-weight: bold; background: #2ecc71; color: white; padding: 6px;")
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setStyleSheet("background: #e74c3c; color: white; padding: 6px;")
        self.stop_btn.setEnabled(False)

        self.demo_btn = QPushButton("Random Chromosome Demo")
        self.demo_btn.setStyleSheet("padding: 4px;")

        form.addRow(self.run_btn, self.stop_btn)
        form.addRow(self.demo_btn)

        self.setLayout(form)

    # ── accessors ────────────────────────────────────────────────────────────

    def get_objective(self) -> str:
        return self.target_edit.text()

    def get_config(self) -> GAConfig:
        seed_text = self.seed_edit.text().strip()
        seed = int(seed_text) if seed_text.isdigit() else None
        return GAConfig(
            population_size=self.pop_spin.value(),
            mutation_rate=self.mut_spin.value(),
            n_iterations=self.iter_spin.value(),
            seed=seed,
        )

    def get_fitness(self):
        return _FITNESS_OPS[self.fitness_combo.currentIndex()]

    def get_selection(self):
        return _SELECTION_OPS[self.selection_combo.currentIndex()]

    def get_crossover(self):
        return _CROSSOVER_OPS[self.crossover_combo.currentIndex()]

    def get_mutation(self):
        return _MUTATION_OPS[self.mutation_combo.currentIndex()]

    def set_running(self, running: bool):
        self.run_btn.setEnabled(not running)
        self.stop_btn.setEnabled(running)
        self.demo_btn.setEnabled(not running)
