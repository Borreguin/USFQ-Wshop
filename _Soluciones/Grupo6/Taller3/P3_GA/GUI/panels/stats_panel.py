from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QGroupBox,
    QHeaderView,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
)

import matplotlib
matplotlib.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class StatsPanel(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("Estadísticas", parent)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout()
        tabs = QTabWidget()

        self.figure = Figure(facecolor="#1e1e1e")
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self._style_axes()
        tabs.addTab(self.canvas, "Convergencia")

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(
            ["Generación", "Mejor apt.", "Media apt.", "Coincidencias", "Mejor individuo"]
        )
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setStyleSheet(
            "background: #1e1e1e; color: #d4d4d4; gridline-color: #333;"
        )
        tabs.addTab(self.table, "Tabla de datos")

        self.summary_label = QLabel("Ejecuta el AG para ver las estadísticas.")
        self.summary_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.summary_label.setStyleSheet(
            "color: #d4d4d4; padding: 12px; font-family: monospace; font-size: 10pt;"
        )
        self.summary_label.setWordWrap(True)
        tabs.addTab(self.summary_label, "Resumen")

        layout.addWidget(tabs)
        self.setLayout(layout)

    def _style_axes(self):
        self.ax.set_facecolor("#1e1e1e")
        self.ax.tick_params(colors="#888")
        for spine in ("bottom", "left"):
            self.ax.spines[spine].set_color("#444")
        for spine in ("top", "right"):
            self.ax.spines[spine].set_visible(False)
        self.ax.set_xlabel("Generación", color="#888")
        self.ax.set_ylabel("Aptitud / Coincidencias", color="#888")
        self.ax.set_title("Convergencia del Algoritmo Genético", color="#ccc")

    def update(self, result: dict):
        history = result.get('history', [])
        if not history:
            return
        self._update_chart(history, result.get('success', False))
        self._update_table(history)
        self._update_summary(history, result)

    def _update_chart(self, history: list, success: bool):
        self.ax.cla()
        self._style_axes()

        gens = [s['generation'] for s in history]
        best_apt = [s['best_aptitude'] for s in history]
        mean_apt = [s['mean_aptitude'] for s in history]
        matches = [s['match_count'] for s in history]

        self.ax.plot(gens, best_apt, color="#2ecc71", label="Mejor aptitud", linewidth=1.5)
        self.ax.plot(gens, mean_apt, color="#3498db", label="Media aptitud",
                     linewidth=1, linestyle="--")
        self.ax.plot(gens, matches, color="#f39c12", label="Coincidencias",
                     linewidth=1, linestyle=":")
        self.ax.fill_between(gens, mean_apt, best_apt, alpha=0.08, color="#2ecc71")

        if success:
            self.ax.axvline(x=gens[-1], color="#e74c3c", linestyle="--",
                            linewidth=0.8, label="Objetivo alcanzado")

        self.ax.legend(facecolor="#2a2a2a", edgecolor="#444", labelcolor="#ccc",
                       fontsize=8)
        self.canvas.draw()

    def _update_table(self, history: list):
        self.table.setRowCount(0)
        step = max(1, len(history) // 200)
        for stats in history[::step]:
            row = self.table.rowCount()
            self.table.insertRow(row)
            values = [
                str(stats['generation']),
                f"{stats['best_aptitude']:.1f}",
                f"{stats['mean_aptitude']:.1f}",
                f"{stats['match_count']}/{len(stats['objective'])}",
                stats['best_individual'],
            ]
            for col, val in enumerate(values):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, col, item)

    def _update_summary(self, history: list, result: dict):
        first = history[0]
        last = history[-1]
        status = "ÉXITO" if result.get('success') else "NO CONVERGIÓ"
        obj = last['objective']

        best_apts = [s['best_aptitude'] for s in history]
        matches = [s['match_count'] for s in history]

        text = (
            f"Estado           : {status}\n"
            f"Generaciones     : {result.get('n_generation', len(history))}\n\n"
            f"Objetivo         : {obj!r}\n"
            f"Mejor inicial    : {first['best_individual']!r}\n"
            f"Mejor final      : {last['best_individual']!r}\n"
            f"Coincidencias    : {last['match_count']}/{len(obj)} caracteres\n\n"
            f"Pico de aptitud  : {max(best_apts):.1f}\n"
            f"Media de aptitud : {sum(best_apts)/len(best_apts):.2f}\n"
            f"Máx. coincid.    : {max(matches)}/{len(obj)}\n"
        )
        self.summary_label.setText(text)
