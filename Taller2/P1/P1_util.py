
def define_color(cell):
    if cell == '#':
        return 'black'
    elif cell == ' ':   # Espacio vacío
        return 'white'
    elif cell == 'E':   # Entrada
        return 'green'
    elif cell == 'S':   # Salida
        return 'red'
from collections import deque
import networkx as nx
from matplotlib import pyplot as plt

def bfs(graph, start, goal):
    queue = deque([start])
    visited = {start: None}

    while queue:
        node = queue.popleft()

        if node == goal:
            break

        for neighbor in graph.neighbors(node):
            if neighbor not in visited:
                visited[neighbor] = node
                queue.append(neighbor)

    # Reconstruir camino
    if goal not in visited:
        return None
    
    path = []
    cur = goal
    while cur is not None:
        path.append(cur)
        cur = visited[cur]
    path.reverse()

    return path


def dfs(graph, start, goal):
    stack = [start]
    visited = {start: None}

    while stack:
        node = stack.pop()

        if node == goal:
            break

        for neighbor in graph.neighbors(node):
            if neighbor not in visited:
                visited[neighbor] = node
                stack.append(neighbor)

    # Reconstrucción del camino
    if goal not in visited:
        return None

    path = []
    cur = goal
    while cur is not None:
        path.append(cur)
        cur = visited[cur]
    path.reverse()

    return path

def plot_path_over_maze(maze, path):
    """
    Recibe el maze en formato de matriz y un path como lista de coordenadas.
    Lo dibuja igual que plot_maze(), pero pintando el camino en azul.
    """
    height = len(maze)
    width = len(maze[0])

    fig = plt.figure(figsize=(width/4, height/4))

    # Dibujar celdas
    for y in range(height):
        for x in range(width):
            cell = maze[y][x]
            color = define_color(cell)
            plt.fill([x, x+1, x+1, x], [y, y, y+1, y+1], color=color, edgecolor='black')

    # Dibujar camino
    if path:
        xs = [p[0] + 0.5 for p in path]
        ys = [p[1] + 0.5 for p in path]
        plt.plot(xs, ys, color='blue', linewidth=3)

    plt.xlim(0, width)
    plt.ylim(0, height)
    plt.gca().invert_yaxis()
    plt.xticks([])
    plt.yticks([])
    fig.tight_layout()
    plt.show()
