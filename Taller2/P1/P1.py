import os, sys
import matplotlib.pyplot as plt
project_path = os.path.dirname(__file__)
sys.path.append(project_path)
from P1_MazeLoader import MazeLoader
from P1_Solver import solve_maze_astar, solve_maze_bfs
import time


def plot_solution(path, fig, ax, algorithm_name='Solución'):
    """
    Añade la ruta de solución al laberinto graficado usando la figura y ejes dados,
    y luego muestra la única figura.
    """
    if path:
        # Excluir inicio y fin para que 'E' y 'S' sigan siendo verdes y rojos
        solution_points = path[1:-1]
        
        # Asigna color y marcador según el algoritmo
        color = 'blue' if algorithm_name == 'A*' else 'red'
        marker = '*' if algorithm_name == 'A*' else 'o'
        
        # Graficar los puntos de la solución en los ejes 'ax' que recibimos
        y_coords = [y + 0.5 for y, x in solution_points]
        x_coords = [x + 0.5 for y, x in solution_points]
        
        ax.plot(x_coords, y_coords, 
                marker=marker, 
                linestyle='', 
                color=color, 
                markersize=5,
                label=f'{algorithm_name} (Pasos: {len(path) - 1})') # Añadir etiqueta
    
    # Asegúrate de que solo se llame a plt.show() al final de la visualización
    ax.legend(loc='lower right') # Mostrar leyenda
    fig.tight_layout()
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
        # Llama a la función auxiliar para dibujar el camino en el plot existente
        plot_solution(path, fig, ax, algorithm_name='A*')
    else:
        print(" No se encontró una solución para el laberinto.")


def study_case_comparison():
    print(" Caso de Estudio de Comparación (A* vs. BFS) ")
    maze_file = 'laberinto1.txt' # Seleccion del laberinto
    maze = MazeLoader(maze_file).load_Maze()
    
    graph, start_node, end_node = maze.get_graph()
    
    # ----------------------------------------------------
    # 1. Ejecutar y medir A*
    # ----------------------------------------------------
    path_a_star, time_a_star, steps_a_star = run_solver(solve_maze_astar, graph, start_node, end_node)
    
    # ----------------------------------------------------
    # 2. Ejecutar y medir BFS
    # ----------------------------------------------------
    path_bfs, time_bfs, steps_bfs = run_solver(solve_maze_bfs, graph, start_node, end_node)
    
    # 3. Mostrar Resultados
    print("\n--- Resultados de la Evaluación ---")
    print(f"| Algoritmo | Tiempo (ms) | Pasos |")
    print(f"|-----------|-------------|-------|")
    print(f"| A*        | {time_a_star:.2f}        | {steps_a_star}    |")
    print(f"| BFS       | {time_bfs:.2f}        | {steps_bfs}    |")
    print("------------------------------------")
    
    # 4. Graficar la solución (usando A* para la visualización)
    maze, fig, ax = maze.plot_maze()
    
    # Dibuja la solución de A*
    plot_solution(path_a_star, fig, ax, algorithm_name='A*')
    
    # Si quieres, puedes modificar plot_solution para que dibuje AMBOS caminos
    # con diferentes marcadores/colores para ver la diferencia de la exploración.
    # plot_solution(path_bfs, fig, ax, algorithm_name='BFS')

if __name__ == '__main__':
    study_case_3()
    # study_case_comparison()
