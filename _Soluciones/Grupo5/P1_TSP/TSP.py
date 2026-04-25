"""
TSP – Travelling Salesman Problem
Entry point. La logica esta en src/tsp.py (diseno OOP).
Uso: python P1_TSP/TSP.py [ruta/a/images/]
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from tsp import TSPSolver  # noqa: E402

def main(save_dir=None):
    TSPSolver(n_runs=20).run(save_dir=save_dir)

if __name__ == "__main__":
    main(save_dir=sys.argv[1] if len(sys.argv) > 1 else None)
