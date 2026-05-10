import random
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QMainWindow, QSplitter, QWidget

from ..constants import all_possible_gens
from .panels.config_panel import ConfigPanel
from .panels.run_panel import RunPanel
from .panels.stats_panel import StatsPanel
from .worker import GAWorker


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Genetic Algorithm — USFQ Workshop")
        self.resize(1500, 720)
        self._worker = None
        self._build_ui()
        self._connect_signals()
        self._apply_dark_theme()

    def _build_ui(self):
        splitter = QSplitter(Qt.Horizontal)

        self.config_panel = ConfigPanel()
        self.config_panel.setMinimumWidth(420)
        self.config_panel.setMaximumWidth(500)

        self.run_panel = RunPanel()
        self.stats_panel = StatsPanel()

        splitter.addWidget(self.config_panel)
        splitter.addWidget(self.run_panel)
        splitter.addWidget(self.stats_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        splitter.setStretchFactor(2, 2)

        container = QWidget()
        layout = QHBoxLayout(container)
        layout.addWidget(splitter)
        self.setCentralWidget(container)

    def _connect_signals(self):
        self.config_panel.run_btn.clicked.connect(self._start_run)
        self.config_panel.stop_btn.clicked.connect(self._stop_run)
        self.config_panel.demo_btn.clicked.connect(self._show_demo)

    def _apply_dark_theme(self):
        self.setStyleSheet("""
            QMainWindow, QWidget { background: #252526; color: #d4d4d4; }
            QGroupBox { border: 1px solid #444; border-radius: 4px; margin-top: 8px; font-weight: bold; }
            QGroupBox::title { subcontrol-origin: margin; left: 8px; padding: 0 4px; }
            QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
                background: #3c3c3c; border: 1px solid #555; color: #d4d4d4;
                padding: 3px; border-radius: 3px;
            }
            QTabWidget::pane { border: 1px solid #444; }
            QTabBar::tab { background: #3c3c3c; color: #aaa; padding: 5px 12px; }
            QTabBar::tab:selected { background: #252526; color: #fff; border-bottom: 2px solid #2ecc71; }
            QProgressBar { border: 1px solid #555; border-radius: 3px; text-align: center; background: #3c3c3c; }
            QProgressBar::chunk { background: #2ecc71; }
            QLabel { color: #d4d4d4; }
            QScrollBar:vertical { background: #2a2a2a; width: 8px; }
            QScrollBar::handle:vertical { background: #555; border-radius: 4px; }
        """)

    # ── slots ────────────────────────────────────────────────────────────────

    def _start_run(self):
        config = self.config_panel.get_config()
        self.run_panel.set_max_iters(config.n_iterations)
        self.run_panel.clear()
        self.config_panel.set_running(True)

        self._worker = GAWorker(
            objective=self.config_panel.get_objective(),
            config=config,
            fitness=self.config_panel.get_fitness(),
            selection=self.config_panel.get_selection(),
            crossover=self.config_panel.get_crossover(),
            mutation=self.config_panel.get_mutation(),
        )
        self._worker.generation_ready.connect(self.run_panel.append_generation)
        self._worker.run_complete.connect(self._on_complete)
        self._worker.start()

    def _stop_run(self):
        if self._worker:
            self._worker.stop()

    def _on_complete(self, history):
        self.run_panel.show_result(history)
        self.stats_panel.update(history)
        self.config_panel.set_running(False)

    def _show_demo(self):
        target = self.config_panel.get_objective()
        n = 10
        lines = [f"Alphabet: {len(all_possible_gens)} chars  |  Length: {len(target)}  |  Space: {len(all_possible_gens)}^{len(target):.0f} ≈ {len(all_possible_gens)**len(target):.2e}", ""]
        for i in range(n):
            chrom = "".join(random.choice(all_possible_gens) for _ in range(len(target)))
            lines.append(f"[{i+1:2d}]  {chrom}")
        self.run_panel.append_demo(lines)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
