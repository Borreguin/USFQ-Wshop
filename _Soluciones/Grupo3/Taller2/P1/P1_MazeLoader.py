import matplotlib.pyplot as plt
import os
import sys

project_path = os.path.dirname(__file__)
sys.path.append(project_path)

from Taller2.P1.P1_util import define_color


class MazeLoader:
    def __init__(self, filename):
        self.filename = filename
        self.maze = None

    def load_Maze(self):
        _maze = []
        file_path = os.path.join(project_path, self.filename)
        print("Loading Maze from", file_path)

        with open(file_path, "r") as file:
            for line in file:
                _maze.append(list(line.rstrip("\n")))

        max_width = max(len(row) for row in _maze)

        for row in _maze:
            while len(row) < max_width:
                row.append("#")

        self.maze = _maze
        return self

    def plot_maze(self):
        height = len(self.maze)
        width = len(self.maze[0])

        fig = plt.figure(figsize=(width / 4, height / 4))

        for y in range(height):
            for x in range(width):
                cell = self.maze[y][x]
                color = define_color(cell)

                plt.fill(
                    [x, x + 1, x + 1, x],
                    [y, y, y + 1, y + 1],
                    color=color,
                    edgecolor="black"
                )

        plt.xlim(0, width)
        plt.ylim(0, height)
        plt.gca().invert_yaxis()
        plt.xticks([])
        plt.yticks([])
        fig.tight_layout()
        plt.show()

        return self

    def get_graph(self):
        graph = {}

        height = len(self.maze)
        width = len(self.maze[0])

        movements = [
            (-1, 0), #arriba
            (1, 0),  #abajo
            (0, -1), #izquierda
            (0, 1)   #derecha
        ]

        for y in range(height):
            for x in range(width):
                cell = self.maze[y][x]

                if cell != "#":
                    graph[(y, x)] = []

                    for dy, dx in movements:
                        ny = y + dy
                        nx = x + dx

                        if 0 <= ny < height and 0 <= nx < width:
                            neighbor = self.maze[ny][nx]

                            if neighbor != "#":
                                graph[(y, x)].append((ny, nx))

        return graph
    
# Transformación del laberinto a grafo:
# Cada celda libre del laberinto se representa como un nodo.
# Se usa un diccionario (lista de adyacencia) donde:
# graph[(fila, columna)] = lista de vecinos accesibles.
# Solo se consideran movimientos arriba, abajo, izquierda y derecha.
# Las paredes (#) no se incluyen en el grafo.