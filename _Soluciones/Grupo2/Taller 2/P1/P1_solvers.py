import time
import heapq
from collections import deque


def _find_endpoints(graph):
    start = next(n for n, d in graph.items() if d['type'] == 'E')
    goal  = next(n for n, d in graph.items() if d['type'] == 'S')
    return start, goal


def _reconstruct_path(parents, goal):
    path, node = [], goal
    while node is not None:
        path.append(node)
        node = parents[node]
    path.reverse()
    return path


def bfs(graph):
    start, goal = _find_endpoints(graph)
    queue        = deque([start])
    visited      = {start}
    parents      = {start: None}
    explored     = 0
    max_frontier = 1

    t0 = time.perf_counter()
    while queue:
        max_frontier = max(max_frontier, len(queue))
        node = queue.popleft()
        explored += 1
        if node == goal:
            break
        for nb in graph[node]['neighbors']:
            if nb not in visited:
                visited.add(nb)
                parents[nb] = node
                queue.append(nb)
    elapsed = (time.perf_counter() - t0) * 1000

    return {
        'path':         _reconstruct_path(parents, goal),
        'explored':     explored,
        'time_ms':      round(elapsed, 4),
        'max_frontier': max_frontier,
    }


def dfs(graph):
    start, goal = _find_endpoints(graph)
    stack        = [start]
    visited      = {start}
    parents      = {start: None}
    explored     = 0
    max_frontier = 1

    t0 = time.perf_counter()
    while stack:
        max_frontier = max(max_frontier, len(stack))
        node = stack.pop()
        explored += 1
        if node == goal:
            break
        for nb in graph[node]['neighbors']:
            if nb not in visited:
                visited.add(nb)
                parents[nb] = node
                stack.append(nb)
    elapsed = (time.perf_counter() - t0) * 1000

    return {
        'path':         _reconstruct_path(parents, goal),
        'explored':     explored,
        'time_ms':      round(elapsed, 4),
        'max_frontier': max_frontier,
    }


def _manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def astar(graph):
    start, goal = _find_endpoints(graph)
    # heap entries: (f, g, node)
    heap         = [((_manhattan(start, goal)), 0, start)]
    visited      = set()
    parents      = {start: None}
    g_cost       = {start: 0}
    explored     = 0
    max_frontier = 1

    t0 = time.perf_counter()
    while heap:
        max_frontier = max(max_frontier, len(heap))
        f, g, node = heapq.heappop(heap)
        if node in visited:
            continue
        visited.add(node)
        explored += 1
        if node == goal:
            break
        for nb in graph[node]['neighbors']:
            new_g = g + 1
            if nb not in g_cost or new_g < g_cost[nb]:
                g_cost[nb]  = new_g
                parents[nb] = node
                heapq.heappush(heap, (new_g + _manhattan(nb, goal), new_g, nb))
    elapsed = (time.perf_counter() - t0) * 1000

    return {
        'path':         _reconstruct_path(parents, goal),
        'explored':     explored,
        'time_ms':      round(elapsed, 4),
        'max_frontier': max_frontier,
    }


def compare(graph):
    algorithms = [('BFS', bfs), ('DFS', dfs), ('A*', astar)]
    results = {}
    for name, fn in algorithms:
        results[name] = fn(graph)

    print(f"\n{'Algoritmo':<12} {'Camino':>8} {'Explorados':>12} {'Tiempo(ms)':>12} {'Frontera máx':>14}")
    print("-" * 62)
    for name, r in results.items():
        print(f"{name:<12} {len(r['path']):>8} {r['explored']:>12} {r['time_ms']:>12.4f} {r['max_frontier']:>14}")
    print()

    return results
