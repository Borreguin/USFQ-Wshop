import matplotlib.pyplot as plt
import os, sys
project_path = os.path.dirname(__file__)
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
                _maze.append(list(line.strip()))
        self.maze = _maze
        return self

    def _draw_maze(self, ax, path=None, visited=None, path_color="cyan", visited_color="lightblue"):
        """
        Dibuja el laberinto y opcionalmente:
        - visited: conjunto/lista de nodos visitados (x,y)
        - path: lista de nodos del camino final (x,y)
        """
        height = len(self.maze)
        width = len(self.maze[0])

        path_set = set(path) if path else set()
        visited_set = set(visited) if visited else set()

        for y in range(height):
            for x in range(width):
                cell = self.maze[y][x]

                # base color por tipo de celda
                color = define_color(cell)

                # si está en visited, pintar suave (sin tapar paredes)
                if (x, y) in visited_set and cell != '#':
                    color = visited_color

                # si está en el path final, pintar más fuerte (prioridad)
                if (x, y) in path_set and cell != '#':
                    # mantenemos entrada/salida con sus colores si quieres:
                    if cell not in ['E', 'S']:
                        color = path_color

                ax.fill([x, x+1, x+1, x], [y, y, y+1, y+1], color=color, edgecolor='black')

        ax.set_xlim(0, width)
        ax.set_ylim(0, height)
        ax.invert_yaxis()
        ax.set_xticks([])
        ax.set_yticks([])

    def plot_maze(self):
        height = len(self.maze)
        width = len(self.maze[0])

        fig = plt.figure(figsize=(width/4, height/4))
        ax = plt.gca()
        self._draw_maze(ax)
        fig.tight_layout()
        plt.show()
        return self

    def plot_solution(self, path, visited=None, save_as=None, show=True, title=None):
        """
        path: lista de nodos (x,y) desde E hasta S
        visited: opcional; para visualizar exploración del algoritmo
        save_as: nombre del PNG a guardar (ej: 'sol_bfs_laberinto1.png')
        """
        if self.maze is None:
            raise ValueError("Maze not loaded")

        height = len(self.maze)
        width = len(self.maze[0])

        fig = plt.figure(figsize=(width/4, height/4))
        ax = plt.gca()
        self._draw_maze(ax, path=path, visited=visited)

        if title:
            ax.set_title(title)

        fig.tight_layout()

        if save_as:
            # Carpeta donde se guardarán las imágenes de soluciones
            output_dir = os.path.join(project_path, "outputs")
            
            # Crear la carpeta si no existe
            os.makedirs(output_dir, exist_ok=True)

            # Ruta final del archivo
            out_path = os.path.join(output_dir, save_as)

            fig.savefig(out_path, dpi=200, bbox_inches='tight')
            print("✅ Imagen guardada en:", out_path)

        if show:
            plt.show()
        else:
            plt.close(fig)

        return self

    def get_graph(self):
        if self.maze is None:
            raise ValueError("Maze not loaded")

        graph = {}
        height = len(self.maze)
        width = len(self.maze[0])

        def is_walkable(cell):
            return cell in [' ', 'E', 'S']

        for y in range(height):
            for x in range(width):
                cell = self.maze[y][x]
                if not is_walkable(cell):
                    continue

                node = (x, y)
                graph[node] = []
                neighbors = [(x, y-1), (x, y+1), (x-1, y), (x+1, y)]

                for nx, ny in neighbors:
                    if 0 <= nx < width and 0 <= ny < height:
                        if is_walkable(self.maze[ny][nx]):
                            graph[node].append((nx, ny))

        return graph
