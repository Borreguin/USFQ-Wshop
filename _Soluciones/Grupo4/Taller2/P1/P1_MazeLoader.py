import matplotlib.pyplot as plt
import os, sys
import heapq
import time
from collections import deque
project_path = os.path.dirname(__file__)
sys.path.append(project_path)
from Taller2.P1.P1_util import define_color


class MazeLoader:
    def __init__(self, filename):
        self.filename = filename
        self.maze = None

    def load_Maze(self):
        _maze = []
        file_path = os.path.join(project_path, self.filename)
        print("Loading Maze from", file_path)
        with open(file_path, 'r') as file:
            for line in file:
                _maze.append(list(line.strip()))
        self.maze = _maze
        return self

    def plot_maze(self):
        height = len(self.maze)
        width = len(self.maze[0])

        fig = plt.figure(figsize=(width/4, height/4))  # Ajusta el tamaño de la figura según el tamaño del Maze
        for y in range(height):
            for x in range(width):
                cell = self.maze[y][x]
                color = define_color(cell)
                plt.fill([x, x+1, x+1, x], [y, y, y+1, y+1], color=color, edgecolor='black')

        plt.xlim(0, width)
        plt.ylim(0, height)
        plt.gca().invert_yaxis()  # Invierte el eje y para que el origen esté en la esquina inferior izquierda
        plt.xticks([])
        plt.yticks([])
        fig.tight_layout()
        plt.show()
        return self

    def plot_solution(self, path):
        if path is None:
            print("No se encontro una solucion para el laberinto.")
            return self

        height = len(self.maze)
        width = len(self.maze[0])
        solution_cells = set(path)

        fig = plt.figure(figsize=(width/4, height/4))
        for y in range(height):
            for x in range(width):
                cell = self.maze[y][x]
                color = define_color(cell)

                if (y, x) in solution_cells and cell not in {'E', 'S'}:
                    color = 'skyblue'

                plt.fill([x, x+1, x+1, x], [y, y, y+1, y+1], color=color, edgecolor='black')

        plt.xlim(0, width)
        plt.ylim(0, height)
        plt.gca().invert_yaxis()
        plt.xticks([])
        plt.yticks([])
        fig.tight_layout()
        plt.show()
        return self

    def get_graph(self):
        graph = {}
        valid_cells = {' ', 'E', 'S'}
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        height = len(self.maze)
        width = len(self.maze[0])

        for y in range(height):
            for x in range(width):
                if self.maze[y][x] not in valid_cells:
                    continue

                node = (y, x)
                graph[node] = []

                for dy, dx in directions:
                    neighbor_y = y + dy
                    neighbor_x = x + dx

                    is_inside_maze = (
                        0 <= neighbor_y < height and
                        0 <= neighbor_x < width
                    )

                    if not is_inside_maze:
                        continue

                    if self.maze[neighbor_y][neighbor_x] in valid_cells:
                        graph[node].append((neighbor_y, neighbor_x))

        return graph

    def reconstruct_path(self, parents, start, goal):
        if goal not in parents:
            return None

        path = []
        current = goal

        while current is not None:
            path.append(current)
            current = parents[current]

        path.reverse()
        return path

    def manhattan_distance(self, node, goal):
        return abs(node[0] - goal[0]) + abs(node[1] - goal[1])

    def print_solution_metrics(self, algorithm_name, path, elapsed_time):
        elapsed_ms = elapsed_time * 1000

        if path is None:
            print(f"{algorithm_name}: no encontro solucion. Tiempo: {elapsed_ms:.4f} ms")
            return

        steps = len(path) - 1
        print(f"{algorithm_name}: tiempo {elapsed_ms:.4f} ms, pasos {steps}")

    def solve_bfs(self, graph=None, start=None, goal=None, show=True):
        if graph is None:
            graph = self.get_graph()

        if start is None:
            start = self.find_cell('E')

        if goal is None:
            goal = self.find_cell('S')

        if start is None or goal is None:
            print("No se encontro la entrada 'E' o la salida 'S'.")
            return None

        visited = {start}
        parents = {start: None}
        queue = deque([start])
        start_time = time.perf_counter()

        while queue:
            node = queue.popleft()

            if node == goal:
                path = self.reconstruct_path(parents, start, goal)
                elapsed_time = time.perf_counter() - start_time
                self.print_solution_metrics("BFS", path, elapsed_time)
                if show:
                    self.plot_solution(path)
                return path

            for neighbor in graph[node]:
                if neighbor in visited:
                    continue

                visited.add(neighbor)
                parents[neighbor] = node
                queue.append(neighbor)

        elapsed_time = time.perf_counter() - start_time
        self.print_solution_metrics("BFS", None, elapsed_time)
        if show:
            self.plot_solution(None)
        return None

    def solve_nayfeth(self, graph=None, start=None, goal=None, show=True):
        if graph is None:
            graph = self.get_graph()

        if start is None:
            start = self.find_cell('E')

        if goal is None:
            goal = self.find_cell('S')

        if start is None or goal is None:
            print("No se encontro la entrada 'E' o la salida 'S'.")
            return None

        visited = {start}
        parents = {start: None}
        stack = [start]
        start_time = time.perf_counter()

        while stack:
            node = stack.pop()

            if node == goal:
                path = self.reconstruct_path(parents, start, goal)
                elapsed_time = time.perf_counter() - start_time
                self.print_solution_metrics("Nayfeth", path, elapsed_time)
                if show:
                    self.plot_solution(path)
                return path

            for neighbor in reversed(graph[node]):
                if neighbor in visited:
                    continue

                visited.add(neighbor)
                parents[neighbor] = node
                stack.append(neighbor)

        elapsed_time = time.perf_counter() - start_time
        self.print_solution_metrics("Nayfeth", None, elapsed_time)
        if show:
            self.plot_solution(None)
        return None

    def solve_astar(self, graph=None, start=None, goal=None, show=True):
        if graph is None:
            graph = self.get_graph()

        if start is None:
            start = self.find_cell('E')

        if goal is None:
            goal = self.find_cell('S')

        if start is None or goal is None:
            print("No se encontro la entrada 'E' o la salida 'S'.")
            return None

        parents = {start: None}
        costs = {start: 0}
        priority_queue = [(self.manhattan_distance(start, goal), 0, start)]
        start_time = time.perf_counter()

        while priority_queue:
            _, current_cost, node = heapq.heappop(priority_queue)

            if node == goal:
                path = self.reconstruct_path(parents, start, goal)
                elapsed_time = time.perf_counter() - start_time
                self.print_solution_metrics("A*", path, elapsed_time)
                if show:
                    self.plot_solution(path)
                return path

            if current_cost > costs[node]:
                continue

            for neighbor in graph[node]:
                new_cost = costs[node] + 1

                if neighbor not in costs or new_cost < costs[neighbor]:
                    costs[neighbor] = new_cost
                    parents[neighbor] = node
                    priority = new_cost + self.manhattan_distance(neighbor, goal)
                    heapq.heappush(priority_queue, (priority, new_cost, neighbor))

        elapsed_time = time.perf_counter() - start_time
        self.print_solution_metrics("A*", None, elapsed_time)
        if show:
            self.plot_solution(None)
        return None

    def plot_graph(self, graph=None):
        if graph is None:
            graph = self.get_graph()

        fig = plt.figure(figsize=(10, 8))

        for node, neighbors in graph.items():
            y, x = node

            for neighbor_y, neighbor_x in neighbors:
                plt.plot(
                    [x, neighbor_x],
                    [-y, -neighbor_y],
                    color='black',
                    linewidth=1
                )

        for y, x in graph:
            plt.scatter(x, -y, color='black', s=35, zorder=3)
            plt.text(
                x + 0.08,
                -y + 0.08,
                f'[{y}, {x}]',
                fontsize=8
            )

        plt.axis('equal')
        plt.axis('off')
        fig.tight_layout()
        plt.show()
        return self

    def find_cell(self, cell_value):
        for y, row in enumerate(self.maze):
            for x, cell in enumerate(row):
                if cell == cell_value:
                    return (y, x)
        return None

    def plot_graph_as_tree(self, graph=None, start=None):
        if graph is None:
            graph = self.get_graph()

        if start is None:
            start = self.find_cell('E')

        if start is None:
            print("No se encontro la entrada 'E' del laberinto.")
            return self

        visited = {start}
        queue = deque([(start, 0)])
        tree_edges = []
        levels = {0: [start]}

        while queue:
            node, depth = queue.popleft()

            for neighbor in graph[node]:
                if neighbor in visited:
                    continue

                visited.add(neighbor)
                tree_edges.append((node, neighbor))
                next_depth = depth + 1
                levels.setdefault(next_depth, []).append(neighbor)
                queue.append((neighbor, next_depth))

        positions = {}
        max_width = max(len(nodes) for nodes in levels.values())

        for depth, nodes in levels.items():
            level_width = len(nodes)
            initial_x = (max_width - level_width) / 2

            for index, node in enumerate(nodes):
                positions[node] = (initial_x + index, -depth)

        fig = plt.figure(figsize=(max(10, max_width / 2), max(8, len(levels) / 2)))

        for parent, child in tree_edges:
            parent_x, parent_y = positions[parent]
            child_x, child_y = positions[child]
            plt.plot(
                [parent_x, child_x],
                [parent_y, child_y],
                color='black',
                linewidth=1
            )

        for node, (x, y) in positions.items():
            plt.scatter(x, y, color='black', s=35, zorder=3)
            plt.text(
                x + 0.08,
                y + 0.08,
                f'[{node[0]}, {node[1]}]',
                fontsize=8
            )

        plt.axis('equal')
        plt.axis('off')
        fig.tight_layout()
        plt.show()
        return self

    def plot_graph_as_dfs_tree(self, graph=None, start=None):
        if graph is None:
            graph = self.get_graph()

        if start is None:
            start = self.find_cell('E')

        if start is None:
            print("No se encontro la entrada 'E' del laberinto.")
            return self

        visited = {start}
        stack = [(start, 0)]
        tree_edges = []
        levels = {0: [start]}

        while stack:
            node, depth = stack.pop()

            for neighbor in reversed(graph[node]):
                if neighbor in visited:
                    continue

                visited.add(neighbor)
                tree_edges.append((node, neighbor))
                next_depth = depth + 1
                levels.setdefault(next_depth, []).append(neighbor)
                stack.append((neighbor, next_depth))

        positions = {}
        max_width = max(len(nodes) for nodes in levels.values())

        for depth, nodes in levels.items():
            level_width = len(nodes)
            initial_x = (max_width - level_width) / 2

            for index, node in enumerate(nodes):
                positions[node] = (initial_x + index, -depth)

        fig = plt.figure(figsize=(max(10, max_width / 2), max(8, len(levels) / 2)))

        for parent, child in tree_edges:
            parent_x, parent_y = positions[parent]
            child_x, child_y = positions[child]
            plt.plot(
                [parent_x, child_x],
                [parent_y, child_y],
                color='black',
                linewidth=1
            )

        for node, (x, y) in positions.items():
            plt.scatter(x, y, color='black', s=35, zorder=3)
            plt.text(
                x + 0.08,
                y + 0.08,
                f'[{node[0]}, {node[1]}]',
                fontsize=8
            )

        plt.axis('equal')
        plt.axis('off')
        fig.tight_layout()
        plt.show()
        return self
