import os, sys
project_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_path)

from P1_MazeLoader import MazeLoader
from P1_solvers import bfs, dfs, a_star

IMAGES_DIR = os.path.join(project_path, '..', 'images')


def run_maze(maze_file, maze_name):
    print(f"\n{'='*60}")
    print(f"  {maze_name}  ({maze_file})")
    print('='*60)

    loader = MazeLoader(maze_file)
    loader.load_Maze()
    graph = loader.get_graph()
    start, end = loader.find_start_end()

    print(f"  Nodos en el grafo : {len(graph)}")
    print(f"  Inicio (E)        : {start}")
    print(f"  Salida (S)        : {end}")

    algorithms = [
        ('BFS',  bfs),
        ('A*',   a_star),
        ('DFS',  dfs),
    ]

    solutions = []
    print(f"\n  {'Algoritmo':<8} {'Pasos':>7} {'Nodos exp.':>12} {'Tiempo (ms)':>13}")
    print(f"  {'-'*8} {'-'*7} {'-'*12} {'-'*13}")

    for name, algo in algorithms:
        path, nodes_visited, elapsed = algo(graph, start, end)
        steps = len(path) - 1 if path else -1
        print(f"  {name:<8} {steps:>7} {nodes_visited:>12} {elapsed*1000:>13.3f}")
        solutions.append((name, path, nodes_visited, elapsed))

    save_path = os.path.join(IMAGES_DIR, f'{maze_file[:-4]}_comparacion.png')
    loader.plot_comparison(solutions, maze_name, save_path=save_path)
    return solutions


def study_case_1():
    return run_maze('laberinto1.txt', 'Laberinto 1 (pequeño)')


def study_case_2():
    return run_maze('laberinto2.txt', 'Laberinto 2 (mediano)')


def study_case_3():
    return run_maze('laberinto3.txt', 'Laberinto 3 (grande)')


def study_case_4():
    return run_maze('laberinto4.txt', 'Laberinto 4 (grande extendido)')


if __name__ == '__main__':
    study_case_1()
    study_case_2()
    study_case_3()
    study_case_4()
    print("\nListo. Imágenes guardadas en Taller2/images/")