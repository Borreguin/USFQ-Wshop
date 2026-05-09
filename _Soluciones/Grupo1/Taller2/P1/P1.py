import os, sys, time
project_path = os.path.dirname(__file__)
sys.path.append(project_path)
from P1_MazeLoader import MazeLoader
from collections import deque
import matplotlib.pyplot as plt




# 1) Convertir laberinto a grafo

def maze_to_graph(maze):
    """
    Cada celda transitable se representa como un nodo (fila, columna).
    Las paredes '#' no se incluyen.
    Hay aristas entre celdas vecinas: arriba, abajo, izquierda, derecha.
    """
    graph = {}
    start = None
    end = None

    for y, row in enumerate(maze):
        for x, cell in enumerate(row):
            if cell != "#":
                node = (y, x)
                graph[node] = []

                if cell == "E":
                    start = node
                elif cell == "S":
                    end = node

    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]

    for y, x in graph:
        for dy, dx in directions:
            neighbor = (y + dy, x + dx)
            if neighbor in graph:
                graph[(y, x)].append(neighbor)

    return graph, start, end


def reconstruct_path(parent, end):
    """Reconstruye la ruta desde E hasta S usando el diccionario de padres."""
    if end not in parent:
        return []

    path = []
    current = end

    while current is not None:
        path.append(current)
        current = parent[current]

    return path[::-1]



# 2) Algoritmo BFS

def bfs(graph, start, end):
    """
    Breadth First Search.
    En laberintos no ponderados encuentra la ruta más corta
    en número de pasos.
    """
    t0 = time.perf_counter()

    queue = deque([start])
    visited = {start}
    parent = {start: None}
    visited_order = []

    while queue:
        current = queue.popleft()
        visited_order.append(current)

        if current == end:
            break

        for neighbor in graph[current]:
            if neighbor not in visited:
                visited.add(neighbor)
                parent[neighbor] = current
                queue.append(neighbor)

    elapsed = time.perf_counter() - t0
    path = reconstruct_path(parent, end)

    return {
        "algorithm": "BFS",
        "path": path,
        "visited_order": visited_order,
        "path_length": len(path) - 1 if path else 0,
        "visited_nodes": len(visited_order),
        "time": elapsed,
    }



# 3) Algoritmo DFS

def dfs(graph, start, end):
    """
    Depth First Search.
    Explora profundo primero. Puede encontrar una solución,
    pero no garantiza que sea la más corta.
    """
    t0 = time.perf_counter()

    stack = [start]
    visited = set()
    parent = {start: None}
    visited_order = []

    while stack:
        current = stack.pop()

        if current in visited:
            continue

        visited.add(current)
        visited_order.append(current)

        if current == end:
            break

        # reversed para que el recorrido sea más estable visualmente
        for neighbor in reversed(graph[current]):
            if neighbor not in visited and neighbor not in parent:
                parent[neighbor] = current
                stack.append(neighbor)

    elapsed = time.perf_counter() - t0
    path = reconstruct_path(parent, end)

    return {
        "algorithm": "DFS",
        "path": path,
        "visited_order": visited_order,
        "path_length": len(path) - 1 if path else 0,
        "visited_nodes": len(visited_order),
        "time": elapsed,
    }



# 4) Graficar solución

def plot_solution(maze, result, output_path):
    """
    Negro: pared
    Blanco: camino libre
    Verde: entrada E
    Rojo: salida S
    Celeste: nodos visitados
    Amarillo: ruta final
    """
    height = len(maze)
    width = len(maze[0])

    path = set(result["path"])
    visited = set(result["visited_order"])

    fig = plt.figure(figsize=(max(width / 8, 4), max(height / 8, 3)))
    ax = plt.gca()

    for y in range(height):
        for x in range(width):
            cell = maze[y][x]
            node = (y, x)

            if cell == "#":
                color = "black"
            elif node in path:
                color = "gold"
            elif node in visited:
                color = "lightblue"
            elif cell == "E":
                color = "green"
            elif cell == "S":
                color = "red"
            else:
                color = "white"

            # Para que E y S siempre se vean claros
            if cell == "E":
                color = "green"
            elif cell == "S":
                color = "red"

            ax.fill(
                [x, x + 1, x + 1, x],
                [y, y, y + 1, y + 1],
                color=color,
                edgecolor="gray",
                linewidth=0.2,
            )

    ax.set_xlim(0, width)
    ax.set_ylim(0, height)
    ax.invert_yaxis()
    ax.set_xticks([])
    ax.set_yticks([])

    title = (
        f'{result["algorithm"]} | '
        f'Longitud ruta: {result["path_length"]} | '
        f'Nodos visitados: {result["visited_nodes"]} | '
        f'Tiempo: {result["time"]:.6f}s'
    )
    ax.set_title(title)

    fig.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)



# 5) Ejecutar caso de estudio

def solve_maze(maze_file):
    maze_loader = MazeLoader(maze_file).load_Maze()
    maze = maze_loader.maze

    graph, start, end = maze_to_graph(maze)

    if start is None or end is None:
        raise ValueError("El laberinto debe tener una entrada E y una salida S.")

    results = [bfs(graph, start, end), dfs(graph, start, end)]

    print("\nResultados para:", maze_file)
    print("Algoritmo | Longitud ruta | Nodos visitados | Tiempo (s)")
    print("-" * 60)

    for result in results:
        print(
            f'{result["algorithm"]:9} | '
            f'{result["path_length"]:13} | '
            f'{result["visited_nodes"]:15} | '
            f'{result["time"]:.6f}'
        )

        image_name = f'{maze_file.replace(".txt", "")}_{result["algorithm"]}.png'
        output_path = os.path.join(os.path.dirname(project_path), 'images', image_name)
        plot_solution(maze, result, output_path)
        print("Imagen guardada:", image_name)

    return results


def study_case_1():
    solve_maze("laberinto1.txt")


def study_case_3():
    solve_maze("laberinto3.txt")


if __name__ == "__main__":
    study_case_1()
    study_case_3()
