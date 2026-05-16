from PyQt5.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from ...constants import (
    AptitudeType,
    BestIndividualSelectionType,
    NewGenerationType,
    MY_SEED,
)

CASOS = [
    {
        'nombre': 'Caso 1 — Coincidencias (DEFAULT)',
        'descripcion': (
            "Función de aptitud: cuenta los caracteres que coinciden "
            "en la misma posición (maximizar).\n"
            "Selección: ruleta proporcional.\n"
            "Cruce: un punto.  Mutación: gen aleatorio."
        ),
        'population_size': 100,
        'mutation_rate': 0.01,
        'n_iterations': 1000,
        'evaluation_type': AptitudeType.DEFAULT,
        'best_individual_type': BestIndividualSelectionType.DEFAULT,
        'new_generation_type': NewGenerationType.DEFAULT,
    },
    {
        'nombre': 'Caso 2 — Distancia Hamming (BY_DISTANCE)',
        'descripcion': (
            "Función de aptitud: distancia de Hamming ASCII (minimizar).\n"
            "Corrección aplicada: se usa abs() en cada diferencia de caracteres,\n"
            "evitando cancelaciones que impedían la convergencia.\n"
            "Selección: partición aleatoria + mejor de cada mitad."
        ),
        'population_size': 100,
        'mutation_rate': 0.01,
        'n_iterations': 1000,
        'evaluation_type': AptitudeType.BY_DISTANCE,
        'best_individual_type': BestIndividualSelectionType.MIN_DISTANCE,
        'new_generation_type': NewGenerationType.MIN_DISTANCE,
    },
    {
        'nombre': 'Caso 3 — Mutación alterada (0.05)',
        'descripcion': (
            "Tasa de mutación incrementada 5× (0.01 → 0.05).\n"
            "Mayor mutación introduce diversidad pero puede destruir\n"
            "buenas soluciones; el efecto sobre la convergencia varía\n"
            "según el balance exploración-explotación."
        ),
        'population_size': 100,
        'mutation_rate': 0.05,
        'n_iterations': 1000,
        'evaluation_type': AptitudeType.DEFAULT,
        'best_individual_type': BestIndividualSelectionType.DEFAULT,
        'new_generation_type': NewGenerationType.DEFAULT,
    },
    {
        'nombre': 'Caso 4 — Población aumentada (200)',
        'descripcion': (
            "Tamaño de población duplicado (100 → 200).\n"
            "Mayor diversidad genética inicial reduce la convergencia\n"
            "prematura; cada generación es más costosa pero el AG\n"
            "explora mejor el espacio de búsqueda."
        ),
        'population_size': 200,
        'mutation_rate': 0.01,
        'n_iterations': 1000,
        'evaluation_type': AptitudeType.DEFAULT,
        'best_individual_type': BestIndividualSelectionType.DEFAULT,
        'new_generation_type': NewGenerationType.DEFAULT,
    },
    {
        'nombre': 'Caso 5 — Combinación óptima (IMPROVED)',
        'descripcion': (
            "Mejor combinación de los ejercicios 4, 5 y 6:\n"
            "• Población 200  |  Mutación 0.05\n"
            "• Elitismo: top 10% pasa directo a la siguiente generación\n"
            "• Selección por torneo (k=3): mayor presión selectiva\n"
            "• Cruce de dos puntos: mejor recombinación genética"
        ),
        'population_size': 200,
        'mutation_rate': 0.05,
        'n_iterations': 1000,
        'evaluation_type': AptitudeType.DEFAULT,
        'best_individual_type': BestIndividualSelectionType.DEFAULT,
        'new_generation_type': NewGenerationType.IMPROVED,
    },
]


class ConfigPanel(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("Configuración", parent)
        self._building = False
        self._build_ui()
        self._load_caso(0)

    def _build_ui(self):
        layout = QVBoxLayout()
        form = QFormLayout()

        self.caso_combo = QComboBox()
        for c in CASOS:
            self.caso_combo.addItem(c['nombre'])
        self.caso_combo.addItem("Personalizado")
        self.caso_combo.currentIndexChanged.connect(self._on_caso_changed)
        form.addRow("Caso de estudio:", self.caso_combo)

        self.target_edit = QLineEdit("GA Workshop! USFQ")
        form.addRow("Expresión objetivo:", self.target_edit)

        self.pop_spin = QSpinBox()
        self.pop_spin.setRange(10, 5000)
        self.pop_spin.setValue(100)
        form.addRow("Tamaño de población:", self.pop_spin)

        self.mut_spin = QDoubleSpinBox()
        self.mut_spin.setRange(0.001, 1.0)
        self.mut_spin.setSingleStep(0.005)
        self.mut_spin.setDecimals(3)
        self.mut_spin.setValue(0.01)
        form.addRow("Tasa de mutación:", self.mut_spin)

        self.iter_spin = QSpinBox()
        self.iter_spin.setRange(10, 50000)
        self.iter_spin.setValue(1000)
        form.addRow("Iteraciones máximas:", self.iter_spin)

        self.seed_edit = QLineEdit(str(MY_SEED))
        self.seed_edit.setPlaceholderText("vacío = sin semilla fija")
        form.addRow("Semilla aleatoria:", self.seed_edit)

        layout.addLayout(form)

        self.desc_label = QTextEdit()
        self.desc_label.setReadOnly(True)
        self.desc_label.setStyleSheet(
            "background: #1e1e1e; color: #9cdcfe; font-family: monospace; font-size: 9pt;"
        )
        layout.addWidget(self.desc_label, stretch=1)

        self.run_btn = QPushButton("Ejecutar AG")
        self.run_btn.setStyleSheet(
            "font-weight: bold; background: #2ecc71; color: white; padding: 7px;"
        )
        self.stop_btn = QPushButton("Detener")
        self.stop_btn.setStyleSheet("background: #e74c3c; color: white; padding: 7px;")
        self.stop_btn.setEnabled(False)

        from PyQt5.QtWidgets import QHBoxLayout
        btn_row = QHBoxLayout()
        btn_row.addWidget(self.run_btn)
        btn_row.addWidget(self.stop_btn)
        layout.addLayout(btn_row)

        self.setLayout(layout)

    def _on_caso_changed(self, idx):
        if idx < len(CASOS):
            self._load_caso(idx)
        else:
            self.desc_label.setPlainText(
                "Personalizado: ajusta los parámetros manualmente."
            )

    def _load_caso(self, idx):
        self._building = True
        caso = CASOS[idx]
        self.pop_spin.setValue(caso['population_size'])
        self.mut_spin.setValue(caso['mutation_rate'])
        self.iter_spin.setValue(caso['n_iterations'])
        self.desc_label.setPlainText(caso['descripcion'])
        self._building = False

    def get_config(self) -> dict:
        idx = self.caso_combo.currentIndex()
        seed_text = self.seed_edit.text().strip()
        seed = int(seed_text) if seed_text.isdigit() else MY_SEED

        if idx < len(CASOS):
            caso = CASOS[idx].copy()
            caso['population_size'] = self.pop_spin.value()
            caso['mutation_rate'] = self.mut_spin.value()
            caso['n_iterations'] = self.iter_spin.value()
            caso['objective'] = self.target_edit.text()
            caso['seed'] = seed
            return caso

        return {
            'objective': self.target_edit.text(),
            'population_size': self.pop_spin.value(),
            'mutation_rate': self.mut_spin.value(),
            'n_iterations': self.iter_spin.value(),
            'evaluation_type': AptitudeType.DEFAULT,
            'best_individual_type': BestIndividualSelectionType.DEFAULT,
            'new_generation_type': NewGenerationType.DEFAULT,
            'seed': seed,
        }

    def set_running(self, running: bool):
        self.run_btn.setEnabled(not running)
        self.stop_btn.setEnabled(running)
        self.caso_combo.setEnabled(not running)
