import os
import numpy as np
import matplotlib.pyplot as plt
import heapq

class AntColonyOptimization:
    def __init__(self, start, end, obstacles, grid_size=(10, 10),
                 num_ants=10, evaporation_rate=0.1, alpha=0.1, beta=15):
        self.start = start
        self.end = end
        self.obstacles = set(obstacles)
        self.rows, self.cols = grid_size
        self.num_ants = num_ants
        self.evaporation_rate = evaporation_rate
        self.alpha = alpha
        self.beta = beta
        self.pheromones = np.ones(grid_size)
        self.best_path = None

    def heuristic(self, a, b):
        return np.linalg.norm(np.array(a) - np.array(b))

    def get_neighbors(self, position):
        x, y = position
        neigh = []
        for dx, dy in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.cols and 0 <= ny < self.rows:
                if (nx, ny) not in self.obstacles:
                    neigh.append((nx, ny))
        return neigh

    def select_next_position(self, position, visited):
        neighbors = self.get_neighbors(position)
        if not neighbors:
            return None

        scores = []
        for n in neighbors:
            if n not in visited:
                pher = self.pheromones[n[1], n[0]]
                h = 1 / (self.heuristic(n, self.end) + 1e-6)
                scores.append((pher ** self.alpha) * (h ** self.beta))
            else:
                scores.append(0)

        scores = np.array(scores)
        total = scores.sum()
        if total <= 0:
            return None

        probs = scores / total
        idx = np.random.choice(len(neighbors), p=probs)
        return neighbors[idx]

    def evaporate_pheromones(self):
        self.pheromones *= (1 - self.evaporation_rate)

    def deposit_pheromones(self, path):
        for pos in set(path):  # Actualización solo posiciones únicas
            x, y = pos
            self.pheromones[y, x] += 1

    def find_best_path(self, iterations=150, max_steps=200):
        for _ in range(iterations):
            paths = []
            for _ in range(self.num_ants):
                pos = self.start
                path = [pos]
                while pos != self.end and len(path) < max_steps:
                    nxt = self.select_next_position(pos, set(path))
                    if nxt is None:
                        break
                    path.append(nxt)
                    pos = nxt

                if path[-1] == self.end:
                    paths.append(path)

            if not paths:
                continue

            best = min(paths, key=len)
            self.evaporate_pheromones()
            self.deposit_pheromones(best)

            if self.best_path is None or len(best) < len(self.best_path):
                self.best_path = best

        return self.best_path

    def solve_a_star(self):
        """Solver correcto de A* integrado"""
        frontier = []
        heapq.heappush(frontier, (0, self.start))
        came = {self.start: None}
        cost = {self.start: 0}

        while frontier:
            _, cur = heapq.heappop(frontier)
            if cur == self.end:
                break

            for nxt in self.get_neighbors(cur):
                new_cost = cost[cur] + self.heuristic(cur, nxt)
                if nxt not in cost or new_cost < cost[nxt]:
                    cost[nxt] = new_cost
                    priority = new_cost + self.heuristic(nxt, self.end)
                    heapq.heappush(frontier, (priority, nxt))
                    came[nxt] = cur

        if self.end not in came:
            print("⚠️ No se encontró camino con A*")
            return None

        path = []
        node = self.end
        while node is not None:
            path.append(node)
            node = came[node]

        return path[::-1]

    def plot(self):
        """Plot corregido"""
        plt.figure(figsize=(6,6))
        plt.imshow(self.pheromones, interpolation="nearest")
        plt.scatter(self.start[0], self.start[1], c="green", s=100, label="Start")
        plt.scatter(self.end[0], self.end[1], c="red", s=100, label="End")

        for x, y in self.obstacles:
            plt.scatter(x, y, c="black", marker="s", s=300)

        if self.best_path:
            px = [n[0] for n in self.best_path]
            py = [n[1] for n in self.best_path]
            plt.plot(px, py, c="blue", linewidth=3, label="ACO Path")

        plt.legend()
        plt.grid(True)
        plt.show()


def run():
    print(" Iniciando solving A* + ACO integrado")

    start = (0, 0)
    end = (4, 7)
    obstacles = [(1,2),(2,2),(3,2),(2,1),(3,3)]

    aco = AntColonyOptimization(start, end, obstacles)

    best_aco = aco.find_best_path(iterations=150)
    print(" Mejor camino ACO:", best_aco)

    best_astar = aco.solve_a_star()
    print(" Solución A* :", best_astar)

    aco.plot()


if __name__ == "__main__":
    run()
