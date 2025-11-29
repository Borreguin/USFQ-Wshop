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
    
    def get_graph(self):
        graph = {}
        start_node = None
        end_node = None
        
        # Dimensiones
        rows = len(self.maze)
        cols = len(self.maze[0])
        
        # Direcciones posibles (Arriba, Abajo, Izquierda, Derecha)
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for y in range(rows):
            for x in range(cols):
                cell = self.maze[y][x]
                
                # Si es pared (#), ignoramos
                if cell == '#':
                    continue
                
                # Detectar Inicio y Fin
                if cell == 'E':
                    start_node = (x, y)
                elif cell == 'S':
                    end_node = (x, y)
                
                # Buscar vecinos válidos
                neighbors = []
                for dy, dx in directions:
                    ny, nx = y + dy, x + dx
                    # Verificar limites y que no sea pared
                    if 0 <= ny < rows and 0 <= nx < cols and self.maze[ny][nx] != '#':
                        neighbors.append((nx, ny))
                
                # Añadir al grafo: La clave es la coordenada (x,y), el valor es la lista de vecinos
                graph[(x, y)] = neighbors
                
        return graph, start_node, end_node

    # Modificamos plot_maze para que acepte un camino opcional (path) y eliminamos la anterior función
    def plot_maze(self, path=None, title="Laberinto"):
        height = len(self.maze)
        width = len(self.maze[0])

        fig = plt.figure(figsize=(width/4, height/4))
        plt.title(title)
        
        for y in range(height):
            for x in range(width):
                cell = self.maze[y][x]
                color = define_color(cell)
                plt.fill([x, x+1, x+1, x], [y, y, y+1, y+1], color=color, edgecolor='black')

        # Si hay un camino solución, lo dibujamos
        if path:
            x_coords = [p[0] + 0.5 for p in path]
            y_coords = [p[1] + 0.5 for p in path]
            plt.plot(x_coords, y_coords, color='blue', linewidth=3, marker='o', markersize=5)

        plt.xlim(0, width)
        plt.ylim(0, height)
        plt.gca().invert_yaxis()
        plt.xticks([])
        plt.yticks([])
        fig.tight_layout()
        plt.show() # Esto mostrará la ventana
        return self
