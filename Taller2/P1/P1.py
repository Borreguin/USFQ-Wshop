import os, sys,time
project_path = os.path.dirname(__file__)
sys.path.append(project_path)
from P1_MazeLoader import MazeLoader
from algoritmos_caso2 import dfs, a_star, plot_comparison
import pandas as pd
def study_case_1():
    print("This is study case 1")
    maze_file = 'laberinto1.txt'
    maze = MazeLoader(maze_file).load_Maze()
    # Aquí la implementación de la solución:
    graph = maze.get_graph()

def study_case_2():
   
    
    print("This is study case 2")
    print(f"Laberinto cargado")
    maze_file = 'laberinto2.txt'
    maze_loader = MazeLoader(maze_file).load_Maze()
    graph, start, end = maze_loader.get_graph()
    
    total_nodos = len(graph)
    
    print("\n" + "─" * 70)
    print(" COMPARACIÓN DFS vs A*")
    print("─" * 70)
    print(f"Nodos transitables: {total_nodos}")
    print(f"Inicio: {start}")
    print(f"Meta: {end}")
 
   
    tiempo_inicio = time.time()
    path_dfs, nodos_dfs, explorados_dfs = dfs(graph, start, end)
    tiempo_dfs = (time.time() - tiempo_inicio) * 1000
    
  
    tiempo_inicio = time.time()
    path_astar, nodos_astar, explorados_astar = a_star(graph, start, end)
    tiempo_astar = (time.time() - tiempo_inicio) * 1000
    
   
    if path_dfs and path_astar:
    
        eficiencia_dfs = 100 - (len(path_dfs) / total_nodos) * 100
        eficiencia_astar = 100 - (len(path_astar) / total_nodos) * 100
     
      
        tasa_exp_dfs = (nodos_dfs / total_nodos) * 100
        tasa_exp_astar = (nodos_astar / total_nodos) * 100
        
  
        factor_dfs = nodos_dfs / len(path_dfs)
        factor_astar = nodos_astar / len(path_astar)
        
        datos = {
            'Algoritmo': ['DFS', 'A*'],
            'Tiempo (ms)': [f"{tiempo_dfs:.4f}", f"{tiempo_astar:.4f}"],
            'Nodos Explorados': [nodos_dfs, nodos_astar],
            'Longitud Camino': [len(path_dfs), len(path_astar)],
            'Eficiencia Camino (%)': [f"{eficiencia_dfs:.2f}", f"{eficiencia_astar:.2f}"],
            'Tasa Exploración (%)': [f"{tasa_exp_dfs:.2f}", f"{tasa_exp_astar:.2f}"],
            'Factor Exploración': [f"{factor_dfs:.2f}", f"{factor_astar:.2f}"],
       
        }
        
        df = pd.DataFrame(datos)
        
        print(df)

        print("\n Generando visualización comparativa")
        dfs_data = (path_dfs, nodos_dfs, explorados_dfs)
        astar_data = (path_astar, nodos_astar, explorados_astar)
        plot_comparison(maze_loader.maze, dfs_data, astar_data, title_prefix="Laberinto 2")
    else:
        print("\nNo se pudieron comparar los algoritmos (uno o ambos no encontraron camino)")
    
    print("\n" + "─" * 70)


def study_case_3():
    print("This is study case 3")
    maze_file = 'laberinto3.txt'
    maze = MazeLoader(maze_file).load_Maze()
    # Aquí la implementación de la solución:
    graph = maze.get_graph()

def mostrar_menu():
    print("\n" + "═" * 50)
    print("  SELECTOR DE LABERINTOS")
    print("═" * 50)
    print("1. Laberinto 1 (laberinto1.txt)")
    print("2. Laberinto 2 (laberinto2.txt)")
    print("3. Laberinto 3 (laberinto3.txt)")
    print("0. Salir")
    print("═" * 50)

def ejecutar_menu():

    while True:
        mostrar_menu()
        try:
            opcion = input("\nSeleccione el laberinto que desea resolver (0-3): ").strip()
            
            if opcion == '0':
                print("\nSaliendo")
                break
            elif opcion == '1':
                study_case_1()
            elif opcion == '2':
                study_case_2()
            elif opcion == '3':
                study_case_3()
            else:
                print("\nOpción inválida. Por favor, seleccione un número entre 0 y 3.")
                continue
                
            # Preguntar si desea continuar
            continuar = input("\n¿Desea resolver otro laberinto? (s/n): ").strip().lower()
            if continuar != 's' and continuar != 'si':
                print("\nSaliendo...")
                break
                
        except KeyboardInterrupt:
            print("\n\nSaliendo...")
            break
        except Exception as e:  
            print(f"\n Error: {e}")
            break

if __name__ == '__main__':
    ejecutar_menu()
