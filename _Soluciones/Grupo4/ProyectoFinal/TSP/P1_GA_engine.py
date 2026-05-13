import csv
import math
import random
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple

City = Tuple[float, float]
Route = List[int]


def load_cities_from_csv(csv_path: Path | str) -> List[City]:
    path = Path(csv_path)
    cities: List[City] = []
    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cities.append((float(row["x"]), float(row["y"])))

    if not cities:
        raise ValueError(f"No se encontraron ciudades en {path}")
    return cities


def load_cities_from_tsplib(tsp_path: Path | str) -> List[City]:
    path = Path(tsp_path)
    lines = path.read_text(encoding="utf-8").splitlines()

    in_coords = False
    cities: List[City] = []
    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        if line.upper() == "NODE_COORD_SECTION":
            in_coords = True
            continue
        if line.upper() == "EOF":
            break
        if not in_coords:
            continue

        parts = line.split()
        if len(parts) < 3:
            continue

        x = float(parts[1])
        y = float(parts[2])
        cities.append((x, y))

    if not cities:
        raise ValueError(f"No se encontraron coordenadas TSPLIB en {path}")
    return cities


def build_distance_matrix(cities: Sequence[City]) -> List[List[float]]:
    n = len(cities)
    matrix = [[0.0] * n for _ in range(n)]
    for i in range(n):
        xi, yi = cities[i]
        for j in range(i + 1, n):
            xj, yj = cities[j]
            d = math.dist((xi, yi), (xj, yj))
            matrix[i][j] = d
            matrix[j][i] = d
    return matrix


def route_distance(route: Sequence[int], distance_matrix: List[List[float]]) -> float:
    total = 0.0
    n = len(route)
    for i in range(n):
        a = route[i]
        b = route[(i + 1) % n]
        total += distance_matrix[a][b]
    return total


def is_valid_route(route: Sequence[int], n_cities: int) -> bool:
    if len(route) != n_cities:
        return False
    if any((city < 0 or city >= n_cities) for city in route):
        return False
    return len(set(route)) == n_cities


def assert_valid_route(route: Sequence[int], n_cities: int, where: str = "") -> None:
    if not is_valid_route(route, n_cities):
        place = f" en {where}" if where else ""
        raise ValueError(f"Ruta inválida{place}: repetidos/faltantes/rango incorrecto")


def random_route(n_cities: int, rng: random.Random) -> Route:
    route = list(range(n_cities))
    rng.shuffle(route)
    assert_valid_route(route, n_cities, "random_route")
    return route


def nearest_neighbor_route(distance_matrix: List[List[float]], start: int = 0) -> Route:
    n = len(distance_matrix)
    unvisited: set[int] = set(range(n))
    unvisited.remove(start)

    route = [start]
    current = start

    while unvisited:
        nxt = min(unvisited, key=lambda c: distance_matrix[current][c])
        route.append(nxt)
        unvisited.remove(nxt)
        current = nxt

    assert_valid_route(route, n, "nearest_neighbor_route")
    return route


def initialize_population(
    n_pop: int,
    distance_matrix: List[List[float]],
    greedy_ratio: float = 0.2,
    seed: int = 42,
) -> List[Route]:
    n_cities = len(distance_matrix)
    rng = random.Random(seed)

    n_greedy = int(n_pop * greedy_ratio)
    population: List[Route] = []

    for _ in range(n_greedy):
        start = rng.randrange(n_cities)
        route = nearest_neighbor_route(distance_matrix, start=start)
        assert_valid_route(route, n_cities, "initialize_population.greedy")
        population.append(route)

    for _ in range(n_pop - n_greedy):
        route = random_route(n_cities, rng)
        assert_valid_route(route, n_cities, "initialize_population.random")
        population.append(route)

    return population


def ox_crossover(parent1: Sequence[int], parent2: Sequence[int], rng: random.Random) -> Route:
    n = len(parent1)
    i, j = sorted(rng.sample(range(n), 2))

    child = [-1] * n
    child[i : j + 1] = parent1[i : j + 1]

    p2_idx = (j + 1) % n
    child_idx = (j + 1) % n

    while -1 in child:
        candidate = parent2[p2_idx]
        if candidate not in child:
            child[child_idx] = candidate
            child_idx = (child_idx + 1) % n
        p2_idx = (p2_idx + 1) % n

    assert_valid_route(child, n, "ox_crossover")
    return child


def inversion_mutation(route: Sequence[int], rng: random.Random) -> Route:
    n = len(route)
    i, j = sorted(rng.sample(range(n), 2))
    mutated = list(route)
    mutated[i : j + 1] = reversed(mutated[i : j + 1])
    assert_valid_route(mutated, n, "inversion_mutation")
    return mutated


def swap_mutation(route: Sequence[int], rng: random.Random) -> Route:
    n = len(route)
    i, j = rng.sample(range(n), 2)
    mutated = list(route)
    mutated[i], mutated[j] = mutated[j], mutated[i]
    assert_valid_route(mutated, n, "swap_mutation")
    return mutated


def tournament_select(
    population: List[Route],
    fitnesses: List[float],
    tournament_size: int,
    rng: random.Random,
) -> Route:
    indices = rng.sample(range(len(population)), tournament_size)
    winner_idx: int = min(indices, key=lambda idx: fitnesses[idx])
    return list(population[winner_idx])


def select_elite(population: List[Route], fitnesses: List[float], elite_size: int) -> List[Route]:
    ranked: List[int] = sorted(range(len(population)), key=lambda idx: fitnesses[idx])
    return [list(population[idx]) for idx in ranked[:elite_size]]


def build_next_generation(
    population: List[Route],
    distance_matrix: List[List[float]],
    p_crossover: float,
    p_mutation: float,
    rng: random.Random,
    tournament_size: int = 3,
    elite_size: int = 1,
    mutation_operator: str = "inversion",
) -> List[Route]:
    if not 0 <= p_crossover <= 1:
        raise ValueError("p_crossover debe estar en [0, 1]")
    if not 0 <= p_mutation <= 1:
        raise ValueError("p_mutation debe estar en [0, 1]")
    if tournament_size < 2 or tournament_size > len(population):
        raise ValueError("tournament_size debe estar entre 2 y n_pop")
    if elite_size < 0 or elite_size > len(population):
        raise ValueError("elite_size debe estar entre 0 y n_pop")

    n_pop = len(population)
    n_cities = len(population[0])
    fitnesses = [route_distance(route, distance_matrix) for route in population]

    next_population = select_elite(population, fitnesses, elite_size)

    while len(next_population) < n_pop:
        parent1 = tournament_select(population, fitnesses, tournament_size, rng)
        parent2 = tournament_select(population, fitnesses, tournament_size, rng)

        child = ox_crossover(parent1, parent2, rng) if rng.random() < p_crossover else list(parent1)

        if rng.random() < p_mutation:
            if mutation_operator == "inversion":
                child = inversion_mutation(child, rng)
            elif mutation_operator == "swap":
                child = swap_mutation(child, rng)
            else:
                raise ValueError("mutation_operator debe ser 'inversion' o 'swap'")

        assert_valid_route(child, n_cities, "build_next_generation.child")
        next_population.append(child)

    return next_population


def population_unique_ratio(population: Sequence[Sequence[int]]) -> float:
    if not population:
        return 0.0
    unique_routes = {tuple(route) for route in population}
    return len(unique_routes) / len(population)


def nearest_neighbor_baseline(distance_matrix: List[List[float]], start: int = 0) -> Tuple[Route, float]:
    route = nearest_neighbor_route(distance_matrix, start=start)
    fitness = route_distance(route, distance_matrix)
    return route, fitness


def run_ga(config: dict) -> dict:
    required_keys = ["cities", "n_pop", "n_gen", "p_crossover", "p_mutation"]
    missing_keys = [key for key in required_keys if key not in config]
    if missing_keys:
        raise ValueError(f"Faltan llaves requeridas en config: {missing_keys}")

    cities_raw: Iterable[Sequence[float]] = config["cities"]
    cities: List[City] = [(float(c[0]), float(c[1])) for c in cities_raw]
    if len(cities) < 2:
        raise ValueError("config['cities'] debe contener al menos 2 ciudades")

    n_pop = int(config["n_pop"])
    n_gen = int(config["n_gen"])
    p_crossover = float(config["p_crossover"])
    p_mutation = float(config["p_mutation"])

    if n_pop < 2:
        raise ValueError("n_pop debe ser >= 2")
    if n_gen < 1:
        raise ValueError("n_gen debe ser >= 1")
    if not 0 <= p_crossover <= 1:
        raise ValueError("p_crossover debe estar en [0, 1]")
    if not 0 <= p_mutation <= 1:
        raise ValueError("p_mutation debe estar en [0, 1]")

    seed = int(config.get("seed", 42))
    greedy_ratio = float(config.get("greedy_ratio", 0.2))
    tournament_size = int(config.get("tournament_size", 3))
    elite_size = int(config.get("elite_size", 1))
    mutation_operator = str(config.get("mutation_operator", "inversion"))

    if not 0 <= greedy_ratio <= 1:
        raise ValueError("greedy_ratio debe estar en [0, 1]")
    if mutation_operator not in {"inversion", "swap"}:
        raise ValueError("mutation_operator debe ser 'inversion' o 'swap'")

    distance_matrix = build_distance_matrix(cities)
    population = initialize_population(
        n_pop=n_pop,
        distance_matrix=distance_matrix,
        greedy_ratio=greedy_ratio,
        seed=seed,
    )
    rng = random.Random(seed)

    best_route: Route | None = None
    best_fitness = math.inf
    fitness_history: List[dict] = []
    diversity_history: List[float] = []

    for _ in range(n_gen):
        fitnesses = [route_distance(route, distance_matrix) for route in population]
        best_idx = min(range(len(population)), key=lambda idx: fitnesses[idx])

        current_best = list(population[best_idx])
        current_best_fitness = fitnesses[best_idx]

        if current_best_fitness < best_fitness:
            best_fitness = current_best_fitness
            best_route = current_best

        fitness_history.append(
            {
                "best": current_best_fitness,
                "avg": sum(fitnesses) / len(fitnesses),
                "worst": max(fitnesses),
            }
        )
        diversity_history.append(population_unique_ratio(population))

        population = build_next_generation(
            population=population,
            distance_matrix=distance_matrix,
            p_crossover=p_crossover,
            p_mutation=p_mutation,
            rng=rng,
            tournament_size=tournament_size,
            elite_size=elite_size,
            mutation_operator=mutation_operator,
        )

    if best_route is None:
        raise RuntimeError("No se pudo calcular best_route")

    n_cities = len(cities)
    assert_valid_route(best_route, n_cities, "run_ga.best_route")
    for route in population:
        assert_valid_route(route, n_cities, "run_ga.final_population")

    return {
        "best_route": best_route,
        "best_fitness": best_fitness,
        "fitness_history": fitness_history,
        "diversity_history": diversity_history,
        "final_population": population,
    }


def compare_ga_with_nearest_neighbor(config: dict, start_city: int = 0) -> dict:
    ga_result = run_ga(config)
    cities_raw: Iterable[Sequence[float]] = config["cities"]
    cities: List[City] = [(float(c[0]), float(c[1])) for c in cities_raw]
    distance_matrix = build_distance_matrix(cities)
    nn_route, nn_fitness = nearest_neighbor_baseline(distance_matrix, start=start_city)

    ga_best = ga_result["best_fitness"]
    if nn_fitness <= 0:
        relative_error_pct = float("nan")
        improvement_vs_nn_pct = float("nan")
    else:
        relative_error_pct = ((ga_best - nn_fitness) / nn_fitness) * 100.0
        improvement_vs_nn_pct = ((nn_fitness - ga_best) / nn_fitness) * 100.0

    return {
        "ga_result": ga_result,
        "nn_route": nn_route,
        "nn_fitness": nn_fitness,
        "ga_best_fitness": ga_best,
        "relative_error_vs_nn_pct": relative_error_pct,
        "improvement_vs_nn_pct": improvement_vs_nn_pct,
    }


__all__ = [
    "City",
    "Route",
    "load_cities_from_csv",
    "load_cities_from_tsplib",
    "build_distance_matrix",
    "route_distance",
    "is_valid_route",
    "assert_valid_route",
    "random_route",
    "nearest_neighbor_route",
    "initialize_population",
    "ox_crossover",
    "inversion_mutation",
    "swap_mutation",
    "tournament_select",
    "select_elite",
    "build_next_generation",
    "population_unique_ratio",
    "nearest_neighbor_baseline",
    "run_ga",
    "compare_ga_with_nearest_neighbor",
]
