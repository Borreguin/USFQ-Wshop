import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os, sys

project_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_path)
from P1_util import define_color


class MazeLoader:
    def __init__(self, filename):
        self.filename = filename
        self.maze = None

    def load_Maze(self):
        _maze = []
        file_path = os.path.join(project_path, self.filename)
        print("Loading Maze from", file_path)
        with open(file_path, 'r') as file:
            for line in file:
                _maze.append(list(line.rstrip('\n')))
        self.maze = _maze
        return self

    def plot_maze(self):
        height = len(self.maze)
        width = max(len(row) for row in self.maze)
        fig, ax = plt.subplots(figsize=(width / 4, height / 4))
        self._draw_maze_on_ax(ax)
        fig.tight_layout()
        plt.savefig(os.path.join(project_path, '..', 'images', f'{self.filename[:-4]}.png'),
                    dpi=100, bbox_inches='tight')
        plt.close(fig)
        return self

    def _draw_maze_on_ax(self, ax, path=None):
        path_set = set(path) if path else set()
        height = len(self.maze)
        for y in range(height):
            for x in range(len(self.maze[y])):
                cell = self.maze[y][x]
                if (y, x) in path_set and cell not in ('E', 'S'):
                    color = '#5B9BD5'  # blue for path
                else:
                    color = define_color(cell) or 'white'
                ax.fill([x, x+1, x+1, x], [y, y, y+1, y+1],
                        color=color, edgecolor='black', linewidth=0.3)
        width = max(len(row) for row in self.maze)
        ax.set_xlim(0, width)
        ax.set_ylim(0, height)
        ax.invert_yaxis()
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_aspect('equal')

    def get_graph(self):
        """Convierte el laberinto en un grafo de adyacencia {nodo: [vecinos]}."""
        if self.maze is None:
            return None
        passable = {' ', 'E', 'S'}
        height = len(self.maze)
        graph = {}
        for row in range(height):
            for col in range(len(self.maze[row])):
                if self.maze[row][col] in passable:
                    neighbors = []
                    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nr, nc = row + dr, col + dc
                        if (0 <= nr < height and 0 <= nc < len(self.maze[nr])
                                and self.maze[nr][nc] in passable):
                            neighbors.append((nr, nc))
                    graph[(row, col)] = neighbors
        return graph

    def find_start_end(self):
        """Retorna (start, end) como coordenadas (fila, columna)."""
        start = end = None
        for row in range(len(self.maze)):
            for col in range(len(self.maze[row])):
                cell = self.maze[row][col]
                if cell == 'E':
                    start = (row, col)
                elif cell == 'S':
                    end = (row, col)
        return start, end

    def plot_comparison(self, solutions, maze_name, save_path=None):
        """
        Genera figura comparativa de algoritmos.
        solutions: list of (algo_name, path, nodes_visited, elapsed_secs)
        """
        n = len(solutions)
        height = len(self.maze)
        width = max(len(row) for row in self.maze)

        cell_size = max(0.10, min(0.20, 16.0 / width))
        title_h = 0.5   # inches per subplot title
        suptitle_h = 0.4  # inches for the figure title
        fig_w = width * cell_size + 2
        fig_h = (height * cell_size + title_h) * n + suptitle_h

        fig, axes = plt.subplots(n, 1, figsize=(fig_w, fig_h))
        if n == 1:
            axes = [axes]

        fig.suptitle(f'Comparación de algoritmos — {maze_name}',
                     fontsize=13, fontweight='bold')

        for ax, (algo_name, path, nodes_visited, elapsed) in zip(axes, solutions):
            self._draw_maze_on_ax(ax, path)
            steps = len(path) - 1 if path else 0
            title = (f'{algo_name}   |   Pasos: {steps}   |   '
                     f'Nodos explorados: {nodes_visited}   |   '
                     f'Tiempo: {elapsed * 1000:.3f} ms')
            ax.set_title(title, fontsize=10, pad=6)

        fig.tight_layout(rect=[0, 0, 1, 0.97])
        fig.subplots_adjust(hspace=0.35)

        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"  Imagen guardada: {save_path}")

        plt.close(fig)
        return fig