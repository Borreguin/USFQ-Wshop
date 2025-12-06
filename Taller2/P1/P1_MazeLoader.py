import matplotlib.pyplot as plt
import os, sys
project_path = os.path.dirname(__file__)
sys.path.append(project_path)
#from Taller2.P1.P1_util import define_color
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

    def plot_maze(self):
        height = len(self.maze)
        width = len(self.maze[0])

        # Usar plt.subplots() para crear y capturar la figura y los ejes
        fig, ax = plt.subplots(figsize=(width/4, height/4)) 
        
        for y in range(height):
            for x in range(width):
                cell = self.maze[y][x]
                color = define_color(cell)
                # Dibujar usando ax.fill en lugar de plt.fill
                ax.fill([x, x+1, x+1, x], [y, y, y+1, y+1], color=color, edgecolor='black')

        ax.set_xlim(0, width)
        ax.set_ylim(0, height)
        ax.invert_yaxis() # Invierte el eje y para que el origen esté en la esquina superior izquierda
        ax.set_xticks([])
        ax.set_yticks([])
        
        # Devolvemos self, la figura (fig) y los ejes (ax)
        # Esto es lo que permite que la línea 'maze, fig, ax = maze.plot_maze()' funcione.
        return self, fig, ax

    def get_graph(self):
        # Implementar la creación del grafo a partir del laberinto
        """
        Implementa la creación del grafo a partir del laberinto.
        El grafo es un diccionario donde:
        - La clave es la celda transitable (y, x) y se representa como nodo
        - El valor es una lista de vecinos transitables [(y1, x1), (y2, x2), ...]
        También identifica los nodos de entrada y salida.
        """
        graph = {}
        self.start_node = None
        self.end_node = None
        height = len(self.maze)
        width = len(self.maze[0])
        
        # Direcciones de movimiento (arriba, abajo, izquierda, derecha)
        # la tupla de 2 posiciones permite combinaciones necesarias para modelar cada
        # movimiento, los valores negativos indican sentido (abajo, derecha)
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

        for y in range(height):
            for x in range(width):
                cell = self.maze[y][x]
                
                # Solo celdas transitables (' ', 'E', 'S') son nodos
                if cell != '#':
                    current_node = (y, x)
                    neighbors = []
                    
                    if cell == 'E':
                        self.start_node = current_node
                    elif cell == 'S':
                        self.end_node = current_node
                        
                    # Buscar vecinos transitables
                    for dy, dx in directions:
                        ny, nx = y + dy, x + dx
                        
                        # Comprobar límites y si la celda es transitable
                        if 0 <= ny < height and 0 <= nx < width and self.maze[ny][nx] != '#':
                            neighbors.append((ny, nx))
                            
                    graph[current_node] = neighbors
        
        if not self.start_node or not self.end_node:
             print("Error: El laberinto debe contener un punto de inicio ('E') y uno de fin ('S').")
             return None
             
        self.graph = graph
        return graph, self.start_node, self.end_node
