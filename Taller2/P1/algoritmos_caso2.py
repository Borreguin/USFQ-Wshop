"""
Algoritmos de Búsqueda para Resolución de Laberintos
=====================================================

Este módulo contiene implementaciones de los principales algoritmos de búsqueda
utilizados para resolver laberintos:

1. DFS (Depth First Search) - búsqueda en profundidad
2. A* (A-Estrella) - búsqueda heurística

"""

from collections import deque
import heapq
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import copy
from P1_util import define_color

def dfs(graph, start, end):
    """    
    Argumentos:
        graph (dict): grafo de adyacencias {nodo: [(vecino, costo), ...]}
        start (tuple): nodo inicial (x, y)
        end (tuple): nodo objetivo (x, y)
    
    Retorna:    
        tuple: (camino, nodos_explorados)
               camino: lista de nodos desde start hasta end
               nodos_explorados: número de nodos visitados

    """
    stack = [(start, [start])]
    visited = set()
    nodes_explored = 0
    explored_list = [] 
    while stack:
        node, path = stack.pop()
        nodes_explored += 1
        
        if node in visited:
            continue
            
        visited.add(node)
        explored_list.append(node)
        if node == end:
            return path, nodes_explored, explored_list
        
        # Agregar vecinos al stack en orden inverso para mantener orden
        if node in graph:
            for neighbor, _ in graph[node]:
                if neighbor not in visited:
                    stack.append((neighbor, path + [neighbor]))
    
    # No se encontró camino
    return None, nodes_explored, explored_list



def a_star(graph, start, end):
    def heuristic(node, end):

        return abs(node[0] - end[0]) + abs(node[1] - end[1])
    
    # Heap: (f_n, contador, nodo, camino, g_n)
    # contador evita comparar nodos cuando f_score es igual
    counter = 0
    heap = [(heuristic(start, end), counter, start, [start], 0)]
    visited = set()
    nodes_explored = 0
    explored_list = [] 
    while heap:
        f_n, _, node, path, g_n = heapq.heappop(heap)
        nodes_explored += 1
        
        if node in visited:
            continue
        
        visited.add(node)
        explored_list.append(node)
        if node == end:
            return path, nodes_explored, explored_list
        
        # Explorar vecinos
        if node in graph:
            for neighbor, cost in graph[node]:
                if neighbor not in visited:
                    new_g = g_n + cost
                    new_h = heuristic(neighbor,end)
                    new_f = new_g + new_h
                    
                    counter += 1
                    heapq.heappush(heap, (new_f, counter, neighbor, path + [neighbor], new_g))
    
    # No se encontró camino
    return None, nodes_explored, explored_list

def plot_comparison(maze, dfs_data, astar_data, title_prefix="Laberinto"):
    """    
    Argumentos:
        maze: Laberinto (matriz 2D)
        dfs_data: tupla (path, nodes_explored, explored_list) de DFS
        astar_data: tupla (path, nodes_explored, explored_list) de A*
        title_prefix: Prefijo para los títulos
    """
    
    height = len(maze)
    width = len(maze[0])
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(width/2, height/4))
    
    def draw_maze(ax, explored_nodes, solution_path, title):
        maze_visual = copy.deepcopy(maze)
        
        if explored_nodes:
            for x, y in explored_nodes:
                if maze_visual[y][x] not in ['E', 'S']:
                    maze_visual[y][x] = 'X'
        
        if solution_path:
        
            for x, y in solution_path:
                if maze_visual[y][x] not in ['E', 'S']:
                    maze_visual[y][x] = 'P'
        
        
        for y in range(height):
            for x in range(width):
                cell = maze_visual[y][x]
                color = define_color(cell)
                ax.fill([x, x+1, x+1, x], [y, y, y+1, y+1], color=color, edgecolor='black')
        
        ax.set_xlim(0, width)
        ax.set_ylim(0, height)
        ax.invert_yaxis()
        ax.set_title(title, fontsize=10, fontweight='bold')
        ax.set_xticks([])
        ax.set_yticks([])
    
  
    dfs_path, dfs_nodes, dfs_explored = dfs_data
    draw_maze(ax1, dfs_explored, dfs_path, f"{title_prefix} - DFS")
    

    astar_path, astar_nodes, astar_explored = astar_data
    draw_maze(ax2, astar_explored, astar_path, f"{title_prefix} - A*")
    
 
    legend_elements = [
        Patch(facecolor='green', edgecolor='black', label='Inicio (E)'),
        Patch(facecolor='red', edgecolor='black', label='Meta (S)'),
        Patch(facecolor='lightblue', edgecolor='black', label='Explorados'),
        Patch(facecolor='yellow', edgecolor='black', label='Solución'),
        Patch(facecolor='black', edgecolor='black', label='Pared')
    ]
    fig.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, 0.05), ncol=5)
    
    plt.tight_layout(rect=[0, 0.05, 1, 1])
    plt.show()