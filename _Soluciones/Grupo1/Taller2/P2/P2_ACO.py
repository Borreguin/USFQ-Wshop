import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import itertools
from tqdm import tqdm

class AntColonyOptimization:
    def __init__(self, start, end, obstacles, grid_size=(10, 10), num_ants=10, evaporation_rate=0.1, alpha=0.1, beta=15, num_iterations=100):
        self.start = start
        self.end = end
        self.obstacles = obstacles
        self.grid_size = grid_size
        self.num_ants = num_ants
        self.evaporation_rate = evaporation_rate
        self.alpha = alpha
        self.beta = beta
        self.num_iterations = num_iterations
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
        if not probabilities or total == 0:
            return None
        probabilities = [(pos, prob / total) for pos, prob in probabilities] # normaliza las probabilidades para que sumen 1
        selected = np.random.choice(len(probabilities), p=[prob for pos, prob in probabilities]) # selecciona la siguiente posición aleatoriamente basado en las probabilidades calculadas
        return probabilities[selected][0]

    def _evaporate_pheromones(self):
        self.pheromones *= (1 - self.evaporation_rate) # evapora las feromonas en cada iteración para evitar que se acumulen indefinidamente y permitir que el algoritmo explore nuevas rutas

    def _deposit_pheromones(self, path):
        for position in path:
            self.pheromones[position[1], position[0]] += 1 # deposita feromona en el camino encontrado para reforzar las rutas exitosas y aumentar la probabilidad de que otras hormigas sigan ese camino en futuras iteraciones

    def find_best_path(self, num_iterations=None):
        if num_iterations is None:
            num_iterations = self.num_iterations
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

def evaluate_parameters(start, end, obstacles, params, num_runs=3, num_iterations=100):
    """
    Evalúa un conjunto de parámetros ejecutando ACO varias veces y devuelve la longitud media del mejor camino.
    """
    lengths = []
    for _ in range(num_runs):
        aco = AntColonyOptimization(
            start=start, end=end, obstacles=obstacles,
            num_ants=params['num_ants'],
            evaporation_rate=params['evaporation_rate'],
            alpha=params['alpha'],
            beta=params['beta'],
            num_iterations=num_iterations
        )
        best_path = aco.find_best_path()
        if best_path is not None:
            lengths.append(len(best_path))
        else:
            lengths.append(float('inf'))  # si no encuentra camino
    return np.mean(lengths)

def grid_search_hyperparameters(start, end, obstacles, param_grid, num_runs=3, num_iterations=100):
    """
    Realiza Grid Search sobre el diccionario param_grid.
    param_grid = {'alpha': [0.5,1.0,1.5], 'beta': [1,3,5], ...}
    """
    best_params = None
    best_score = float('inf')
    results = []
    
    keys = list(param_grid.keys())
    values = list(param_grid.values())
    total_combinations = np.prod([len(v) for v in values])
    
    print(f"🔍 Iniciando Grid Search con {total_combinations} combinaciones...")
    
    for combination in itertools.product(*values):
        params = dict(zip(keys, combination))
        score = evaluate_parameters(start, end, obstacles, params, num_runs, num_iterations)
        results.append((params, score))
        print(f"Parametros: {params} -> Longitud media del camino: {score:.2f}")
        if score < best_score:
            best_score = score
            best_params = params
    
    print(f"\n✅ Mejores parámetros encontrados: {best_params} con longitud media = {best_score:.2f}")
    return best_params, best_score, results

def random_search_hyperparameters(start, end, obstacles, param_distributions, n_iter=20, num_runs=3, num_iterations=100):
    """
    Realiza Random Search.
    param_distributions = {'alpha': (low, high), 'beta': (low, high), ...}
    Para parámetros discretos, pasar lista.
    """
    best_params = None
    best_score = float('inf')
    results = []
    
    print(f"🎲 Iniciando Random Search con {n_iter} iteraciones...")
    
    for i in range(n_iter):
        params = {}
        for key, dist in param_distributions.items():
            if isinstance(dist, tuple):  # distribución uniforme continua
                low, high = dist
                params[key] = np.random.uniform(low, high)
            elif isinstance(dist, list):  # valores discretos
                params[key] = np.random.choice(dist)
            else:
                params[key] = dist  # valor fijo
        
        # Ajustes discretos para num_ants (entero) y evaporation_rate (0-1)
        if 'num_ants' in params:
            params['num_ants'] = int(params['num_ants'])
        if 'evaporation_rate' in params:
            params['evaporation_rate'] = np.clip(params['evaporation_rate'], 0.01, 0.99)
        
        score = evaluate_parameters(start, end, obstacles, params, num_runs, num_iterations)
        results.append((params, score))
        print(f"Iter {i+1}: {params} -> Longitud media: {score:.2f}")
        if score < best_score:
            best_score = score
            best_params = params
    
    print(f"\n✅ Mejores parámetros (Random Search): {best_params} con longitud media = {best_score:.2f}")
    return best_params, best_score, results

# ==================== ESTUDIO DE CASO CON OPTIMIZACIÓN ====================

def study_case_optimized():
    print("=== Optimización de hiperparámetros para ACO ===")
    
    # Definir el problema (caso 1)
    start = (0, 0)
    end = (4, 7)
    obstacles = [(1, 2), (2, 2), (3, 2)]
    
    # 1. Grid Search (recomendado)
    param_grid = {
        'alpha': [0.5, 1.0, 1.5, 2.0],
        'beta': [1, 2, 3, 5],
        'evaporation_rate': [0.05, 0.1, 0.2],
        'num_ants': [5, 10, 15]
    }
    
    best_params_grid, best_score_grid, _ = grid_search_hyperparameters(
        start, end, obstacles, param_grid, num_runs=3, num_iterations=50
    )
    
    # 2. (Opcional) Random Search como comparación
    param_distributions = {
        'alpha': (0.2, 2.5),
        'beta': (1, 8),
        'evaporation_rate': (0.02, 0.3),
        'num_ants': (5, 20)  # uniforme entero
    }
    
    best_params_rand, best_score_rand, _ = random_search_hyperparameters(
        start, end, obstacles, param_distributions, n_iter=15, num_runs=3, num_iterations=50
    )
    
    # Ejecutar ACO con los mejores parámetros (Grid Search) y graficar
    print("\n=== Ejecución final con mejores parámetros (Grid Search) ===")
    aco_best = AntColonyOptimization(
        start, end, obstacles,
        num_ants=int(best_params_grid['num_ants']),
        evaporation_rate=best_params_grid['evaporation_rate'],
        alpha=best_params_grid['alpha'],
        beta=best_params_grid['beta'],
        num_iterations=100
    )
    aco_best.find_best_path()
    aco_best.plot()
    print(f"Mejor camino encontrado: {aco_best.best_path}")
    print(f"Longitud del camino: {len(aco_best.best_path)}")

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



