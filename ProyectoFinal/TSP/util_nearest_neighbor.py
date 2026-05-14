from typing import List


# find the best path using the nearest neighbor heuristic

# ciudad: dict[str, tuple[float, float]], ex: {'A': (0.0, 0.0), 'B': (1.0, 1.0), 'C': (2.0, 2.0)}
# distancias: dict[tuple[str, str], float], ex: {('A', 'B'): 1.4142135623730951, ('A', 'C'): 2.8284271247461903, ('B', 'C'): 1.4142135623730951}

def nearest_neighbor(ciudad: dict[str, tuple[float, float]], distancias: dict[tuple[str, str], float]) -> List[str]:
    cities = list(ciudad.keys())
    first_city = cities[0]
    cities.remove(first_city)
    path = [first_city]
    current_city = first_city
    while cities:
        next_city = min(cities, key=lambda city: distancias[(current_city, city)])
        cities.remove(next_city)
        path.append(next_city)
        current_city = next_city
    # add first city to close the path
    path.append(first_city)
    return path