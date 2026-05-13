from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QTextCharFormat, QTextCursor
from PyQt5.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QTextEdit,
    QVBoxLayout,
)

from ...models.ga_stats import GAHistory, GenerationStats


class RunPanel(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("Live Output", parent)
        self._build_ui()
        self._max_iters = 1000

    def _build_ui(self):
        layout = QVBoxLayout()

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setFont(QFont("Monospace", 9))
        self.log.setStyleSheet("background: #1e1e1e; color: #d4d4d4;")
        layout.addWidget(self.log, stretch=4)

        # progress bar + match label
        bar_row = QHBoxLayout()
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.match_label = QLabel("Match: 0 / ?")
        bar_row.addWidget(self.progress, stretch=3)
        bar_row.addWidget(self.match_label)
        layout.addLayout(bar_row)

        # status row
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    def set_max_iters(self, n: int):
        self._max_iters = n

    def clear(self):
        self.log.clear()
        self.progress.setValue(0)
        self.match_label.setText("Match: 0 / ?")
        self.status_label.setText("Running…")

    def append_generation(self, stats: GenerationStats):
        pct = stats.match_ratio * 100
        self.progress.setValue(int(pct))
        self.match_label.setText(f"Match: {stats.match_count} / {len(stats.objective)}")

        # Build colored HTML diff
        diff_html = ""
        for a, b in zip(stats.best_individual, stats.objective):
            color = "#2ecc71" if a == b else "#e74c3c"
            diff_html += f'<span style="color:{color}">{a}</span>'

        line = (
            f'<span style="color:#888">Gen {stats.generation:5d}</span> '
            f'| Best <span style="color:#f1c40f">{stats.best_fitness:6.1f}</span> '
            f'| Mean {stats.mean_fitness:6.1f} '
            f'| Div {stats.diversity:.2f} '
            f'&rarr; {diff_html}<br>'
        )
        self.log.moveCursor(QTextCursor.End)
        self.log.insertHtml(line)
        self.log.moveCursor(QTextCursor.End)

    def append_demo(self, lines: list):
        self.log.clear()
        html = '<span style="color:#56b6c2; font-weight:bold">Random Chromosome Demo</span><br><br>'
        for line in lines:
            html += f'<span style="color:#abb2bf">{line}</span><br>'
        self.log.setHtml(html)

    def show_result(self, history: GAHistory):
        if history.success:
            self.status_label.setText(
                f"SUCCESS — found in {history.total_generations} generations"
            )
            self.status_label.setStyleSheet("color: #2ecc71; font-weight: bold;")
            self.progress.setValue(100)
        else:
            self.status_label.setText(
                f"Not found in {history.total_generations} iterations"
            )
            self.status_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
