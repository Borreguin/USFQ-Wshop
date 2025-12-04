import heapq
import math

def heuristic(a, b):
    """
    Calcula la Distancia Manhattan entre dos nodos (a y b).
    Se utiliza como la heurística h(n) para A*.
    """
    # a y b son tuplas (y, x)
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def solve_maze_astar(graph, start_node, end_node):
    """
    Resuelve el laberinto usando el algoritmo de búsqueda A*.
    
    :param graph: Diccionario de adyacencia del laberinto.
    :param start_node: Tupla (y, x) del inicio ('E').
    :param end_node: Tupla (y, x) del final ('S').
    :return: Una lista de tuplas [(y1, x1), (y2, x2), ...] representando el camino
             o None si no se encuentra un camino.
    """
  
    # Priority Queue (Cola de Prioridad): Almacena (f_score, nodo)
    # heapq mantiene el elemento con el f_score más bajo en la parte superior.
    # El f_score es g_score + h_score.
    open_list = [(0 + heuristic(start_node, end_node), start_node)] # (f_score, nodo)
    
    # g_score: Costo del camino desde el inicio hasta el nodo actual.
    # Inicialmente, infinito para todos, 0 para el inicio.
    g_score = {node: float('inf') for node in graph}
    g_score[start_node] = 0
    
    # came_from: Diccionario para reconstruir el camino.
    # Almacena el nodo inmediatamente anterior en el camino óptimo.
    came_from = {}
    
    # 2. Búsqueda
    while open_list:
        # Extrae el nodo con el menor f_score
        f_score, current_node = heapq.heappop(open_list)
        
        # Si hemos llegado a la meta
        if current_node == end_node:
            return reconstruct_path(came_from, end_node)

        # Iterar sobre los vecinos del nodo actual
        for neighbor in graph[current_node]:
            # El costo para ir de current_node a neighbor es 1 (un paso)
            tentative_g_score = g_score[current_node] + 1 
            
            # Si encontramos un camino mejor
            if tentative_g_score < g_score[neighbor]:
                # Este camino al vecino es mejor, lo registramos.
                came_from[neighbor] = current_node
                g_score[neighbor] = tentative_g_score
                h_score = heuristic(neighbor, end_node)
                f_score_new = tentative_g_score + h_score
                
                # Añadir o actualizar el vecino en la cola de prioridad
                # Nota: No es necesario comprobar si ya está en la open_list, 
                # simplemente añadimos la nueva entrada (f_score_new, neighbor).
                # Cuando se procese, la entrada con menor f_score prevalecerá.
                heapq.heappush(open_list, (f_score_new, neighbor))
                
    # Si el bucle termina, no se encontró un camino
    return None

def reconstruct_path(came_from, current):
    """
    Reconstruye el camino desde el nodo final hasta el inicio.
    """
    total_path = [current]
    while current in came_from:
        current = came_from[current]
        total_path.append(current)
    # El camino se reconstruye desde el final al inicio, por lo que lo invertimos.
    return total_path[::-1]

from collections import deque # deque para la cola

def solve_maze_bfs(graph, start_node, end_node):
    """
    Resuelve el laberinto usando el algoritmo de Búsqueda en Amplitud (BFS).
    Garantiza el camino más corto en grafos no ponderados.
    
    :param graph: Diccionario de adyacencia del laberinto.
    :param start_node: Tupla (y, x) del inicio ('E').
    :param end_node: Tupla (y, x) del final ('S').
    :return: Una lista de tuplas [(y1, x1), ...] representando el camino
             o None si no se encuentra un camino.
    """
    # Usamos deque (cola doble) como cola FIFO (First-In, First-Out)
    queue = deque([start_node]) 
    
    # Diccionario para rastrear el camino (nodo anterior)
    came_from = {start_node: None}
    
    while queue:
        current_node = queue.popleft() # Saca el primer elemento de la cola
        
        if current_node == end_node:
            # Reconstruir y devolver el camino
            return reconstruct_path(came_from, end_node)

        # Iterar sobre los vecinos
        for neighbor in graph[current_node]:
            # Si el vecino no ha sido visitado
            if neighbor not in came_from:
                came_from[neighbor] = current_node
                queue.append(neighbor) # Añade el vecino al final de la cola
                
    # Si la cola se vacía y no se encontró la meta
    return None