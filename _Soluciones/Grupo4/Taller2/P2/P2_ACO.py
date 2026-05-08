import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

class AntColonyOptimization:
    def __init__(self, start, end, obstacles, grid_size=(10, 10), num_ants=10, evaporation_rate=0.1, alpha=0.1, beta=15):
        self.start = start
        self.end = end
        self.obstacles = obstacles
        self.grid_size = grid_size
        self.num_ants = num_ants
        self.evaporation_rate = evaporation_rate
        self.alpha = alpha
        self.beta = beta
        self.pheromones = np.ones(grid_size)
        self.best_path = None

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

    def _deposit_pheromones(self, path):
        for position in path:
            self.pheromones[position[1], position[0]] += 1

    def find_best_path(self, num_iterations):
        for _ in range(num_iterations):
            all_paths = []
            for _ in range(self.num_ants):
                current_position = self.start
                path = [current_position]
                while current_position != self.end:
                    next_position = self._select_next_position(current_position, path)
                    if next_position is None:
                        break
                    path.append(next_position)
                    current_position = next_position
                all_paths.append(path)

            # Filtrar solo los caminos que llegaron al destino
            valid_paths = [p for p in all_paths if p[-1] == self.end]

            if valid_paths:
                valid_paths.sort(key=lambda x: len(x))
                best_iteration_path = valid_paths[0]

                self._evaporate_pheromones()
                self._deposit_pheromones(best_iteration_path)

                if self.best_path is None or len(best_iteration_path) < len(self.best_path):
                    self.best_path = best_iteration_path
            else:
                # Si ninguna hormiga llega al destino, solo se evaporan las feromonas
                self._evaporate_pheromones()

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

def run_study_case(case_number, start, end, obstacles, iterations=100, **kwargs):
    print(f"--- Caso de Estudio {case_number} ---")
    aco = AntColonyOptimization(start, end, obstacles, **kwargs)
    aco.find_best_path(iterations)
    aco.plot()
    if aco.best_path:
        print("Mejor camino encontrado:", aco.best_path)
        print("Longitud del camino:", len(aco.best_path))
    else:
        print("No se encontró un camino válido.")

import itertools

def grid_search_aco(start, end, obstacles, alpha_values, beta_values, iterations=100):
    best_overall_path = None
    best_params = None
    min_length = float('inf')
    
    print(f"{'Alpha':<10} | {'Beta':<10} | {'Longitud':<10}")
    print("-" * 35)
    
    for alpha, beta in itertools.product(alpha_values, beta_values):
        aco = AntColonyOptimization(start, end, obstacles, alpha=alpha, beta=beta, num_ants=20)
        aco.find_best_path(iterations)
        
        if aco.best_path:
            length = len(aco.best_path)
            print(f"{alpha:<10.2f} | {beta:<10.2f} | {length:<10}")
            
            if length < min_length:
                min_length = length
                best_params = (alpha, beta)
                best_overall_path = aco.best_path
        else:
            print(f"{alpha:<10.2f} | {beta:<10.2f} | No path")
            
    print("-" * 35)
    print(f"Mejor configuración: Alpha={best_params[0]}, Beta={best_params[1]} con longitud {min_length}")
    return best_params

if __name__ == '__main__':
    # Ejecución del Caso 1 solicitado
    run_study_case(1, (0, 0), (4, 7), [(1, 2), (2, 2), (3, 2)])

    # Definir rangos de búsqueda para el Caso 2
    alphas = [0.1, 0.5, 1.0]
    betas = [1.0, 5.0, 10.0]

    # Ejecutar búsqueda para el Caso 2
    print("\nEjecutando Grid Search para el Caso 2...")
    best_alpha, best_beta = grid_search_aco(
        start=(0, 0), 
        end=(4, 7), 
        obstacles=[(0, 2), (1, 2), (2, 2), (3, 2)],
        alpha_values=alphas,
        beta_values=betas,
        iterations=100
    )

    # Visualizar el mejor resultado encontrado por la búsqueda
    print("\n--- Visualización de la Mejor Configuración Encontrada para el Caso 2 ---")
    run_study_case(
        2, (0, 0), (4, 7), [(0, 2), (1, 2), (2, 2), (3, 2)],
        iterations=150, alpha=best_alpha, beta=best_beta, num_ants=20
    )



