from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QTextCursor
from PyQt5.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QTextEdit,
    QVBoxLayout,
)


class RunPanel(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("Salida en tiempo real", parent)
        self._max_iters = 1000
        self._objective_len = 17
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout()

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setFont(QFont("Monospace", 9))
        self.log.setStyleSheet("background: #1e1e1e; color: #d4d4d4;")
        layout.addWidget(self.log, stretch=4)

        # Barra de progreso + etiqueta de coincidencias
        bar_row = QHBoxLayout()
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setFormat("%p%  coincidencias")
        self.match_label = QLabel("Coinc: 0 / ?")
        bar_row.addWidget(self.progress, stretch=3)
        bar_row.addWidget(self.match_label)
        layout.addLayout(bar_row)

        # Etiqueta de estado
        self.status_label = QLabel("Listo para ejecutar.")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    # ── Interfaz pública ──────────────────────────────────────────────────────

    def set_max_iters(self, n: int):
        self._max_iters = n

    def set_objective_len(self, n: int):
        self._objective_len = n

    def clear(self):
        self.log.clear()
        self.progress.setValue(0)
        self.match_label.setText(f"Coinc: 0 / {self._objective_len}")
        self.status_label.setText("Ejecutando…")
        self.status_label.setStyleSheet("color: #d4d4d4;")

    def append_generation(self, stats: dict):
        """Recibe el dict de estadísticas y actualiza la vista."""
        objective = stats['objective']
        best = stats['best_individual']
        match_count = stats['match_count']
        gen = stats['generation']
        apt = stats['best_aptitude']
        mean = stats['mean_aptitude']

        pct = (match_count / len(objective)) * 100 if objective else 0
        self.progress.setValue(int(pct))
        self.match_label.setText(f"Coinc: {match_count} / {len(objective)}")

        # Diff coloreado: verde = coincide, rojo = difiere
        diff_html = ""
        for a, b in zip(best, objective):
            color = "#2ecc71" if a == b else "#e74c3c"
            char = a.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            diff_html += f'<span style="color:{color}">{char}</span>'

        line = (
            f'<span style="color:#888">Gen {gen:5d}</span> '
            f'| Apt <span style="color:#f1c40f">{apt:7.1f}</span> '
            f'| Med {mean:7.1f} '
            f'| Coinc <span style="color:#2ecc71">{match_count}/{len(objective)}</span> '
            f'&rarr; {diff_html}<br>'
        )
        self.log.moveCursor(QTextCursor.End)
        self.log.insertHtml(line)
        self.log.moveCursor(QTextCursor.End)

    def show_result(self, result: dict):
        history = result.get('history', [])
        if result['success']:
            gens = result['n_generation']
            self.status_label.setText(f"ÉXITO — objetivo alcanzado en {gens} generaciones")
            self.status_label.setStyleSheet("color: #2ecc71; font-weight: bold;")
            self.progress.setValue(100)
        else:
            gens = result['n_generation']
            last_match = history[-1]['match_count'] if history else 0
            obj_len = len(result.get('objective', '?'))
            self.status_label.setText(
                f"No convergió en {gens} iteraciones  "
                f"(mejor: {last_match}/{obj_len} coincidencias)"
            )
            self.status_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
