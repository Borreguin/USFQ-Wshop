from typing import List, Tuple
from Taller1.P1_TSP.util import plotear_ruta, generar_ciudades_con_distancias


class TSP:
    def __init__(self, ciudades, distancias):
        self.ciudades = ciudades
        self.distancias = distancias
        # Build adjacency dict: destinos[city] = {neighbor: distance, ...}
        self.destinos = {}
        keys = list(distancias.keys())
        for ciudad in ciudades:
            if ciudad not in self.destinos:
                self.destinos[ciudad] = {}
            for key in keys:
                if ciudad == key[0]:
                    self.destinos[ciudad][key[1]] = distancias[key]

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _tour_distance(self, tour: List[str]) -> float:
        """Return the total distance of a closed tour (last city → first city included)."""
        total = 0.0
        n = len(tour)
        for i in range(n - 1):
            total += self.destinos[tour[i]][tour[i + 1]]
        # Close the loop back to the start
        total += self.destinos[tour[-1]][tour[0]]
        return total

    def _nearest_neighbor_tour(self, start_city: str) -> List[str]:
        """Build a greedy nearest-neighbor tour starting from *start_city*."""
        visited = {start_city}
        path = [start_city]
        while len(visited) < len(self.ciudades):
            current = path[-1]
            best_city, best_dist = None, float('inf')
            for neighbor, dist in self.destinos[current].items():
                if neighbor not in visited and dist < best_dist:
                    best_dist = dist
                    best_city = neighbor
            path.append(best_city)
            visited.add(best_city)
        return path  # open tour; caller closes it when computing distance

    def _two_opt(self, tour: List[str]) -> List[str]:
        """
        Improve a tour with 2-opt local search.

        Repeatedly reverses segments of the tour whenever doing so reduces
        the total distance, until no improving swap can be found.
        """
        n = len(tour)
        improved = True
        best_tour = tour[:]
        best_dist = self._tour_distance(best_tour)

        while improved:
            improved = False
            for i in range(1, n - 1):
                for j in range(i + 1, n):
                    # Reverse the segment between i and j
                    new_tour = best_tour[:i] + best_tour[i:j + 1][::-1] + best_tour[j + 1:]
                    new_dist = self._tour_distance(new_tour)
                    if new_dist < best_dist - 1e-10:
                        best_tour = new_tour
                        best_dist = new_dist
                        improved = True
            # Restart the sweep with the improved tour
            tour = best_tour

        return best_tour

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def encontrar_la_ruta_mas_corta(self) -> Tuple[List[str], float]:
        """
        Find the shortest Hamiltonian cycle using multi-start nearest-neighbor
        construction followed by 2-opt local search.

        Strategy
        --------
        1. For every city as a potential starting point, build a greedy
           nearest-neighbor tour (O(n²) per start → O(n³) total).
        2. Improve each candidate tour with 2-opt edge swaps, which
           eliminates crossing edges and typically yields solutions
           within 5 % of optimal.
        3. Return the best tour found and its total distance.

        Returns
        -------
        best_path : List[str]
            Ordered list of city names forming the best closed tour
            (the first city is *not* repeated at the end).
        best_distance : float
            Total distance of that tour (including the return leg).
        """
        print("Pensando...........")
        cities = list(self.ciudades.keys())
        best_path: List[str] = []
        best_distance = float('inf')

        for start_city in cities:
            # 1. Greedy construction
            tour = self._nearest_neighbor_tour(start_city)
            # 2. Local-search improvement
            tour = self._two_opt(tour)
            # 3. Evaluate
            dist = self._tour_distance(tour)
            if dist < best_distance:
                best_distance = dist
                best_path = tour

        print(f"Mejor distancia encontrada: {best_distance:.2f}")
        return best_path, best_distance

    def plotear_resultado(self, ruta: List[str], mostrar_anotaciones: bool = True):
        plotear_ruta(self.ciudades, ruta, mostrar_anotaciones)

# ----------------------------------------------------------------------
# Study cases
# ----------------------------------------------------------------------
def study_case_1():
    n_cities = 10
    ciudades, distancias = generar_ciudades_con_distancias(n_cities)
    tsp = TSP(ciudades, distancias)
    ruta, distancia = tsp.encontrar_la_ruta_mas_corta()
    print(f"Ruta: {' → '.join(ruta)} → {ruta[0]}")
    tsp.plotear_resultado(ruta)

def study_case_2():
    n_cities = 100
    ciudades, distancias = generar_ciudades_con_distancias(n_cities)
    tsp = TSP(ciudades, distancias)
    ruta, distancia = tsp.encontrar_la_ruta_mas_corta()
    tsp.plotear_resultado(ruta, False)
