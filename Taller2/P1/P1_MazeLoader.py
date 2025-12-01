import matplotlib.pyplot as plt
import os, sys
project_path = os.path.dirname(__file__)
sys.path.append(project_path)
from P1_util import define_color


class MazeLoader:
    def __init__(self, filename):
        self.filename = filename
        self.maze = None
        self.start = None
        self.end = None

    def load_Maze(self):
        _maze = []
        file_path = os.path.join(project_path, self.filename)
        print("Loading Maze from", file_path)
        with open(file_path, 'r') as file:
            for line in file:
                _maze.append(list(line.strip()))
        self.maze = _maze
        for y in range(len(self.maze)):
           for x in range(len(self.maze[0])):
               if self.maze[y][x] == 'E':
                   self.start = (x, y)
               elif self.maze[y][x] == 'S':
                   self.end = (x, y)
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
    

    def get_graph(self, cost=1):

        graph = {}
        height = len(self.maze)
        width = len(self.maze[0])
        
        # Direcciones: arriba, abajo, izquierda, derecha
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        
        for y in range(height):
            for x in range(width):
                if self.maze[y][x] != '#':  # Si no es pared
                    neighbors = []
                    for dx, dy in directions:
                        nx, ny = x + dx, y + dy
                        # Verificar límites y que no sea pared
                        if (0 <= nx < width and 0 <= ny < height and 
                            self.maze[ny][nx] != '#'):
                            neighbors.append(((nx, ny), cost))  # Costo uniforme de 1
                    graph[(x, y)] = neighbors
        
        return graph,self.start, self.end
    
    