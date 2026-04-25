"""
Acertijo del Granjero y el Bote
Entry point. La logica esta en src/granjero.py (diseno OOP).
Uso: python P2_Granjero/Acertijo.py [ruta/a/images/]
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from granjero import FarmerPuzzle, PuzzleVisualizer  # noqa: E402

def main(save_dir=None):
    puzzle = FarmerPuzzle()
    puzzle.print_solution()
    viz = PuzzleVisualizer(puzzle)
    if save_dir:
        viz.save_all(save_dir)
    else:
        viz.show()

if __name__ == "__main__":
    main(save_dir=sys.argv[1] if len(sys.argv) > 1 else None)
