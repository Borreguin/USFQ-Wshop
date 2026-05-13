import random
from pathlib import Path

# generate cities for TSP problem and save them in a file
seeds = [123, 456, 789, 101112, 131415, 161718, 192021, 222324, 252627, 282930]
n_cities = 100
dataset_dir = Path(__file__).resolve().parent


def generate_unique_cities(total_cities: int, seed: int) -> list[tuple[str, float, float]]:
    rng = random.Random(seed)
    cities: list[tuple[str, float, float]] = []
    for i in range(total_cities):
        city = f"C{i:03d}"
        x = round(rng.uniform(-100, 100), 1)
        y = round(rng.uniform(-100, 100), 1)
        cities.append((city, x, y))
    return cities


for seed in seeds:
    cities = generate_unique_cities(n_cities, seed)
    filename = f"cities_{n_cities}_{seed}.csv"
    header = "city,x,y\n"
    file_path = dataset_dir / filename
    with file_path.open("w", encoding="utf-8") as f:
        f.write(header)
        for city, x, y in cities:
            f.write(f"{city},{x},{y}\n")
