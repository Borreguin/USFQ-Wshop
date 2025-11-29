import collections

def bfs_search(graph, start, goal):
    queue = collections.deque([start])
    visited = set([start])
    came_from = {start: None}
    nodes_visited = 0

    while queue:
        current = queue.popleft()
        nodes_visited += 1

        if current == goal:
            # Retornamos el camino Y la cantidad de nodos visitados
            return reconstruct_path(came_from, start, goal), nodes_visited

        for neighbor in graph[current]:
            if neighbor not in visited:
                visited.add(neighbor)
                came_from[neighbor] = current
                queue.append(neighbor)
    return None, nodes_visited # Retornar conteo aunque falle

def dfs_search(graph, start, goal):
    stack = [start]
    visited = set([start])
    came_from = {start: None}
    nodes_visited = 0

    while stack:
        current = stack.pop()
        nodes_visited += 1

        if current == goal:
            return reconstruct_path(came_from, start, goal), nodes_visited

        for neighbor in graph[current]:
            if neighbor not in visited:
                visited.add(neighbor)
                came_from[neighbor] = current
                stack.append(neighbor)
    return None, nodes_visited

def reconstruct_path(came_from, start, goal):
    current = goal
    path = []
    while current != start:
        path.append(current)
        current = came_from[current]
    path.append(start)
    path.reverse()
    return path