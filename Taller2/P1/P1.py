import os, sys
project_path = os.path.dirname(__file__)
sys.path.append(project_path)
from P1_MazeLoader import MazeLoader
from P1_util import bfs, dfs, plot_path_over_maze
from matplotlib import pyplot as plt

def study_case_1():
    print("Study Case 1")

    maze_file = 'laberinto1.txt'
    maze_obj = MazeLoader(maze_file).load_Maze().plot_maze()
    graph = maze_obj.get_graph()

    # Encontrar inicio (E) y salida (S)
    start = None
    goal = None
    maze = maze_obj.maze

    for y in range(len(maze)):
        for x in range(len(maze[0])):
            if maze[y][x] == 'E':
                start = (x, y)
            elif maze[y][x] == 'S':
                goal = (x, y)

    print("Inicio:", start)
    print("Salida:", goal)

    # BFS
    path_bfs = bfs(graph, start, goal)
    print("BFS Path length:", len(path_bfs))

    # DFS
    path_dfs = dfs(graph, start, goal)
    print("DFS Path length:", len(path_dfs))

    print("\n--- Visualización BFS ---")
    plot_path_over_maze(maze, path_bfs)

    print("\n--- Visualización DFS ---")
    plot_path_over_maze(maze, path_dfs)



def study_case_2():
    print("This is study case 2")
    maze_file = 'laberinto2.txt'
    maze_obj = MazeLoader(maze_file).load_Maze().plot_maze()

    graph = maze_obj.get_graph()

    # Encontrar inicio (E) y salida (S)
    start = None
    goal = None
    maze = maze_obj.maze

    for y in range(len(maze)):
        for x in range(len(maze[0])):
            if maze[y][x] == 'E':
                start = (x, y)
            elif maze[y][x] == 'S':
                goal = (x, y)

    print("Inicio:", start)
    print("Salida:", goal)

    # BFS
    path_bfs = bfs(graph, start, goal)
    print("BFS Path length:", len(path_bfs))

    # DFS
    path_dfs = dfs(graph, start, goal)
    print("DFS Path length:", len(path_dfs))

    print("\n--- Visualización BFS ---")
    plot_path_over_maze(maze, path_bfs)

    print("\n--- Visualización DFS ---")
    plot_path_over_maze(maze, path_dfs)


def study_case_3():
    print("Study Case 3")

    maze_file = 'laberinto3.txt'
    maze_obj = MazeLoader(maze_file).load_Maze().plot_maze()
    graph = maze_obj.get_graph()

    # Encontrar inicio (E) y salida (S)
    start = None
    goal = None
    maze = maze_obj.maze

    for y in range(len(maze)):
        for x in range(len(maze[0])):
            if maze[y][x] == 'E':
                start = (x, y)
            elif maze[y][x] == 'S':
                goal = (x, y)

    print("Inicio:", start)
    print("Salida:", goal)

    # BFS
    path_bfs = bfs(graph, start, goal)
    print("BFS Path length:", len(path_bfs))

    # DFS
    path_dfs = dfs(graph, start, goal)
    print("DFS Path length:", len(path_dfs))

    print("\n--- Visualización BFS ---")
    plot_path_over_maze(maze, path_bfs)

    print("\n--- Visualización DFS ---")
    plot_path_over_maze(maze, path_dfs)



if __name__ == '__main__':
    study_case_1()
    study_case_2()
    study_case_3()
