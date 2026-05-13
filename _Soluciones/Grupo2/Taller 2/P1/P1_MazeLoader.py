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
                _maze.append(list(line.rstrip('\n\r')))
        self.maze = _maze
        return self

    def plot_maze(self):
        height = len(self.maze)
        width = max(len(row) for row in self.maze)

        fig = plt.figure(figsize=(width/4, height/4))  # Ajusta el tamaño de la figura según el tamaño del Maze
        for y in range(height):
            for x in range(len(self.maze[y])):
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

    def plot_solution(self, path, title=''):
        height = len(self.maze)
        width  = max(len(row) for row in self.maze)
        path_set = set(path)

        fig = plt.figure(figsize=(width / 4, height / 4))
        for y in range(height):
            for x in range(len(self.maze[y])):
                cell = self.maze[y][x]
                if (y, x) in path_set and cell not in ('E', 'S'):
                    color = 'cornflowerblue'
                else:
                    color = define_color(cell)
                plt.fill([x, x+1, x+1, x], [y, y, y+1, y+1], color=color, edgecolor='black')

        plt.xlim(0, width)
        plt.ylim(0, height)
        plt.gca().invert_yaxis()
        plt.xticks([])
        plt.yticks([])
        if title:
            plt.title(title)
        fig.tight_layout()
        plt.show()
        return self

    def get_graph(self):
        WALKABLE = {' ', 'E', 'S'}
        DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # arriba, abajo, izquierda, derecha
        graph = {}

        for row in range(len(self.maze)):
            for col in range(len(self.maze[row])):
                cell = self.maze[row][col]
                if cell not in WALKABLE:
                    continue

                neighbors = []
                for dr, dc in DIRECTIONS:
                    nr, nc = row + dr, col + dc
                    if 0 <= nr < len(self.maze) and 0 <= nc < len(self.maze[nr]):
                        if self.maze[nr][nc] in WALKABLE:
                            neighbors.append((nr, nc))

                graph[(row, col)] = {'neighbors': neighbors, 'type': cell}

        return graph
    
    