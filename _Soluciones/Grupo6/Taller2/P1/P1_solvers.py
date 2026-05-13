from collections import deque
import heapq
import time


def bfs(graph, start, end):
    """BFS - Breadth-First Search. Garantiza el camino más corto."""
    t0 = time.time()
    came_from = {start: None}
    queue = deque([start])
    nodes_visited = 0

    while queue:
        node = queue.popleft()
        nodes_visited += 1
        if node == end:
            break
        for neighbor in graph.get(node, []):
            if neighbor not in came_from:
                came_from[neighbor] = node
                queue.append(neighbor)

    elapsed = time.time() - t0
    if end not in came_from:
        return None, nodes_visited, elapsed
    return _reconstruct(came_from, end), nodes_visited, elapsed


def dfs(graph, start, end):
    """DFS - Depth-First Search. No garantiza el camino más corto."""
    t0 = time.time()
    came_from = {}
    stack = [(start, None)]
    nodes_visited = 0
    found = False

    while stack:
        node, parent = stack.pop()
        if node in came_from:
            continue
        came_from[node] = parent
        nodes_visited += 1
        if node == end:
            found = True
            break
        for neighbor in graph.get(node, []):
            if neighbor not in came_from:
                stack.append((neighbor, node))

    elapsed = time.time() - t0
    if not found:
        return None, nodes_visited, elapsed
    return _reconstruct(came_from, end), nodes_visited, elapsed


def a_star(graph, start, end):
    """A* con heurística de distancia Manhattan."""
    t0 = time.time()

    def h(node):
        return abs(node[0] - end[0]) + abs(node[1] - end[1])

    counter = 0
    open_set = [(h(start), 0, counter, start)]
    came_from = {start: None}
    g_score = {start: 0}
    closed = set()
    nodes_visited = 0

    while open_set:
        _, cost, _, node = heapq.heappop(open_set)
        if node in closed:
            continue
        closed.add(node)
        nodes_visited += 1
        if node == end:
            break
        for neighbor in graph.get(node, []):
            if neighbor in closed:
                continue
            new_cost = cost + 1
            if neighbor not in g_score or new_cost < g_score[neighbor]:
                g_score[neighbor] = new_cost
                came_from[neighbor] = node
                counter += 1
                heapq.heappush(open_set, (new_cost + h(neighbor), new_cost, counter, neighbor))

    elapsed = time.time() - t0
    if end not in closed:
        return None, nodes_visited, elapsed
    return _reconstruct(came_from, end), nodes_visited, elapsed


def _reconstruct(came_from, end):
    path = []
    node = end
    while node is not None:
        path.append(node)
        node = came_from[node]
    path.reverse()
    return path