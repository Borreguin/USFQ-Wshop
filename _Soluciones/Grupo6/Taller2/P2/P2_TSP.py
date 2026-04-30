import numpy as np
import matplotlib.pyplot as plt


class ACO_TSP:
    def __init__(self, cities, num_ants=20, num_iterations=100,
                 alpha=1.0, beta=5.0, evaporation_rate=0.3, Q=100):
        self.cities        = cities                  # lista de coordenadas (x, y)
        self.n             = len(cities)
        self.num_ants      = num_ants
        self.num_iterations = num_iterations
        self.alpha         = alpha
        self.beta          = beta
        self.evaporation_rate = evaporation_rate
        self.Q             = Q

        # Matriz de distancias entre todas las ciudades
        self.distances  = self._compute_distances()

        # Matriz de feromonas n x n inicializada en 1.0
        self.pheromones = np.ones((self.n, self.n))

        self.best_tour     = None
        self.best_distance = float('inf')
        self.history       = []           # para graficar convergencia

    def _compute_distances(self):
        dist = np.zeros((self.n, self.n))
        for i in range(self.n):
            for j in range(self.n):
                if i != j:
                    dx = self.cities[i][0] - self.cities[j][0]
                    dy = self.cities[i][1] - self.cities[j][1]
                    dist[i][j] = np.sqrt(dx**2 + dy**2)
        return dist

    def _select_next_city(self, current, visited):
        probabilities = []
        total = 0.0

        for city in range(self.n):
            if city not in visited:
                pheromone  = self.pheromones[current][city] ** self.alpha
                heuristic  = (1.0 / self.distances[current][city]) ** self.beta
                score      = pheromone * heuristic
                probabilities.append((city, score))
                total += score

        if total == 0:
            return None

        probabilities = [(c, s / total) for c, s in probabilities]
        idx = np.random.choice(len(probabilities),
                               p=[s for _, s in probabilities])
        return probabilities[idx][0]

    def _build_tour(self):
        # Cada hormiga construye un tour completo
        start = np.random.randint(self.n)     # ciudad inicial aleatoria
        tour    = [start]
        visited = {start}

        while len(visited) < self.n:
            next_city = self._select_next_city(tour[-1], visited)
            if next_city is None:
                break
            tour.append(next_city)
            visited.add(next_city)

        tour.append(start)    # cerrar el ciclo regresando al inicio
        return tour

    def _tour_distance(self, tour):
        total = 0.0
        for i in range(len(tour) - 1):
            total += self.distances[tour[i]][tour[i + 1]]
        return total

    def _evaporate(self):
        self.pheromones *= (1 - self.evaporation_rate)
        self.pheromones  = np.clip(self.pheromones, 0.01, None)

    def _deposit(self, tour, distance):
        deposit = self.Q / distance
        for i in range(len(tour) - 1):
            self.pheromones[tour[i]][tour[i + 1]] += deposit
            self.pheromones[tour[i + 1]][tour[i]] += deposit   # grafo no dirigido

    def run(self):
        for iteration in range(self.num_iterations):
            all_tours = [self._build_tour() for _ in range(self.num_ants)]

            # Solo tours completos (que visitaron todas las ciudades)
            valid_tours = [t for t in all_tours if len(t) == self.n + 1]

            if not valid_tours:
                continue

            self._evaporate()

            # Depositar en todos los tours válidos
            for tour in valid_tours:
                self._deposit(tour, self._tour_distance(tour))

            # Actualizar mejor solución
            iteration_best = min(valid_tours, key=self._tour_distance)
            iteration_dist = self._tour_distance(iteration_best)

            if iteration_dist < self.best_distance:
                self.best_distance = iteration_dist
                self.best_tour     = iteration_best
                print(f"  [Iter {iteration+1:3d}] Nuevo mejor: {self.best_distance:.2f}")

            self.history.append(self.best_distance)

        return self.best_tour, self.best_distance

    def plot(self):
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))

        # ── Gráfico 1: el tour en el mapa de ciudades ──
        ax = axes[0]
        cx = [self.cities[i][0] for i in self.best_tour]
        cy = [self.cities[i][1] for i in self.best_tour]
        ax.plot(cx, cy, 'b-o', linewidth=2, markersize=8, zorder=3)
        for i, (x, y) in enumerate(self.cities):
            ax.annotate(f'C{i}', (x, y), textcoords='offset points',
                        xytext=(8, 8), fontsize=9)
        ax.scatter(self.cities[self.best_tour[0]][0],
                   self.cities[self.best_tour[0]][1],
                   color='red', s=200, zorder=5, label='Inicio/Fin')
        ax.set_title(f'Mejor Tour — Distancia: {self.best_distance:.2f}')
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.legend()
        ax.grid(True, alpha=0.4)

        # ── Gráfico 2: convergencia ──
        ax = axes[1]
        ax.plot(self.history, color='green', linewidth=2)
        ax.set_title('Convergencia — Distancia por Iteración')
        ax.set_xlabel('Iteración')
        ax.set_ylabel('Mejor distancia acumulada')
        ax.grid(True, alpha=0.4)

        plt.suptitle('ACO — Travelling Salesman Problem', fontsize=13, fontweight='bold')
        plt.tight_layout()
        plt.savefig('aco_tsp.png', dpi=150, bbox_inches='tight')
        plt.close()
        print("Gráfico guardado como 'aco_tsp.png'")


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    np.random.seed(42)

    # 10 ciudades con coordenadas aleatorias
    cities = [(np.random.randint(0, 100), np.random.randint(0, 100))
              for _ in range(10)]

    print("Ciudades:", cities)
    print()

    aco = ACO_TSP(
        cities,
        num_ants=20,
        num_iterations=100,
        alpha=1.0,
        beta=5.0,
        evaporation_rate=0.3,
        Q=100
    )

    tour, distance = aco.run()

    print(f"\nMejor tour:     {tour}")
    print(f"Distancia total: {distance:.2f}")
    aco.plot()