"""
Torre de Hanoi
Entry point. La logica esta en src/hanoi.py (diseno OOP).
Uso: python P3_Torres/Torres.py [ruta/a/images/] [n_discos]
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from hanoi import HanoiSolver, HanoiVisualizer  # noqa: E402

def main(save_dir=None, n=None):
    if n is None:
        n = int(input("Numero de discos (recomendado 3-5): ") or "4")
    n = max(1, min(n, 10))

    solver = HanoiSolver(n).solve()
    solver.print_moves()

    viz = HanoiVisualizer(solver)
    if save_dir:
        viz.save_all(save_dir)
    else:
        viz.show()

if __name__ == "__main__":
    _save = sys.argv[1] if len(sys.argv) > 1 else None
    _n    = int(sys.argv[2]) if len(sys.argv) > 2 else None
    main(save_dir=_save, n=_n)
