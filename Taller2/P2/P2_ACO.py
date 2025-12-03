import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

class AntColonyOptimization:
    def __init__(self, start, end, obstacles, grid_size=(10, 10), num_ants=10, evaporation_rate=0.1, alpha=0.1, beta=2):
        self.start = start
        self.end = end
        self.obstacles = obstacles
        self.grid_size = grid_size
        self.num_ants = num_ants
        self.evaporation_rate = evaporation_rate
        self.alpha = alpha
        self.beta = beta
        # Inicializar feromonas con un valor pequeño, no 1, para evitar sesgo inicial
        self.pheromones = np.ones(grid_size) * 0.1
        self.best_path = None
        self.best_path_length = float('inf')

    def _get_neighbors(self, position):
        pos_x, pos_y = position
        neighbors = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                new_x, new_y = pos_x + i, pos_y + j
                if (0 <= new_x < self.grid_size[0] and 0 <= new_y < self.grid_size[1] and
                        (new_x, new_y) != position and (new_x, new_y) not in self.obstacles):
                    neighbors.append((new_x, new_y))
        return neighbors

    def _select_next_position(self, position, visited):
        neighbors = self._get_neighbors(position)
        probabilities = []
        total = 0
        for neighbor in neighbors:
            if neighbor not in visited:
                pheromone = self.pheromones[neighbor[1], neighbor[0]]
                heuristic = 1 / (np.linalg.norm(np.array(neighbor) - np.array(self.end)) + 0.1)
                probabilities.append((neighbor, pheromone ** self.alpha * heuristic ** self.beta))
                total += pheromone ** self.alpha * heuristic ** self.beta
        if not probabilities:
            return None
        probabilities = [(pos, prob / total) for pos, prob in probabilities]
        selected = np.random.choice(len(probabilities), p=[prob for pos, prob in probabilities])
        return probabilities[selected][0]

    def _evaporate_pheromones(self):
        self.pheromones *= (1 - self.evaporation_rate)

    def _deposit_pheromones(self, path, path_length):
        # Depósito inversamente proporcional a la longitud del camino
        # Cuanto más corto sea el camino, más feromona se deposita
        if path_length > 0:
            pheromone_deposit = 1.0 / path_length  # Puedes ajustar este factor
            for position in path:
                self.pheromones[position[1], position[0]] += pheromone_deposit

    def find_best_path(self, num_iterations):
        for iteration in range(num_iterations):
            all_paths = []
            for ant in range(self.num_ants):
                current_position = self.start
                path = [current_position]
                while current_position != self.end:
                    next_position = self._select_next_position(current_position, path)
                    if next_position is None:
                        break  # Hormiga atascada
                    path.append(next_position)
                    current_position = next_position
                # Solo agregar el camino si llegó al destino
                if current_position == self.end:
                    all_paths.append(path)

            # Actualizar mejor camino global
            if all_paths:
                # Encontrar el camino más corto entre los válidos
                best_path_this_iter = min(all_paths, key=len)
                best_path_length_this_iter = len(best_path_this_iter)

                # Actualizar el mejor camino global si este es mejor
                if best_path_length_this_iter < self.best_path_length:
                    self.best_path = best_path_this_iter
                    self.best_path_length = best_path_length_this_iter

                # Evaporar y depositar feromonas basadas en el mejor camino de esta iteración
                self._evaporate_pheromones()
                self._deposit_pheromones(best_path_this_iter, best_path_length_this_iter)
            else:
                # Si ninguna hormiga llegó al destino, solo evaporar
                self._evaporate_pheromones()

            print(f"Iteration {iteration + 1}: Best path length so far: {self.best_path_length}")

    def plot(self):
        cmap = LinearSegmentedColormap.from_list('pheromone', ['white', 'green', 'red'])
        plt.figure(figsize=(8, 8))
        plt.imshow(self.pheromones, cmap=cmap, vmin=np.min(self.pheromones), vmax=np.max(self.pheromones))
        plt.colorbar(label='Pheromone intensity')
        plt.scatter(self.start[0], self.start[1], color='orange', label='Start', s=100)
        plt.scatter(self.end[0], self.end[1], color='magenta', label='End', s=100)
        for obstacle in self.obstacles:
            plt.scatter(obstacle[0], obstacle[1], color='gray', s=900, marker='s')
        if self.best_path:
            path_x, path_y = zip(*self.best_path)
            plt.plot(path_x, path_y, color='blue', label='Best Path', linewidth=3)
        plt.xlabel('Column')
        plt.ylabel('Row')
        plt.title('Ant Colony Optimization')
        plt.legend()
        plt.grid(True)
        plt.show()

def study_case_1():
    print("Start of Ant Colony Optimization - First Study Case")
    start = (0, 0)
    end = (4, 7)
    obstacles = [(1, 2), (2, 2), (3, 2)]
    aco = AntColonyOptimization(start, end, obstacles)
    aco.find_best_path(100)
    aco.plot()
    print("End of Ant Colony Optimization")
    print("Best path: ", aco.best_path)
    print("Length of best path: ", aco.best_path_length)

def study_case_2():
    print("Start of Ant Colony Optimization - Second Study Case")
    start = (0, 0)
    end = (4, 7)
    obstacles = [(0, 2), (1, 2), (2, 2), (3, 2)]
    aco = AntColonyOptimization(start, end, obstacles)
    aco.find_best_path(100)
    aco.plot()
    print("End of Ant Colony Optimization")
    print("Best path: ", aco.best_path)
    print("Length of best path: ", aco.best_path_length)

if __name__ == '__main__':
    study_case_1()
    #study_case_2()