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
        # retorna las posiciones vecinas (8 direcciones incluyendo diagonales) que no son obstáculos ni fuera del grid ni la posición actual
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
        # calcula las probabilidades de moverse a cada vecino basado en la cantidad de feromona y la heurística (inversa de la distancia al objetivo)
        neighbors = self._get_neighbors(position)
        probabilities = []
        total = 0
        for neighbor in neighbors:
            if neighbor not in visited:
                pheromone = self.pheromones[neighbor[1], neighbor[0]]
                heuristic = 1 / (np.linalg.norm(np.array(neighbor) - np.array(self.end)) + 0.1) # para evitar división por cero se agrega un pequeño valor
                
                # se calcula la probabilidad sin normalizar con parámetros alpha y beta que determinan la importancia relativa de la feromona y la heurística
                probabilities.append((neighbor, pheromone ** self.alpha * heuristic ** self.beta))
                total += pheromone ** self.alpha * heuristic ** self.beta
        if not probabilities:
            return None
        probabilities = [(pos, prob / total) for pos, prob in probabilities] # normaliza las probabilidades para que sumen 1
        selected = np.random.choice(len(probabilities), p=[prob for pos, prob in probabilities]) # selecciona la siguiente posición aleatoriamente basado en las probabilidades calculadas
        return probabilities[selected][0]

    def _evaporate_pheromones(self):
        self.pheromones *= (1 - self.evaporation_rate) # evapora las feromonas en cada iteración para evitar que se acumulen indefinidamente y permitir que el algoritmo explore nuevas rutas

    def _deposit_pheromones(self, path):
        for position in path:
            self.pheromones[position[1], position[0]] += 1 # deposita feromona en el camino encontrado para reforzar las rutas exitosas y aumentar la probabilidad de que otras hormigas sigan ese camino en futuras iteraciones

    def find_best_path(self, num_iterations):
        # el algoritmo principal que ejecuta el proceso de optimización durante un número determinado de iteraciones, 
        # donde cada hormiga construye un camino desde el inicio hasta el final, se actualizan las feromonas y se mantiene el mejor camino encontrado
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

            # Escoger el mejor camino por su tamaño?
            # Modificamos para quedarnos solo con los caminos que llegaron al destino, y luego escoger el más corto entre ellos
            valid_paths = [path for path in all_paths if path[-1] == self.end]
            
            if valid_paths:
                valid_paths.sort(key=lambda x: len(x))
                best_path = valid_paths[0]
            else:
                # Si no hay caminos válidos, no depositamos feromona en esta iteración
                best_path = None

            if best_path is not None:
                self._evaporate_pheromones()
                self._deposit_pheromones(best_path)

                if self.best_path is None or len(best_path) <= len(self.best_path):
                    self.best_path = best_path
            else:
                self._evaporate_pheromones()
            # --------------------------

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

def study_case_2():
    print("Start of Ant Colony Optimization - Second Study Case")
    start = (0, 0)
    end = (4, 7)
    obstacles = [(0, 2), (1, 2), (2, 2), (3, 2)]
    # Parámetros optimizados para barrera continua: más hormigas, menos evaporación, más alfa
    aco = AntColonyOptimization(start, end, obstacles, num_ants=30, evaporation_rate=0.05, alpha=0.5, beta=15)
    aco.find_best_path(200)
    aco.plot()
    print("End of Ant Colony Optimization")
    print("Best path: ", aco.best_path)

if __name__ == '__main__':
    study_case_1()
    study_case_2()



