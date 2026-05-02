import os, sys
project_path = os.path.dirname(__file__)
sys.path.append(project_path)
from P1_MazeLoader import MazeLoader


def solve_study_case(maze_file):
    maze = MazeLoader(maze_file).load_Maze().plot_maze()
    graph = maze.get_graph()

    print("Grafo del laberinto")
    maze.plot_graph(graph)

    print("Arbol BFS")
    maze.plot_graph_as_tree(graph)

    print("Arbol Nayfeth")
    maze.plot_graph_as_dfs_tree(graph)

    print("Solucion BFS")
    maze.solve_bfs(graph)

    print("Solucion Nayfeth")
    maze.solve_nayfeth(graph)

    print("Solucion A*")
    maze.solve_astar(graph)


def study_case_1():
    print("This is study case 1")
    solve_study_case('laberinto1.txt')


def study_case_2():
    print("This is study case 2")
    solve_study_case('laberinto2.txt')


def study_case_3():
    print("This is study case 3")
    solve_study_case('laberinto3.txt')


if __name__ == '__main__':
    study_case_2()
