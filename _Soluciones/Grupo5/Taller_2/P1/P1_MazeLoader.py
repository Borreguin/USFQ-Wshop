"""Lector y graficador de laberintos para la Parte 1 del Taller 2.

Convierte un archivo .txt de laberinto en una matriz y en un grafo no dirigido.
Coordenadas usadas en el grafo: (fila, columna).
"""

import os
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple

import matplotlib.pyplot as plt

try:
    from P1_util import define_color
except ImportError:  # Permite ejecutar desde la raíz del repo: python Taller2/P1/P1.py
    from Taller2.P1.P1_util import define_color

Position = Tuple[int, int]
Graph = Dict[Position, List[Position]]
PASSABLE_CELLS = {' ', 'E', 'S'}


class MazeLoader:
    def __init__(self, filename: str):
        self.filename = filename
        self.maze: Optional[List[List[str]]] = None
        self.graph: Optional[Graph] = None
        self.start: Optional[Position] = None
        self.end: Optional[Position] = None

    def load_Maze(self):
        """Carga el laberinto desde texto sin eliminar espacios internos ni finales."""
        project_path = Path(__file__).resolve().parent
        file_path = project_path / self.filename
        print(f"Loading Maze from {file_path}")

        rows: List[List[str]] = []
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                rows.append(list(line.rstrip('\n')))

        if not rows:
            raise ValueError(f"El archivo {self.filename} está vacío.")

        # Normaliza filas desiguales rellenando con paredes.
        width = max(len(row) for row in rows)
        self.maze = [row + ['#'] * (width - len(row)) for row in rows]
        return self

    def _require_maze(self) -> List[List[str]]:
        if self.maze is None:
            raise ValueError("Primero debes cargar el laberinto con load_Maze().")
        return self.maze

    def get_graph(self) -> Graph:
        """Transforma el laberinto en un grafo de adyacencia con movimientos 4-direcciones.

        Cada celda transitable (' ', 'E', 'S') es un nodo. Existe una arista entre dos
        nodos cuando son vecinos verticales u horizontales y no son pared.
        """
        maze = self._require_maze()
        graph: Graph = {}
        self.start = None
        self.end = None

        for row_index, row in enumerate(maze):
            for col_index, cell in enumerate(row):
                if cell in PASSABLE_CELLS:
                    node = (row_index, col_index)
                    graph[node] = []
                    if cell == 'E':
                        self.start = node
                    elif cell == 'S':
                        self.end = node

        if self.start is None or self.end is None:
            raise ValueError("El laberinto debe contener una entrada 'E' y una salida 'S'.")

        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for row, col in graph:
            for d_row, d_col in directions:
                neighbor = (row + d_row, col + d_col)
                if neighbor in graph:
                    graph[(row, col)].append(neighbor)

        self.graph = graph
        return graph

    def get_start_end(self) -> Tuple[Position, Position]:
        if self.start is None or self.end is None:
            self.get_graph()
        return self.start, self.end  # type: ignore[return-value]

    def plot_maze(
        self,
        path: Optional[Iterable[Position]] = None,
        visited: Optional[Iterable[Position]] = None,
        title: str = "Laberinto",
        save_path: Optional[str] = None,
        show: bool = False,
    ):
        """Grafica el laberinto y, opcionalmente, las celdas visitadas y la ruta solución."""
        maze = self._require_maze()
        path_set: Set[Position] = set(path or [])
        visited_set: Set[Position] = set(visited or [])
        height = len(maze)
        width = len(maze[0])

        fig_width = max(6, min(24, width / 3))
        fig_height = max(4, min(14, height / 3))
        fig, ax = plt.subplots(figsize=(fig_width, fig_height))

        for row in range(height):
            for col in range(width):
                cell = maze[row][col]
                draw_cell = cell
                position = (row, col)
                if position in visited_set and cell not in {'#', 'E', 'S'}:
                    draw_cell = '*'
                if position in path_set and cell not in {'#', 'E', 'S'}:
                    draw_cell = '.'
                color = define_color(draw_cell)
                ax.fill(
                    [col, col + 1, col + 1, col],
                    [row, row, row + 1, row + 1],
                    color=color,
                    edgecolor='black',
                    linewidth=0.35,
                )

        ax.set_xlim(0, width)
        ax.set_ylim(0, height)
        ax.invert_yaxis()
        ax.set_aspect('equal')
        ax.set_title(title)
        ax.set_xticks([])
        ax.set_yticks([])
        fig.tight_layout()

        if save_path:
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(save_path, dpi=180, bbox_inches='tight')
        if show:
            plt.show()
        plt.close(fig)
        return self
