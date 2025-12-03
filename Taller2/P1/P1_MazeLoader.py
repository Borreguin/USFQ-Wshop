import matplotlib.pyplot as plt
import os, sys
project_path = os.path.dirname(__file__)
sys.path.append(project_path)
from P1_util import define_color
import networkx as nx

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

    def plot_maze(self):
        height = len(self.maze)
        width = len(self.maze[0])

        fig = plt.figure(figsize=(width/4, height/4))  # Ajusta el tamaño de la figura según el tamaño del Maze
        for y in range(height):
            for x in range(width):
                cell = self.maze[y][x]
                color = define_color(cell)
                plt.fill([x, x+1, x+1, x], [y, y, y+1, y+1], color=color, edgecolor='black')

        plt.xlim(0, width)
        plt.ylim(0, height)
        plt.gca().invert_yaxis()  # Invierte el eje y para que el origen esté en la esquina inferior izquierda
        plt.xticks([])
        plt.yticks([])
        fig.tight_layout()
        plt.show()
        return self


    def get_graph(self):
        """
        Crea un grafo donde cada celda libre (' ', 'E', 'S') es un nodo,
        y se conectan celdas adyacentes arriba/abajo/izquierda/derecha.
        """
        G = nx.Graph()
        height = len(self.maze)
        width = len(self.maze[0])

        for y in range(height):
            for x in range(width):
                cell = self.maze[y][x]

                if cell in [' ', 'E', 'S']:  # Espacios transitables
                    G.add_node((x, y))

                    # Vecinos posibles
                    for dx, dy in [(1,0), (-1,0), (0,1), (0,-1)]:
                        nx_x, nx_y = x + dx, y + dy

                        # Validación de límites
                        if 0 <= nx_x < width and 0 <= nx_y < height:
                            if self.maze[nx_y][nx_x] in [' ', 'E', 'S']:
                                G.add_edge((x, y), (nx_x, nx_y))

        return G
