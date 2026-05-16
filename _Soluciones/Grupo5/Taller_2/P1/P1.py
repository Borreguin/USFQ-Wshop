"""Parte 1 - Uso de algoritmos de búsqueda en laberintos.

Ejecuta BFS, DFS y A* sobre los laberintos .txt y guarda imágenes con las rutas.
Aunque el taller pide comparar al menos 2 algoritmos, se incluyen 3 para tener
una comparación más clara.
"""

import csv
import heapq
import os
import sys
import time
from collections import deque
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional, Set, Tuple

project_path = os.path.dirname(__file__)
sys.path.append(project_path)

from P1_MazeLoader import Graph, MazeLoader, Position


class SearchResult:
    def __init__(
        self,
        algorithm: str,
        path: Optional[List[Position]],
        visited_order: List[Position],
        expanded_nodes: int,
        max_frontier_size: int,
        elapsed_ms: float,
    ):
        self.algorithm = algorithm
        self.path = path or []
        self.visited_order = visited_order
        self.expanded_nodes = expanded_nodes
        self.max_frontier_size = max_frontier_size
        self.elapsed_ms = elapsed_ms

    @property
    def found(self) -> bool:
        return len(self.path) > 0

    @property
    def path_nodes(self) -> int:
        return len(self.path)

    @property
    def path_steps(self) -> int:
        return max(0, len(self.path) - 1)

    def to_row(self, maze_file: str, graph_nodes: int, graph_edges: int) -> Dict[str, object]:
        return {
            'maze': maze_file,
            'algorithm': self.algorithm,
            'found': self.found,
            'path_steps': self.path_steps if self.found else None,
            'path_nodes': self.path_nodes if self.found else None,
            'visited_nodes': len(self.visited_order),
            'expanded_nodes': self.expanded_nodes,
            'max_frontier_size': self.max_frontier_size,
            'time_ms': round(self.elapsed_ms, 4),
            'graph_nodes': graph_nodes,
            'graph_edges': graph_edges,
        }


def reconstruct_path(parent: Dict[Position, Optional[Position]], end: Position) -> List[Position]:
    path: List[Position] = []
    current: Optional[Position] = end
    while current is not None:
        path.append(current)
        current = parent[current]
    path.reverse()
    return path


def run_bfs(graph: Graph, start: Position, end: Position) -> SearchResult:
    """Búsqueda en anchura: garantiza ruta más corta en grafos no ponderados."""
    begin = time.perf_counter()
    queue = deque([start])
    parent: Dict[Position, Optional[Position]] = {start: None}
    visited_order: List[Position] = []
    expanded = 0
    max_frontier = 1

    while queue:
        current = queue.popleft()
        visited_order.append(current)
        expanded += 1
        if current == end:
            elapsed_ms = (time.perf_counter() - begin) * 1000
            return SearchResult('BFS', reconstruct_path(parent, end), visited_order, expanded, max_frontier, elapsed_ms)

        for neighbor in graph[current]:
            if neighbor not in parent:
                parent[neighbor] = current
                queue.append(neighbor)
        max_frontier = max(max_frontier, len(queue))

    elapsed_ms = (time.perf_counter() - begin) * 1000
    return SearchResult('BFS', None, visited_order, expanded, max_frontier, elapsed_ms)


def run_dfs(graph: Graph, start: Position, end: Position) -> SearchResult:
    """Búsqueda en profundidad: encuentra una ruta, pero no garantiza que sea la más corta."""
    begin = time.perf_counter()
    stack = [start]
    parent: Dict[Position, Optional[Position]] = {start: None}
    visited_order: List[Position] = []
    expanded = 0
    max_frontier = 1

    while stack:
        current = stack.pop()
        visited_order.append(current)
        expanded += 1
        if current == end:
            elapsed_ms = (time.perf_counter() - begin) * 1000
            return SearchResult('DFS', reconstruct_path(parent, end), visited_order, expanded, max_frontier, elapsed_ms)

        # Se invierte para conservar un orden de exploración estable.
        for neighbor in reversed(graph[current]):
            if neighbor not in parent:
                parent[neighbor] = current
                stack.append(neighbor)
        max_frontier = max(max_frontier, len(stack))

    elapsed_ms = (time.perf_counter() - begin) * 1000
    return SearchResult('DFS', None, visited_order, expanded, max_frontier, elapsed_ms)


def manhattan_distance(a: Position, b: Position) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def run_astar(graph: Graph, start: Position, end: Position) -> SearchResult:
    """A*: usa distancia Manhattan como heurística admisible para movimiento 4-direcciones."""
    begin = time.perf_counter()
    frontier: List[Tuple[int, int, Position]] = []
    heapq.heappush(frontier, (0, 0, start))
    parent: Dict[Position, Optional[Position]] = {start: None}
    cost_so_far: Dict[Position, int] = {start: 0}
    visited_order: List[Position] = []
    expanded = 0
    max_frontier = 1
    push_count = 1
    closed: Set[Position] = set()

    while frontier:
        _, _, current = heapq.heappop(frontier)
        if current in closed:
            continue
        closed.add(current)
        visited_order.append(current)
        expanded += 1

        if current == end:
            elapsed_ms = (time.perf_counter() - begin) * 1000
            return SearchResult('A*', reconstruct_path(parent, end), visited_order, expanded, max_frontier, elapsed_ms)

        for neighbor in graph[current]:
            new_cost = cost_so_far[current] + 1
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                priority = new_cost + manhattan_distance(neighbor, end)
                parent[neighbor] = current
                heapq.heappush(frontier, (priority, push_count, neighbor))
                push_count += 1
        max_frontier = max(max_frontier, len(frontier))

    elapsed_ms = (time.perf_counter() - begin) * 1000
    return SearchResult('A*', None, visited_order, expanded, max_frontier, elapsed_ms)


def count_edges(graph: Graph) -> int:
    return sum(len(neighbors) for neighbors in graph.values()) // 2


def solve_maze(maze_file: str, output_dir: Path) -> List[Dict[str, object]]:
    maze = MazeLoader(maze_file).load_Maze()
    graph = maze.get_graph()
    start, end = maze.get_start_end()
    graph_nodes = len(graph)
    graph_edges = count_edges(graph)

    algorithms: List[Callable[[Graph, Position, Position], SearchResult]] = [run_bfs, run_dfs, run_astar]
    rows: List[Dict[str, object]] = []

    print(f"\n{maze_file}: nodos={graph_nodes}, aristas={graph_edges}, inicio={start}, salida={end}")
    for algorithm in algorithms:
        result = algorithm(graph, start, end)
        image_path = output_dir / f"{Path(maze_file).stem}_{result.algorithm.lower().replace('*', 'star')}.png"
        maze.plot_maze(
            path=result.path,
            visited=result.visited_order,
            title=f"{maze_file} - {result.algorithm}: pasos={result.path_steps}, visitados={len(result.visited_order)}",
            save_path=str(image_path),
            show=False,
        )
        row = result.to_row(maze_file, graph_nodes, graph_edges)
        row['image'] = str(image_path.relative_to(Path(__file__).resolve().parent))
        rows.append(row)
        print(
            f"  {result.algorithm:<3} | encontrado={result.found} | pasos={row['path_steps']} | "
            f"visitados={row['visited_nodes']} | expandidos={row['expanded_nodes']} | "
            f"frontera_max={row['max_frontier_size']} | tiempo_ms={row['time_ms']}"
        )
    return rows


def write_metrics_csv(rows: List[Dict[str, object]], output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / 'metricas_busqueda.csv'
    fieldnames = [
        'maze', 'algorithm', 'found', 'path_steps', 'path_nodes', 'visited_nodes',
        'expanded_nodes', 'max_frontier_size', 'time_ms', 'graph_nodes', 'graph_edges', 'image'
    ]
    with open(csv_path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return csv_path


def main():
    output_dir = Path(__file__).resolve().parent / 'results'
    # El enunciado pide 3 laberintos; si laberinto4.txt existe se procesa también como caso adicional.
    maze_files = ['laberinto1.txt', 'laberinto2.txt', 'laberinto3.txt']
    optional_maze = Path(__file__).resolve().parent / 'laberinto4.txt'
    if optional_maze.exists():
        maze_files.append('laberinto4.txt')

    all_rows: List[Dict[str, object]] = []
    for maze_file in maze_files:
        all_rows.extend(solve_maze(maze_file, output_dir))

    csv_path = write_metrics_csv(all_rows, output_dir)
    print(f"\nMétricas guardadas en: {csv_path}")


# Mantengo los nombres de funciones del archivo base.
def study_case_1():
    solve_maze('laberinto1.txt', Path(__file__).resolve().parent / 'results')


def study_case_2():
    solve_maze('laberinto2.txt', Path(__file__).resolve().parent / 'results')


def study_case_3():
    solve_maze('laberinto3.txt', Path(__file__).resolve().parent / 'results')


if __name__ == '__main__':
    main()
