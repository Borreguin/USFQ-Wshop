import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap


class AntColonyOptimization:
    def __init__(self, start, end, obstacles, grid_size=(10, 10),
                 # ORIGINAL: num_ants=10  → pocas hormigas, poca exploración
                 # CAMBIO:   num_ants=30  → más hormigas = más caminos explorados por iteración
                 num_ants=30,

                 # ORIGINAL: evaporation_rate=0.1 → feromonas antiguas persisten demasiado
                 # CAMBIO:   evaporation_rate=0.3 → se borran más rápido, el algoritmo explora más rutas
                 evaporation_rate=0.3,

                 # ORIGINAL: alpha=0.1 → las feromonas casi no influían en la decisión
                 # CAMBIO:   alpha=1.0 → las feromonas tienen peso real, el aprendizaje funciona
                 alpha=1.0,

                 # ORIGINAL: beta=15 → la heurística dominaba completamente, el algoritmo
                 #                        se comportaba como greedy puro (ignoraba feromonas)
                 # CAMBIO:   beta=5.0 → balance real entre feromona y heurística
                 beta=5.0):

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
        # Sin cambios: retorna los vecinos válidos en las 8 direcciones
        pos_x, pos_y = position
        neighbors = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                new_x, new_y = pos_x + i, pos_y + j
                if (0 <= new_x < self.grid_size[0] and
                        0 <= new_y < self.grid_size[1] and
                        (new_x, new_y) != position and
                        (new_x, new_y) not in self.obstacles):
                    neighbors.append((new_x, new_y))
        return neighbors

    def _select_next_position(self, position, visited):
        # Sin cambios en la lógica: selección probabilística por feromona + heurística
        # Fórmula ACO: P(n) = (τ^alpha * η^beta) / Σ(τ^alpha * η^beta)
        # τ = feromona en la celda vecina
        # η = 1 / distancia_al_destino  (heurística)
        neighbors = self._get_neighbors(position)
        probabilities = []
        total = 0
        for neighbor in neighbors:
            if neighbor not in visited:
                pheromone = self.pheromones[neighbor[1], neighbor[0]]
                heuristic = 1 / (np.linalg.norm(np.array(neighbor) - np.array(self.end)) + 0.1)
                score = pheromone ** self.alpha * heuristic ** self.beta
                probabilities.append((neighbor, score))
                total += score
        if not probabilities:
            return None
        probabilities = [(pos, prob / total) for pos, prob in probabilities]
        selected = np.random.choice(len(probabilities), p=[prob for pos, prob in probabilities])
        return probabilities[selected][0]

    def _evaporate_pheromones(self):
        # Sin cambios en la lógica, pero el parámetro evaporation_rate sí cambió (ver __init__)
        self.pheromones *= (1 - self.evaporation_rate)
        # AÑADIDO: clip para evitar que feromonas lleguen a 0 y bloqueen la exploración
        self.pheromones = np.clip(self.pheromones, 0.01, None)

    def _deposit_pheromones(self, path):
        # ORIGINAL: += 1 fijo para todos los caminos
        #    Problema: un camino largo (20 pasos) y uno corto (8 pasos) recibían
        #              el mismo refuerzo por celda → no premia la calidad
        #
        # CAMBIO: depósito = 100 / len(path)
        #    Ahora un camino corto deposita MÁS feromona que uno largo
        #    Ejemplo: camino de  8 pasos → +12.5 por celda
        #             camino de 20 pasos → + 5.0 por celda
        deposit = 100.0 / len(path)
        for position in path:
            self.pheromones[position[1], position[0]] += deposit

    def find_best_path(self, num_iterations):
        for iteration in range(num_iterations):
            all_paths = []
            for _ in range(self.num_ants):
                current_position = self.start
                path = [current_position]
                while current_position != self.end:
                    next_position = self._select_next_position(current_position, path)
                    if next_position is None:
                        break  # hormiga atrapada sin vecinos disponibles
                    path.append(next_position)
                    current_position = next_position
                all_paths.append(path)

            # ============================================================
            # PROBLEMA ORIGINAL (Bug principal — Pista 1):
            #
            #   all_paths.sort(key=lambda x: len(x))
            #   best_path = all_paths[0]
            #
            #   El código solo ordenaba por TAMAÑO, sin verificar si el camino
            #   realmente LLEGÓ al destino.
            #
            #   En el Caso 2, la barrera bloquea el camino directo y muchas
            #   hormigas quedan atrapadas (next_position = None → break).
            #   Esos caminos incompletos tienen pocos pasos → ganan el ranking.
            #
            #   Resultado: best_path = [(0,0),(1,0),(1,1),(0,1)]  ← NO llegó a (4,7)
            #   Las feromonas se refuerzan en celdas INCORRECTAS y el algoritmo
            #   nunca aprende el camino real.
            #
            # FIX: filtrar primero solo los caminos que llegaron al destino
            # ============================================================
            valid_paths = [p for p in all_paths if p[-1] == self.end]

            if not valid_paths:
                # Ninguna hormiga llegó en esta iteración → solo evaporar y continuar
                self._evaporate_pheromones()
                continue

            # Ahora sí: elegir el más corto ENTRE LOS QUE SÍ LLEGARON
            valid_paths.sort(key=lambda x: len(x))
            best_path = valid_paths[0]

            self._evaporate_pheromones()

            # MEJORA ADICIONAL: depositar en TODOS los caminos válidos,
            #    no solo en el mejor → refuerzo colectivo más rico
            for path in valid_paths:
                self._deposit_pheromones(path)

            # Actualizar el mejor camino global
            if self.best_path is None or len(best_path) < len(self.best_path):
                self.best_path = best_path
                print(f"  [Iter {iteration+1:3d}] Nuevo mejor: {len(self.best_path)} pasos → {self.best_path}")

    def plot(self, title='Ant Colony Optimization', filename='resultado_ACO.png'):
        # Sin cambios en la visualización, solo se añaden parámetros title/filename
        cmap = LinearSegmentedColormap.from_list('pheromone', ['white', 'green', 'red'])
        plt.figure(figsize=(8, 8))
        plt.imshow(self.pheromones, cmap=cmap,
                   vmin=np.min(self.pheromones),
                   vmax=np.max(self.pheromones))
        plt.colorbar(label='Pheromone intensity')
        plt.scatter(self.start[0], self.start[1], color='orange', label='Start', s=200, zorder=5)
        plt.scatter(self.end[0],   self.end[1],   color='magenta', label='End',   s=200, zorder=5)
        for obstacle in self.obstacles:
            plt.scatter(obstacle[0], obstacle[1], color='gray', s=900, marker='s', zorder=4)
        if self.best_path:
            path_x, path_y = zip(*self.best_path)
            plt.plot(path_x, path_y, color='blue',
                     label=f'Best Path ({len(self.best_path)} steps)',
                     linewidth=3, zorder=6)
        plt.xlabel('Column (x)')
        plt.ylabel('Row (y)')
        plt.title(title)
        plt.legend()
        plt.grid(True)
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"Gráfico guardado como '{filename}'")


# ─────────────────────────────────────────────────────────────────────────────
def study_case_1():
    print("Start of Ant Colony Optimization - First Study Case")
    start     = (0, 0)
    end       = (4, 7)
    obstacles = [(1, 2), (2, 2), (3, 2)]
    aco = AntColonyOptimization(start, end, obstacles)
    aco.find_best_path(100)
    aco.plot(title='ACO - Caso 1 (Barrera Parcial)', filename='caso1_ACO.png')
    print("End of Ant Colony Optimization")
    print("Best path: ", aco.best_path)


def study_case_2():
    print("\n" + "="*55)
    print("Caso de Estudio 2 — Barrera casi total (cols 0,1,2,3 en y=2)")
    print("="*55)
    start     = (0, 0)
    end       = (4, 7)
    # Barrera más dura: bloquea columnas 0,1,2,3 en fila y=2
    # Solo queda libre la columna 4 → las hormigas deben rodear por la derecha
    obstacles = [(0, 2), (1, 2), (2, 2), (3, 2)]
    aco = AntColonyOptimization(start, end, obstacles)
    aco.find_best_path(100)
    aco.plot(title='ACO - Caso 2 (Barrera Casi Total)', filename='caso2_ACO.png')
    print(f"\nMejor camino ({len(aco.best_path)} pasos): {aco.best_path}")
    print(f"¿Llegó al destino? {aco.best_path[-1] == end}")


if __name__ == '__main__':
    study_case_1()
    study_case_2()