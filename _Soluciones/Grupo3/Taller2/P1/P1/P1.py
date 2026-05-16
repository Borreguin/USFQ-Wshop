import os
import sys
import time
from collections import deque

import matplotlib.pyplot as plt

project_path = os.path.dirname(__file__)
sys.path.append(project_path)

from Taller2.P1.P1_MazeLoader import MazeLoader


def find_start_goal(maze_matrix):
    start = None
    goal = None

    height = len(maze_matrix)
    width = len(maze_matrix[0])

    for y in range(height):
        for x in range(width):
            cell = maze_matrix[y][x]

            if cell == "S":
                start = (y, x)

            if cell == "E":
                goal = (y, x)

    return start, goal


def reconstruct_path(parents, goal):
    if goal not in parents:
        return []

    path = []
    current = goal

    while current is not None:
        path.append(current)
        current = parents[current]

    path.reverse()
    return path


def bfs(graph, start, goal):
    queue = deque([start])
    visited = {start}
    parents = {start: None}
    explored_nodes = 0

    while queue:
        current = queue.popleft()
        explored_nodes += 1

        if current == goal:
            break

        for neighbor in graph.get(current, []):
            if neighbor not in visited:
                visited.add(neighbor)
                parents[neighbor] = current
                queue.append(neighbor)

    return reconstruct_path(parents, goal), explored_nodes


def dfs(graph, start, goal):
    stack = [start]
    visited = {start}
    parents = {start: None}
    explored_nodes = 0

    while stack:
        current = stack.pop()
        explored_nodes += 1

        if current == goal:
            break

        for neighbor in graph.get(current, []):
            if neighbor not in visited:
                visited.add(neighbor)
                parents[neighbor] = current
                stack.append(neighbor)

    return reconstruct_path(parents, goal), explored_nodes


def plot_solution(maze_matrix, path, title, filename):
    height = len(maze_matrix)
    width = len(maze_matrix[0])

    fig = plt.figure(figsize=(width / 4, height / 4))

    path_set = set(path)

    for y in range(height):
        for x in range(width):
            cell = maze_matrix[y][x]

            if cell == "#":
                color = "black"
            elif cell == "S":
                color = "green"
            elif (y, x) in path_set:
                color = "blue"
            else:
                color = "white"

            plt.fill(
                [x, x + 1, x + 1, x],
                [y, y, y + 1, y + 1],
                color=color,
                edgecolor="gray"
            )

    plt.title(title)
    plt.xlim(0, width)
    plt.ylim(0, height)
    plt.gca().invert_yaxis()
    plt.xticks([])
    plt.yticks([])
    fig.tight_layout()

    plt.savefig(filename)
    plt.close()


def solve_maze(maze_file, case_name):
    print(f"\n===== {case_name} =====")

    maze = MazeLoader(maze_file).load_Maze().plot_maze()
    symbols = sorted(set(cell for row in maze.maze for cell in row))
    print("Símbolos encontrados:", symbols)
    graph = maze.get_graph()

    start, goal = find_start_goal(maze.maze)

    print("Archivo:", maze_file)
    print("Inicio:", start)
    print("Meta:", goal)
    print("Nodos del grafo:", len(graph))

    if start is None:
        print("ERROR: No se encontró el punto inicial S.")
        return

    if goal is None:
        print("ERROR: No se encontró una salida en el borde del laberinto.")
        return

    # BFS
    initial_time = time.time()
    bfs_path, bfs_explored = bfs(graph, start, goal)
    bfs_time = time.time() - initial_time

    # DFS
    initial_time = time.time()
    dfs_path, dfs_explored = dfs(graph, start, goal)
    dfs_time = time.time() - initial_time

    print("\n--- RESULTADOS BFS ---")
    print("Encontró solución:", len(bfs_path) > 0)
    print("Longitud del camino:", len(bfs_path))
    print("Nodos explorados:", bfs_explored)
    print("Tiempo:", round(bfs_time, 6), "segundos")

    print("\n--- RESULTADOS DFS ---")
    print("Encontró solución:", len(dfs_path) > 0)
    print("Longitud del camino:", len(dfs_path))
    print("Nodos explorados:", dfs_explored)
    print("Tiempo:", round(dfs_time, 6), "segundos")

    images_path = os.path.join(os.getcwd(), "Taller2", "images")
    os.makedirs(images_path, exist_ok=True)

    maze_name = maze_file.replace(".txt", "")

    bfs_image = os.path.join(images_path, f"{maze_name}_bfs.png")
    dfs_image = os.path.join(images_path, f"{maze_name}_dfs.png")

    plot_solution(
        maze.maze,
        bfs_path,
        f"BFS - {maze_name}",
        bfs_image
    )

    plot_solution(
        maze.maze,
        dfs_path,
        f"DFS - {maze_name}",
        dfs_image
    )

    print("\nImágenes guardadas:")
    print(bfs_image)
    print(dfs_image)


def study_case_1():
    solve_maze("laberinto1.txt", "Caso de estudio 1")


def study_case_2():
    solve_maze("laberinto2.txt", "Caso de estudio 2")


def study_case_3():
    solve_maze("laberinto3.txt", "Caso de estudio 3")


def study_case_4():
    solve_maze("laberinto4.txt", "Caso de estudio 4")


if __name__ == "__main__":
    study_case_1()
    study_case_2()
    study_case_3()
    study_case_4()