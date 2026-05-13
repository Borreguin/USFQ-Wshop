from PyQt5.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QHeaderView,
)
from PyQt5.QtCore import Qt
import matplotlib
matplotlib.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from ...models.ga_stats import GAHistory


class StatsPanel(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("Statistics", parent)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout()
        tabs = QTabWidget()

        # ── Chart tab ──────────────────────────────────────────────────────
        self.figure = Figure(facecolor="#1e1e1e")
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self._style_axes()
        tabs.addTab(self.canvas, "Convergence Chart")

        # ── Table tab ──────────────────────────────────────────────────────
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Gen", "Best", "Mean", "Worst", "Diversity"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setStyleSheet("background: #1e1e1e; color: #d4d4d4; gridline-color: #333;")
        tabs.addTab(self.table, "Data Table")

        # ── Summary tab ────────────────────────────────────────────────────
        self.summary_label = QLabel("Run the GA to see statistics.")
        self.summary_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.summary_label.setStyleSheet("color: #d4d4d4; padding: 10px; font-family: monospace;")
        self.summary_label.setWordWrap(True)
        tabs.addTab(self.summary_label, "Summary")

        layout.addWidget(tabs)
        self.setLayout(layout)

    def _style_axes(self):
        self.ax.set_facecolor("#1e1e1e")
        self.ax.tick_params(colors="#888")
        self.ax.spines["bottom"].set_color("#444")
        self.ax.spines["left"].set_color("#444")
        self.ax.spines["top"].set_visible(False)
        self.ax.spines["right"].set_visible(False)
        self.ax.set_xlabel("Generation", color="#888")
        self.ax.set_ylabel("Fitness", color="#888")
        self.ax.set_title("Fitness Convergence", color="#ccc")

    def update(self, history: GAHistory):
        self._update_chart(history)
        self._update_table(history)
        self._update_summary(history)

    def _update_chart(self, history: GAHistory):
        self.ax.cla()
        self._style_axes()
        gens = [s.generation for s in history.generations]
        self.ax.plot(gens, history.best_fitness_history, color="#2ecc71", label="Best", linewidth=1.5)
        self.ax.plot(gens, history.mean_fitness_history, color="#3498db", label="Mean", linewidth=1, linestyle="--")
        self.ax.fill_between(gens, history.mean_fitness_history, history.best_fitness_history, alpha=0.1, color="#2ecc71")
        self.ax.legend(facecolor="#2a2a2a", edgecolor="#444", labelcolor="#ccc")
        self.canvas.draw()

    def _update_table(self, history: GAHistory):
        self.table.setRowCount(0)
        step = max(1, len(history.generations) // 200)
        for stats in history.generations[::step]:
            row = self.table.rowCount()
            self.table.insertRow(row)
            for col, val in enumerate([
                str(stats.generation),
                f"{stats.best_fitness:.1f}",
                f"{stats.mean_fitness:.1f}",
                f"{stats.worst_fitness:.1f}",
                f"{stats.diversity:.2%}",
            ]):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, col, item)

    def _update_summary(self, history: GAHistory):
        if not history.generations:
            return
        first = history.generations[0]
        last = history.generations[-1]
        status = "SUCCESS" if history.success else "NOT FOUND"
        bfh = history.best_fitness_history
        dh = history.diversity_history
        text = (
            f"Status         : {status}\n"
            f"Generations    : {history.total_generations}\n\n"
            f"Initial best   : {first.best_fitness:.1f}  (\"{first.best_individual}\")\n"
            f"Final best     : {last.best_fitness:.1f}  (\"{last.best_individual}\")\n"
            f"Objective      : \"{last.objective}\"\n"
            f"Match          : {last.match_count}/{len(last.objective)} chars\n\n"
            f"Peak fitness   : {max(bfh):.1f}\n"
            f"Avg fitness    : {sum(bfh)/len(bfh):.2f}\n"
            f"Avg diversity  : {sum(dh)/len(dh):.2%}\n"
        )
        self.summary_label.setText(text)
