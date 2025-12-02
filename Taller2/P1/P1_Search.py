from collections import deque
import heapq
import time


def find_start_goal(maze):
    """
    maze: matriz de chars (lista de listas)
    retorna: start (x,y), goal (x,y)
    """
    start = goal = None
    for y, row in enumerate(maze):
        for x, cell in enumerate(row):
            if cell == 'E':
                start = (x, y)
            elif cell == 'S':
                goal = (x, y)
    if start is None or goal is None:
        raise ValueError("No se encontró 'E' (entrada) o 'S' (salida) en el laberinto.")
    return start, goal


def reconstruct_path(parent, start, goal):
    """
    parent: dict {node: prev_node}
    retorna lista de nodos desde start a goal (incluye ambos) o [] si no hay ruta
    """
    if goal not in parent and goal != start:
        return []

    path = []
    cur = goal
    while cur != start:
        path.append(cur)
        cur = parent[cur]
    path.append(start)
    path.reverse()
    return path


def dfs(graph, start, goal):
    """
    DFS (profundidad)
    """
    t0 = time.perf_counter()

    stack = [start]
    visited = set([start])
    parent = {}

    while stack:
        node = stack.pop()
        if node == goal:
            break

        for nb in graph.get(node, []):
            if nb not in visited:
                visited.add(nb)
                parent[nb] = node
                stack.append(nb)

    path = reconstruct_path(parent, start, goal)
    t1 = time.perf_counter()

    return {
        "algo": "DFS",
        "found": len(path) > 0,
        "path": path,
        "path_len": max(0, len(path) - 1),
        "visited": len(visited),
        "time_ms": (t1 - t0) * 1000.0,
        "cost": None  # DFS no optimiza costo
    }


def bfs(graph, start, goal):
    """
    BFS (anchura) 
    """
    t0 = time.perf_counter()

    q = deque([start])
    visited = set([start])
    parent = {}

    while q:
        node = q.popleft()
        if node == goal:
            break

        for nb in graph.get(node, []):
            if nb not in visited:
                visited.add(nb)
                parent[nb] = node
                q.append(nb)

    path = reconstruct_path(parent, start, goal)
    t1 = time.perf_counter()

    return {
        "algo": "BFS",
        "found": len(path) > 0,
        "path": path,
        "path_len": max(0, len(path) - 1),
        "visited": len(visited),
        "time_ms": (t1 - t0) * 1000.0,
        "cost": max(0, len(path) - 1) if path else None
    }


def dijkstra(graph, start, goal, weight_fn=None):
    """
    Dijkstra 
    """
    if weight_fn is None:
        weight_fn = lambda u, v: 1

    t0 = time.perf_counter()

    dist = {start: 0}
    parent = {}
    visited = set()
    pq = [(0, start)]  # (dist, node)

    while pq:
        d, node = heapq.heappop(pq)
        if node in visited:
            continue
        visited.add(node)

        if node == goal:
            break

        for nb in graph.get(node, []):
            nd = d + weight_fn(node, nb)
            if nb not in dist or nd < dist[nb]:
                dist[nb] = nd
                parent[nb] = node
                heapq.heappush(pq, (nd, nb))

    path = reconstruct_path(parent, start, goal)
    t1 = time.perf_counter()

    return {
        "algo": "Dijkstra",
        "found": len(path) > 0,
        "path": path,
        "path_len": max(0, len(path) - 1),
        "visited": len(visited),
        "time_ms": (t1 - t0) * 1000.0,
        "cost": dist.get(goal, None)
    }


def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def astar(graph, start, goal, heuristic=None, weight_fn=None):
    """
    A* 
    """
    if heuristic is None:
        heuristic = manhattan
    if weight_fn is None:
        weight_fn = lambda u, v: 1

    t0 = time.perf_counter()

    g = {start: 0}  # costo real
    parent = {}
    visited = set()

    pq = [(heuristic(start, goal), 0, start)]  # (f, g, node)

    while pq:
        f, gcur, node = heapq.heappop(pq)
        if node in visited:
            continue
        visited.add(node)

        if node == goal:
            break

        for nb in graph.get(node, []):
            ng = gcur + weight_fn(node, nb)
            if nb not in g or ng < g[nb]:
                g[nb] = ng
                parent[nb] = node
                nf = ng + heuristic(nb, goal)
                heapq.heappush(pq, (nf, ng, nb))

    path = reconstruct_path(parent, start, goal)
    t1 = time.perf_counter()

    return {
        "algo": "A*",
        "found": len(path) > 0,
        "path": path,
        "path_len": max(0, len(path) - 1),
        "visited": len(visited),
        "time_ms": (t1 - t0) * 1000.0,
        "cost": g.get(goal, None)
    }
