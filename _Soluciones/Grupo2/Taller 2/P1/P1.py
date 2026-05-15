import os, sys
project_path = os.path.dirname(__file__)
sys.path.append(project_path)
from P1_MazeLoader import MazeLoader
from P1_solvers import compare


def run_case(label, filename):
    print(f"\n{'='*50}")
    print(f"  {label}  —  {filename}")
    print('='*50)
    maze  = MazeLoader(filename).load_Maze().plot_maze()
    graph = maze.get_graph()
    print(f"  Nodos transitables: {len(graph)}")

    results = compare(graph)

    # Muestra la solución de cada algoritmo sobre el laberinto
    for algo, r in results.items():
        maze.plot_solution(r['path'], title=f"{algo}  |  camino={len(r['path'])}  explorados={r['explored']}")


def study_case_1():
    run_case('Study case 1', 'laberinto1.txt')

def study_case_2():
    run_case('Study case 2', 'laberinto2.txt')

def study_case_3():
    run_case('Study case 3', 'laberinto3.txt')

def study_case_4():
    run_case('Study case 4', 'laberinto4.txt')


if __name__ == '__main__':
    study_case_1()
    study_case_2()
    study_case_3()
    study_case_4()
