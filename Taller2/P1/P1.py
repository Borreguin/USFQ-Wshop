import os, sys
import matplotlib.pyplot as plt
project_path = os.path.dirname(__file__)
sys.path.append(project_path)
from P1_MazeLoader import MazeLoader
from P1_Solver import solve_maze_astar, solve_maze_bfs
import time


def plot_solution(path, fig, ax, algorithm_name, show=True):
    """
    Añade la ruta de solución al laberinto graficado usando la figura y ejes dados, y luego muestra la única figura.

    Args:
        path: Lista de tuplas (y, x) representando el camino
        fig: Figura de matplotlib
        ax: Ejes de matplotlib
        algorithm_name: Nombre del algoritmo para la leyenda
        show: Si True, muestra la figura. Si False, solo dibuja sin mostrar.
    """
    # Excluir inicio y fin para que 'E' y 'S' sigan siendo verdes y rojos
    solution_points = path[1:-1]

    styles = {
        'A*': ('blue', '*', 15),
        'BFS': ('orange', 'o', 4),
    }
    color, marker, size = styles.get(algorithm_name, ('cyan', 'd', 6))

    # Graficar los puntos de la solución en los ejes 'ax' que recibimos
    if solution_points:
        y_coords = [y + 0.5 for y, x in solution_points]
        x_coords = [x + 0.5 for y, x in solution_points]

        ax.plot(x_coords, y_coords,
                marker=marker,
                linestyle='',
                color=color,
                markersize=size,
                alpha=0.8,
                label=f'{algorithm_name} (Pasos: {len(path) - 1})') # Añadir etiqueta

    ax.legend(loc='lower right')
    fig.tight_layout()
    if show:
        plt.show()


def run_solver(solver_func, graph, start_node, end_node):
    """Ejecuta un algoritmo de búsqueda y mide el tiempo."""
    start_time = time.time()
    path = solver_func(graph, start_node, end_node)
    end_time = time.time()

    runtime = (end_time - start_time) * 1000 # Tiempo en milisegundos
    steps = len(path) - 1 if path else 0
    return path, runtime, steps


def study_case_1():
    print("This is study case 1")
    maze_file = 'laberinto1.txt'
    maze = MazeLoader(maze_file).load_Maze()

    # 1. Obtener el grafo, inicio y fin
    graph, start_node, end_node = maze.get_graph()

    # 2. Aplicar el algoritmo A*
    path = solve_maze_astar(graph, start_node, end_node)

    # 3. Graficar laberinto y solución
    _, fig, ax = maze.plot_maze() # Esto mostrará el laberinto.

    if path:
        print(f"¡Solución encontrada! Pasos: {len(path) - 1}")
        # Llama a la función auxiliar para dibujar el camino en el plot existente
        plot_solution(path, fig, ax, algorithm_name='A*')
    else:
        print(" No se encontró una solución para el laberinto.")


def study_case_2():
    print("This is study case 2")
    maze_file = 'laberinto2.txt'

    maze = MazeLoader(maze_file).load_Maze()
    graph, start_node, end_node = maze.get_graph()
    path = solve_maze_astar(graph, start_node, end_node)
    _, fig, ax = maze.plot_maze()

    if path:
        print(f" ¡Solución encontrada! Pasos: {len(path) - 1}")
        plot_solution(path, fig, ax, algorithm_name='A*')
    else:
        print(" No se encontró una solución para el laberinto.")


def study_case_3():
    print("This is study case 3")
    maze_file = 'laberinto3.txt'

    maze = MazeLoader(maze_file).load_Maze()
    graph, start_node, end_node = maze.get_graph()
    path = solve_maze_astar(graph, start_node, end_node)
    _, fig, ax = maze.plot_maze()

    if path:
        print(f" ¡Solución encontrada! Pasos: {len(path) - 1}")
        plot_solution(path, fig, ax, algorithm_name='A*')
    else:
        print(" No se encontró una solución para el laberinto.")


def study_case_comparison(maze_file):
    print(" Caso de Estudio de Comparación (A* vs. BFS) ")
    maze = MazeLoader(maze_file).load_Maze()
    graph, start_node, end_node = maze.get_graph()

    # 1. Ejecutar y medir A*
    path_a_star, time_a_star, steps_a_star = run_solver(solve_maze_astar, graph, start_node, end_node)

    # 2. Ejecutar y medir BFS
    path_bfs, time_bfs, steps_bfs = run_solver(solve_maze_bfs, graph, start_node, end_node)

    print("\n--- Resultados de la Evaluación ---")
    print(f"| Algoritmo | Tiempo (ms) | Pasos |")
    print(f"|-----------|-------------|-------|")
    print(f"| A*        | {time_a_star:.2f}        | {steps_a_star}    |")
    print(f"| BFS       | {time_bfs:.2f}        | {steps_bfs}    |")
    print("------------------------------------")

    # 4. Graficar la solución de A* y BFS
    maze, fig, ax = maze.plot_maze()
    if path_a_star:
        plot_solution(path_bfs, fig, ax, algorithm_name='A*', show=False) # No lo muestra

    if path_bfs:
        plot_solution(path_a_star, fig, ax, algorithm_name='BFS', show=True) # Muestra las 2 soluciones


def compare_every_case():
    files = ['laberinto1.txt', 'laberinto2.txt', 'laberinto3.txt']
    for maze_file in files:
        study_case_comparison(maze_file)


if __name__ == '__main__':
    # study_case_3()
    compare_every_case()
