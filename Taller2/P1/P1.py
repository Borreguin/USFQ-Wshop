import os, sys
import time # Para medir tiempo
project_path = os.path.dirname(__file__)
sys.path.append(project_path)

from P1_MazeLoader import MazeLoader
from P1_Algoritmos import bfs_search, dfs_search

def run_algorithm(name, algorithm_func, graph, start, end, loader, title_prefix):
    print(f"\n--- Ejecutando {name} ---")
    
    # 1. Medir Tiempo Inicial
    start_time = time.perf_counter() 
    
    # 2. Ejecutar Algoritmo
    path, visited_count = algorithm_func(graph, start, end)
    
    # 3. Medir Tiempo Final
    end_time = time.perf_counter()
    elapsed_time = (end_time - start_time) * 1000 # Convertir a milisegundos

    # 4. Reportar Métricas
    if path:
        path_length = len(path)
        print(f"✅ Solución encontrada:")
        print(f"   - Tiempo: {elapsed_time:.4f} ms")
        print(f"   - Pasos en solución (Costo): {path_length}")
        print(f"   - Nodos explorados (Esfuerzo): {visited_count}")
        
        loader.plot_maze(path=path, title=f"{title_prefix} - {name} (Largo: {path_length})")
    else:
        print("❌ No se encontró solución.")
        print(f"   - Nodos explorados: {visited_count}")

def study_case_1():
    print("=== ESTUDIO DE CASO 1 ===")
    maze_file = 'laberinto1.txt'
    loader = MazeLoader(maze_file)
    loader.load_Maze()
    graph, start, end = loader.get_graph()
    
    # Ejecutar BFS
    run_algorithm("BFS", bfs_search, graph, start, end, loader, "Caso 1")
    
    # Ejecutar DFS
    run_algorithm("DFS", dfs_search, graph, start, end, loader, "Caso 1")

def study_case_2():
    print("\n=== ESTUDIO DE CASO 2 ===")
    maze_file = 'laberinto2.txt'
    loader = MazeLoader(maze_file)
    loader.load_Maze()
    graph, start, end = loader.get_graph()
    
    run_algorithm("BFS", bfs_search, graph, start, end, loader, "Caso 2")
    run_algorithm("DFS", dfs_search, graph, start, end, loader, "Caso 2")

def study_case_3():
    print("\n=== ESTUDIO DE CASO 3 ===")
    maze_file = 'laberinto3.txt'
    loader = MazeLoader(maze_file)
    loader.load_Maze()
    graph, start, end = loader.get_graph()
    
    run_algorithm("BFS", bfs_search, graph, start, end, loader, "Caso 3")
    run_algorithm("DFS", dfs_search, graph, start, end, loader, "Caso 3")

if __name__ == '__main__':
    study_case_1()
    study_case_2()
    study_case_3()