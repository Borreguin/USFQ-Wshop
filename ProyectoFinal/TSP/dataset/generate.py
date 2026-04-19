from os import path

from Taller1.P1_TSP.util import generar_ciudades

# generate cities for TSP problem and save them in a file
seeds = [123, 456, 789, 101112, 131415, 161718, 192021, 222324, 252627, 282930]
n_cities = 100
current_path = __file__
for seed in seeds:
    cities = generar_ciudades(n_cities, seed)
    filename = f"cities_{n_cities}_{seed}.csv"
    header = "city,x,y\n"
    file_path = path.join(path.dirname(current_path), filename)
    with open(file_path, "w") as f:
        f.write(header)
        for city, (x, y) in cities.items():
            f.write(f"{city},{x},{y}\n")
