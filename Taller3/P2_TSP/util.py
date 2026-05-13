import random
import string
import math
from typing import List
import datetime as dt

from matplotlib import pyplot as plt

def generar_ciudades(n_cities: int):
    ciudades = {}
    for i in range(n_cities):
        ciudad = get_different_city_name(list(ciudades.keys()))
        x = round(random.uniform(-100, 100) ,1) # Coordenada x aleatoria entre -100 y 100
        y = round(random.uniform(-100, 100), 1)  # Coordenada y aleatoria entre -100 y 100
        ciudades[ciudad] = (x, y)
    return ciudades

def get_different_city_name(cities: List[str]):
    city = f"{random.choice(string.ascii_uppercase)}{random.randint(0,9)}"
    while city in cities:
        city = f"{random.choice(string.ascii_uppercase)}{random.randint(0,9)}"
    return city

def calcular_distancia(ciudad1, ciudad2):
    x1, y1 = ciudad1
    x2, y2 = ciudad2
    distancia = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    return distancia

def generar_distancias(ciudades):
    distancias = {}
    for ciudad1, coord1 in ciudades.items():
        for ciudad2, coord2 in ciudades.items():
            if ciudad1 != ciudad2:
                distancia = calcular_distancia(coord1, coord2)
                distancias[(ciudad1, ciudad2)] = distancia
    return distancias

def generar_ciudades_con_distancias(n_cities: int, seed: int =123):
    random.seed(seed)  # This fixes the seed for reproducibility
    ciudades = generar_ciudades(n_cities)
    distancias = generar_distancias(ciudades)
    return ciudades, distancias

def plotear_ruta(ciudades, distancias, ruta, mostrar_anotaciones=True):
    if None in ruta:
        print("La ruta contiene valores nulos, no se encontró una solución válida.")
        return
    # Extraer coordenadas de las ciudades
    coordenadas_x = [ciudades[ciudad][0] for ciudad in ruta]
    coordenadas_y = [ciudades[ciudad][1] for ciudad in ruta]

    # Trama de las ubicaciones de las ciudades
    plt.figure(figsize=(8, 6))
    plt.scatter(coordenadas_x, coordenadas_y, color='blue', label='Ciudades')

    # Trama del mejor camino encontrado
    plt.plot(coordenadas_x, coordenadas_y, linestyle='-', marker='o', color='red', label='Mejor Ruta')

    if mostrar_anotaciones:
        # Anotar las letras de las ciudades
        for i, ciudad in enumerate(ruta):
            plt.text(coordenadas_x[i], coordenadas_y[i], ciudad)

    # Calcular la distancia total de la ruta, agregando la distancia de regreso a la primera ciudad
    path_distance = calculate_path_distance(distancias, ruta)
    plt.xlabel('Coordenada X')
    plt.ylabel('Coordenada Y')
    plt.title('({:d}) Ciudades (Distancia: {:.2f})'.format(len(ciudades), path_distance))
    plt.legend()
    plt.grid(True)
    plt.show()




def get_path(edges: dict, initial_city: str, path: List[str]):
    next_node = edges.get(initial_city, None)
    if next_node is None:
        return [next_node]
    elif next_node in path:
        return path
    path.append(next_node)
    return get_path(edges, next_node, path)

def calculate_path_distance(distances: dict, path: List[str]):
    distance = 0
    for i in range(len(path) - 1):
        if path[i] is not None and path[i+1] is not None:
            distance += distances[(path[i], path[i+1])]
    return distance

def delta_time_mm_ss(delta_time: dt.timedelta):
    minutes, seconds = divmod(delta_time.seconds, 60)
    return f"{0 if minutes < 10 else ''}{minutes}:{0 if seconds < 10 else ''}{seconds}"

def get_min_distance(distances: dict):
    min_distance = min(distances.values())
    return min_distance

def get_max_distance(distances: dict):
    max_distance = max(distances.values())
    return max_distance

def get_average_distance(distances: dict):
    avg_distance = sum(distances.values()) / len(distances)
    return avg_distance

def get_mean_distance_for_city(city:str, distances: dict):
    acc_distances = 0
    neighbors = 0
    for k, v in distances.items():
        if city in k:
            acc_distances += v
            neighbors += 1
    return acc_distances / neighbors

def get_average_distance_for_city(distances: dict):
    cities = list(set([city for k in distances.keys() for city in k]))
    best_max_distances = {}
    for city in cities:
        best_max_distances[city] = get_mean_distance_for_city(city, distances)
    return best_max_distances

def get_min_distance_for_city(city:str, distances: dict):
    min_distance = None
    for d in distances.keys():
        if city in d:
            if min_distance is None or distances[d] < min_distance:
                min_distance = distances[d]
    return min_distance

def get_min_distances(distances: dict):
    cities = list(set([city for k in distances.keys() for city in k]))
    min_distances = {}
    for city in cities:
        min_distances[city] = get_min_distance_for_city(city, distances)
    return min_distances

def get_max_distance_for_city(city:str, distances: dict):
    max_distance = None
    for d in distances.keys():
        if city in d:
            if max_distance is None or distances[d] > max_distance:
                max_distance = distances[d]
    return max_distance

def get_max_distances(distances: dict):
    cities = list(set([city for k in distances.keys() for city in k]))
    max_distances = {}
    for city in cities:
        max_distances[city] = get_max_distance_for_city(city, distances)
    return max_distances